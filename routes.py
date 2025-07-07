import uuid
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, ChatMessage, MessageFeedback, QuestionCategory
from gemini_service import banking_chatbot
from categorization_service import question_categorizer
from auth_utils import require_user, create_user_session, get_current_user, is_session_valid


@app.route('/')
def index():
    """Main chat interface - no longer creates user sessions"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_session():
    """
    Initialize user session and create user if needed.
    This should be called once on page load from the frontend.
    """
    try:
        # Check if session already exists and is valid
        if is_session_valid():
            user = get_current_user()
            return jsonify({
                'status': 'existing_session',
                'session_id': session['session_id'],
                'user_id': user.id,
                'created_at': user.created_at.isoformat()
            }), 200
        
        # Create new session and user
        user = create_user_session()
        
        return jsonify({
            'status': 'session_created',
            'session_id': session['session_id'],
            'user_id': user.id,
            'created_at': user.created_at.isoformat()
        }), 201
        
    except Exception as e:
        logging.error(f"Error initializing session: {e}")
        return jsonify({
            'error': 'Failed to initialize session',
            'details': str(e)
        }), 500


@app.route('/api/chat', methods=['POST'])
@require_user
def chat(user):
    """Handle chat messages - requires valid user session"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Get conversation history for context
        recent_messages = ChatMessage.query.filter_by(user_id=user.id)\
            .order_by(ChatMessage.timestamp.desc()).limit(5).all()

        conversation_history = []
        for msg in reversed(recent_messages):
            conversation_history.append({
                'message': msg.message,
                'response': msg.response
            })

        # Get AI response
        ai_response = banking_chatbot.get_response(user_message,
                                                   conversation_history)

        # Categorize the question
        category = question_categorizer.categorize_question(user_message)

        # Save the conversation
        chat_message = ChatMessage(
            user_id=user.id,
            message=user_message,
            response=ai_response,
            category_id=category.id if category else None)
        db.session.add(chat_message)
        db.session.commit()

        return jsonify({
            'response': ai_response,
            'message_id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat(),
            'category': category.name if category else None
        })

    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        return jsonify({'error':
                        'An error occurred processing your message'}), 500


@app.route('/api/history', methods=['GET'])
@require_user
def get_chat_history(user):
    """Get chat history for the current session"""
    try:
        # Get all messages for this user
        messages = ChatMessage.query.filter_by(user_id=user.id)\
            .order_by(ChatMessage.timestamp.asc()).all()

        return jsonify({'messages': [msg.to_dict() for msg in messages]})

    except Exception as e:
        logging.error(f"Error getting chat history: {e}")
        return jsonify({'error':
                        'An error occurred getting chat history'}), 500


@app.route('/api/clear', methods=['POST'])
@require_user
def clear_chat(user):
    """Clear chat history for the current session"""
    try:
        # Delete all messages for this user
        ChatMessage.query.filter_by(user_id=user.id).delete()
        db.session.commit()

        return jsonify({'success': True})

    except Exception as e:
        logging.error(f"Error clearing chat: {e}")
        return jsonify({'error':
                        'An error occurred clearing chat history'}), 500


@app.route('/api/feedback', methods=['POST'])
@require_user
def submit_feedback(user):
    """Submit feedback for a message"""
    try:
        data = request.get_json()
        message_id = data.get('message_id')
        rating = data.get('rating')
        comment = data.get('comment', '')
        is_helpful = data.get('is_helpful')

        if not message_id or not rating:
            return jsonify({'error':
                            'Message ID and rating are required'}), 400

        # Verify the message exists and belongs to the current user
        message = ChatMessage.query.filter_by(id=message_id,
                                              user_id=user.id).first()
        if not message:
            return jsonify({'error': 'Message not found'}), 404

        # Check if feedback already exists
        existing_feedback = MessageFeedback.query.filter_by(
            message_id=message_id).first()
        if existing_feedback:
            # Update existing feedback
            existing_feedback.rating = rating
            existing_feedback.comment = comment
            existing_feedback.is_helpful = is_helpful
        else:
            # Create new feedback
            feedback = MessageFeedback(message_id=message_id,
                                       rating=rating,
                                       comment=comment,
                                       is_helpful=is_helpful)
            db.session.add(feedback)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully'
        })

    except Exception as e:
        logging.error(f"Error submitting feedback: {e}")
        return jsonify({'error': 'An error occurred submitting feedback'}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all question categories"""
    try:
        categories = question_categorizer.get_categories()
        return jsonify(
            {'categories': [category.to_dict() for category in categories]})
    except Exception as e:
        logging.error(f"Error getting categories: {e}")
        return jsonify({'error': 'An error occurred getting categories'}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data for categories and feedback"""
    try:
        # Get category statistics
        category_stats = question_categorizer.get_category_stats()

        # Get feedback statistics
        from sqlalchemy import func
        feedback_stats = db.session.query(
            func.avg(MessageFeedback.rating).label('avg_rating'),
            func.count(MessageFeedback.id).label('total_feedback'),
            func.sum(
                func.case([(MessageFeedback.is_helpful == True, 1)],
                          else_=0)).label('helpful_count')).first()

        return jsonify({
            'category_stats': category_stats,
            'feedback_stats': {
                'average_rating':
                float(feedback_stats.avg_rating)
                if feedback_stats.avg_rating else 0,
                'total_feedback':
                feedback_stats.total_feedback,
                'helpful_count':
                feedback_stats.helpful_count or 0
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
