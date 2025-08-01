import os
from dotenv import load_dotenv
load_dotenv()


import asyncio
from fastmcp import FastMCP
from bank_functions import (
    get_balance, get_transactions, transfer_money, get_last_incoming_transaction, 
    get_accounts_info, get_incoming_sum_for_period, get_outgoing_sum_for_period, 
    get_last_3_transfer_recipients, get_largest_transaction
)
from demir_functions import (
    list_all_card_names, get_card_details, compare_cards, get_card_limits, get_card_benefits, 
    get_cards_by_type, get_cards_by_payment_system, get_cards_by_fee_range, get_cards_by_currency,
    get_card_instructions, get_card_conditions, get_cards_with_features, get_card_recommendations,
    get_bank_info, get_bank_mission, get_bank_values, get_ownership_info, get_branch_network,
    get_contact_info, get_complete_about_us, get_about_us_section,
    list_all_deposit_names, get_deposit_details, compare_deposits, get_deposits_by_currency,
    get_deposits_by_term_range, get_deposits_by_min_amount, get_deposits_by_rate_range,
    get_deposits_with_replenishment, get_deposits_with_capitalization, get_deposits_by_withdrawal_type,
    get_deposit_recommendations, get_government_securities, get_child_deposits, get_online_deposits
)

from models import User
from app import app
import json
import logging


# Create FastMCP server
server = FastMCP("banking-mcp-server")

# Tool: Get balance
@server.tool(
    name="get_balance",
    description="Колдонуучунун бардык эсептериндеги жалпы балансты алуу."
)
async def get_balance_tool(user_id: int):
    """Get user's total balance across all accounts"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        _, result = get_balance(user)
        return result

# Tool: Get transactions (limit as function argument)
@server.tool(
    name="get_transactions",
    description="Колдонуучунун акыркы транзакцияларынын тизмесин алуу (5ке чейин)."
)
async def get_transactions_tool(user_id: int, limit: int = 5):
    """Get user's recent transactions"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        txs, err = get_transactions(user, limit=limit)
        if err:
            return err
        resp = "Акыркы транзакциялар:\n"
        for t in txs:
            resp += f"- {t['type']}: {t['amount']:.2f} сом {t['direction']}, {t['timestamp']}\n"
        return resp

# Tool: Transfer money (params from function signature)
@server.tool(
    name="transfer_money",
    description="Башка колдонуучуга аты боюнча акча которуу."
)
async def transfer_money_tool(user_id: int, to_name: str, amount: float = 0):
    """Transfer money to another user by name"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        ok, result = transfer_money(user, to_name, amount)
        return result

# Tool: Get last incoming transaction
@server.tool(
    name="get_last_incoming_transaction",
    description="Акыркы кирген транзакция тууралуу маалымат алуу (ким акча которду жана канча)."
)
async def get_last_incoming_transaction_tool(user_id: int):
    """Get information about the last incoming transaction"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        _, result = get_last_incoming_transaction(user)
        return result

# Tool: Get accounts info
@server.tool(
    name="get_accounts_info",
    description="Колдонуучунун бардык эсептеринин тизмеси жана балансы."
)
async def get_accounts_info_tool(user_id: int):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        accounts, err = get_accounts_info(user)
        if err:
            return err
        resp = "Сиздин эсептериңиз:\n"
        for acc in accounts:
            resp += f"- {acc['account_type']}: {acc['balance']:.2f} сом\n"
        return resp

# Tool: Get incoming sum for period
@server.tool(
    name="get_incoming_sum_for_period",
    description="Көрсөтүлгөн аралыкта кирген которуулар (входящие) жалпы суммасы."
)
async def get_incoming_sum_for_period_tool(user_id: int, start_date: str, end_date: str):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        total, msg = get_incoming_sum_for_period(user, start_date, end_date)
        return msg

# Tool: Get outgoing sum for period
@server.tool(
    name="get_outgoing_sum_for_period",
    description="Көрсөтүлгөн аралыкта чыккан которуулар (исходящие) жалпы суммасы."
)
async def get_outgoing_sum_for_period_tool(user_id: int, start_date: str, end_date: str):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        total, msg = get_outgoing_sum_for_period(user, start_date, end_date)
        return msg

