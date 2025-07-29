import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Загружаем модель
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Путь к файлу
file_path = Path("generalInfo/retail/useful-info.json")

# Загружаем JSON
with open(file_path, encoding="utf-8") as f:
    data = json.load(f)

updated = False

# Для каждой секции
for section, qas in data["useful-info"].items():
    print("section",section)
    print("qas", qas)
    for qa in qas:
        print("qa", qa)
        if "embedding" not in qa:
            embedding = model.encode(qa["question"]).tolist()
            qa["embedding"] = embedding
            updated = True

# Если есть изменения — сохраняем
if updated:
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✅ Embeddings saved.")
else:
    print("ℹ️ Embeddings already present.")
