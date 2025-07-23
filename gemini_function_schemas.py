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
            "required": ["to_name"]
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
    },
    "get_accounts_info": {
        "name": "get_accounts_info",
        "description": "Колдонуучунун бардык эсептеринин тизмеси жана балансы.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_incoming_sum_for_period": {
        "name": "get_incoming_sum_for_period",
        "description": "Көрсөтүлгөн аралыкта кирген которуулар (входящие) жалпы суммасы.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Башталыш датасы (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"}
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_outgoing_sum_for_period": {
        "name": "get_outgoing_sum_for_period",
        "description": "Көрсөтүлгөн аралыкта чыккан которуулар (исходящие) жалпы суммасы.",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "Башталыш датасы (YYYY-MM-DD)"},
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"}
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_last_3_transfer_recipients": {
        "name": "get_last_3_transfer_recipients",
        "description": "Акыркы 3 которуунун алуучуларынын тизмеси.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_largest_transaction": {
        "name": "get_largest_transaction",
        "description": "Эң чоң транзакция (суммасы боюнча) жана анын багыты.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}