# Tool: Get last 3 transfer recipients
@server.tool(
    name="get_last_3_transfer_recipients",
    description="Акыркы 3 которуунун алуучуларынын тизмеси."
)
async def get_last_3_transfer_recipients_tool(user_id: int):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        recipients, err = get_last_3_transfer_recipients(user)
        if err:
            return err
        if not recipients:
            return "Акыркы алуучулар табылган жок."
        resp = "Акыркы 3 алуучу:\n"
        for name in recipients:
            resp += f"- {name}\n"
        return resp

# Tool: Get largest transaction
@server.tool(
    name="get_largest_transaction",
    description="Эң чоң транзакция (суммасы боюнча) жана анын багыты."
)
async def get_largest_transaction_tool(user_id: int):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "Колдонуучу табылган жок."
        tx, err = get_largest_transaction(user)
        if err:
            return err
        return f"Эң чоң транзакция: {tx['amount']:.2f} сом {tx['direction']}, {tx['timestamp']}"

@server.tool(
    name="list_all_card_names",
    description="DemirBank'тагы бардык карталардын тизмесин кайтарат"
)
async def list_all_card_names_tool():
    result = list_all_card_names()
    result_text = ""
    for card in result:
        result_text += f"Карта аты: {card['name']}\n"
    return result_text

@server.tool(
    name="get_card_details",
    description="Карта аталышы боюнча бардык негизги маалыматты кайтарат (валюта, мөөнөтү, чыгымдар, лимиттер, сүрөттөмө)."
)
async def get_card_details_tool(card_name: str):
    result = get_card_details(card_name)
    result_text = ""
    for key, value in result.items():
        if key == "error":
            return result["error"]
        result_text += f"{key}: {value}\n"
    return result_text

@server.tool(
    name="compare_cards",
    description="Карталарды негизги параметрлер боюнча салыштырат. Аргумент катары карталардын аттарынын тизмеси берилет (2-4 карта)."
)
async def compare_cards_tool(card_names: list):
    cards = compare_cards(card_names)
    
    if len(cards) < 2:
        return "Карта салыштыруу үчүн эң азы 2 карта керек."
    
    # Бардык карталардан бардык уникалдуу ачкычтарды алуу
    all_keys = set()
    for card in cards:
        all_keys.update(card.keys())
    all_keys = list(all_keys)
    
    # Карталардын тизмеси
    result_text = "📋 Салыштырылган карталар:\n"
    for i, card in enumerate(cards, 1):
        result_text += f"{i}. {card['name']}\n"
    result_text += "\n"
    
    # Окшоштуктар жана айырмачылыктарды эсептөө
    similarities = []
    differences = []
    
    for key in all_keys:
        if key == "name":
            continue
            
        values = []
        for card in cards:
            value = card.get(key, "белгисиз")
            if isinstance(value, list):
                value = ", ".join(value)
            elif isinstance(value, dict):
                value = str(value)  # Словарьды строкага айландыруу
            values.append(value)
        
        # Бардык маанилер бирдейби? (словарьларды да эске алуу менен)
        unique_values = set()
        for val in values:
            if isinstance(val, dict):
                unique_values.add(str(val))
            else:
                unique_values.add(val)
        
        if len(unique_values) == 1:
            similarities.append((key, values[0]))
        else:
            diff_info = []
            for i, (card, value) in enumerate(zip(cards, values), 1):
                diff_info.append(f"{card['name']}: {value}")
            differences.append((key, diff_info))
    
    # Окшоштуктар бөлүмү
    result_text += "✅ Окшоштуктары:\n"
    if similarities:
        for key, value in similarities:
            key_name = key.replace('_', ' ').title()
            result_text += f"• {key_name}: {value}\n"
    else:
        result_text += "• Жок\n"
        
    # Айырмачылыктар бөлүмү
    result_text += "⚖️ Айырмачылыктары:\n"
    if differences:
        for key, diff_info in differences:
            key_name = key.replace('_', ' ').title()
            result_text += f"• {key_name}:\n"
            for info in diff_info:
                result_text += f"  - {info}\n"
    else:
        result_text += "• Жок\n"
    
    return result_text

@server.tool(
    name="get_card_limits",
    description="Карта аталышы боюнча лимиттерди кайтарат (ATM, POS, контактсыз ж.б.)."
)
async def get_card_limits_tool(card_name: str):
    result = get_card_limits(card_name)
    if "error" in result:
        return result["error"]
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@server.tool(
    name="get_card_benefits",
    description="Карта аталышы боюнча артыкчылыктарды жана өзгөчөлүктөрдү кайтарат."
)
async def get_card_benefits_tool(card_name: str):
    result = get_card_benefits(card_name)
    return json.dumps(result, ensure_ascii=False, indent=2)

