from wikimedia_service import get_wikimedia_service
"""
TravelSphere AI - RAG Engine & Multilingual Processing Module
Handles Language Detection, Hybrid Vector Search, Context Construction, and Grounded Response Generation.
"""

import os
import re
import json
import math
from typing import Dict, List, Any, Tuple, Optional
from collections import Counter

# Language Definitions & Metadata
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "code": "en"},
    "te": {"name": "Telugu", "native": "తెలుగు", "code": "te"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "code": "hi"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "code": "ta"},
    "kn": {"name": "Kannada", "native": "కన్నడ / ಕನ್ನಡ", "code": "kn"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "code": "ml"},
    "bn": {"name": "Bengali", "native": "বাংলা", "code": "bn"},
    "mr": {"name": "Marathi", "native": "मराठी", "code": "mr"},
    "es": {"name": "Spanish", "native": "Español", "code": "es"},
    "fr": {"name": "French", "native": "Français", "code": "fr"},
    "de": {"name": "German", "native": "Deutsch", "code": "de"},
    "it": {"name": "Italian", "native": "Italiano", "code": "it"},
    "pt": {"name": "Portuguese", "native": "Português", "code": "pt"},
    "ar": {"name": "Arabic", "native": "العربية", "code": "ar"},
    "ja": {"name": "Japanese", "native": "日本語", "code": "ja"},
    "ko": {"name": "Korean", "native": "한국어", "code": "ko"},
    "zh": {"name": "Chinese", "native": "中文", "code": "zh"}
}

