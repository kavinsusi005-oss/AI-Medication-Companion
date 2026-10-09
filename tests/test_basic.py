import unittest
from backend.services.ai_service import get_fallback_response, process_message
from backend.services.language_service import detect_language
from backend.services.intent_service import detect_intent_simple
from backend.services.speech_service import clean_text, is_valid_speech_input

class TestMedMateSuite(unittest.TestCase):

    def test_clean_text_and_validation(self):
        self.assertEqual(clean_text("   take medicine   now   "), "take medicine now")
        self.assertTrue(is_valid_speech_input("Metformin 500mg"))
        self.assertTrue(is_valid_speech_input("எடுத்துட்டேன்"))
        self.assertFalse(is_valid_speech_input("   "))
        self.assertFalse(is_valid_speech_input("...!!??"))

    def test_language_detection(self):
        self.assertEqual(detect_language("I took my medicine"), "english")
        self.assertEqual(detect_language("நான் மருந்து எடுத்துட்டேன்"), "tamil")
        self.assertEqual(detect_language("நான் tablet எடுத்துட்டேன்"), "tanglish")

    def test_intent_detection(self):
        self.assertEqual(detect_intent_simple("I took it"), "MEDICINE_TAKEN")
        self.assertEqual(detect_intent_simple("done"), "MEDICINE_TAKEN")
        self.assertEqual(detect_intent_simple("எடுத்துட்டேன்"), "MEDICINE_TAKEN")
        self.assertEqual(detect_intent_simple("remind me later"), "REMIND_LATER")
        self.assertEqual(detect_intent_simple("10 minutes later"), "REMIND_LATER")
        self.assertEqual(detect_intent_simple("பத்து நிமிஷம் கழிச்சு சொல்லு"), "REMIND_LATER")
        self.assertEqual(detect_intent_simple("what medicine should I take?"), "MEDICATION_QUERY")
        self.assertEqual(detect_intent_simple("என்ன மருந்து?"), "MEDICATION_QUERY")
        self.assertEqual(detect_intent_simple("I haven't taken it"), "NOT_TAKEN")
        self.assertEqual(detect_intent_simple("எடுக்கல"), "NOT_TAKEN")

    def test_fallback_response_english(self):
        res = get_fallback_response("I took my medication", "Metformin 500mg")
        self.assertEqual(res["intent"], "MEDICINE_TAKEN")
        self.assertEqual(res["language"], "english")
        self.assertIn("taken", res["response"].lower())

    def test_fallback_response_tamil(self):
        res = get_fallback_response("எடுத்துட்டேன்", "Metformin 500mg")
        self.assertEqual(res["intent"], "MEDICINE_TAKEN")
        self.assertEqual(res["language"], "tamil")
        self.assertIn("பதிவு", res["response"])

    def test_fallback_response_delay_minutes(self):
        res = get_fallback_response("remind me in 15 minutes", "Metformin 500mg")
        self.assertEqual(res["intent"], "REMIND_LATER")
        self.assertEqual(res["delay_minutes"], 15)

    def test_process_message_always_returns_valid_structure(self):
        res = process_message("hello", "Metformin")
        self.assertIn("language", res)
        self.assertIn("intent", res)
        self.assertIn("response", res)
        self.assertIn("delay_minutes", res)

if __name__ == "__main__":
    unittest.main()
