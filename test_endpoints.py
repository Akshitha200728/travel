"""
Automated REST API verification script for TravelSphere AI server running at http://127.0.0.1:5000
"""

import json
import urllib.request

BASE_URL = "http://127.0.0.1:5000"

def test_homepage():
    req = urllib.request.Request(f"{BASE_URL}/")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        assert resp.status == 200
        assert "TravelSphere AI" in html
        assert "uiLangSelect" in html
        print("[OK] Homepage GET / verified successfully (HTTP 200).")

def test_chat_telugu():
    payload = json.dumps({
        "query": "హైదరాబాద్లో చూడదగిన ప్రదేశాలు ఏవి?",
        "language": "auto"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/chat", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert resp.status == 200
        assert data["status"] == "success"
        assert data["detected_language"] == "Telugu"
        assert data["is_grounded"] is True
        assert "Charminar" in data["answer"]
        print("[OK] Chat API Telugu Query RAG Grounded response verified successfully.")

def test_chat_english():
    payload = json.dumps({
        "query": "What are the best places to visit in Japan?",
        "language": "en"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/chat", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert resp.status == 200
        assert data["status"] == "success"
        assert "Tokyo" in data["answer"]
        print("[OK] Chat API English Query RAG Grounded response verified successfully.")

def test_trip_planner():
    payload = json.dumps({
        "destination": "Goa",
        "days": 5,
        "budget": 50000,
        "currency": "INR",
        "style": "family"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/plan-trip", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert resp.status == 200
        assert data["status"] == "success"
        assert len(data["itinerary"]) == 5
        assert "cost_breakdown" in data
        print("[OK] Trip Planner API 5-Day Plan verified successfully.")

def test_destinations():
    req = urllib.request.Request(f"{BASE_URL}/api/destinations?region=Europe")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert resp.status == 200
        assert data["count"] >= 3
        print("[OK] Destinations Explorer API verified successfully.")

def test_stats():
    req = urllib.request.Request(f"{BASE_URL}/api/stats")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert resp.status == 200
        assert data["total_destinations"] >= 8
        print(f"[OK] System Stats API verified successfully ({data['total_destinations']} destinations, {data['rag_document_chunks']} RAG chunks).")

if __name__ == "__main__":
    print("\n--- Running TravelSphere AI Live Endpoint Verification ---")
    test_homepage()
    test_chat_telugu()
    test_chat_english()
    test_trip_planner()
    test_destinations()
    test_stats()
    print("ALL API ENDPOINTS OPERATIONAL & VERIFIED!\n")
