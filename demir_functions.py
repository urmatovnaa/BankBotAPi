import json
import os
from typing import List, Dict, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)

CARDS_PATH = Path("generalInfo/retail/cards.json")


def load_cards_data() -> Dict[str, Any]:
    try:
        with open(CARDS_PATH, encoding='utf-8') as f:
            cards_json = json.load(f)
            return cards_json.get('cards', {})
    except Exception as e:
        logging.exception(f"Error loading cards data: {e}")
        return {}

# 1. List all card types

def list_all_card_names() -> List[Dict[str, str]]:
    cards = load_cards_data()
    result = []
    for card in cards.values():
        logging.info(card)
        result.append({
            "name": card.get("name", ""),
        })
    return result

# 2. Get card details by name

def get_card_details(card_name: str) -> Dict[str, Any]:
    cards = load_cards_data()
    for card in cards.values():
        if card.get("name", "").lower() == card_name.lower():
            return card
    return {"error": "Card not found"}

# 3. Compare cards by names

def compare_cards(card_names: List[str]) -> List[Dict[str, Any]]:
    cards = load_cards_data()
    found = []
    names_lower = [n.lower() for n in card_names]
    for section in cards.values():
        if isinstance(section, dict):
            for card in section.values():
                if isinstance(card, dict) and card.get("name", "").lower() in names_lower:
                    found.append(card)
    return found

# 4. Get card limits

def get_card_limits(card_name: str) -> Dict[str, Any]:
    card = get_card_details(card_name)
    if "limits" in card:
        return card["limits"]
    return {"error": "Limits not found for this card"}

# 5. Get card benefits

def get_card_benefits(card_name: str) -> List[str]:
    card = get_card_details(card_name)
    # Try to extract benefits, instructions, notes, or descr
    benefits = []
    if "benefits" in card:
        benefits.extend(card["benefits"])
    if "Services" in card:
        benefits.extend(card["Services"])
    if "instuctions" in card:
        benefits.extend(list(card["instuctions"].values()))
    if "notes" in card:
        benefits.extend(card["notes"])
    if "descr" in card:
        benefits.append(card["descr"])
    return benefits or ["No benefits found for this card"]