# Offline Multilingual Response Templates for Synthesizer Fallback
MULTILINGUAL_TEMPLATES = {
    "te": {
        "greeting": "🌍 **TravelSphere AI ప్రయాణ సహాయకుడు**: ",
        "fallback": "నేను నా ప్రస్తుత ప్రయాణ సమాచార డేటాబేస్‌లో దీనికి సంబంధించి సరైన మరియు విశ్వసనీయ సమాచారాన్ని కనుగొనలేకపోయాను.",
        "best_time": "సందర్శించడానికి ఉత్తమ సమయం",
        "budget": "అంచనా బడ్జెట్",
        "attractions": "ముఖ్యమైన చూడదగిన పర్యాటక ప్రాంతాలు",
        "food": "ప్రసిద్ధ ఆహార పదార్థాలు & రుచులు",
        "stays": "వసతి & హోటళ్ళు",
        "tips": "ముఖ్యమైన ప్రయాణ చిట్కాలు",
        "source": "మూలం"
    },
    "hi": {
        "greeting": "🌍 **TravelSphere AI यात्रा सहायक**: ",
        "fallback": "मुझे अपने वर्तमान यात्रा ज्ञान आधार में इसके बारे में विश्वसनीय जानकारी नहीं मिली।",
        "best_time": "घूमने का सबसे अच्छा समय",
        "budget": "अनुमानित बजट",
        "attractions": "प्रमुख दर्शनीय स्थल",
        "food": "प्रसिद्ध भोजन और व्यंजन",
        "stays": "आवास और होटल",
        "tips": "यात्रा युक्तियाँ",
        "source": "स्रोत"
    },
    "ta": {
        "greeting": "🌍 **TravelSphere AI பயண உதவியாளர்**: ",
        "fallback": "எங்கள் தற்போதைய சுற்றுலா தரவுத்தளத்தில் இதற்கு தொடர்பான தகவல் கிடைக்கவில்லை.",
        "best_time": "பார்வையிட சிறந்த நேரம்",
        "budget": "மதிப்பிடப்பட்ட பட்ஜெட்",
        "attractions": "முக்கிய பார்க்க வேண்டிய இடங்கள்",
        "food": "பிரபலமான உணவு மற்றும் வகைகள்",
        "stays": "தங்குமிடம் மற்றும் ஹோட்டல்கள்",
        "tips": "பயணக் குறிப்புகள்",
        "source": "சரிபார்க்கப்பட்ட ஆதாரம்"
    },
    "kn": {
        "greeting": "🌍 **TravelSphere AI ಪ್ರವಾಸ ಸಹಾಯಕ**: ",
        "fallback": "ನಮ್ಮ ಸದ್ಯದ ಪ್ರವಾಸೋದ್ಯಮ ದತ್ತಸಂಚಯದಲ್ಲಿ ಈ ಮಾಹಿತಿಯು ದೊರೆತಿಲ್ಲ.",
        "best_time": "ಭೇಟಿ ನೀಡಲು ಅತ್ಯುತ್ತಮ ಸಮಯ",
        "budget": "ಅಂದಾಜು ಬಜೆಟ್",
        "attractions": "ಪ್ರಮುಖ ಭೇಟಿ ನೀಡಬೇಕಾದ ಸ್ಥಳಗಳು",
        "food": "ಪ್ರಸಿದ್ಧ ಆಹಾರ ಮತ್ತು ಅಡುಗೆ",
        "stays": "ವಸತಿ ಮತ್ತು ಹೋಟೆಲ್‌ಗಳು",
        "tips": "ಪ್ರಯಾಣದ ಸಲಹೆಗಳು",
        "source": "ದೃಢೀಕರಿಸಿದ ಮೂಲ"
    },
    "ml": {
        "greeting": "🌍 **TravelSphere AI യാത്രാ സഹായി**: ",
        "fallback": "ഞങ്ങളുടെ വിവരശേഖരത്തിൽ ഇതിനെക്കുറിച്ചുള്ള വിവരങ്ങൾ ലഭ്യമായിട്ടില്ല.",
        "best_time": "സന്ദർശിക്കാൻ മികച്ച സമയം",
        "budget": "ഏകദേശ ബജറ്റ്",
        "attractions": "പ്രധാന കാണേണ്ട സ്ഥലങ്ങൾ",
        "food": "പ്രസിദ്ധമായ ഭക്ഷണ വിഭവങ്ങൾ",
        "stays": "താമസ സൗകര്യങ്ങൾ",
        "tips": "യാത്രാ വിവരങ്ങൾ",
        "source": "സ്ഥിരീകരിച്ച ഉറവിടം"
    },
    "bn": {
        "greeting": "🌍 **TravelSphere AI ভ্রমণ সহকারী**: ",
        "fallback": "আমাদের বর্তমান ভ্রমণ তথ্যভাণ্ডারে এই সংক্রান্ত কোনো সঠিক তথ্য পাওয়া যায়নি।",
        "best_time": "ভ্রমণের সেরা সময়",
        "budget": "আনুমানিক বাজেট",
        "attractions": "প্রধান দর্শনীয় স্থানসমূহ",
        "food": "বিখ্যাত খাবার ও রন্ধনশৈলী",
        "stays": "থাকার ব্যবস্থা ও হোটেল",
        "tips": "ভ্রমণ টিপস",
        "source": "যাচাইকৃত উৎস"
    },
    "mr": {
        "greeting": "🌍 **TravelSphere AI प्रवास सहाय्यक**: ",
        "fallback": "आमच्या सध्याच्या पर्यटन डेटाबेसमध्ये याबद्दल अचूक माहिती सापडली नाही.",
        "best_time": "भेट देण्यासाठी सर्वोत्तम वेळ",
        "budget": "अंदाजे बजेट",
        "attractions": "प्रमुख प्रेक्षणीय स्थळे",
        "food": "प्रसिद्ध खाद्यपदार्थ आणि पाककृती",
        "stays": "राहण्याची सोय आणि हॉटेल्स",
        "tips": "महत्त्वाच्या प्रवास टिप्स",
        "source": "सत्यापित स्त्रोत"
    },
    "es": {
        "greeting": "🌍 **Asistente de Viajes TravelSphere AI**: ",
        "fallback": "No se encontró información verificada en la base de datos para esta consulta.",
        "best_time": "Mejor época para visitar",
        "budget": "Presupuesto estimado",
        "attractions": "Principales atracciones y lugares",
        "food": "Gastronomía y platos típicos",
        "stays": "Alojamiento y hoteles",
        "tips": "Consejos prácticos de viaje",
        "source": "Fuente verificada"
    },
    "fr": {
        "greeting": "🌍 **Assistant de Voyage TravelSphere AI**: ",
        "fallback": "Informations non trouvées dans notre base de données touristique.",
        "best_time": "Meilleure période pour visiter",
        "budget": "Budget estimé",
        "attractions": "Principales attractions et sites",
        "food": "Gastronomie locale et spécialités",
        "stays": "Hébergement et hôtels",
        "tips": "Conseils pratiques de voyage",
        "source": "Source vérifiée"
    },
    "de": {
        "greeting": "🌍 **TravelSphere AI Reiseassistent**: ",
        "fallback": "Keine verifizierten Informationen in unserer Datenbank gefunden.",
        "best_time": "Beste Reisezeit",
        "budget": "Geschätztes Budget",
        "attractions": "Top Sehenswürdigkeiten",
        "food": "Lokale Küche & Spezialitäten",
        "stays": "Unterkünfte & Hotels",
        "tips": "Reisetipps & Ratschläge",
        "source": "Verifizierte Quelle"
    },
    "it": {
        "greeting": "🌍 **Assistente di Viaggio TravelSphere AI**: ",
        "fallback": "Nessuna informazione verificata trovata nel nostro database turistico.",
        "best_time": "Periodo migliore per visitare",
        "budget": "Budget stimato",
        "attractions": "Principali attrazioni turistici",
        "food": "Cucina locale e piatti tipici",
        "stays": "Alloggi e hotel",
        "tips": "Consigli pratici di viaggio",
        "source": "Fonte verificata"
    },
    "pt": {
        "greeting": "🌍 **Assistente de Viagens TravelSphere AI**: ",
        "fallback": "Nenhuma informação verificada encontrada em nosso banco de dados.",
        "best_time": "Melhor época para visitar",
        "budget": "Orçamento estimado",
        "attractions": "Principais atrações turísticas",
        "food": "Culinária local e pratos típicos",
        "stays": "Acomodação e hotéis",
        "tips": "Dicas práticas de viagem",
        "source": "Fonte verificada"
    },
    "ar": {
        "greeting": "🌍 **مساعد السفر الذكي TravelSphere AI**: ",
        "fallback": "لم يتم العثور على معلومات موثوقة في قاعدة بيانات السياحة الحالية.",
        "best_time": "أفضل وقت للزيارة",
        "budget": "الميزانية التقديرية",
        "attractions": "أهم المعالم والأماكن السياحية",
        "food": "المأكولات والأطباق المحلية الشهيرة",
        "stays": "الإقامة والفنادق",
        "tips": "نصائح وإرشادات السفر",
        "source": "المصدر المعتمد"
    },
    "ko": {
        "greeting": "🌍 **TravelSphere AI 여행 어시스턴트**: ",
        "fallback": "현재 관광 데이터베이스에서 이 장소에 대한 정보를 찾을 수 없습니다.",
        "best_time": "방문하기 가장 좋은 시기",
        "budget": "예상 여행 예산",
        "attractions": "주요 명소 및 관광지",
        "food": "대표 음식 및 맛집 정보",
        "stays": "숙박 및 호텔 안내",
        "tips": "유용한 여행 팁",
        "source": "검증된 출처"
    },
    "zh": {
        "greeting": "🌍 **TravelSphere AI 智能旅游助手**: ",
        "fallback": "在当前的旅游数据库中未找到相关验证信息。",
        "best_time": "最佳旅游季节",
        "budget": "预估旅游预算",
        "attractions": "热门景点与名胜",
        "food": "当地特色美食与小吃",
        "stays": "住宿与酒店推荐",
        "tips": "实用旅游提示与指南",
        "source": "权威验证来源"
    },
    "en": {
        "greeting": "🌍 **TravelSphere AI Companion**: ",
        "fallback": "I couldn't find reliable information about this in my current travel knowledge base.",
        "best_time": "Best Time to Visit",
        "budget": "Estimated Budget",
        "attractions": "Top Attractions & Landmarks",
        "food": "Famous Cuisine & Dining",
        "stays": "Accommodations & Stays",
        "tips": "Practical Travel Tips",
        "source": "Source Attribution"
    }
}

