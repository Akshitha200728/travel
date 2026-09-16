"""
TravelMate AI - Web Application Backend Server (Flask)
Exposes REST APIs for Multilingual RAG Chatbot, Wikimedia Integration, Trip Planner, Explorer, and Debug Diagnostics.
"""

import sys
import os

os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from rag_engine import get_rag_pipeline, SUPPORTED_LANGUAGES
from wikimedia_service import get_wikimedia_service

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Initialize RAG Pipeline
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.json")
rag_pipeline = get_rag_pipeline(DATA_PATH)


@app.route("/")
def index():
    """Renders the main TravelMate AI Single Page Application."""
    return render_template("index.html")


@app.route("/api/languages", methods=["GET"])
def get_languages():
    """Returns list of supported Indian & International languages."""
    return jsonify({
        "status": "success",
        "languages": SUPPORTED_LANGUAGES
    })


@app.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """RAG Chat API endpoint with Wikimedia Integration & Session Context."""
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    user_language = data.get("language", "auto")
    session_context = data.get("session_context", {})

    if not query:
        return jsonify({
            "status": "error",
            "message": "Query cannot be empty."
        }), 400

    try:
        rag_response = rag_pipeline.query(user_query=query, lang_override=user_language, session_context=session_context)
        return jsonify({
            "status": "success",
            "query": query,
            **rag_response
        })
    except Exception as e:
        print(f"Error processing chat query: {e}")
        return jsonify({
            "status": "error",
            "message": "An internal server error occurred while processing your travel query."
        }), 500


@app.route("/api/wikimedia-search", methods=["GET"])
@app.route("/api/wikimedia/search", methods=["GET"])
def wikimedia_search_endpoint():
    """Live Wikimedia API search endpoint for Wikipedia, Wikivoyage, and Commons media."""
    query = request.args.get("query", "Paris").strip()
    lang = request.args.get("language", "en").strip()
    wm_service = get_wikimedia_service()
    data = wm_service.fetch_combined_travel_context(query, lang)
    return jsonify({
        "status": "success",
        **data
    })


@app.route("/api/debug", methods=["POST"])
def debug_endpoint():
    """Dev Mode Diagnostic API endpoint returning full RAG trace & Wikimedia payload."""
    data = request.get_json() or {}
    query = data.get("query", "Paris").strip()
    lang = data.get("language", "auto")
    session_context = data.get("session_context", {})
    rag_response = rag_pipeline.query(user_query=query, lang_override=lang, session_context=session_context)
    return jsonify({
        "status": "success",
        "debug_payload": rag_response.get("debug_info", {}),
        "wikimedia_sources": rag_response.get("sources", []),
        "images": rag_response.get("images", []),
        "wikimedia_results": rag_response.get("wikimedia_results", {})
    })


@app.route("/api/destinations", methods=["GET"])
def get_destinations():
    """Retrieve catalog of destinations with optional region and category filtering."""
    region = request.args.get("region", "all").strip().lower()
    category = request.args.get("category", "all").strip().lower()
    search = request.args.get("search", "").strip().lower()

    destinations = rag_pipeline.raw_data.get("destinations", [])
    filtered = []

    for d in destinations:
        if region != "all" and d.get("region", "").lower() != region:
            continue
        if category != "all" and category not in d.get("category", "").lower():
            continue
        if search and (search not in d.get("destination", "").lower() and search not in d.get("country", "").lower() and search not in " ".join(d.get("tags", [])).lower()):
            continue
        filtered.append(d)

    return jsonify({
        "status": "success",
        "count": len(filtered),
        "destinations": filtered
    })


