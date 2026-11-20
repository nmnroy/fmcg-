"""
Unit tests for UoM & Packaging Normalizer
"""
import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rfp-automation")))

from utils.uom_normalizer import normalize_quantity


class TestUOMNormalizer(unittest.TestCase):
    def test_direct_units(self):
        res = normalize_quantity(50, "units", "Sunsilk Shampoo 180ml")
        self.assertEqual(res["normalized_units"], 50)
        self.assertEqual(res["consumer_unit"], "bottle")
        self.assertEqual(res["pack_multiplier"], 1)

    def test_cases_multiplier(self):
        res = normalize_quantity(10, "cases", "Dove Shampoo 340ml")
        self.assertEqual(res["normalized_units"], 120)  # 10 cases * 12
        self.assertEqual(res["packaging_type"], "case")

    def test_cartons_multiplier(self):
        res = normalize_quantity(5, "cartons", "Vim Gel 750ml")
        self.assertEqual(res["normalized_units"], 120)  # 5 cartons * 24

    def test_dozens_multiplier(self):
        res = normalize_quantity(12, "dozen", "Lux Soap bars")
        self.assertEqual(res["normalized_units"], 144)
        self.assertEqual(res["consumer_unit"], "bar")

    def test_explicit_pack_pattern(self):
        res = normalize_quantity(10, "packs", "Case of 24 Maggi Noodles")
        self.assertEqual(res["normalized_units"], 240)

    def test_fallback_invalid_quantity(self):
        res = normalize_quantity("invalid_string", "units", "Surf Excel")
        self.assertEqual(res["normalized_units"], 1)


if __name__ == "__main__":
    unittest.main()
