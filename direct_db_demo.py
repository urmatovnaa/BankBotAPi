# direct_db_demo.py
"""
Скрипт для прямых запросов к БД: создание пользователей, счетов и транзакций между ними.
"""
from app import app, db
from models import User, Account, Transaction
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_demo_data():
    with app.app_context():
        db.drop_all()
        db.create_all()
        # Создание пользователей
        user1 = User(name="Айзада", email="aizada@example.com", password_hash=generate_password_hash("pass1"))
        user2 = User(name="Бакыт", email="bakyt@example.com", password_hash=generate_password_hash("pass2"))
        user3 = User(name="Чынгыз", email="chyngyz@example.com", password_hash=generate_password_hash("pass3"))
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        # Счета (на кыргызском)
        acc1 = Account(user_id=user1.id, account_type="Жинак", balance=10000)
        acc2 = Account(user_id=user2.id, account_type="Агымдагы", balance=5000)
        acc3 = Account(user_id=user3.id, account_type="Жинак", balance=7000)
        acc4 = Account(user_id=user1.id, account_type="Агымдагы", balance=2000)
        acc5 = Account(user_id=user2.id, account_type="Жинак", balance=3000)
        db.session.add_all([acc1, acc2, acc3, acc4, acc5])
        db.session.commit()
        # Транзакции (типы и описания на кыргызском)
        tx1 = Transaction(account_from_id=acc1.id, account_to_id=acc2.id, type="Которуу", amount=1500, timestamp=datetime.now(), description="Айзада -> Бакыт (Которуу)")
        tx2 = Transaction(account_from_id=acc1.id, account_to_id=acc2.id, type="Толуктоо", amount=1500, timestamp=datetime.now(), description="Айзададан алынган каражат")
        tx3 = Transaction(account_from_id=None, account_to_id=acc3.id, type="Толуктоо", amount=2000, timestamp=datetime.now(), description="Айлык маяна")
        tx4 = Transaction(account_from_id=acc4.id, account_to_id=None, type="Чыгым", amount=500, timestamp=datetime.now(), description="Банкоматтан алуу")
        tx5 = Transaction(account_from_id=acc2.id, account_to_id=acc3.id, type="Которуу", amount=1000, timestamp=datetime.now(), description="Бакыт -> Чыңгыз (Которуу)")
        db.session.add_all([tx1, tx2, tx3, tx4, tx5])
        db.session.commit()
        print("Demo data created!")

if __name__ == "__main__":
    create_demo_data()