class LanguageDetector:
    """Detects script and language from natural language text."""
    
    SCRIPT_RANGES = [
        (re.compile(r'[\u0C00-\u0C7F]'), 'te'),  # Telugu
        (re.compile(r'[\u0900-\u097F]'), 'hi'),  # Devanagari (Hindi/Marathi)
        (re.compile(r'[\u0B80-\u0BFF]'), 'ta'),  # Tamil
        (re.compile(r'[\u0C80-\u0CFF]'), 'kn'),  # Kannada
        (re.compile(r'[\u0D00-\u0D7F]'), 'ml'),  # Malayalam
        (re.compile(r'[\u0980-\u09FF]'), 'bn'),  # Bengali
        (re.compile(r'[\u0600-\u06FF]'), 'ar'),  # Arabic
        (re.compile(r'[\u3040-\u30FF\u31F0-\u31FF]'), 'ja'),  # Japanese Hiragana/Katakana
        (re.compile(r'[\uAC00-\uD7AF\u1100-\u11FF]'), 'ko'),  # Korean Hangul
        (re.compile(r'[\u4E00-\u9FFF]'), 'zh'),  # Chinese Hanzi
    ]
    
    LATIN_STOPWORDS = {
        'es': {'de', 'el', 'la', 'en', 'un', 'una', 'por', 'que', 'los', 'las', 'como', 'mejores', 'lugares', 'visitar', 'cuanto', 'cuesta'},
        'fr': {'du', 'de', 'la', 'le', 'et', 'des', 'les', 'pour', 'dans', 'combien', 'meilleur', 'visiter', 'hotel', 'paris'},
        'de': {'der', 'die', 'das', 'und', 'in', 'von', 'mit', 'fuer', 'wie', 'beste', 'reisezeit', 'wo'},
        'it': {'il', 'la', 'di', 'che', 'per', 'in', 'un', 'una', 'dove', 'migliori', 'cosa', 'vedere'},
        'pt': {'do', 'da', 'em', 'um', 'para', 'com', 'nao', 'quais', 'melhores', 'lugares'},
    }

    @classmethod
    def detect(cls, text: str, user_override: Optional[str] = None) -> Tuple[str, float]:
        """Detect language code and return (language_code, confidence)."""
        if user_override and user_override in SUPPORTED_LANGUAGES and user_override != "auto":
            return user_override, 1.0

        if not text or not text.strip():
            return "en", 1.0
            
        # Check unicode script patterns
        for pattern, lang_code in cls.SCRIPT_RANGES:
            matches = pattern.findall(text)
            if len(matches) > 0:
                # Distinguish Devanagari between Hindi and Marathi if needed
                if lang_code == 'hi' and ('आहे' in text or 'नाही' in text or 'कसा' in text):
                    return 'mr', 0.95
                return lang_code, 0.95
                
        # Check Latin stopwords
        tokens = set(re.findall(r'\b\w+\b', text.lower()))
        best_lang = 'en'
        max_matches = 0
        
        for lang_code, stopwords in cls.LATIN_STOPWORDS.items():
            overlap = len(tokens.intersection(stopwords))
            if overlap > max_matches:
                max_matches = overlap
                best_lang = lang_code
                
        if max_matches >= 2:
            return best_lang, 0.85
            
        return "en", 0.80


class DocumentChunk:
    """Represents a chunk of travel document with metadata."""
    def __init__(self, doc_id: str, title: str, content: str, metadata: Dict[str, Any]):
        self.doc_id = doc_id
        self.title = title
        self.content = content
        self.metadata = metadata
        self.tokens = self._tokenize(title + " " + content + " " + " ".join(metadata.get("tags", [])))
        
    def _tokenize(self, text: str) -> List[str]:
        # Lowercase, clean alphanumeric tokens
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        return [t for t in text_clean.split() if len(t) > 1]


class HybridVectorIndex:
    """Vector Retrieval Index using TF-IDF, Keyword matching, and Cosine Similarity."""
    
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.doc_freqs: Dict[str, int] = Counter()
        self.total_docs = 0
        self.vocabulary: Dict[str, int] = {}
        
    def add_chunk(self, chunk: DocumentChunk):
        self.chunks.append(chunk)
        unique_tokens = set(chunk.tokens)
        for token in unique_tokens:
            self.doc_freqs[token] += 1
        self.total_docs += 1

    def build_index(self):
        """Build vocabulary index and precompute IDFs."""
        all_words = list(self.doc_freqs.keys())
        self.vocabulary = {w: i for i, w in enumerate(all_words)}

    def search(self, query: str, top_k: int = 4, category_filter: Optional[str] = None, region_filter: Optional[str] = None) -> List[Tuple[DocumentChunk, float]]:
        """Search top-k matching documents using hybrid score."""
        query_tokens = [t for t in re.sub(r'[^\w\s]', ' ', query.lower()).split() if len(t) > 1]
        if not query_tokens or not self.chunks:
            return []

        query_counter = Counter(query_tokens)
        STOP_WORDS = {'what', 'are', 'the', 'top', 'best', 'places', 'to', 'visit', 'in', 'on', 'under', 'a', 'for', 'with', 'show', 'me', 'luxury', 'budget', 'hotels', 'resorts', 'trip', 'plan', 'how', 'much', 'cost', 'where', 'is', 'of', 'and', 'or', 'some'}
        
        filtered_query_tokens = [t for t in query_tokens if t not in STOP_WORDS]
        scores = []

        for chunk in self.chunks:
            # Metadata filtering
            if category_filter and chunk.metadata.get("category", "").lower() != category_filter.lower():
                continue
            if region_filter and chunk.metadata.get("region", "").lower() != region_filter.lower():
                continue

            # TF-IDF & Keyword Score Calculation
            score = 0.0
            chunk_token_counts = Counter(chunk.tokens)
            doc_len = len(chunk.tokens) or 1
            
            for q_term, q_count in query_counter.items():
                if q_term in chunk_token_counts:
                    tf = chunk_token_counts[q_term] / doc_len
                    df = self.doc_freqs.get(q_term, 1)
                    idf = math.log((self.total_docs + 1) / (df + 1)) + 1.0
                    # Weight non-stopwords higher
                    weight = 1.5 if q_term not in STOP_WORDS else 0.2
                    score += tf * idf * q_count * weight

            # Boost for explicit destination / country / unique tag matches
            dest_name = chunk.metadata.get("destination", "").lower()
            country_name = chunk.metadata.get("country", "").lower()
            tags = [t.lower() for t in chunk.metadata.get("tags", [])]
            
            non_stop_matches = 0
            for q_term in filtered_query_tokens:
                if q_term in dest_name:
                    score += 2.5
                    non_stop_matches += 1
                elif q_term in country_name:
                    score += 2.0
                    non_stop_matches += 1
                elif q_term in tags:
                    score += 1.2
                    non_stop_matches += 1
                elif q_term in chunk.tokens:
                    score += 1.0
                    non_stop_matches += 1

            # Only consider results if at least one meaningful non-stop word matched or base TFIDF score is significant
            if score > 0.4 and (non_stop_matches > 0 or len(filtered_query_tokens) == 0):
                scores.append((chunk, score))

        # Sort descending by score
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


