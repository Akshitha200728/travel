"""
TravelSphere AI - Live Demonstration Script
Runs sample chatbot queries in Telugu, Hindi, English, Spanish, and Japanese and displays the RAG responses.
"""

import sys
from rag_engine import get_rag_pipeline

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def run_demonstration():
    print("=" * 80)
    print("🌍 TRAVELSPHERE AI - LIVE MULTILINGUAL RAG CHATBOT DEMONSTRATION")
    print("=" * 80)

    pipeline = get_rag_pipeline("data/knowledge_base.json")

    sample_queries = [
        ("🇮🇳 Telugu Query", "హైదరాబాద్లో చూడదగిన ప్రదేశాలు ఏవి?"),
        ("🇮🇳 Hindi Query", "गोवा में घूमने की सबसे अच्छी जगहें कौन सी हैं?"),
        ("🇬🇧 English Query", "What are the best places to visit in Japan?"),
        ("🇪🇸 Spanish Query", "Planifica un viaje de 5 días a París con consejos de presupuesto."),
        ("🇯🇵 Japanese Query", "スイスのベストシーズンと観光名所を教えてください。")
    ]

    for label, query in sample_queries:
        print(f"\n{"="*80}")
        print(f"❓ {label}: \"{query}\"")
        print("="*80)

        res = pipeline.query(query)

        print(f"🌐 Language Detected: {res['detected_language']} (Confidence: {res['confidence']*100:.0f}%)")
        print(f"🛡️ RAG Grounded: {res['is_grounded']} | Retrieved Documents: {res['retrieved_count']}")
        print("-" * 80)
        print(res['answer'])

        if res.get('sources'):
            print("\n📖 Sources & Attribution:")
            for s in res['sources']:
                print(f"   • [{s['title']}] - {s['source']}")
        print("-" * 80)

if __name__ == "__main__":
    run_demonstration()