@server.tool(
    name="get_cards_by_type",
    description="Карталарды түрү боюнча фильтрлейт (дебеттик/кредиттик)."
)
async def get_cards_by_type_tool(card_type: str):
    result = get_cards_by_type(card_type)
    result_text = f"📋 {card_type.title()} карталары:\n\n"
    for card in result:
        result_text += f"• {card['name']}\n"
    return result_text

@server.tool(
    name="get_cards_by_payment_system",
    description="Карталарды төлөм системасы боюнча фильтрлейт (Visa/Mastercard)."
)
async def get_cards_by_payment_system_tool(system: str):
    result = get_cards_by_payment_system(system)
    result_text = f"📋 {system.title()} карталары:\n\n"
    for card in result:
        result_text += f"• {card['name']}\n"
    return result_text

@server.tool(
    name="get_cards_by_fee_range",
    description="Карталарды жылдык акы диапазону боюнча фильтрлейт."
)
async def get_cards_by_fee_range_tool(min_fee: str = None, max_fee: str = None):
    result = get_cards_by_fee_range(min_fee, max_fee)
    result_text = "📋 Карталар:\n\n"
    for card in result:
        fee = card.get("annual_fee", "белгисиз")
        result_text += f"• {card['name']}: {fee}\n"
    return result_text

@server.tool(
    name="get_cards_by_currency",
    description="Карталарды валюта боюнча фильтрлейт (KGS, USD, EUR)."
)
async def get_cards_by_currency_tool(currency: str):
    result = get_cards_by_currency(currency)
    result_text = f"📋 {currency.upper()} валютасын колдогон карталар:\n\n"
    for card in result:
        result_text += f"• {card['name']}\n"
    return result_text

@server.tool(
    name="get_card_instructions",
    description="Картанын колдонуу көрсөтмөлөрүн кайтарат (Card Plus, Virtual Card үчүн)."
)
async def get_card_instructions_tool(card_name: str):
    result = get_card_instructions(card_name)
    if "error" in result:
        return result["error"]
    
    result_text = f"📖 {card_name} картасынын көрсөтмөлөрү:\n\n"
    for key, value in result.items():
        if isinstance(value, dict):
            result_text += f"🔹 {key.title()}:\n"
            for sub_key, sub_value in value.items():
                result_text += f"  • {sub_key}: {sub_value}\n"
        elif isinstance(value, list):
            result_text += f"🔹 {key.title()}:\n"
            for item in value:
                result_text += f"  • {item}\n"
        else:
            result_text += f"🔹 {key.title()}: {value}\n"
    return result_text

@server.tool(
    name="get_card_conditions",
    description="Картанын шарттарын жана талаптарын кайтарат (Elkart үчүн)."
)
async def get_card_conditions_tool(card_name: str):
    result = get_card_conditions(card_name)
    if "error" in result:
        return result["error"]
    
    result_text = f"📋 {card_name} картасынын шарттары:\n\n"
    for key, value in result.items():
        if isinstance(value, dict):
            result_text += f"🔹 {key.title()}:\n"
            for sub_key, sub_value in value.items():
                result_text += f"  • {sub_key}: {sub_value}\n"
        else:
            result_text += f"🔹 {key.title()}: {value}\n"
    return result_text

@server.tool(
    name="get_cards_with_features",
    description="Белгилүү өзгөчөлүктөргө ээ карталарды табат."
)
async def get_cards_with_features_tool(features: list):
    result = get_cards_with_features(features)
    result_text = f"📋 '{', '.join(features)}' өзгөчөлүктөрү бар карталар:\n\n"
    for card in result:
        result_text += f"• {card['name']}\n"
    return result_text

@server.tool(
    name="get_card_recommendations",
    description="Критерийлерге ылайык карта сунуштарын кайтарат."
)
async def get_card_recommendations_tool(criteria: dict):
    result = get_card_recommendations(criteria)
    result_text = "🎯 Карта сунуштары:\n\n"
    for i, card in enumerate(result, 1):
        score = card.get("recommendation_score", 0)
        fee = card.get("annual_fee", "белгисиз")
        result_text += f"{i}. {card['name']} (упай: {score})\n"
        result_text += f"   Жылдык акы: {fee}\n"
        if "descr" in card:
            descr = card["descr"][:100] + "..." if len(card["descr"]) > 100 else card["descr"]
            result_text += f"   Сүрөттөмө: {descr}\n"
        result_text += "\n"
    return result_text