@app.route("/api/plan-trip", methods=["POST"])
def plan_trip_endpoint():
    """Interactive Trip Itinerary Generator endpoint based on user budget, style, and duration."""
    data = request.get_json() or {}
    destination_name = data.get("destination", "Goa").strip()
    days = int(data.get("days", 5))
    budget = float(data.get("budget", 50000))
    currency = data.get("currency", "INR")
    style = data.get("style", "balanced") # solo, family, honeymoon, budget, luxury

    # Query RAG for destination knowledge
    query_text = f"Plan a trip to {destination_name} budget {budget} {currency}"
    rag_res = rag_pipeline.query(query_text)
    
    # Locate exact destination record if available
    dest_data = None
    for d in rag_pipeline.raw_data.get("destinations", []):
        if destination_name.lower() in d.get("destination", "").lower() or d.get("destination", "").lower() in destination_name.lower():
            dest_data = d
            break

    # Build Day-by-Day Customized Plan
    daily_budget = round(budget / days, 2)
    attractions = dest_data.get("attractions", ["Main City Sightseeing", "Local Culture Walk", "Famous Landmark Visit", "Scenic Sunset Spot", "Souvenir Shopping"]) if dest_data else ["City Highlights Tour", "Heritage Walk", "Local Cuisine Tasting", "Scenic Viewpoint"]
    food_list = dest_data.get("food_and_cuisine", {}).get("famous_dishes", ["Local Cuisine", "Regional Specialty", "Street Food Treats"]) if dest_data else ["Local Specialties"]
    
    itinerary_days = []
    attraction_idx = 0
    
    for day in range(1, days + 1):
        att1 = attractions[attraction_idx % len(attractions)]
        attraction_idx += 1
        att2 = attractions[attraction_idx % len(attractions)]
        attraction_idx += 1
        food1 = food_list[(day - 1) % len(food_list)]
        
        itinerary_days.append({
            "day": day,
            "title": f"Day {day}: Exploring {dest_data['destination'] if dest_data else destination_name} - Highlights & Culture",
            "morning": f"Morning breakfast & visit to **{att1}**.",
            "afternoon": f"Lunch break sampling **{food1}** followed by exploring **{att2}**.",
            "evening": f"Evening leisure stroll, local sunset views, and casual street food tasting.",
            "night": f"Dinner at recommended top-rated bistro / restaurant and restful stay.",
            "estimated_daily_cost": f"{currency} {daily_budget:,.2f}"
        })

    cost_breakdown = {
        "accommodations": f"{currency} {round(budget * 0.40, 2):,.2f} (40%)",
        "food_and_dining": f"{currency} {round(budget * 0.25, 2):,.2f} (25%)",
        "local_transport": f"{currency} {round(budget * 0.15, 2):,.2f} (15%)",
        "attractions_and_activities": f"{currency} {round(budget * 0.12, 2):,.2f} (12%)",
        "emergency_and_shopping": f"{currency} {round(budget * 0.08, 2):,.2f} (8%)",
        "total_budget": f"{currency} {budget:,.2f}"
    }

    return jsonify({
        "status": "success",
        "destination": dest_data.get("destination", destination_name) if dest_data else destination_name,
        "country": dest_data.get("country", "") if dest_data else "",
        "days": days,
        "style": style.capitalize(),
        "total_budget": f"{currency} {budget:,.2f}",
        "daily_budget": f"{currency} {daily_budget:,.2f}",
        "best_season": dest_data.get("best_time_to_visit", "October to March") if dest_data else "Seasonal",
        "visa_info": dest_data.get("visa_requirements", "Check official embassy portal.") if dest_data else "Standard tourist visa required.",
        "cost_breakdown": cost_breakdown,
        "itinerary": itinerary_days,
        "source": dest_data.get("source", "TravelSphere AI Itinerary Planner") if dest_data else "TravelSphere AI Planner"
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns analytics statistics for knowledge base."""
    destinations = rag_pipeline.raw_data.get("destinations", [])
    regions = set(d.get("region") for d in destinations)
    countries = set(d.get("country") for d in destinations)

    return jsonify({
        "status": "success",
        "total_destinations": len(destinations),
        "total_countries": len(countries),
        "total_regions": len(regions),
        "rag_document_chunks": rag_pipeline.index.total_docs,
        "supported_languages_count": len(SUPPORTED_LANGUAGES),
        "regions_covered": list(regions)
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"[TravelMate AI] Starting server on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
