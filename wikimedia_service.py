"""
TravelMate AI - Wikimedia Integration Service
Programmatic integration with Wikipedia, Wikivoyage, and Wikimedia Commons APIs.
Complies with Wikimedia User-Agent policies.
"""

import json
import re
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple, Any

USER_AGENT = "TravelMateAI/1.0 (https://github.com/travelmate-ai; travelmate-ai-contact@example.com)"

# Supported Language Domain Mapping
WIKIMEDIA_LANG_DOMAINS = {
    "en": "en", "te": "te", "hi": "hi", "ta": "ta",
    "kn": "kn", "ml": "ml", "bn": "bn", "mr": "mr",
    "fr": "fr", "es": "es", "de": "de", "ja": "ja"
}

class WikimediaService:
    def __init__(self):
        self.headers = {"User-Agent": USER_AGENT}

    def _http_get_json(self, url: str, timeout: int = 8) -> Optional[Dict[str, Any]]:
        """Utility method to make HTTP GET request and return JSON object."""
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
        except Exception as e:
            print(f"[WikimediaService HTTP Warning] Failed to fetch {url}: {e}")
        return None

    def search_wikipedia(self, query: str, lang_code: str = "en", limit: int = 3) -> List[Dict[str, Any]]:
        """
        Searches Wikipedia REST and MediaWiki API for article extracts and metadata.
        Uses language-specific Wikipedia domain (e.g. te.wikipedia.org).
        """
        domain_lang = WIKIMEDIA_LANG_DOMAINS.get(lang_code, "en")
        results = []
        clean_entity = self.extract_entity_name(query)

        # 1. Direct REST API Page Summary lookup for exact title match
        direct_summary_url = f"https://{domain_lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_entity.replace(' ', '_'))}"
        direct_data = self._http_get_json(direct_summary_url)

        if direct_data and direct_data.get('type') == 'standard' and direct_data.get('extract'):
            results.append({
                "title": direct_data.get('title', clean_entity),
                "page_id": direct_data.get('pageid'),
                "summary": direct_data.get('extract', ''),
                "description": direct_data.get('description', ''),
                "thumbnail": direct_data.get('thumbnail', {}).get('source', ''),
                "source_type": "Wikipedia",
                "language": domain_lang,
                "url": direct_data.get('content_urls', {}).get('desktop', {}).get('page', f"https://{domain_lang}.wikipedia.org/wiki/{urllib.parse.quote(clean_entity.replace(' ', '_'))}")
            })

        # 2. MediaWiki API Search
        search_url = f"https://{domain_lang}.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_entity)}&utf8=1&format=json"
        search_json = self._http_get_json(search_url)

        if search_json and 'query' in search_json and 'search' in search_json.get('query', {}):
            search_items = search_json['query']['search'][:limit]
            for item in search_items:
                if len(results) >= limit + 1:
                    break
                title = item.get('title')
                if not title or any(r['title'].lower() == title.lower() for r in results):
                    continue

                summary_url = f"https://{domain_lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                summary_data = self._http_get_json(summary_url)
                if summary_data and summary_data.get('extract'):
                    results.append({
                        "title": title,
                        "page_id": item.get('pageid'),
                        "summary": summary_data.get('extract', ''),
                        "description": summary_data.get('description', ''),
                        "thumbnail": summary_data.get('thumbnail', {}).get('source', ''),
                        "source_type": "Wikipedia",
                        "language": domain_lang,
                        "url": f"https://{domain_lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    })

        # Fallback to English Wikipedia if native language search returned no results
        if not results and domain_lang != "en":
            return self.search_wikipedia(clean_entity, "en", limit)

        return results

    def search_wikivoyage(self, query: str, lang_code: str = "en", limit: int = 3) -> List[Dict[str, Any]]:
        """
        Searches Wikivoyage travel guide API for destination guides, activities, cuisine, and itineraries.
        """
        domain_lang = WIKIMEDIA_LANG_DOMAINS.get(lang_code, "en")
        results = []
        clean_entity = self.extract_entity_name(query)

        # 1. Direct REST API Page Summary lookup for exact title match
        direct_summary_url = f"https://{domain_lang}.wikivoyage.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_entity.replace(' ', '_'))}"
        direct_data = self._http_get_json(direct_summary_url)

        if direct_data and direct_data.get('type') == 'standard' and direct_data.get('extract'):
            results.append({
                "title": direct_data.get('title', clean_entity),
                "page_id": direct_data.get('pageid'),
                "summary": direct_data.get('extract', ''),
                "description": direct_data.get('description', ''),
                "thumbnail": direct_data.get('thumbnail', {}).get('source', ''),
                "source_type": "Wikivoyage",
                "language": domain_lang,
                "url": direct_data.get('content_urls', {}).get('desktop', {}).get('page', f"https://{domain_lang}.wikivoyage.org/wiki/{urllib.parse.quote(clean_entity.replace(' ', '_'))}")
            })

        # 2. MediaWiki API Search
        search_url = f"https://{domain_lang}.wikivoyage.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(clean_entity)}&utf8=1&format=json"
        search_json = self._http_get_json(search_url)

        if search_json and 'query' in search_json and 'search' in search_json.get('query', {}):
            search_items = search_json['query']['search'][:limit]
            for item in search_items:
                if len(results) >= limit + 1:
                    break
                title = item.get('title')
                if not title or any(r['title'].lower() == title.lower() for r in results):
                    continue

                summary_url = f"https://{domain_lang}.wikivoyage.org/api/rest_v1/page/summary/{urllib.parse.quote(title.replace(' ', '_'))}"
                summary_data = self._http_get_json(summary_url)
                if summary_data and summary_data.get('extract'):
                    results.append({
                        "title": title,
                        "page_id": item.get('pageid'),
                        "summary": summary_data.get('extract', ''),
                        "description": summary_data.get('description', ''),
                        "thumbnail": summary_data.get('thumbnail', {}).get('source', ''),
                        "source_type": "Wikivoyage",
                        "language": domain_lang,
                        "url": f"https://{domain_lang}.wikivoyage.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    })

        # Fallback to English Wikivoyage if native search yielded no results
        if not results and domain_lang != "en":
            return self.search_wikivoyage(clean_entity, "en", limit)

        return results

    def extract_entity_name(self, query: str) -> str:
        """Extracts main destination/monument entity title from natural language query across languages."""
        clean = re.sub(r'[?\!\.,]', '', query.strip())
        # English patterns
        clean = re.sub(r'^(tell me about the|tell me about|what are the best places in|what is the history of|what can i do in|give me a 3-day itinerary for|give me an itinerary for|best tourist attractions in|what food is famous in|places to visit in|how to reach|where to stay in|about)\s+', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s+(history|culture|food|cuisine|itinerary|weather|attractions|places|hotels|budget|visa)$', '', clean, flags=re.IGNORECASE)
        # Multilingual suffix/prefix strippers
        clean = re.sub(r'\s+(గురించి చెప్పండి|గురించి|చూడదగిన ప్రదేశాలు|చూడదగిన స్థలాలు|ఏమిటి|కే గురించి|के बारे में बताएं|के बारे में|दर्शनीय स्थल|பற்றி சொல்லுங்கள்|பற்றி|ಬಗ್ಗೆ ಹೇಳಿ|കുറിച്ച് പറയൂ|সম্পর্কে বলুন|बद्दल सांगा)$', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'^(గురించి|के बारे में|பற்றி)\s+', '', clean, flags=re.IGNORECASE)
        return clean.strip() or query.strip()

    def get_wikimedia_images(self, entity_name: str, lang_code: str = "en", limit: int = 4) -> List[Dict[str, str]]:
        """
        Fetches high-quality images with license attribution metadata from Wikimedia Commons and Wikipedia Page Media APIs.
        """
        images = []
        seen_urls = set()
        domain_lang = WIKIMEDIA_LANG_DOMAINS.get(lang_code, "en")
        extracted_entity = self.extract_entity_name(entity_name)

        # 1. Fetch images associated with Wikipedia page media REST API
        clean_title = extracted_entity.strip().replace(' ', '_')
        wiki_media_url = f"https://{domain_lang}.wikipedia.org/api/rest_v1/page/media-list/{urllib.parse.quote(clean_title)}"
        media_data = self._http_get_json(wiki_media_url)

        if media_data and 'items' in media_data:
            for item in media_data['items']:
                if len(images) >= limit:
                    break
                if item.get('type') == 'image' and 'srcset' in item:
                    srcset = item['srcset']
                    if srcset:
                        img_url = srcset[-1].get('src', '')
                        if img_url and img_url not in seen_urls:
                            if img_url.startswith('//'):
                                img_url = 'https:' + img_url
                            title_clean = item.get('title', entity_name).replace('File:', '').replace('_', ' ')
                            artist_clean = item.get('caption', {}).get('text', 'Wikimedia Commons Contributor') or "Wikimedia Contributor"
                            license_name = item.get('license', {}).get('type', 'CC BY-SA 4.0')
                            
                            images.append({
                                "url": img_url,
                                "title": title_clean,
                                "author": artist_clean,
                                "license": license_name,
                                "attribution": f"Image: Wikimedia Commons — {title_clean}",
                                "commons_link": f"https://commons.wikimedia.org/wiki/File:{urllib.parse.quote(title_clean.replace(' ', '_'))}"
                            })
                            seen_urls.add(img_url)

        # 2. Search Wikimedia Commons generator API as secondary source
        if len(images) < limit:
            commons_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(entity_name)}&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata|mime&iiurlwidth=800&format=json"
            data = self._http_get_json(commons_url)

            if data and 'query' in data and 'pages' in data['query']:
                pages = data['query']['pages']
                for pid, pdata in pages.items():
                    if len(images) >= limit:
                        break
                    imageinfo = pdata.get('imageinfo', [])
                    if not imageinfo:
                        continue
                    info = imageinfo[0]
                    mime = info.get('mime', '')
                    if not (mime.startswith('image/jpeg') or mime.startswith('image/png') or mime.startswith('image/webp')):
                        continue

                    url = info.get('thumburl') or info.get('url')
                    if not url or url in seen_urls:
                        continue

                    extmeta = info.get('extmetadata', {})
                    artist_raw = extmeta.get('Artist', {}).get('value', 'Wikimedia Contributor')
                    artist_clean = re.sub(r'<[^>]+>', '', artist_raw).strip() or "Wikimedia Contributor"
                    license_name = extmeta.get('LicenseShortName', {}).get('value', 'CC BY-SA 4.0')
                    title_clean = pdata.get('title', 'Wikimedia Media').replace('File:', '')

                    images.append({
                        "url": url,
                        "title": title_clean,
                        "author": artist_clean,
                        "license": license_name,
                        "attribution": f"Image: Wikimedia Commons — {artist_clean} ({license_name})",
                        "commons_link": info.get('descriptionurl', f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(pdata.get('title', ''))}")
                    })
                    seen_urls.add(url)

        return images

    def fetch_combined_travel_context(self, query: str, lang_code: str = "en") -> Dict[str, Any]:
        """
        Performs full RAG retrieval pipeline: Wikipedia + Wikivoyage + Wikimedia Commons images.
        """
        q_lower = query.lower()
        prefer_wikivoyage = any(k in q_lower for k in ['do', 'visit', 'stay', 'hotel', 'itinerary', 'food', 'eat', 'dish', 'transport', 'how to get', 'things to do', 'attractions', 'tips'])

        wiki_results = self.search_wikipedia(query, lang_code, limit=3)
        voyage_results = self.search_wikivoyage(query, lang_code, limit=3)
        images = self.get_wikimedia_images(query, limit=4)

        sources = []
        seen_titles = set()

        if prefer_wikivoyage:
            primary_list = voyage_results + wiki_results
        else:
            primary_list = wiki_results + voyage_results

        for res in primary_list:
            t = res['title']
            if t not in seen_titles:
                sources.append({
                    "title": t,
                    "type": res['source_type'],
                    "url": res['url'],
                    "summary": res['summary']
                })
                seen_titles.add(t)

        return {
            "query": query,
            "language": lang_code,
            "sources": sources,
            "wikipedia_results": wiki_results,
            "wikivoyage_results": voyage_results,
            "images": images,
            "prefer_wikivoyage": prefer_wikivoyage
        }


# Singleton service instance helper
_wikimedia_service_instance: Optional[WikimediaService] = None

def get_wikimedia_service() -> WikimediaService:
    global _wikimedia_service_instance
    if _wikimedia_service_instance is None:
        _wikimedia_service_instance = WikimediaService()
    return _wikimedia_service_instance
