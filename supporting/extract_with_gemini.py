import os
import json
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import google.generativeai as genai
import sys

def safe_json_loads(content):
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    idx = content.find('{')
    if idx > 0:
        content = content[idx:]
    return json.loads(content)

# --- Основная логика ---

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in (
    "correspondent-banks", 
    "to-our-partners", 
    "corporate-cards",
    "acquiring", 
    "corporate-deposits-investments", 
    "corporate-loans", 
    "other" ,
    "settlement-account"):
        print("Usage: python extract_with_gemini.py [cards|deposits|loans]")
        sys.exit(1)
    target = sys.argv[1]
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не найден в .env")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    PAGES_DIR = Path("demirbank_pages_by_url")
    EXAMPLES = {
        "correspondent-banks": Path("generalInfo/financial-institutions/correspondent-banks.json"),
        "to-our-partners": Path("generalInfo/financial-institutions/to-our-partners.json"),
        "corporate-cards": Path("generalInfo/corporate/corporate-cards.json"),
        "corporate-deposits-investments": Path("generalInfo/corporate/corporate-deposits-investments.json"),
        "corporate-loans": Path("generalInfo/corporate/corporate-loans.json"),
        "acquiring": Path("generalInfo/corporate/acquiring.json"),
        "other": Path("generalInfo/corporate/other.json"),
        "settlement-account": Path("generalInfo/corporate/settlement-account.json")
    }
    OUTFILE = f"structured_{target}.json"
    KEY = target

    with open(EXAMPLES[target], "r", encoding="utf-8") as f:
        example = json.load(f)

    INSTRUCTION = f"""
Ты — ассистент, который извлекает банковскую информацию из markdown сайта DemirBank на кыргызском языке.
Верни JSON со структурой, как в этом примере ({target}.json):

{json.dumps(example, ensure_ascii=False, indent=2)} или улучши эту структуру в зависимости от данных

Игнорируй рекламный или общий текст. Верни только информацию по продуктам.
"""

    all_dicts = []

    for page_file in tqdm(sorted(PAGES_DIR.glob("page_*.json"))):
        with open(page_file, "r", encoding="utf-8") as f:
            page_data = json.load(f)
        url = page_data.get("url")
        if not (f"{target}" in url and "financial-institutions" in url):
            continue
        print(url)
        markdown = page_data.get("markdown")
        if not markdown:
            continue
        try:
            response = model.generate_content([INSTRUCTION, markdown])
            content = response.text
            if not content.strip():
                print(f"[!] Пустой ответ на {page_file.name}")
                continue
            try:
                structured = safe_json_loads(content)
            except Exception as e:
                print(f"[!] Не удалось распарсить JSON на {page_file.name}. Ответ Gemini:\n{content}\n---")
                continue
            data = structured.get(KEY, {})
            print("data", data)

            if data:
                all_dicts.append(data)
            print(f"[✓] Обработано: {page_file.name}")
        except Exception as e:
            print(f"[✗] Ошибка на {page_file.name}: {e}")

    # Теперь объединяем всё в один итоговый JSON через LLM
    MERGE_PROMPT = f"""
Ты — ассистент-структуризатор банковских данных.
Перед тобой список dict-структур, каждая из которых содержит информацию о продуктах банка (например, {target}).
Твоя задача — объединить их в один итоговый JSON по образцу ниже, убрать дубли, сохранить вложенность и структуру, как в примере.

Пример структуры:
{json.dumps(example, ensure_ascii=False, indent=2)}

Список dict-структур для объединения:
{json.dumps(all_dicts, ensure_ascii=False, indent=2)}

Верни ТОЛЬКО итоговый JSON, не python file
"""

    response = model.generate_content([MERGE_PROMPT])
    content = response.text
    print(content)

    try:
        final_structured = safe_json_loads(content)
        print("final", final_structured)
        with open(OUTFILE, "w", encoding="utf-8") as f:
            json.dump({KEY: final_structured}, f, ensure_ascii=False, indent=2)
        print(f"\n✅ ! Все данные сохранены в {OUTFILE}")
    except Exception as e:
        print("error", e)
        print("Ошибка парсинга ответа LLM. Сырой ответ ниже:\n")
        print(content)

if __name__ == "__main__":
    main()