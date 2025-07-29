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
    },
    "list_all_card_names": {
        "name": "list_all_card_names",
        "description": "DemirBank'тагы бардык карталардын тизмесин кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_card_details": {
        "name": "get_card_details",
        "description": "Карта аталышы боюнча бардык негизги маалыматты кайтарат (мисалы, валюта, мөөнөтү, чыгымдар, лимиттер, сүрөттөмө).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {"type": "string", "description": "Карта аталышы (мисалы, 'Visa Classic Debit')"}
            },
            "required": ["card_name"]
        }
    },
    "compare_cards": {
        "name": "compare_cards",
        "description": "Бир нече картаны негизги параметрлер боюнча салыштырат. Аргумент катары карталардын аттарынын тизмеси берилет.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_names": {"type": "array", "items": {"type": "string"}, "description": "Карталардын аттарынын тизмеси"}
            },
            "required": ["card_names"]
        }
    },
    "get_card_limits": {
        "name": "get_card_limits",
        "description": "Карта аталышы боюнча лимиттерди кайтарат (ATM, POS, контактсыз ж.б.).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {"type": "string", "description": "Карта аталышы (мисалы, 'Visa Classic Debit')"}
            },
            "required": ["card_name"]
        }
    },
    "get_card_benefits": {
        "name": "get_card_benefits",
        "description": "Карта аталышы боюнча артыкчылыктарды жана өзгөчөлүктөрдү кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {"type": "string", "description": "Карта аталышы (мисалы, 'Visa Classic Debit')"}
            },
            "required": ["card_name"]
        }
    }
}
