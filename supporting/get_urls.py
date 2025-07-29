import re
import json
from pathlib import Path

PAGES_DIR = Path("demirbank_pages")
all_urls = set()

# Регулярка для markdown-ссылок и обычных http/https
url_pattern = re.compile(
    r'\[.*?\]\((https?://[^\s)]+)\)|'  # [текст](url)
    r'(https?://[^\s)]+)'              # просто http/https
)

for page_file in sorted(PAGES_DIR.glob("page_*.json")):
    with open(page_file, "r", encoding="utf-8") as f:
        page_data = json.load(f)
    markdown = page_data.get("markdown", "")
    for match in url_pattern.finditer(markdown):
        url = match.group(1) or match.group(2)
        if url:
            all_urls.add(url)

# Сохраняем в файл
with open("all_urls.txt", "w", encoding="utf-8") as f:
    for url in sorted(all_urls):
        f.write(url + "\n")

print(f"Найдено {len(all_urls)} уникальных URL. Сохранено в all_urls.txt")