@server.tool(
    name="get_bank_info",
    description="Банк тууралуу негизги маалыматты кайтарат (аты, негизделген жылы, лицензия)."
)
async def get_bank_info_tool():
    result = get_bank_info()
    result_text = f"🏦 {result['bank_name']}\n\n"
    result_text += f"📅 Негизделген: {result['founded']}\n"
    result_text += f"📜 Лицензия: {result['license']}\n"
    result_text += f"📝 Сүрөттөмө: {result['descr']}\n"
    return result_text

@server.tool(
    name="get_bank_mission",
    description="Банктын миссиясын жана тарыхын кайтарат."
)
async def get_bank_mission_tool():
    mission = get_bank_mission()
    result_text = "🎯 Банктын миссиясы:\n\n"
    result_text += mission
    return result_text

@server.tool(
    name="get_bank_values",
    description="Банктын баалуулуктарын жана принциптерин кайтарат."
)
async def get_bank_values_tool():
    values = get_bank_values()
    result_text = "💎 Банктын баалуулуктары:\n\n"
    for i, value in enumerate(values, 1):
        result_text += f"{i}. {value}\n"
    return result_text

@server.tool(
    name="get_ownership_info",
    description="Банктын ээлик маалыматтарын кайтарат."
)
async def get_ownership_info_tool():
    ownership = get_ownership_info()
    result_text = "👥 Ээлик маалыматтары:\n\n"
    result_text += f"🔹 Негизги акционер: {ownership.get('main_shareholder', 'белгисиз')}\n"
    result_text += f"🔹 Өлкө: {ownership.get('country', 'белгисиз')}\n"
    result_text += f"🔹 Ээлик пайы: {ownership.get('ownership_percentage', 'белгисиз')}\n"
    return result_text

@server.tool(
    name="get_branch_network",
    description="Банктын филиалдар тармагын кайтарат."
)
async def get_branch_network_tool():
    branches = get_branch_network()
    result_text = "🏢 Филиалдар тармагы:\n\n"
    result_text += f"🏛️ Башкы кеңсе: {branches.get('head_office', 'белгисиз')}\n\n"
    
    regions = branches.get('regions', [])
    if regions:
        result_text += "📍 Аймактык филиалдар:\n"
        for i, region in enumerate(regions, 1):
            result_text += f"{i}. {region}\n"
    
    return result_text

@server.tool(
    name="get_contact_info",
    description="Банктын байланыш маалыматтарын кайтарат."
)
async def get_contact_info_tool():
    contact = get_contact_info()
    result_text = "📞 Байланыш маалыматтары:\n\n"
    result_text += f"📱 Телефон: {contact.get('phone', 'белгисиз')}\n"
    result_text += f"📧 Электрондук почта: {contact.get('email', 'белгисиз')}\n"
    result_text += f"📍 Дарек: {contact.get('address', 'белгисиз')}\n"
    return result_text

@server.tool(
    name="get_complete_about_us",
    description="Банк тууралуу толук маалыматты кайтарат."
)
async def get_complete_about_us_tool():
    data = get_complete_about_us()
    result_text = f"🏦 {data.get('bank_name', 'DemirBank')}\n\n"
    
    # Mission
    result_text += "🎯 Миссия:\n"
    result_text += f"{data.get('mission', '')}\n\n"
    
    # Values
    values = data.get('values', [])
    if values:
        result_text += "💎 Баалуулуктар:\n"
        for i, value in enumerate(values, 1):
            result_text += f"{i}. {value}\n"
        result_text += "\n"
    
    # Ownership
    ownership = data.get('ownership', {})
    if ownership:
        result_text += "👥 Ээлик:\n"
        result_text += f"• Негизги акционер: {ownership.get('main_shareholder', '')}\n"
        result_text += f"• Өлкө: {ownership.get('country', '')}\n"
        result_text += f"• Ээлик пайы: {ownership.get('ownership_percentage', '')}\n\n"
    
    # Branches
    branches = data.get('branches', {})
    if branches:
        result_text += "🏢 Филиалдар:\n"
        result_text += f"• Башкы кеңсе: {branches.get('head_office', '')}\n"
        regions = branches.get('regions', [])
        if regions:
            result_text += "• Аймактык филиалдар:\n"
            for region in regions:
                result_text += f"  - {region}\n"
        result_text += "\n"
    
    # Contact
    contact = data.get('contact', {})
    if contact:
        result_text += "📞 Байланыш:\n"
        result_text += f"• Телефон: {contact.get('phone', '')}\n"
        result_text += f"• Электрондук почта: {contact.get('email', '')}\n"
        result_text += f"• Дарек: {contact.get('address', '')}\n"
    
    return result_text

