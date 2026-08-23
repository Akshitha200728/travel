"""
TravelSphere AI - Interactive Terminal CLI Chatbot
Run this script to chat directly with the TravelSphere AI RAG chatbot in your command line terminal.
"""

import os
import sys
from rag_engine import get_rag_pipeline, SUPPORTED_LANGUAGES

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    print("=" * 70)
    print("🌍 WELCOME TO TRAVELSPHERE AI - MULTILINGUAL RAG CHATBOT")
    print("=" * 70)
    print("Supports 17+ languages (Telugu, Hindi, English, Spanish, French, Japanese, etc.)")
    print("Type your travel question below. Type 'exit' or 'quit' to stop.\n")

    pipeline = get_rag_pipeline("data/knowledge_base.json")
    
    current_lang = "auto"
    
    while True:
        try:
            prompt_label = f"User [{current_lang}] > "
            query = input(prompt_label).strip()
            
            if not query:
                continue
                
            if query.lower() in ["exit", "quit", "q"]:
                print("\nThank you for using TravelSphere AI. Happy travels! ✈️🌍\n")
                break
                
            if query.startswith("/lang"):
                parts = query.split()
                if len(parts) > 1 and parts[1] in SUPPORTED_LANGUAGES:
                    current_lang = parts[1]
                    print(f"[System] Selected language override set to: {SUPPORTED_LANGUAGES[current_lang]['name']}\n")
                else:
                    print(f"[System] Available languages: {', '.join(SUPPORTED_LANGUAGES.keys())}\n")
                continue

            # Execute RAG query
            res = pipeline.query(user_query=query, lang_override=current_lang)
            
            print("\n" + "-" * 60)
            print(f"🤖 TravelSphere AI (Detected: {res['detected_language']} | Grounded: {res['is_grounded']})")
            print("-" * 60)
            print(res['answer'])
            
            if res.get('sources'):
                print("\n📖 Sources:")
                for src in res['sources']:
                    print(f"   • {src['title']} ({src['source']})")
            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\nExiting TravelSphere AI Chatbot. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    main()
