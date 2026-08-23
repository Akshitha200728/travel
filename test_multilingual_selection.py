# -*- coding: utf-8 -*-
"""
Test Script: Multilingual Selection Verification across 17 Languages
"""

import sys
from rag_engine import get_rag_pipeline, SUPPORTED_LANGUAGES

def main():
    rag = get_rag_pipeline("data/knowledge_base.json")
    
    print("\n--- Testing All 17 Selected Languages ---")
    
    test_languages = [
        ("te", "ఆంధ్రప్రదేశ్ లో 10 చూడదగిన ప్రదేశాలు ఏవి?"),
        ("hi", "राजस्थान में घूमने की मुख्य जगहें कौन सी हैं?"),
        ("ta", "கேரளாவில் பார்க்க வேண்டிய இடங்கள் எவை?"),
        ("kn", "ಕರ್ನಾಟಕದಲ್ಲಿ ಪ್ರಮುಖ ಭೇಟಿ ನೀಡಬೇಕಾದ ಸ್ಥಳಗಳು ಯಾವುವು?"),
        ("ml", "തമിഴ്‌നാട്ടിലെ പ്രധാന കാണേണ്ട സ്ഥലങ്ങൾ ഏതൊക്കെയാണ്?"),
        ("bn", "পশ্চিমবঙ্গের প্রধান দর্শনীয় স্থান কোনগুলো?"),
        ("mr", "महाराष्ट्रातील मुख्य प्रेक्षणीय स्थळे कोणती आहेत?"),
        ("es", "¿Cuáles son los mejores lugares para visitar en París?"),
        ("fr", "Quels sont les meilleurs endroits à visiter à Paris?"),
        ("de", "Was sind die besten Sehenswürdigkeiten in Dubai?"),
        ("it", "Quali sono i migliori posti da visitare in Svizzera?"),
        ("pt", "Quais são os melhores lugares para visitar no Japão?"),
        ("ja", "東京と京都のおすすめの観光スポットは何ですか？"),
        ("ar", "ما هي أفضل الأماكن للسياحة في دبي؟"),
        ("ko", "스위스에서 꼭 가봐야 할 주요 명소는 어디인가요?"),
        ("zh", "日本东京和京都最值得去的地方有哪些？"),
        ("en", "What are the top 10 places to visit in Kerala?")
    ]

    for lang_code, query in test_languages:
        lang_name = SUPPORTED_LANGUAGES.get(lang_code, {}).get("name", lang_code)
        res = rag.query(user_query=query, lang_override=lang_code)
        
        print(f"\n[Language Selected: {lang_name} ({lang_code})]")
        print(f"User Query: {query}")
        print(f"Response Status: Grounded={res['is_grounded']} | Language={res['detected_language']}")
        print(f"Greeting Preview: {res['answer'][:120]}...\n" + "-"*50)

if __name__ == "__main__":
    main()
