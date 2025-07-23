import logging
from functools import wraps
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, ChatMessage, MessageFeedback, QuestionCategory
# from gemini_service import banking_chatbot
from aitilbot import AitilBankingChatbot
from categorization_service import question_categorizer

import asyncio

banking_chatbot = AitilBankingChatbot()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
        return f(user, *args, **kwargs)
    return decorated_function


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400

    user = User(name=name, email=email)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Registration successful'}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', '').lower()
    password = data.get('password', '')

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Сохраняем user id в сессии для идентификации
    session['user_id'] = user.id

    return jsonify({'message': 'Login successful', 'user_id': user.id})


@app.route('/api/logout', methods=['POST'])
@login_required
def logout(user):
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})


@app.route('/')
def index():
    """Main chat interface - no longer creates user sessions"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
@login_required
def chat(user):
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        recent_messages = ChatMessage.query.filter_by(user_id=user.id)\
            .order_by(ChatMessage.timestamp.desc()).limit(5).all()

        conversation_history = [
            {'message': msg.message, 'response': msg.response}
            for msg in reversed(recent_messages)
        ]

        # Передаем user в get_response
        # ai_response = banking_chatbot.get_response(user_message, conversation_history, user=user)
        ai_response = asyncio.run(banking_chatbot.get_response(user_message, conversation_history, user=user))
        # ai_response = asyncio.run(AitilBankingChatbot.get_response(user_message, conversation_history, user=user))
        category = question_categorizer.categorize_question(user_message)

        chat_message = ChatMessage(
            user_id=user.id,
            message=user_message,
            response=ai_response,
            category_id=category.id if category else None
        )
        db.session.add(chat_message)
        db.session.commit()

        return jsonify({
            'response': ai_response,
            'message_id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat(),
            'category': category.name if category else None,
            'user_name': user.name if user.name else None
        })

    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'An error occurred processing your message'}), 500


@app.route('/api/history', methods=['GET'])
@login_required
def get_chat_history(user):
    try:
        messages = ChatMessage.query.filter_by(user_id=user.id).order_by(ChatMessage.timestamp.asc()).all()
        return jsonify({
            'messages': [msg.to_dict() for msg in messages],
            'user_name': user.name if user.name else None
        })
    except Exception as e:
        logging.error(f"Error getting chat history: {e}")
        return jsonify({'error': 'An error occurred getting chat history'}), 500

@app.route('/api/user', methods=['GET'])
@login_required
def get_user_info(user):
    try:
        return jsonify({
            'user_name': user.name if user.name else None,
            'email': user.email
        })
    except Exception as e:
        logging.error(f"Error getting user info: {e}")
        return jsonify({'error': 'An error occurred getting user info'}), 500


@app.route('/api/clear', methods=['POST'])
@login_required
def clear_chat(user):
    try:
        ChatMessage.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error clearing chat: {e}")
        return jsonify({'error': 'An error occurred clearing chat history'}), 500


@app.route('/api/feedback', methods=['POST'])
@login_required
def submit_feedback(user):
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        is_helpful = data.get('is_helpful')

        if not message_id or not rating:
            return jsonify({'error': 'Message ID and rating are required'}), 400

        message = ChatMessage.query.filter_by(id=message_id, user_id=user.id).first()
        if not message:
            return jsonify({'error': 'Message not found'}), 404

        existing_feedback = MessageFeedback.query.filter_by(message_id=message_id).first()
        if existing_feedback:
            existing_feedback.rating = rating
            existing_feedback.comment = comment
            existing_feedback.is_helpful = is_helpful
        else:
            feedback = MessageFeedback(
                message_id=message_id,
                rating=rating,
                comment=comment,
                is_helpful=is_helpful
            )
            db.session.add(feedback)

        db.session.commit()
        return jsonify({'success': True, 'message': 'Feedback submitted successfully'})

    except Exception as e:
        logging.error(f"Error submitting feedback: {e}")
        return jsonify({'error': 'An error occurred submitting feedback'}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = question_categorizer.get_categories()
        return jsonify({'categories': [category.to_dict() for category in categories]})
    except Exception as e:
        logging.error(f"Error getting categories: {e}")
        return jsonify({'error': 'An error occurred getting categories'}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        category_stats = question_categorizer.get_category_stats()

        from sqlalchemy import func, case
        feedback_stats = db.session.query(
            func.avg(MessageFeedback.rating).label('avg_rating'),
            func.count(MessageFeedback.id).label('total_feedback'),
            func.sum(case((MessageFeedback.is_helpful == True, 1), else_=0)).label('helpful_count')
        ).first()

        return jsonify({
            'category_stats': category_stats,
            'feedback_stats': {
                'average_rating': float(feedback_stats.avg_rating or 0),
                'total_feedback': feedback_stats.total_feedback,
                'helpful_count': feedback_stats.helpful_count or 0
            }
        })

    except Exception as e:
        logging.error(f"Error getting analytics: {e}")
        return jsonify({'error': 'An error occurred getting analytics'}), 500


@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500