@server.tool(
    name="get_about_us_section",
    description="Банк тууралуу маалыматтын белгилүү бөлүмүн кайтарат."
)
async def get_about_us_section_tool(section: str):
    data = get_about_us_section(section)
    if isinstance(data, str) and "not found" in data:
        return data
    
    result_text = f"📋 {section.title()}:\n\n"
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, list):
                result_text += f"🔹 {key.replace('_', ' ').title()}:\n"
                for item in value:
                    result_text += f"  • {item}\n"
            else:
                result_text += f"🔹 {key.replace('_', ' ').title()}: {value}\n"
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            result_text += f"{i}. {item}\n"
    else:
        result_text += str(data)
    
    return result_text


# Deposit tools

@server.tool(
    name="list_all_deposit_names",
    description="DemirBank'тагы бардык депозиттердин тизмесин кайтарат"
)
async def list_all_deposit_names_tool():
    deposits = list_all_deposit_names()
    result_text = "💰 Бардык депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
    return result_text

@server.tool(
    name="get_deposit_details",
    description="Депозит аталышы боюнча бардык негизги маалыматты кайтарат (валюта, мөөнөт, пайыздык ставка, минималдык сумма, сүрөттөмө)."
)
async def get_deposit_details_tool(deposit_name: str):
    deposit = get_deposit_details(deposit_name)
    if "error" in deposit:
        return deposit["error"]
    
    result_text = f"💰 {deposit['name']}\n\n"
    result_text += f"💱 Валюта: {', '.join(deposit.get('currency', []))}\n"
    result_text += f"💵 Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n"
    result_text += f"⏰ Мөөнөт: {deposit.get('term', 'белгисиз')}\n"
    result_text += f"📈 Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
    result_text += f"💸 Чыгаруу: {deposit.get('withdrawal', 'белгисиз')}\n"
    result_text += f"➕ Толуктоо: {deposit.get('replenishment', 'белгисиз')}\n"
    result_text += f"📊 Капитализация: {deposit.get('capitalization', 'белгисиз')}\n"
    result_text += f"📝 Сүрөттөмө: {deposit.get('descr', 'белгисиз')}\n"
    
    return result_text

@server.tool(
    name="compare_deposits",
    description="Депозиттерди негизги параметрлер боюнча салыштырат. Аргумент катары депозиттердин аттарынын тизмеси берилет (2-4 депозит)."
)
async def compare_deposits_tool(deposit_names: list):
    deposits = compare_deposits(deposit_names)
    if len(deposits) < 2:
        return "Депозит салыштыруу үчүн эң азы 2 депозит керек."
    
    all_keys = set()
    for deposit in deposits:
        all_keys.update(deposit.keys())
    all_keys = list(all_keys)
    
    result_text = "📋 Салыштырылган депозиттер:\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
    result_text += "\n"
    
    # Detailed comparison
    for key in all_keys:
        if key == "name": continue
        values = []
        for deposit in deposits:
            value = deposit.get(key, "белгисиз")
            if isinstance(value, list): value = ", ".join(value)
            elif isinstance(value, dict): value = str(value)
            values.append(value)
        
        unique_values = set()
        for val in values:
            if isinstance(val, dict): unique_values.add(str(val))
            else: unique_values.add(val)
        
        if len(unique_values) == 1:
            result_text += f"✅ Бардыгы бирдей: {values[0]}\n"
        else:
            for i, (deposit, value) in enumerate(zip(deposits, values), 1):
                result_text += f"  {i}. {deposit['name']}: {value}\n"
        result_text += "\n"
    
    return result_text

