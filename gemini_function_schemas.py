gemini_function_schemas = {
    "get_balance": {
        "name": "get_balance",
        "description": "Колдонуучунун бардык эсептериндеги жалпы балансты алуу.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_transactions": {
        "name": "get_transactions",
        "description": "Колдонуучунун акыркы транзакцияларынын тизмесин алуу (5ке чейин).",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Максималдуу транзакциялар саны (демейки 5)"}
            },
            "required": []
        }
    },
    "transfer_money": {
        "name": "transfer_money",
        "description": "Башка колдонуучуга аты боюнча акча которуу.",
        "parameters": {
            "type": "object",
            "properties": {
                "to_name": {"type": "string", "description": "Алуучунун аты"},
                "amount": {"type": "number", "description": "Которуу суммасы"}
            },
            "required": ["to_name", "amount"]
        }
    },
    "get_last_incoming_transaction": {
        "name": "get_last_incoming_transaction",
        "description": "Акыркы кирген транзакция тууралуу маалымат алуу (ким акча которду жана канча).",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
