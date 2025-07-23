from models import Account, Transaction, User
from sqlalchemy import func
from decimal import Decimal
from database import db
import pytz


LOCAL_TZ = pytz.timezone('Asia/Bishkek')

def format_local_time(dt):
    # If dt is naive, treat as UTC
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    else:
        dt = dt.astimezone(pytz.utc)
    return dt.astimezone(LOCAL_TZ).strftime('%Y-%m-%d %H:%M')

def get_balance(user):
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    total = sum([float(a.balance) for a in accounts])
    return total, f"Сиздин бардык эсептериңиздеги жалпы сумма: {total:.2f} сом."

def get_transactions(user, limit=5):
    account_types_kg = {
        'savings': 'Жинак',
        'checking': 'Агымдагы',
    }
    tx_types_kg = {
        'deposit': 'Толуктоо',
        'withdrawal': 'Чыгым',
        'transfer': 'Которуу',
    }
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    txs = Transaction.query.filter(
        (Transaction.account_from_id.in_(acc_ids)) | (Transaction.account_to_id.in_(acc_ids))
    ).order_by(Transaction.timestamp.desc()).limit(limit).all()
    if not txs:
        return [], "Акыркы транзакциялар табылган жок."
    resp = []
    for t in txs:
        tx_type = tx_types_kg.get(t.type, t.type)
        if t.account_from_id in acc_ids and t.account_to_id:
            to_acc = Account.query.get(t.account_to_id)
            to_user = User.query.get(to_acc.user_id) if to_acc else None
            direction = f"-> {to_user.name}" if to_user else "-> белгисиз"
        elif t.account_to_id in acc_ids and t.account_from_id:
            from_acc = Account.query.get(t.account_from_id)
            from_user = User.query.get(from_acc.user_id) if from_acc else None
            direction = f"<- {from_user.name}" if from_user else "<- белгисиз"
        else:
            direction = ""
        resp.append({
            'type': tx_type,
            'amount': float(t.amount),
            'direction': direction,
            'timestamp': format_local_time(t.timestamp),
        })
    return resp, None

def get_last_incoming_transaction(user):
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    tx = Transaction.query.filter(
        Transaction.account_to_id.in_(acc_ids)
    ).order_by(Transaction.timestamp.desc()).first()
    if not tx:
        return None, "Сизге акыркы убакта акча которулган эмес."
    from_acc = Account.query.get(tx.account_from_id)
    from_user = User.query.get(from_acc.user_id) if from_acc else None
    sender = from_user.name if from_user else "белгисиз"
    return None, f"Сизге акыркы акчаны {sender} {float(tx.amount):.2f} сом которгон ({format_local_time(tx.timestamp)})."


def transfer_money(user, to_name, amount=0):
    users = User.query.all()
    
    to_user = User.query.filter(func.trim(User.name) == to_name.strip()).first()
    if not to_user:
        return False, f"{to_name} аттуу колдонуучу табылган жок."
    if not amount:
        return False, "Акча которуу суммасын көрсөтүңүз."
    if user.id == to_user.id:
        return False, "Сиз өзүңүзгө которо албайсыз."
    from_acc = Account.query.filter_by(user_id=user.id).first()
    to_acc = Account.query.filter_by(user_id=to_user.id).first()
    if not from_acc or not to_acc:
        return False, "Эсептер табылган жок."
    if from_acc.balance < amount:
        return False, "Сиздин эсебиңизде жетиштүү каражат жок."
    amount = Decimal(str(amount))
    from_acc.balance -= amount
    to_acc.balance += amount
    tx = Transaction(account_from_id=from_acc.id, account_to_id=to_acc.id, type="Которуу", amount=amount, description=f"{user.name} -> {to_user.name}")
    db.session.add(tx)
    db.session.commit()
    return True, f"{amount:.2f} сом {to_user.name} аттуу адамга ийгиликтүү которулду!"

def get_accounts_info(user):
    """
    Колдонуучунун бардык эсептеринин тизмеси жана балансы.
    """
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    resp = []
    for acc in accounts:
        resp.append({
            'account_type': acc.account_type,
            'balance': float(acc.balance)
        })
    return resp, None


def get_incoming_sum_for_period(user, start_date, end_date):
    """
    Көрсөтүлгөн аралыкта кирген которуулар (входящие) жалпы суммасы.
    start_date, end_date — строки 'YYYY-MM-DD' формата
    """
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    txs = Transaction.query.filter(
        Transaction.account_to_id.in_(acc_ids),
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    ).all()
    total = sum([float(t.amount) for t in txs])
    return total, f"{start_date} - {end_date} аралыгында кирген которуулар: {total:.2f} сом."


def get_outgoing_sum_for_period(user, start_date, end_date):
    """
    Көрсөтүлгөн аралыкта чыккан которуулар (исходящие) жалпы суммасы.
    start_date, end_date — строки 'YYYY-MM-DD' формата
    """
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    txs = Transaction.query.filter(
        Transaction.account_from_id.in_(acc_ids),
        Transaction.timestamp >= start_date,
        Transaction.timestamp <= end_date
    ).all()
    total = sum([float(t.amount) for t in txs])
    return total, f"{start_date} - {end_date} аралыгында чыккан которуулар: {total:.2f} сом."


def get_last_3_transfer_recipients(user):
    """
    Акыркы 3 которуунун алуучуларынын тизмеси.
    """
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    txs = Transaction.query.filter(
        Transaction.account_from_id.in_(acc_ids),
        Transaction.type == 'Которуу'
    ).order_by(Transaction.timestamp.desc()).limit(3).all()
    recipients = []
    for t in txs:
        to_acc = Account.query.get(t.account_to_id)
        to_user = User.query.get(to_acc.user_id) if to_acc else None
        recipients.append(to_user.name if to_user else "белгисиз")
    return recipients, None


def get_largest_transaction(user):
    """
    Эң чоң транзакция (суммасы боюнча) жана анын багыты.
    """
    accounts = Account.query.filter_by(user_id=user.id).all()
    if not accounts:
        return None, "Сиздин банк эсебиңиз табылган жок."
    acc_ids = [a.id for a in accounts]
    tx = Transaction.query.filter(
        (Transaction.account_from_id.in_(acc_ids)) | (Transaction.account_to_id.in_(acc_ids))
    ).order_by(Transaction.amount.desc()).first()
    if not tx:
        return None, "Транзакциялар табылган жок."
    direction = ""
    if tx.account_from_id in acc_ids and tx.account_to_id:
        to_acc = Account.query.get(tx.account_to_id)
        to_user = User.query.get(to_acc.user_id) if to_acc else None
        direction = f"-> {to_user.name}" if to_user else "-> белгисиз"
    elif tx.account_to_id in acc_ids and tx.account_from_id:
        from_acc = Account.query.get(tx.account_from_id)
        from_user = User.query.get(from_acc.user_id) if from_acc else None
        direction = f"<- {from_user.name}" if from_user else "<- белгисиз"
    return {
        'amount': float(tx.amount),
        'direction': direction,
        'timestamp': format_local_time(tx.timestamp)
    }, None
