import os
import logging
import re
from google import genai
from google.genai import types
from app import db
from decimal import Decimal

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

class BankingChatbot:
    def __init__(self):
        self.system_prompt = """
        Сиз жардамчы жана кесиптүү банк кызматчысысыз. Сиздин ролуңуз:
        
        1. Банк кызматтары тууралуу жалпы маалымат берүү (текущий эсептер, жинак эсептери, кредиттер, кредиттик карталар ж.б.)
        2. Кардарларга банк процедураларын жана процесстерин түшүнүүгө жардам берүү
        3. Жалпы банк суроолору жана тынчсызданууларында жардам берүү
        4. Каржы сабаттуулугу боюнча маалымат берүү
        5. Кардарларды тиешелүү ресурстарга багыттоо же эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну сунуштоо
        6. Жеке суроолорго жооп берүү: колдонуучунун банк эсебиндеги баланс, эсептердин тизмеси, акыркы транзакциялар, кимге жана канча акча которгон, жана акча которуу ассистенти катары иштөө (мисалы, "100 сомду Бакытка котор" ж.б.).
        
        МААНИЛҮҮ КӨРСӨТМӨЛӨР:
        - Эч качан эсеп номурлары, жеке номурлар, сыр сөздөр же PIN-коддор сыяктуу купуя маалыматты сурабаңыз же иштетпеңиз
        - Эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну дайыма эскертиңиз
        - Жалпы жана жеке банк темалары боюнча так, пайдалуу маалымат бериңиз
        - Кесиптүү, сылык жана боордоштук менен мамиле кылыңыз
        - Эгер бир нерсеге ишенбесеңиз, муну мойнуна алыңыз жана банкка кайрылууну сунуштаңыз
        - Өзгөчө каржы кеңештерин бербеңиз - жалпы маалымат гана
        - Жоопторду кыска, бирок маалымдуу кылыңыз
        
        Эсиңизде болсун: Сиз жалпы жана жеке банк суроолору боюнча жардам берүү жана маалымат берүү үчүн бул жердесиз, эсептерди көрүү же өзгөртүү үчүн эмес.
        
        МААНИЛҮҮ: Бардык жоопторуңузду кыргыз тилинде жазыңыз.
        """
    
    def get_personal_response(self, user, user_message):
        from models import Account, Transaction, User
        from sqlalchemy import func
        # Словари для перевода типов
        account_types_kg = {
            'savings': 'Жинак',
            'checking': 'Агымдагы',
        }
        tx_types_kg = {
            'deposit': 'Толуктоо',
            'withdrawal': 'Чыгым',
            'transfer': 'Которуу',
        }
        # Баланс
        if re.search(r'(баланс|канча акча|сколько.*денег|how much.*money|how much.*balance)', user_message, re.I):
            accounts = Account.query.filter_by(user_id=user.id).all()
            if not accounts:
                return "Сиздин банк эсебиңиз табылган жок."
            total = sum([float(a.balance) for a in accounts])
            return f"Сиздин бардык эсептериңиздеги жалпы сумма: {total:.2f} сом."
        # Список счетов
        if re.search(r'(эсептер|счета|accounts|list.*accounts)', user_message, re.I):
            accounts = Account.query.filter_by(user_id=user.id).all()
            if not accounts:
                return "Сиздин банк эсебиңиз табылган жок."
            resp = "Сиздин эсептериңиз:\n"
            for a in accounts:
                acc_type = account_types_kg.get(a.account_type, a.account_type)
                resp += f"- {acc_type}: {float(a.balance):.2f} сом\n"
            return resp
        # Последние транзакции (исправлено: используем только account_from_id и account_to_id)
        if re.search(r'(транзакц|transactions|акыркы которуулар|последние операции)', user_message, re.I):
            accounts = Account.query.filter_by(user_id=user.id).all()
            if not accounts:
                return "Сиздин банк эсебиңиз табылган жок."
            acc_ids = [a.id for a in accounts]
            txs = Transaction.query.filter(
                (Transaction.account_from_id.in_(acc_ids)) | (Transaction.account_to_id.in_(acc_ids))
            ).order_by(Transaction.timestamp.desc()).limit(5).all()
            if not txs:
                return "Акыркы транзакциялар табылган жок."
            resp = "Акыркы 5 транзакция:\n"
            for t in txs:
                tx_type = tx_types_kg.get(t.type, t.type)
                # Определяем направление
                if t.account_from_id in acc_ids and t.account_to_id:
                    # Исходящий перевод
                    to_acc = Account.query.get(t.account_to_id)
                    to_user = User.query.get(to_acc.user_id) if to_acc else None
                    direction = f"-> {to_user.name}" if to_user else "-> белгисиз"
                elif t.account_to_id in acc_ids and t.account_from_id:
                    # Входящий перевод
                    from_acc = Account.query.get(t.account_from_id)
                    from_user = User.query.get(from_acc.user_id) if from_acc else None
                    direction = f"<- {from_user.name}" if from_user else "<- белгисиз"
                else:
                    direction = ""
                resp += f"- {tx_type}: {float(t.amount):.2f} сом {direction}, {t.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            return resp
        # Кому я последний раз переводила?
        if re.search(r'(кому.*переводил|кому.*отправил|акыркы.*перевод|последний.*перевод|кому.*акча жибердим)', user_message, re.I):
            accounts = Account.query.filter_by(user_id=user.id).all()
            acc_ids = [a.id for a in accounts]
            tx = Transaction.query.filter(Transaction.account_from_id.in_(acc_ids), Transaction.account_to_id != None).order_by(Transaction.timestamp.desc()).first()
            if not tx:
                return "Сиз акыркы убакта эч кимге акча которгон эмессиз." 
            to_acc = Account.query.get(tx.account_to_id)
            to_user = User.query.get(to_acc.user_id) if to_acc else None
            name = to_user.name if to_user else "белгисиз"
            return f"Сиз акыркы жолу {float(tx.amount):.2f} сом {name} аттуу адамга которгонсуз." 
        # Перевести 100 сомов Бакыту
        m = re.match(r'которуу\s*(\d+)\s*сом(?:ов)?\s*(\w+)', user_message, re.I)
        if m:
            amount = float(m.group(1))
            to_name = m.group(2)
            # Найти получателя
            to_user = User.query.filter(func.lower(User.name) == to_name.lower()).first()
            if not to_user:
                return f"{to_name} аттуу колдонуучу табылган жок."
            from_acc = Account.query.filter_by(user_id=user.id).first()
            to_acc = Account.query.filter_by(user_id=to_user.id).first()
            if not from_acc or not to_acc:
                return "Эсептер табылган жок."
            if from_acc.balance < amount:
                return "Сиздин эсебиңизде жетиштүү каражат жок."
            # Совершаем перевод
            from_acc.balance -= amount
            to_acc.balance += amount
            tx = Transaction(account_id=from_acc.id, account_from_id=from_acc.id, account_to_id=to_acc.id, type="transfer", amount=amount, description=f"{user.name} -> {to_user.name}")
            db.session.add(tx)
            db.session.commit()
            return f"{amount:.2f} сом {to_user.name} аттуу адамга ийгиликтүү которулду!"
        # Перевести по ключевым словам на кыргызском
        m_kg = re.match(r'(которуу|жиберуу|жөнөт)\s*(\d+)\s*сом(?:ов)?\s*(\w+)', user_message, re.I)
        if m_kg:
            amount = float(m_kg.group(2))
            to_name = m_kg.group(3)
            to_user = User.query.filter(func.lower(User.name) == to_name.lower()).first()
            if not to_user:
                return f"{to_name} аттуу колдонуучу табылган жок."
            from_acc = Account.query.filter_by(user_id=user.id).first()
            to_acc = Account.query.filter_by(user_id=to_user.id).first()
            if not from_acc or not to_acc:
                return "Эсептер табылган жок."
            if from_acc.balance < amount:
                return "Сиздин эсебиңизде жетиштүү каражат жок."
            from_acc.balance -= amount
            to_acc.balance += amount
            tx = Transaction(account_from_id=from_acc.id, account_to_id=to_acc.id, type="Которуу", amount=amount, description=f"{user.name} -> {to_user.name}")
            db.session.add(tx)
            db.session.commit()
            return f"{amount:.2f} сом {to_user.name} аттуу адамга ийгиликтүү которулду!"
        # Распознавание разных вариантов перевода денег на кыргызском
        # Варианты: 'которуу 100 сом Айзадага', '100 сом Айзадага котор', 'Айзадага 100 сом жөнөт', 'жиберуу 100 сом Бакытка', и т.д.
        patterns = [
            r'(которуу|жиберуу|жөнөт)\s*(\d+)\s*сом(?:ов)?\s*(\w+)',
            r'(\d+)\s*сом(?:ов)?\s*(\w+)га?\s*(котор|жөнөт|жибер)',
            r'(\w+)га?\s*(\d+)\s*сом(?:ов)?\s*(котор|жөнөт|жибер)'
        ]
        for pat in patterns:
            m = re.match(pat, user_message, re.I)
            if m:
                # Определяем, где имя и сумма
                if pat == patterns[0]:
                    amount = float(m.group(2))
                    to_name = m.group(3)
                elif pat == patterns[1]:
                    amount = float(m.group(1))
                    to_name = m.group(2)
                elif pat == patterns[2]:
                    to_name = m.group(1)
                    amount = float(m.group(2))
                else:
                    continue
                print(to_name, amount)  
                to_user = User.query.filter(func.lower(User.name) == to_name.lower()).first()
                print(func.lower(User.name), to_name.lower())
                print(User.query.filter(func.lower(User.name) == to_name.lower()))

                if not to_user:
                    # Приводим имя к нижнему регистру и убираем окончания типа 'га', 'ге', 'ка', 'ке', 'на', 'не', 'га', 'ге', 'га', 'ге'
                    to_name_clean = to_name.lower()
                    # Сравниваем с именами пользователей без учета регистра
                    all_users = User.query.all()
                    found_user = None
                    print("Проверка пользователей:")
                    for u in all_users:
                        print(u.name, to_name_clean)
                        if u.name and u.name.lower() == to_name_clean:
                            found_user = u
                            break
                    if not found_user:
                        return f"{to_name} аттуу колдонуучу табылган жок."
                    to_user = found_user
                from_acc = Account.query.filter_by(user_id=user.id).first()
                to_acc = Account.query.filter_by(user_id=to_user.id).first()
                if not from_acc or not to_acc:
                    return "Эсептер табылган жок."
                if from_acc.balance < amount:
                    return "Сиздин эсебиңизде жетиштүү каражат жок."
                amount = Decimal(str(amount))
                from_acc.balance -= amount
                to_acc.balance += amount
                tx = Transaction(account_from_id=from_acc.id, account_to_id=to_acc.id, type="Которуу", amount=amount, description=f"{user.name} -> {to_user.name}")
                db.session.add(tx)
                db.session.commit()
                return f"{amount:.2f} сом {to_user.name} аттуу адамга ийгиликтүү которулду!"
        # Последние входящие транзакции (кто мне прислал денег)
        if re.search(r'(кимден.*акча|ким.*жөнөттү|последний.*полученный|акыркы.*келген|кто.*отправил|кто.*перевел.*мне)', user_message, re.I):
            accounts = Account.query.filter_by(user_id=user.id).all()
            if not accounts:
                return "Сиздин банк эсебиңиз табылган жок."
            acc_ids = [a.id for a in accounts]
            txs = Transaction.query.filter(Transaction.account_to_id.in_(acc_ids), Transaction.account_from_id != None).order_by(Transaction.timestamp.desc()).limit(5).all()
            if not txs:
                return "Акыркы келген акча табылган жок."
            resp = "Акыркы 5 келген акча:\n"
            for t in txs:
                from_acc = Account.query.get(t.account_from_id)
                from_user = User.query.get(from_acc.user_id) if from_acc else None
                name = from_user.name if from_user else "белгисиз"
                resp += f"- {float(t.amount):.2f} сом {name} аттуу адамдан, {t.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
            return resp
        return None

    def get_response(self, user_message: str, conversation_history: list = None, user=None) -> str:
        """
        Get a response from Gemini for the banking chatbot
        
        Args:
            user_message: The user's message
            conversation_history: List of previous messages for context
            
        Returns:
            The AI's response
        """
        try:
            # Build the conversation context
            conversation_context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                    conversation_context += f"User: {msg['message']}\nAssistant: {msg['response']}\n\n"
            
            # Construct the full prompt
            full_prompt = f"{self.system_prompt}\n\n"
            if conversation_context:
                full_prompt += f"Previous conversation:\n{conversation_context}"
            full_prompt += f"Current user message: {user_message}\n\nPlease provide a helpful response:"
            
            # Если персональный ответ найден, всегда возвращаем его (даже если пустая строка или False)
            if user:
                personal = self.get_personal_response(user, user_message)
                if personal is not None:
                    return personal
            
            # Generate response using Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=full_prompt)])
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=1000,
                    temperature=0.7,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "Кечиресиз, азыр жооп берүүдө кыйынчылык жаралууда. Кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."
        except Exception as e:
            logging.error(f"Error getting Gemini response: {e}")
            return "Кечиресиз, техникалык ката кетти. Бир аздан кийин кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."

# Create a global instance
banking_chatbot = BankingChatbot()
