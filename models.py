from database import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)          
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)  # хэш пароля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, 
                           default=datetime.utcnow, 
                           onupdate=datetime.utcnow)

    # Relationship to chat messages
    messages = db.relationship('ChatMessage',
                               backref='user',
                               lazy=True,
                               cascade='all, delete-orphan')
    accounts = db.relationship('Account', 
                               backref='user', 
                               lazy=True,         
                               cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Account(db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # checking, savings и т.п.
    balance = db.Column(db.Numeric(15, 2), default=0.0, nullable=False)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Исходящие транзакции (отправленные)
    outgoing_transactions = db.relationship(
        'Transaction',
        backref='from_account',
        lazy=True,
        cascade='all, delete-orphan',
        foreign_keys='Transaction.account_from_id'
    )
    # Входящие транзакции (полученные)
    incoming_transactions = db.relationship(
        'Transaction',
        backref='to_account',
        lazy=True,
        cascade='all, delete-orphan',
        foreign_keys='Transaction.account_to_id'
    )


class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    account_from_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'), nullable=True)
    account_to_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete='CASCADE'), nullable=True)
    type = db.Column(db.String(50), nullable=False)  # deposit, withdrawal, transfer
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    

class QuestionCategory(db.Model):
    __tablename__ = 'question_category'

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
    __tablename__ = 'chat_message'

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
    __tablename__ = 'message_feedback'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(
        db.Integer, db.ForeignKey('chat_message.id', ondelete='CASCADE'))
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
