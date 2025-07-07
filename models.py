from app import db
from datetime import datetime
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to chat messages
    messages = db.relationship('ChatMessage',
                               backref='user',
                               lazy=True,
                               cascade='all, delete-orphan')


class QuestionCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    keywords = db.Column(
        db.Text)  # JSON string of keywords for auto-categorization
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to chat messages
    messages = db.relationship('ChatMessage', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords
        }


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer,
                            db.ForeignKey('question_category.id'),
                            nullable=True)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to feedback
    feedback = db.relationship('MessageFeedback',
                               backref='message',
                               lazy=True,
                               cascade='all, delete-orphan',
                               passive_deletes=True)

    def to_dict(self):
        feedback_data = None
        if self.feedback:
            feedback_data = self.feedback[0].to_dict()

        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category_id.name if self.category_id else None,
            'feedback': feedback_data
        }


class MessageFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer,
                           db.ForeignKey('chat_message.id'),
                           ondelete='CASCADE')
    rating = db.Column(db.Integer, nullable=False)  # 1-5 star rating
    comment = db.Column(db.Text, nullable=True)
    is_helpful = db.Column(db.Boolean, nullable=True)  # True/False for helpful
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rating': self.rating,
            'comment': self.comment,
            'is_helpful': self.is_helpful,
            'created_at': self.created_at.isoformat()
        }
