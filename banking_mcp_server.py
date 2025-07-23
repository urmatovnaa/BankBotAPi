import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastmcp import FastMCP
from bank_functions import get_balance, get_transactions, transfer_money, get_last_incoming_transaction, get_accounts_info, get_incoming_sum_for_period, get_outgoing_sum_for_period, get_last_3_transfer_recipients, get_largest_transaction
from models import User
from app import app

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

# Run the MCP server
if __name__ == "__main__":
    server.run()
