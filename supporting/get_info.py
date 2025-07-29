import asyncio
import json
from pathlib import Path
from crawl4ai import (
    AsyncWebCrawler,
    AdaptiveCrawler,
    AdaptiveConfig
)

OUTPUT_DIR = Path("demirbank_pages_by_url")
OUTPUT_DIR.mkdir(exist_ok=True)

# Адаптивный конфиг: только саму страницу
config = AdaptiveConfig(
    confidence_threshold=0.6,
    max_depth=1,
    max_pages=1,
    strategy="statistical"
)

def load_urls(path="all_urls.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

async def crawl_urls():
    urls = load_urls()
    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(urls):
            try:
                adaptive_crawler = AdaptiveCrawler(crawler, config)
                state = await adaptive_crawler.digest(
                    start_url=url,
                    query="банковские продукты, карты, кредиты, депозиты"
                )
                # Сохраняем только первую страницу (max_depth=0)
                for page in state.knowledge_base:
                    page_data = {
                        "url": page.url,
                        "title": page.metadata.get("title", ""),
                        "markdown": page.markdown,
                        "html": page.html
                    }
                    fname = OUTPUT_DIR / f"page_{i:03}.json"
                    with open(fname, "w", encoding="utf-8") as f:
                        json.dump(page_data, f, ensure_ascii=False, indent=2)
                    print(f"[✓] Сохранено: {fname}")
                    break  # только первая страница
            except Exception as e:
                print(f"[✗] Ошибка на {url}: {e}")

    print("✅ Сбор завершён.")

if __name__ == "__main__":
    asyncio.run(crawl_urls())
