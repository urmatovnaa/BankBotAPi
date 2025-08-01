gemini_function_schemas = {
    "get_balance": {
        "name": "get_balance",
        "description": "Колдонуучунун бардык эсептериндеги жалпы балансты алуу.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_transactions": {
        "name": "get_transactions",
        "description": "Колдонуучунун акыркы транзакцияларынын тизмесин алуу (5ке чейин).",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Максималдуу транзакциялар саны (демейки 5)"},
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
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
                "amount": {"type": "number", "description": "Которуу суммасы"},
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["to_name"]
        }
    },
    "get_last_incoming_transaction": {
        "name": "get_last_incoming_transaction",
        "description": "Акыркы кирген транзакция тууралуу маалымат алуу (ким акча которду жана канча).",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_accounts_info": {
        "name": "get_accounts_info",
        "description": "Колдонуучунун бардык эсептеринин тизмеси жана балансы.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
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
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"},
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
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
                "end_date": {"type": "string", "description": "Аякталыш датасы (YYYY-MM-DD)"},
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["start_date", "end_date"]
        }
    },
    "get_last_3_transfer_recipients": {
        "name": "get_last_3_transfer_recipients",
        "description": "Акыркы 3 которуунун алуучуларынын тизмеси.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_largest_transaction": {
        "name": "get_largest_transaction",
        "description": "Эң чоң транзакция (суммасы боюнча) жана анын багыты.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "list_all_card_names": {
        "name": "list_all_card_names",
        "description": "DemirBank'тагы бардык карталардын тизмесин кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_card_details": {
        "name": "get_card_details",
        "description": "Карта аталышы боюнча бардык негизги маалыматты кайтарат (мисалы, валюта, мөөнөтү, чыгымдар, лимиттер, сүрөттөмө).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["card_name"]
        }
    },
    "compare_cards": {
        "name": "compare_cards",
        "description": "Карталарды негизги параметрлер боюнча салыштырат. Аргумент катары карталардын аттарынын тизмеси берилет.",
        "parameters": {
            "type": "object",
            "properties": {
                "card_names": {
                    "type": "array", 
                    "items": {
                        "type": "string",
                        "enum": [
                            "Visa Classic Debit",
                            "Visa Gold Debit", 
                            "Visa Platinum Debit",
                            "Mastercard Standard Debit",
                            "Mastercard Gold Debit",
                            "Mastercard Platinum Debit", 
                            "Card Plus",
                            "Virtual Card",
                            "Visa Classic Credit",
                            "Visa Gold Credit",
                            "Visa Platinum Credit",
                            "Mastercard Standard Credit",
                            "Mastercard Gold Credit",
                            "Mastercard Platinum Credit",
                            "Elkart",
                            "Visa Campus Card"
                        ]
                    }, 
                    "description": "Карталардын аттарынын тизмеси (2-4 карта)"
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
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
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
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
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Visa Classic Debit",
                        "Visa Gold Debit", 
                        "Visa Platinum Debit",
                        "Mastercard Standard Debit",
                        "Mastercard Gold Debit",
                        "Mastercard Platinum Debit", 
                        "Card Plus",
                        "Virtual Card",
                        "Visa Classic Credit",
                        "Visa Gold Credit",
                        "Visa Platinum Credit",
                        "Mastercard Standard Credit",
                        "Mastercard Gold Credit",
                        "Mastercard Platinum Credit",
                        "Elkart",
                        "Visa Campus Card"
                    ]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["card_name"]
        }
    },
    "get_cards_by_type": {
        "name": "get_cards_by_type",
        "description": "Карталарды түрү боюнча фильтрлейт (дебеттик/кредиттик).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_type": {
                    "type": "string",
                    "description": "Карта түрү",
                    "enum": ["debit", "credit"]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["card_type"]
        }
    },
    "get_cards_by_payment_system": {
        "name": "get_cards_by_payment_system",
        "description": "Карталарды төлөм системасы боюнча фильтрлейт (Visa/Mastercard).",
        "parameters": {
            "type": "object",
            "properties": {
                "system": {
                    "type": "string",
                    "description": "Төлөм системасы",
                    "enum": ["visa", "mastercard"]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["system"]
        }
    },
    "get_cards_by_fee_range": {
        "name": "get_cards_by_fee_range",
        "description": "Карталарды жылдык акы диапазону боюнча фильтрлейт.",
        "parameters": {
            "type": "object",
            "properties": {
                "min_fee": {"type": "string", "description": "Минималдуу жылдык акы (сом)"},
                "max_fee": {"type": "string", "description": "Максималдуу жылдык акы (сом)"},
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_cards_by_currency": {
        "name": "get_cards_by_currency",
        "description": "Карталарды валюта боюнча фильтрлейт (KGS, USD, EUR).",
        "parameters": {
            "type": "object",
            "properties": {
                "currency": {
                    "type": "string",
                    "description": "Валюта",
                    "enum": ["KGS", "USD", "EUR"]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["currency"]
        }
    },
    "get_card_instructions": {
        "name": "get_card_instructions",
        "description": "Картанын колдонуу көрсөтмөлөрүн кайтарат (Card Plus, Virtual Card үчүн).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": [
                        "Card Plus",
                        "Virtual Card"
                    ]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["card_name"]
        }
    },
    "get_card_conditions": {
        "name": "get_card_conditions",
        "description": "Картанын шарттарын жана талаптарын кайтарат (Elkart үчүн).",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string", 
                    "description": "Карта аталышы",
                    "enum": ["Elkart"]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["card_name"]
        }
    },
    "get_cards_with_features": {
        "name": "get_cards_with_features",
        "description": "Белгилүү өзгөчөлүктөргө ээ карталарды табат.",
        "parameters": {
            "type": "object",
            "properties": {
                "features": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Өзгөчөлүктөрдүн тизмеси"
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["features"]
        }
    },
    "get_card_recommendations": {
        "name": "get_card_recommendations",
        "description": "Критерийлерге ылайык карта сунуштарын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "criteria": {
                    "type": "object",
                    "description": "Карта тандау критерийлери",
                    "properties": {
                        "type": {"type": "string", "description": "Карта түрү (debit/credit)", "enum": ["debit", "credit"]},
                        "max_fee": {"type": "integer", "description": "Максималдуу жылдык акы (сом)"},
                        "currency": {"type": "string", "description": "Валюта", "enum": ["KGS", "USD", "EUR"]},
                        "features": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Керектүү өзгөчөлүктөр"
                        }
                    }
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["criteria"]
        }
    },
    "get_bank_info": {
        "name": "get_bank_info",
        "description": "Банк тууралуу негизги маалыматты кайтарат (аты, негизделген жылы, лицензия).",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_bank_mission": {
        "name": "get_bank_mission",
        "description": "Банктын миссиясын жана тарыхын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_bank_values": {
        "name": "get_bank_values",
        "description": "Банктын баалуулуктарын жана принциптерин кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_ownership_info": {
        "name": "get_ownership_info",
        "description": "Банктын ээлик маалыматтарын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_branch_network": {
        "name": "get_branch_network",
        "description": "Банктын филиалдар тармагын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_contact_info": {
        "name": "get_contact_info",
        "description": "Банктын байланыш маалыматтарын кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_complete_about_us": {
        "name": "get_complete_about_us",
        "description": "Банк тууралуу толук маалыматты кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": []
        }
    },
    "get_about_us_section": {
        "name": "get_about_us_section",
        "description": "Банк тууралуу маалыматтын белгилүү бөлүмүн кайтарат.",
        "parameters": {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Маалымат бөлүмү",
                    "enum": [
                        "bank_name",
                        "founded", 
                        "license",
                        "mission",
                        "values",
                        "ownership",
                        "branches",
                        "contact",
                        "descr"
                    ]
                },
                "language": {"type": "string", "description": "Язык ответа (ky, ru, en)", "enum": ["ky", "ru", "en"]}
            },
            "required": ["section"]
        }
    }
}