@server.tool(
    name="get_deposits_by_currency",
    description="Депозиттерди валюта боюнча фильтрлейт (KGS, USD, EUR, RUB)."
)
async def get_deposits_by_currency_tool(currency: str):
    deposits = get_deposits_by_currency(currency)
    result_text = f"💰 {currency.upper()} валютасындагы депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_by_term_range",
    description="Депозиттерди мөөнөт диапазону боюнча фильтрлейт."
)
async def get_deposits_by_term_range_tool(min_term: str = None, max_term: str = None):
    deposits = get_deposits_by_term_range(min_term, max_term)
    result_text = "⏰ Мөөнөт боюнча депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_by_min_amount",
    description="Депозиттерди минималдык сумма боюнча фильтрлейт."
)
async def get_deposits_by_min_amount_tool(max_amount: str):
    deposits = get_deposits_by_min_amount(max_amount)
    result_text = f"💵 {max_amount} чейинки минималдык суммадагы депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_by_rate_range",
    description="Депозиттерди пайыздык ставка диапазону боюнча фильтрлейт."
)
async def get_deposits_by_rate_range_tool(min_rate: str = None, max_rate: str = None):
    deposits = get_deposits_by_rate_range(min_rate, max_rate)
    result_text = "📈 Пайыздык ставка боюнча депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_with_replenishment",
    description="Толуктоого мүмкүндүк берген депозиттерди кайтарат."
)
async def get_deposits_with_replenishment_tool():
    deposits = get_deposits_with_replenishment()
    result_text = "➕ Толуктоого мүмкүндүк берген депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_with_capitalization",
    description="Капитализация мүмкүндүгүн берген депозиттерди кайтарат."
)
async def get_deposits_with_capitalization_tool():
    deposits = get_deposits_with_capitalization()
    result_text = "📊 Капитализация мүмкүндүгүн берген депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposits_by_withdrawal_type",
    description="Депозиттерди чыгаруу түрү боюнча фильтрлейт."
)
async def get_deposits_by_withdrawal_type_tool(withdrawal_type: str):
    deposits = get_deposits_by_withdrawal_type(withdrawal_type)
    result_text = f"💸 {withdrawal_type} чыгаруу түрүндөгү депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Чыгаруу: {deposit.get('withdrawal', 'белгисиз')}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_deposit_recommendations",
    description="Критерийлерге ылайык депозит сунуштарын кайтарат."
)
async def get_deposit_recommendations_tool(criteria: dict):
    deposits = get_deposit_recommendations(criteria)
    result_text = "🎯 Депозит сунуштары:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n"
        result_text += f"   Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n"
        if 'recommendation_score' in deposit:
            result_text += f"   Сунуштук балл: {deposit['recommendation_score']}\n"
        result_text += "\n"
    return result_text

@server.tool(
    name="get_government_securities",
    description="Мамлекеттик баалуу кагаздарды кайтарат (Treasury Bills, NBKR Notes)."
)
async def get_government_securities_tool():
    securities = get_government_securities()
    result_text = "🏛️ Мамлекеттик баалуу кагаздар:\n\n"
    for i, security in enumerate(securities, 1):
        result_text += f"{i}. {security['name']}\n"
        result_text += f"   Мөөнөт: {security.get('term', 'белгисиз')}\n"
        result_text += f"   Номиналдык сумма: {security.get('nominal_amount', 'белгисиз')}\n"
        result_text += f"   Түрү: {security.get('type', 'белгисиз')}\n"
        result_text += f"   Чыгаруучу: {security.get('issuer', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_child_deposits",
    description="Балдар үчүн атайын депозиттерди кайтарат."
)
async def get_child_deposits_tool():
    deposits = get_child_deposits()
    result_text = "👶 Балдар үчүн депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n"
        result_text += f"   Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n\n"
    return result_text

@server.tool(
    name="get_online_deposits",
    description="Онлайн ачылуучу депозиттерди кайтарат."
)
async def get_online_deposits_tool():
    deposits = get_online_deposits()
    result_text = "🌐 Онлайн депозиттер:\n\n"
    for i, deposit in enumerate(deposits, 1):
        result_text += f"{i}. {deposit['name']}\n"
        result_text += f"   Пайыздык ставка: {deposit.get('rate', 'белгисиз')}\n"
        result_text += f"   Мөөнөт: {deposit.get('term', 'белгисиз')}\n"
        result_text += f"   Минималдык сумма: {deposit.get('min_amount', 'белгисиз')}\n\n"
    return result_text


# Run the MCP server
if __name__ == "__main__":
    server.run()