class TravelRAGPipeline:
    """Main RAG Orchestrator handling query processing, retrieval, anti-hallucination, and LLM synthesis."""

    def __init__(self, data_path: str):
        self.index = HybridVectorIndex()
        self.raw_data = {}
        self.lang_detector = LanguageDetector()
        self.load_knowledge_base(data_path)

    def load_knowledge_base(self, path: str):
        """Loads destinations and FAQs from knowledge_base.json and indexes document chunks."""
        if not os.path.exists(path):
            print(f"Warning: Data file not found at {path}")
            return
            
        with open(path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

        destinations = self.raw_data.get("destinations", [])
        for dest in destinations:
            tags_str = " ".join(dest.get('tags', []))
            attraction_text = f"Destination: {dest['destination']} ({tags_str}), Country: {dest['country']}, Region: {dest['region']}. Category: {dest['category']}. Main Attractions: " + ", ".join(dest['attractions']) + ". Hidden Gems: " + ", ".join(dest.get('hidden_gems', []))
            self.index.add_chunk(DocumentChunk(
                doc_id=f"{dest['id']}_attractions",
                title=f"{dest['destination']} - Top Attractions & Overview",
                content=attraction_text,
                metadata={
                    "destination": dest['destination'],
                    "country": dest['country'],
                    "region": dest['region'],
                    "category": dest['category'],
                    "source": dest['source'],
                    "tags": dest['tags'],
                    "chunk_type": "attractions",
                    "raw_dest": dest
                }
            ))
            
            # Chunk 2: Weather & Best time to visit
            weather_text = f"{dest['destination']} in {dest['country']}. Best time to visit: {dest['best_time_to_visit']}. Weather overview: {dest['weather']}."
            self.index.add_chunk(DocumentChunk(
                doc_id=f"{dest['id']}_weather",
                title=f"{dest['destination']} - Best Time & Weather",
                content=weather_text,
                metadata={
                    "destination": dest['destination'],
                    "country": dest['country'],
                    "region": dest['region'],
                    "category": dest['category'],
                    "source": dest['source'],
                    "tags": dest['tags'],
                    "chunk_type": "weather",
                    "raw_dest": dest
                }
            ))
            # Chunk 3: Budget, Currency & Accommodations
            budget_text = f"{dest['destination']} Budget & Cost: USD daily range {dest['budget_range_usd']}, INR daily range {dest['approx_budget_inr']}. Currency: {dest['currency']}. Accommodations: Budget: {dest['accommodations']['budget']}, Mid-range: {dest['accommodations']['mid_range']}, Luxury: {dest['accommodations']['luxury']}."
            self.index.add_chunk(DocumentChunk(
                doc_id=f"{dest['id']}_budget",
                title=f"{dest['destination']} - Budget, Stays & Currency",
                content=budget_text,
                metadata={
                    "destination": dest['destination'],
                    "country": dest['country'],
                    "region": dest['region'],
                    "category": dest['category'],
                    "source": dest['source'],
                    "tags": dest['tags'],
                    "chunk_type": "budget",
                    "raw_dest": dest
                }
            ))

            # Chunk 4: Food & Cuisine
            food_info = dest.get("food_and_cuisine", {})
            food_text = f"Food & Dining in {dest['destination']}: Famous dishes: " + ", ".join(food_info.get("famous_dishes", [])) + f". Vegetarian & Vegan options: {food_info.get('vegetarian_vegan_options', '')}. Street food: " + ", ".join(food_info.get("popular_street_food", [])) + f". Budget tips: {food_info.get('budget_food_tips', '')}."
            self.index.add_chunk(DocumentChunk(
                doc_id=f"{dest['id']}_food",
                title=f"{dest['destination']} - Local Cuisine & Vegetarian Food",
                content=food_text,
                metadata={
                    "destination": dest['destination'],
                    "country": dest['country'],
                    "region": dest['region'],
                    "category": dest['category'],
                    "source": dest['source'],
                    "tags": dest['tags'],
                    "chunk_type": "food",
                    "raw_dest": dest
                }
            ))

            # Chunk 5: Practical Tips, Visa & Transport
            tips_text = f"{dest['destination']} Travel Logistics & Visa: Visa requirements: {dest['visa_requirements']}. Local transportation: {dest['local_transport']}. Practical tips: " + " ".join(dest.get('practical_tips', [])) + f". Safety & Etiquette: {dest['safety_and_etiquette']}."
            self.index.add_chunk(DocumentChunk(
                doc_id=f"{dest['id']}_practical",
                title=f"{dest['destination']} - Visa, Transport & Safety Tips",
                content=tips_text,
                metadata={
                    "destination": dest['destination'],
                    "country": dest['country'],
                    "region": dest['region'],
                    "category": dest['category'],
                    "source": dest['source'],
                    "tags": dest['tags'],
                    "chunk_type": "practical",
                    "raw_dest": dest
                }
            ))

        self.index.build_index()
        print(f"RAG Pipeline initialized: Indexed {self.index.total_docs} document chunks.")

    def query(self, user_query: str, lang_override: Optional[str] = None, session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        RAG Retrieval & Generation Method powering TravelMate AI.
        Integrates Wikipedia, Wikivoyage, Wikimedia Commons, Vector Search, LLM Synthesis & Translation.
        """
        # Step 1: Language Detection
        if lang_override and lang_override in SUPPORTED_LANGUAGES:
            detected_lang = lang_override
            confidence = 1.0
        else:
            detected_lang, confidence = self.lang_detector.detect(user_query)

        # Step 2: Real-time Live Information Warning Check
        q_lower = user_query.lower()
        is_realtime_query = any(k in q_lower for k in ['flight price', 'hotel availability tonight', 'is open right now', 'today weather', 'train ticket price live', 'ticket price today'])
        if is_realtime_query:
            warning_msg = (
                "⚠️ **Live Data Notice**: Wikimedia sources (Wikipedia & Wikivoyage) provide static encyclopedic "
                "and travel guide knowledge. For real-time flight schedules, live hotel availability, or today's current weather, "
                "please check official booking platforms or live weather APIs."
            )
            if detected_lang != "en":
                warning_msg = self._translate_text(warning_msg, detected_lang)
            return {
                "answer": warning_msg,
                "detected_language": SUPPORTED_LANGUAGES.get(detected_lang, {}).get("name", "English"),
                "language_code": detected_lang,
                "confidence": round(confidence, 2),
                "is_grounded": True,
                "sources": [],
                "images": [],
                "retrieved_count": 0
            }

        # Step 3: Conversation Memory & Context-Aware Query Resolution
        current_dest = session_context.get("current_destination", "") if session_context else ""
        resolved_query = user_query
        if current_dest and any(pron in q_lower for pron in ['there', 'this place', 'that city', 'here', 'అక్కడ', 'वहाँ', 'அங்கே', 'అక్కడి']):
            resolved_query = f"{user_query} in {current_dest}"

        # Step 4: Local Knowledge Base Vector Retrieval & Keyword Mapping
        search_query = resolved_query
        dest_keywords = {
            "అండమాన్": "Andaman Nicobar Islands Havelock Radhanagar Beach",
            "अंडमान": "Andaman Nicobar Islands Havelock Radhanagar Beach",
            "ఆంధ్రప్రదేశ్": "Andhra Pradesh Tirupati Vizag Araku Gandikota",
            "ఆంధ్ర": "Andhra Pradesh Tirupati Vizag Araku Gandikota",
            "ఆంధ్రా": "Andhra Pradesh Tirupati Vizag Araku Gandikota",
            "आंध्र प्रदेश": "Andhra Pradesh Tirupati Vizag Araku Gandikota",
            "పాండిచ్చేరి": "Puducherry Pondicherry Promenade Beach French Quarter",
            "పాండిచేరి": "Puducherry Pondicherry Promenade Beach French Quarter",
            "పండిచేరి": "Puducherry Pondicherry Promenade Beach French Quarter",
            "पांडीचेरी": "Puducherry Pondicherry Promenade Beach French Quarter",
            "పుదుచ్చేరి": "Puducherry Pondicherry Promenade Beach French Quarter",
            "తమిళనాడు": "Tamil Nadu Chennai Madurai Mahabalipuram Ooty Kodaikanal",
            "தமிழ்நாடு": "Tamil Nadu Chennai Madurai Mahabalipuram Ooty Kodaikanal",
            "తెలంగాణ": "Telangana Hyderabad Charminar Biryani Golconda Warangal",
            "तेलंगाना": "Telangana Hyderabad Charminar Biryani Golconda Warangal",
            "ఉత్తర ప్రదేశ్": "Uttar Pradesh Agra Taj Mahal Varanasi Kashi Ayodhya",
            "उत्तर प्रदेश": "Uttar Pradesh Agra Taj Mahal Varanasi Kashi Ayodhya",
            "తాజ్ మహల్": "Taj Mahal Agra Uttar Pradesh India",
            "తాజ్‌మహల్": "Taj Mahal Agra Uttar Pradesh India",
            "ताज महल": "Taj Mahal Agra Uttar Pradesh India",
            "ఈఫిల్ టవర్": "Eiffel Tower Paris France",
            "एफ़िल टावर": "Eiffel Tower Paris France",
            "పారిస్": "Paris France Eiffel Tower Louvre",
            "పేరిస్": "Paris France Eiffel Tower Louvre",
            "पेरिस": "Paris France Eiffel Tower Louvre",
            "టోక్యో": "Tokyo Japan Sensoji Shibuya",
            "టొక్యో": "Tokyo Japan Sensoji Shibuya",
            "टोक्यो": "Tokyo Japan Sensoji Shibuya",
            "రోమ్": "Rome Italy Colosseum Vatican",
            "रोम": "Rome Italy Colosseum Vatican",
            "బిర్యానీ": "Telangana Hyderabad Dum Biryani food cuisine",
            "बिरयानी": "Telangana Hyderabad Dum Biryani food cuisine",
            "సద్య": "Kerala Sadya feast food cuisine",
            "మోమోస్": "Sikkim Momos food cuisine",
            "దోశ": "South India Dosa food cuisine",
            "వడా": "Maharashtra Vada Pav food cuisine",
            "寿司": "Japan Tokyo Kyoto Sushi food cuisine",
            "ラーメン": "Japan Tokyo Kyoto Ramen food cuisine"
        }
        for kw, mapped_str in dest_keywords.items():
            if kw.lower() in user_query.lower():
                search_query = mapped_str
                break

        # Step 5: Live Wikimedia Search with clean entity query
        wm_service = get_wikimedia_service()
        wm_entity_query = resolved_query
        if "Taj Mahal" in search_query or "తాజ్" in user_query or "ताज" in user_query:
            wm_entity_query = "Taj Mahal"
        elif "Eiffel Tower" in search_query or "ఈఫిల్" in user_query:
            wm_entity_query = "Eiffel Tower"
        elif "Paris" in search_query or "పారిస్" in user_query or "पेरिस" in user_query:
            wm_entity_query = "Paris"
        elif "Tokyo" in search_query or "టోక్యో" in user_query or "टोक्यो" in user_query:
            wm_entity_query = "Tokyo"
        elif "Rome" in search_query or "రోమ్" in user_query or "रोम" in user_query:
            wm_entity_query = "Rome"
        elif "Hyderabad" in search_query or "హైదరాబాద్" in user_query or "हैदराबाद" in user_query:
            wm_entity_query = "Hyderabad"
        else:
            wm_entity_query = wm_service.extract_entity_name(resolved_query)

        wm_context = wm_service.fetch_combined_travel_context(wm_entity_query, detected_lang)

        retrieved_results = self.index.search(search_query, top_k=4)

        # Step 6: Build Combined RAG Context Block
        context_blocks = []
        sources = []
        seen_sources = set()

        # Add live Wikimedia sources
        for wm_src in wm_context.get('sources', []):
            context_blocks.append('--- WIKIMEDIA SOURCE (' + str(wm_src.get('type')) + '): ' + str(wm_src.get('title')) + ' ---\n' + str(wm_src.get('summary')) + '\nURL: ' + str(wm_src.get('url')) + '\n')
            if wm_src['title'] not in seen_sources:
                sources.append({
                    "title": wm_src['title'],
                    "type": wm_src['type'],
                    "url": wm_src['url'],
                    "source": f"{wm_src['type']} — {wm_src['title']}"
                })
                seen_sources.add(wm_src['title'])

        # Add local vector search chunks
        for chunk, score in retrieved_results:
            context_blocks.append('--- LOCAL KB: ' + str(chunk.title) + ' ---\n' + str(chunk.content) + '\nSource: ' + str(chunk.metadata.get('source', 'TravelMate KB')) + '\n')
            src_name = chunk.metadata.get('source', 'Official Travel Guide')
            if src_name not in seen_sources:
                sources.append({
                    "title": chunk.title,
                    "destination": chunk.metadata.get("destination", ""),
                    "source": src_name,
                    "url": "https://wikivoyage.org"
                })
                seen_sources.add(src_name)

        combined_context = "\n".join(context_blocks)
        wm_images = wm_context.get('images', [])

        # Anti-Hallucination Guardrail Check
        if not wm_context.get('sources') and (not retrieved_results or retrieved_results[0][1] < 0.05):
            tmpl = MULTILINGUAL_TEMPLATES.get(detected_lang, MULTILINGUAL_TEMPLATES["en"])
            return {
                "answer": f"I couldn't find reliable information about this topic in the available Wikimedia sources.",
                "detected_language": SUPPORTED_LANGUAGES.get(detected_lang, {}).get("name", "English"),
                "language_code": detected_lang,
                "confidence": round(confidence, 2),
                "is_grounded": False,
                "sources": [],
                "images": [],
                "retrieved_count": 0
            }

        # Step 7: LLM Response Generation or Grounded Synthesizer
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        response_text = ""
        if gemini_api_key and gemini_api_key != "your_gemini_api_key_here":
            response_text = self._call_gemini_llm(resolved_query, combined_context, detected_lang, gemini_api_key, wm_context)
            if ("couldn't find" in response_text.lower() or "could not find" in response_text.lower()) and (wm_context.get('wikipedia_results') or wm_context.get('wikivoyage_results')):
                response_text = self._synthesize_grounded_response(resolved_query, retrieved_results, detected_lang, wm_context)
        
        if not response_text:
            response_text = self._synthesize_grounded_response(resolved_query, retrieved_results, detected_lang, wm_context)

        # Append Wikimedia Commons Images Section if available
        if wm_images:
            img_lines = ['\n\n🖼️ **Relevant Wikimedia Commons Media**:']
            for img in wm_images[:3]:
                img_lines.append(f"![{img['title']}]({img['url']})")
                img_lines.append(f"*[{img['attribution']}]({img['commons_link']})*\n")
            response_text += '\n'.join(img_lines)

        # Step 8: Post-process translation safeguard for selected language guarantee
        if detected_lang != "en":
            response_text = self._translate_text(response_text, detected_lang)

        # Build Debug Metrics for Development Panel
        debug_info = {
            "user_query": user_query,
            "resolved_query": resolved_query,
            "detected_language": SUPPORTED_LANGUAGES.get(detected_lang, {}).get("name", "English"),
            "language_code": detected_lang,
            "confidence": round(confidence, 2),
            "wikipedia_count": len(wm_context.get('wikipedia_results', [])),
            "wikivoyage_count": len(wm_context.get('wikivoyage_results', [])),
            "images_found": len(wm_images),
            "local_chunks_count": len(retrieved_results)
        }

        return {
            "answer": response_text,
            "detected_language": SUPPORTED_LANGUAGES.get(detected_lang, {}).get("name", "English"),
            "language_code": detected_lang,
            "confidence": round(confidence, 2),
            "is_grounded": True,
            "sources": sources,
            "images": wm_images,
            "wikimedia_results": wm_context,
            "debug_info": debug_info,
            "retrieved_count": len(sources)
        }

    def _detect_intent(self, query: str) -> str:
        """Classifies query into user intent: best_time, budget, food, stays, tips, or general."""
        q = query.lower()
        if any(k in q for k in ['time', 'when', 'month', 'season', 'weather', 'climate', 'best time', 'సమయం', 'వాతావరణం', 'समय', 'मौसम', 'நேரம்', 'வானிலை', 'ಸಮಯ', 'ಹವಾಮಾನ', 'മഴ', 'സമയം', 'সময়', 'वेळ', 'tiempo', 'clima', 'météo', 'wetter', '天気', 'طقس', '날씨']):
            return 'best_time'
        if any(k in q for k in ['budget', 'cost', 'price', 'expense', 'how much', 'cheap', 'money', 'dollar', 'rupee', 'inr', 'బడ్జెట్', 'ధర', 'बजट', 'खर्च', 'பட்ஜெட்', 'ಬಜೆಟ್', 'ഖരച', 'বাজেট', 'किंमत', 'presupuesto', 'costo', 'budget', 'prix', 'kosten', '費用', 'ميزانية', '비용']):
            return 'budget'
        food_terms = ['food', 'eat', 'dish', 'cuisine', 'restaurant', 'vegetarian', 'vegan', 'lunch', 'dinner', 'biryani', 'sadya', 'momos', 'sushi', 'dosa', 'idli', 'thali', 'shawarma', 'croissant', 'macarons', 'petha', 'fondue', 'ramen', 'vada', 'pav', 'haleem', 'prawns', 'curry', 'seafood', 'sweet', 'tea', 'chai', 'coffee', 'pesarattu', 'pootharekulu', 'guntur', 'uttapam', 'kachori', 'lassi', 'rogan', 'wazwan', 'appam', 'puttu', 'parotta', 'bikaneri', 'gatte', 'ghevar', 'bhelpuri', 'falafel', 'baklava', 'kebab', 'tacos', 'tapas', 'paella', 'schnitzel', 'gelato', 'pasta', 'pizza', '딤섬', '초밥', '라멘', 'ఆహారం', 'రుచులు', 'భోజనం', 'బిర్యానీ', 'దోశ', 'ఇడ్లీ', 'సద్య', 'మోమోస్', 'పెసరట్టు', 'పూతరేకులు', 'పరోటా', 'खाना', 'व्यंजन', 'बिरयानी', 'दौसा', 'मोमो', 'डोसा', 'कचौरी', 'जलेबी', 'लस्सी', 'पेठा', 'உணவு', 'சாப்பாடு', 'பிரியாணி', 'தோசை', 'ஆಹಾರ', 'ಬಿರಿಯಾನಿ', 'ದೋಸೆ', 'ഭക്ഷണം', 'ബിരിയാണി', 'സദ്യ', 'പുട്ട്', 'അപ്പം', 'খাবার', 'বিরিয়ানি', 'মোমো', 'রসগোল্লা', 'জেवण', 'बिरयानी', 'वडा', 'पाव', 'comida', 'platos', 'cuisine', 'manger', 'essen', '料理', '寿司', 'ラーメン', 'طعام', 'برياني', 'شاورما', '음식', '비빔밥']
        if any(k in q for k in food_terms):
            return 'food'
        if any(k in q for k in ['hotel', 'stay', 'resort', 'room', 'hostel', 'accommodation', 'వసతి', 'హోటళ్ళు', 'होटल', 'आवास', 'தங்குமிடம்', 'ವಸತಿ', 'താമസം', 'ഹോട്ടൽ', 'रहाणे', 'hotel', 'alojamiento', 'hébergement', 'unterkunft', 'ホテル', 'فندق', '숙소']):
            return 'stays'
        if any(k in q for k in ['visa', 'transport', 'flight', 'reach', 'bus', 'train', 'taxi', 'safety', 'passport', 'వీసా', 'ప్రయాణం', 'वीजा', 'परिवहन', 'விசா', 'ವಿಸಾ', 'വിസ', 'ভিসা', 'व्हिसा', 'visado', 'visa', 'visum', 'ビザ', 'تأشيرة', '비자']):
            return 'tips'
        return 'general'

    def _call_gemini_llm(self, query: str, context: str, lang_code: str, api_key: str, wm_context: Optional[Dict[str, Any]] = None) -> str:
        """Invokes Google Gemini API with strict instruction to output ONLY the direct answer with markdown photos."""
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            target_lang_name = SUPPORTED_LANGUAGES.get(lang_code, {}).get("name", "English")
            intent = self._detect_intent(query)
            
            intent_guidance = {
                "best_time": "Output ONLY the best time to visit, weather overview, and ideal climate months.",
                "budget": "Output ONLY the estimated daily budget, expenses, currency, and stays budget breakdown.",
                "food": "Output ONLY famous local cuisine, must-try dishes, vegetarian/vegan options, and street food.",
                "stays": "Output ONLY accommodations, budget stays, mid-range hotels, and luxury resorts.",
                "tips": "Output ONLY visa requirements, transport logistics, safety guidelines, and practical travel tips.",
                "general": "Output ONLY top attractions, landmarks, and hidden gems."
            }
            specific_focus = intent_guidance.get(intent, intent_guidance["general"])

            system_prompt = f"""You are TravelMate AI, a world-class multilingual travel assistant.
Answer the user's travel question directly and comprehensively using the provided RAG CONTEXT below.
Extract and summarize all relevant destination information, top attractions, history, culture, food, accommodations, or travel tips from the context.
Format your output cleanly in Markdown with bold titles, emojis, and clear bullet points.
IMPORTANT: Respond fully in language: {target_lang_name} ({lang_code}).

RAG CONTEXT:
{context}
"""
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_prompt}\n\nUSER QUESTION: {query}"
            )
            res_text = response.text
            if lang_code != "en":
                res_text = self._translate_text(res_text, lang_code)
            return res_text
        except Exception as e:
            print(f"Gemini API Call failed: {e}. Falling back to RAG Synthesizer.")
            return self._synthesize_grounded_response(query, self.index.search(query, top_k=4), lang_code, wm_context)

    def _synthesize_grounded_response(self, query: str, results: List[Tuple[DocumentChunk, float]], lang_code: str, wm_context: Optional[Dict[str, Any]] = None) -> str:
        """Grounded RAG Generator synthesizing answer from live Wikimedia sources and Knowledge Base."""
        lines = []

        wm_items = []
        if wm_context:
            wm_items = wm_context.get('wikipedia_results', []) + wm_context.get('wikivoyage_results', [])

        # 1. Synthesize from Live Wikimedia Wikipedia/Wikivoyage extracts first
        if wm_items:
            for item in wm_items[:3]:
                title = item.get('title', 'Travel Info')
                src_type = item.get('source_type', 'Wikimedia')
                summary = item.get('summary', '').strip()
                if summary:
                    lines.append(f"📍 **{title}** *({src_type})*\n{summary}\n")

            if lines:
                msg = "\n".join(lines)
                if lang_code != "en":
                    msg = self._translate_text(msg, lang_code)
                return msg

        # 2. Fallback to local Knowledge Base
        top_dest = results[0][0].metadata.get("raw_dest", {}) if results and "raw_dest" in results[0][0].metadata else None
        
        if not top_dest:
            if results:
                chunk = results[0][0]
                msg = f"### 📌 {chunk.title}\n{chunk.content}"
                if lang_code != "en":
                    msg = self._translate_text(msg, lang_code)
                return msg

            msg = f"I couldn't find reliable information about this topic in the available Wikimedia sources."
            if lang_code != "en":
                msg = self._translate_text(msg, lang_code)
            return msg

        intent = self._detect_intent(query)
        lines = []

        food_photo_md = f"\n![Famous Food & Local Cuisine in {top_dest['destination']}]({top_dest['food_image_url']})\n" if top_dest.get('food_image_url') else ""

        if intent == "food":
            food = top_dest.get('food_and_cuisine', {})
            lines.append(f"🍱 **Famous Cuisine & Food in {top_dest['destination']}, {top_dest['country']}**:\n")
            if food_photo_md:
                lines.append(food_photo_md)
            if food:
                lines.append(f"- **Must-Try Dishes**: " + ", ".join(food.get('famous_dishes', [])))
                lines.append(f"- **Vegetarian & Vegan Options**: {food.get('vegetarian_vegan_options', 'Available')}")
                lines.append(f"- **Popular Street Food**: " + ", ".join(food.get('popular_street_food', [])))
                if food.get('budget_food_tips'):
                    lines.append(f"- 💡 **Dining Tip**: {food.get('budget_food_tips')}")

        elif intent == "best_time":
            lines.append(f"🗓️ **Best Time & Weather for {top_dest['destination']}, {top_dest['country']}**:\n")
            if top_dest.get('image_url'):
                lines.append(f"![{top_dest['destination']} Climate & View]({top_dest['image_url']})\n")
            lines.append(f"- **Best Time to Visit**: {top_dest.get('best_time_to_visit', 'N/A')}")
            lines.append(f"- **Weather Overview**: {top_dest.get('weather', 'N/A')}")
            if food_photo_md:
                lines.append(f"\n🍱 **Famous Local Dishes & Food**:")
                lines.append(food_photo_md)

        elif intent == "budget":
            lines.append(f"💰 **Estimated Travel Budget for {top_dest['destination']}, {top_dest['country']}**:\n")
            if top_dest.get('image_url'):
                lines.append(f"![{top_dest['destination']} Travel View]({top_dest['image_url']})\n")
            lines.append(f"- **Daily Cost Range**: {top_dest.get('approx_budget_inr', 'N/A')} ({top_dest.get('budget_range_usd', '')})")
            lines.append(f"- **Currency**: {top_dest.get('currency', 'Local Currency')}")
            acc = top_dest.get('accommodations', {})
            if acc:
                lines.append(f"- **Budget Stays**: {acc.get('budget', 'N/A')}")
                lines.append(f"- **Mid-range Hotels**: {acc.get('mid_range', 'N/A')}")
                lines.append(f"- **Luxury Resorts**: {acc.get('luxury', 'N/A')}")
            food = top_dest.get('food_and_cuisine', {})
            if food and food.get('budget_food_tips'):
                lines.append(f"- 💡 **Budget Dining Tip**: {food.get('budget_food_tips')}")
            if food_photo_md:
                lines.append(f"\n🍱 **Local Food & Cuisine Preview**:")
                lines.append(food_photo_md)

        elif intent == "stays":
            acc = top_dest.get('accommodations', {})
            lines.append(f"🏨 **Accommodations & Stays in {top_dest['destination']}, {top_dest['country']}**:\n")
            if top_dest.get('image_url'):
                lines.append(f"![{top_dest['destination']} Hotels & Stays]({top_dest['image_url']})\n")
            if acc:
                lines.append(f"- **Budget Stays**: {acc.get('budget', 'N/A')}")
                lines.append(f"- **Mid-range Hotels**: {acc.get('mid_range', 'N/A')}")
                lines.append(f"- **Luxury Resorts**: {acc.get('luxury', 'N/A')}")
            if food_photo_md:
                lines.append(f"\n🍱 **Famous Local Dining & Food**:")
                lines.append(food_photo_md)

        elif intent == "tips":
            lines.append(f"🛂 **Practical Travel Tips, Transport & Visa for {top_dest['destination']}, {top_dest['country']}**:\n")
            if top_dest.get('image_url'):
                lines.append(f"![{top_dest['destination']} Travel View]({top_dest['image_url']})\n")
            lines.append(f"- **Visa Requirements**: {top_dest.get('visa_requirements', 'N/A')}")
            lines.append(f"- **Local Transport**: {top_dest.get('local_transport', 'N/A')}")
            lines.append(f"- **Safety & Etiquette**: {top_dest.get('safety_and_etiquette', 'Follow standard tourist guidelines.')}")
            for tip in top_dest.get('practical_tips', []):
                lines.append(f"- 💡 {tip}")
            if food_photo_md:
                lines.append(f"\n🍱 **Famous Local Food**:")
                lines.append(food_photo_md)

        else: # general overview: attractions & highlights
            lines.append(f"📍 **Top Places to Visit in {top_dest['destination']}, {top_dest['country']}**:\n")
            if top_dest.get('image_url'):
                lines.append(f"![{top_dest['destination']} Attractions & Landmarks]({top_dest['image_url']})\n")
            for att in top_dest.get('attractions', []):
                lines.append(f"- {att}")
            if top_dest.get('hidden_gems'):
                lines.append(f"\n💎 **Hidden Gems**: " + ", ".join(top_dest.get('hidden_gems', [])))
            if food_photo_md:
                lines.append(f"\n🍱 **Famous Local Cuisine & Food Items**:")
                lines.append(food_photo_md)

        full_english_text = "\n".join(lines)
        if lang_code != "en":
            translated_body = self._translate_text(full_english_text, lang_code)
            return translated_body
        
        return full_english_text

    def _translate_text(self, text: str, target_lang: str) -> str:
        """Translates text to target language using deep_translator GoogleTranslator while preserving markdown images."""
        if not text or target_lang == "en":
            return text
        try:
            from deep_translator import GoogleTranslator
            lang_map = {
                "te": "te", "hi": "hi", "ta": "ta", "kn": "kn",
                "ml": "ml", "bn": "bn", "mr": "mr", "es": "es",
                "fr": "fr", "de": "de", "it": "it", "pt": "pt",
                "ar": "ar", "ja": "ja", "ko": "ko", "zh": "zh-CN"
            }
            target = lang_map.get(target_lang, target_lang)
            translator = GoogleTranslator(source='auto', target=target)
            
            # Extract and protect markdown images
            image_placeholders = {}
            def replace_img(match):
                key = f"__IMG_HOLDER_{len(image_placeholders)}__"
                image_placeholders[key] = match.group(0)
                return key

            protected_text = re.sub(r'!\[.*?\]\(https?://[^\s\)]+\)', replace_img, text)

            # Paragraph chunking for text translation
            paragraphs = protected_text.split("\n\n")
            translated_paragraphs = []
            for p in paragraphs:
                if not p.strip():
                    translated_paragraphs.append("")
                    continue
                try:
                    tr = translator.translate(p)
                    translated_paragraphs.append(tr if tr else p)
                except Exception as chunk_err:
                    print(f"[Chunk Translation Warning] {chunk_err}")
                    translated_paragraphs.append(p)
                    
            translated_full = "\n\n".join(translated_paragraphs)

            # Restore original image markdown placeholders
            for key, orig_img in image_placeholders.items():
                translated_full = translated_full.replace(key, orig_img)

            return translated_full
        except Exception as e:
            print(f"[Translation Warning] {e}")
            return text


# Singleton RAG instance initialization helper
_rag_instance: Optional[TravelRAGPipeline] = None

def get_rag_pipeline(data_path: str = "data/knowledge_base.json") -> TravelRAGPipeline:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = TravelRAGPipeline(data_path)
    return _rag_instance