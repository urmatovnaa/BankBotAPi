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
    return {"error": "Карта табылган жок."}

# 3. Compare cards by names
def compare_cards(card_names: List[str]) -> List[Dict[str, Any]]:
    cards = load_cards_data()
    found = []
    names_lower = [n.lower() for n in card_names]
    for card in cards.values():
        if card.get("name", "").lower() in names_lower:
            found.append(card)
    return found

# 4. Get card limits

def get_card_limits(card_name: str) -> Dict[str, Any]:
    card = get_card_details(card_name)
    if "limits" in card:
        return card["limits"]
    if "error" in card:
        return {"error": card["error"]}
    return {"error": "Лимиттер табылган жок."}

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

# 6. Get cards by type (debit/credit)
def get_cards_by_type(card_type: str) -> List[Dict[str, Any]]:
    """Get cards filtered by type (debit/credit)"""
    cards = load_cards_data()
    result = []
    card_type_lower = card_type.lower()
    
    for card in cards.values():
        name = card.get("name", "").lower()
        if card_type_lower in name:
            result.append(card)
    
    return result

# 7. Get cards by payment system (Visa/Mastercard)
def get_cards_by_payment_system(system: str) -> List[Dict[str, Any]]:
    """Get cards filtered by payment system (Visa/Mastercard)"""
    cards = load_cards_data()
    result = []
    system_lower = system.lower()
    
    for card in cards.values():
        name = card.get("name", "").lower()
        if system_lower in name:
            result.append(card)
    
    return result

# 8. Get cards by annual fee range
def get_cards_by_fee_range(min_fee: str = None, max_fee: str = None) -> List[Dict[str, Any]]:
    """Get cards filtered by annual fee range"""
    cards = load_cards_data()
    result = []
    
    for card in cards.values():
        fee = card.get("annual_fee", "")
        if fee == "акысыз":
            fee_value = 0
        elif "сом" in fee:
            try:
                fee_value = int(fee.replace(" сом", "").replace(" ", ""))
            except:
                fee_value = float('inf')
        else:
            fee_value = float('inf')
        
        # Apply filters
        if min_fee is not None:
            min_fee_value = int(min_fee) if min_fee.isdigit() else 0
            if fee_value < min_fee_value:
                continue
                
        if max_fee is not None:
            max_fee_value = int(max_fee) if max_fee.isdigit() else float('inf')
            if fee_value > max_fee_value:
                continue
        
        result.append(card)
    
    return result

# 9. Get cards by currency
def get_cards_by_currency(currency: str) -> List[Dict[str, Any]]:
    """Get cards that support specific currency"""
    cards = load_cards_data()
    result = []
    currency_upper = currency.upper()
    
    for card in cards.values():
        card_currencies = card.get("currency", [])
        if isinstance(card_currencies, list) and currency_upper in card_currencies:
            result.append(card)
    
    return result

# 10. Get card instructions (for Card Plus and Virtual cards)
def get_card_instructions(card_name: str) -> Dict[str, Any]:
    """Get card instructions and usage guide"""
    card = get_card_details(card_name)
    if "error" in card:
        return card
    
    instructions = {}
    if "instructions" in card:
        instructions["instructions"] = card["instructions"]
    if "instuctions" in card:  # Note: typo in original data
        instructions["instructions"] = card["instuctions"]
    if "rates" in card:
        instructions["rates"] = card["rates"]
    if "notes" in card:
        instructions["notes"] = card["notes"]
    
    return instructions if instructions else {"error": "Instructions not found for this card"}

# 11. Get card conditions (for Elkart)
def get_card_conditions(card_name: str) -> Dict[str, Any]:
    """Get card conditions and requirements"""
    card = get_card_details(card_name)
    if "error" in card:
        return card
    
    if "conditions" in card:
        return card["conditions"]
    
    return {"error": "Conditions not found for this card"}

# 12. Get cards with specific features
def get_cards_with_features(features: List[str]) -> List[Dict[str, Any]]:
    """Get cards that have specific features"""
    cards = load_cards_data()
    result = []
    features_lower = [f.lower() for f in features]
    
    for card in cards.values():
        card_text = str(card).lower()
        if all(feature in card_text for feature in features_lower):
            result.append(card)
    
    return result

# 13. Get best card recommendations
def get_card_recommendations(criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Get card recommendations based on criteria"""
    cards = load_cards_data()
    result = []
    
    # Extract criteria
    card_type = criteria.get("type", "").lower()  # debit/credit
    max_fee = criteria.get("max_fee", None)
    currency = criteria.get("currency", "").upper()
    features = criteria.get("features", [])
    
    for card in cards.values():
        score = 0
        name = card.get("name", "").lower()
        
        # Type matching
        if card_type and card_type in name:
            score += 10
        
        # Fee matching
        if max_fee is not None:
            fee = card.get("annual_fee", "")
            if fee == "акысыз":
                score += 5
            elif "сом" in fee:
                try:
                    fee_value = int(fee.replace(" сом", "").replace(" ", ""))
                    if fee_value <= max_fee:
                        score += 3
                except:
                    pass
        
        # Currency matching
        if currency:
            card_currencies = card.get("currency", [])
            if isinstance(card_currencies, list) and currency in card_currencies:
                score += 5
        
        # Features matching
        if features:
            card_text = str(card).lower()
            for feature in features:
                if feature.lower() in card_text:
                    score += 2
        
        if score > 0:
            card["recommendation_score"] = score
            result.append(card)
    
    # Sort by score
    result.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
    return result[:5]  # Return top 5 recommendations

# About Us functions
ABOUT_US_PATH = Path("generalInfo/retail/about-us.json")

def load_about_us_data() -> Dict[str, Any]:
    """Load about us data from JSON file"""
    try:
        with open(ABOUT_US_PATH, encoding='utf-8') as f:
            about_us_json = json.load(f)
            return about_us_json.get('about-us', {})
    except Exception as e:
        logging.exception(f"Error loading about us data: {e}")
        return {}

# 14. Get general bank information
def get_bank_info() -> Dict[str, Any]:
    """Get general bank information"""
    data = load_about_us_data()
    return {
        "bank_name": data.get("bank_name", ""),
        "founded": data.get("founded", ""),
        "license": data.get("license", ""),
        "descr": data.get("descr", "")
    }

# 15. Get bank mission
def get_bank_mission() -> str:
    """Get bank mission statement"""
    data = load_about_us_data()
    return data.get("mission", "Mission not found")

# 16. Get bank values
def get_bank_values() -> List[str]:
    """Get bank values and principles"""
    data = load_about_us_data()
    return data.get("values", [])

# 17. Get ownership information
def get_ownership_info() -> Dict[str, Any]:
    """Get bank ownership information"""
    data = load_about_us_data()
    return data.get("ownership", {})

# 18. Get branch network information
def get_branch_network() -> Dict[str, Any]:
    """Get bank branch network information"""
    data = load_about_us_data()
    return data.get("branches", {})

# 19. Get contact information
def get_contact_info() -> Dict[str, Any]:
    """Get bank contact information"""
    data = load_about_us_data()
    return data.get("contact", {})

# 20. Get complete about us information
def get_complete_about_us() -> Dict[str, Any]:
    """Get complete about us information"""
    return load_about_us_data()

# 21. Get specific about us section
def get_about_us_section(section: str) -> Any:
    """Get specific section of about us information"""
    data = load_about_us_data()
    return data.get(section, f"Section '{section}' not found")
