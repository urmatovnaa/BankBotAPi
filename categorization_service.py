import json
import logging
from models import QuestionCategory, db

class QuestionCategorizer:
    def __init__(self):
        self.default_categories = [
            {
                'name': 'Account Services',
                'description': 'Questions about checking, savings, and account management',
                'keywords': ['account', 'checking', 'savings', 'balance', 'statement', 'deposit', 'withdrawal', 'transfer', 'account type', 'minimum balance']
            },
            {
                'name': 'Loans & Credit',
                'description': 'Questions about loans, mortgages, and credit cards',
                'keywords': ['loan', 'mortgage', 'credit card', 'personal loan', 'auto loan', 'home loan', 'credit score', 'credit limit', 'interest rate', 'refinance']
            },
            {
                'name': 'Online Banking',
                'description': 'Questions about digital banking and mobile apps',
                'keywords': ['online banking', 'mobile app', 'digital', 'login', 'password', 'security', 'two-factor', 'mobile deposit', 'online payment']
            },
            {
                'name': 'Fees & Charges',
                'description': 'Questions about banking fees and charges',
                'keywords': ['fee', 'charge', 'cost', 'penalty', 'overdraft', 'ATM fee', 'monthly fee', 'maintenance fee', 'transaction fee']
            },
            {
                'name': 'Investment Services',
                'description': 'Questions about investment and wealth management',
                'keywords': ['investment', 'portfolio', 'stocks', 'bonds', 'mutual funds', 'retirement', '401k', 'IRA', 'financial advisor', 'wealth management']
            },
            {
                'name': 'Customer Service',
                'description': 'General customer service and support questions',
                'keywords': ['hours', 'location', 'branch', 'ATM', 'customer service', 'contact', 'phone', 'support', 'help', 'assistance']
            },
            {
                'name': 'Security & Fraud',
                'description': 'Questions about account security and fraud protection',
                'keywords': ['security', 'fraud', 'suspicious', 'protect', 'identity theft', 'phishing', 'scam', 'unauthorized', 'dispute', 'stolen']
            }
        ]
        
        self._initialized = False
    
    def initialize_categories(self):
        """Initialize default categories in the database if they don't exist"""
        if self._initialized:
            return
            
        try:
            existing_categories = QuestionCategory.query.count()
            if existing_categories == 0:
                for category_data in self.default_categories:
                    category = QuestionCategory(
                        name=category_data['name'],
                        description=category_data['description'],
                        keywords=json.dumps(category_data['keywords'])
                    )
                    db.session.add(category)
                db.session.commit()
                logging.info(f"Initialized {len(self.default_categories)} default categories")
            self._initialized = True
        except Exception as e:
            logging.error(f"Error initializing categories: {e}")
            db.session.rollback()
    
    def categorize_question(self, question_text):
        """
        Categorize a question based on keywords and content
        
        Args:
            question_text: The user's question
            
        Returns:
            QuestionCategory object or None
        """
        try:
            # Initialize categories if not done yet
            self.initialize_categories()
            
            question_lower = question_text.lower()
            categories = QuestionCategory.query.all()
            
            best_match = None
            best_score = 0
            
            for category in categories:
                keywords = json.loads(category.keywords or '[]')
                score = 0
                
                # Count keyword matches
                for keyword in keywords:
                    if keyword.lower() in question_lower:
                        score += 1
                
                # Weight by keyword density
                if len(keywords) > 0:
                    score = score / len(keywords)
                
                if score > best_score:
                    best_score = score
                    best_match = category
            
            # Only return a category if we have a reasonable match
            if best_score > 0.1:  # At least 10% keyword match
                return best_match
            
            return None
            
        except Exception as e:
            logging.error(f"Error categorizing question: {e}")
            return None
    
    def get_categories(self):
        """Get all available categories"""
        try:
            return QuestionCategory.query.all()
        except Exception as e:
            logging.error(f"Error getting categories: {e}")
            return []
    
    def get_category_stats(self):
        """Get statistics about category usage"""
        try:
            from sqlalchemy import func
            from models import ChatMessage
            
            stats = db.session.query(
                QuestionCategory.name,
                func.count(ChatMessage.id).label('count')
            ).outerjoin(ChatMessage).group_by(QuestionCategory.id, QuestionCategory.name).all()
            
            return [{'category': stat[0], 'count': stat[1]} for stat in stats]
        except Exception as e:
            logging.error(f"Error getting category stats: {e}")
            return []

# Create a global instance
question_categorizer = QuestionCategorizer()