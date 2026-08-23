"""
TravelSphere AI - Test Suite for RAG Pipeline, Language Detector & REST APIs
"""

import sys
import json
import unittest
from rag_engine import LanguageDetector, get_rag_pipeline, SUPPORTED_LANGUAGES

class TestTravelSphereRAG(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pipeline = get_rag_pipeline("data/knowledge_base.json")

    def test_language_detection(self):
        """Test script & language detection across Indian & International languages."""
        test_cases = [
            ("హైదరాబాద్లో చూడదగిన ప్రదేశాలు ఏవి?", "te"),
            ("गोवा में घूमने की सबसे अच्छी जगहें कौन सी हैं?", "hi"),
            ("What are the best places to visit in Japan?", "en"),
            ("¿Cuáles son los mejores lugares para visitar en París?", "es"),
            ("日本の京都で有名なお寺は何ですか？", "ja"),
        ]
        for query, expected_lang in test_cases:
            detected, conf = LanguageDetector.detect(query)
            self.assertEqual(detected, expected_lang, f"Failed for query '{query}'. Expected {expected_lang}, got {detected}")
            self.assertGreater(conf, 0.5)

    def test_rag_query_grounded_response(self):
        """Test RAG retrieval for indexed destinations."""
        res_japan = self.pipeline.query("What are the best places to visit in Japan?")
        self.assertTrue(res_japan["is_grounded"])
        self.assertEqual(res_japan["language_code"], "en")
        self.assertIn("Tokyo", res_japan["answer"])
        self.assertGreater(len(res_japan["sources"]), 0)

        # Test Telugu query for Hyderabad
        res_hyderabad = self.pipeline.query("హైదరాబాద్లో చూడదగిన ప్రదేశాలు ఏవి?")
        self.assertTrue(res_hyderabad["is_grounded"])
        self.assertEqual(res_hyderabad["language_code"], "te")
        self.assertIn("Charminar", res_hyderabad["answer"])

    def test_anti_hallucination_guardrail(self):
        """Test fallback when query cannot be answered by knowledge base."""
        res_fake = self.pipeline.query("What are the top luxury resorts on Planet Mars under 50 credits?")
        self.assertFalse(res_fake["is_grounded"])
        self.assertIn("couldn't find reliable information", res_fake["answer"].lower())

    def test_trip_planner(self):
        """Test trip planner output logic."""
        res_plan = self.pipeline.query("Plan a 5 day trip to Goa with 50000 INR budget")
        self.assertTrue(res_plan["is_grounded"])
        self.assertIn("Goa", res_plan["answer"])


if __name__ == "__main__":
    unittest.main()
