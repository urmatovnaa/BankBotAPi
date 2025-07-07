import uuid
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, ChatMessage
from gemini_service import banking_chatbot

@app.route('/')
def index():
    """Main chat interface"""
    # Create or get session ID
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        
        # Create user record
        user = User(session_id=session['session_id'])
        db.session.add(user)
        db.session.commit()
    
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Get user from session
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'Session not found'}), 400
        
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 400
        
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
        ai_response = banking_chatbot.get_response(user_message, conversation_history)
        
        # Save the conversation
        chat_message = ChatMessage(
            user_id=user.id,
            message=user_message,
            response=ai_response
        )
        db.session.add(chat_message)
        db.session.commit()
        
        return jsonify({
            'response': ai_response,
            'message_id': chat_message.id,
            'timestamp': chat_message.timestamp.isoformat()
        })
        
    except Exception as e:
        logging.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'An error occurred processing your message'}), 500

@app.route('/api/history', methods=['GET'])
def get_chat_history():
    """Get chat history for the current session"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'messages': []})
        
        user = User.query.filter_by(session_id=session_id).first()
        if not user:
            return jsonify({'messages': []})
        
        # Get all messages for this user
        messages = ChatMessage.query.filter_by(user_id=user.id)\
            .order_by(ChatMessage.timestamp.asc()).all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        logging.error(f"Error getting chat history: {e}")
        return jsonify({'error': 'An error occurred getting chat history'}), 500

@app.route('/api/clear', methods=['POST'])
def clear_chat():
    """Clear chat history for the current session"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'success': True})
        
        user = User.query.filter_by(session_id=session_id).first()
        if user:
            # Delete all messages for this user
            ChatMessage.query.filter_by(user_id=user.id).delete()
            db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error clearing chat: {e}")
        return jsonify({'error': 'An error occurred clearing chat history'}), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500
