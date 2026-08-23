import sys
import requests

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"

test_queries = [
    {"query": "What are the top places to visit in Andhra Pradesh?", "lang": "en"},
    {"query": "ఆంధ్రప్రదేశ్ లో 10 చూడదగిన ప్రదేశాలు ఏవి?", "lang": "te"},
    {"query": "What are the top 10 places in Rajasthan?", "lang": "en"},
    {"query": "What are the top places to visit in Karnataka?", "lang": "en"},
    {"query": "What are the top places in Meghalaya?", "lang": "en"},
    {"query": "What are the top places to visit in Ladakh?", "lang": "en"}
]

print("--- Testing RAG Engine Across Indian State Queries ---")
for t in test_queries:
    res = requests.post(f"{BASE_URL}/api/chat", json={"query": t["query"], "language": t["lang"]})
    data = res.json()
    print(f"\nQuery: {t['query']}")
    print(f"Status: {data.get('status')} | Grounded: {data.get('is_grounded')} | Lang: {data.get('detected_language')}")
    print("Answer:\n" + data.get('answer', '')[:400] + "...\n")
