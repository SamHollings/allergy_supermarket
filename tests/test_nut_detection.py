import unittest

from scripts.nut_detection import detect_nut_flags


class NutDetectionTests(unittest.TestCase):
    def test_gluten_trace_is_not_nut_warning(self):
        result = detect_nut_flags("Può contenere tracce di altri cereali contenenti glutine")
        self.assertFalse(result["contains_nuts"])
        self.assertFalse(result["may_contain_nuts"])
        self.assertEqual(result["explicit_allergen_phrases"], [])

    def test_nut_warning_with_real_nut_name_is_detected(self):
        result = detect_nut_flags("Potrebbe contenere arachidi e nocciole")
        self.assertFalse(result["contains_nuts"])
        self.assertTrue(result["may_contain_nuts"])
        self.assertIn("potrebbe contenere arachidi", result["explicit_allergen_phrases"][0])

    def test_direct_nut_ingredient_is_detected(self):
        result = detect_nut_flags("Contiene noci, mandorle e pistacchi")
        self.assertTrue(result["contains_nuts"])
        self.assertFalse(result["may_contain_nuts"])


if __name__ == "__main__":
    unittest.main()
