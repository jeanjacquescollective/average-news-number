import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))

from numextract import extract_numbers, parse_dutch_word  # noqa: E402


def values(text):
    return [n["v"] for n in extract_numbers(text)]


class DigitTests(unittest.TestCase):
    def test_plain_and_separators(self):
        self.assertEqual(values("Er waren 12 mensen en 10.000 meldingen."), [12, 10000])
        self.assertEqual(values("Dat is 3,5 procent of 1.234,56 euro."), [3.5, 1234.56])
        self.assertEqual(values("It cost 1,234.5 dollars."), [1234.5])

    def test_negative_only_when_detached(self):
        self.assertEqual(values("Het vriest -5 graden."), [-5])
        self.assertEqual(values("Het werd 3-1 en COVID-19."), [3, 1, 19])

    def test_glued_to_letters_is_ignored(self):
        self.assertEqual(values("Ongeval op de E34 en de A12."), [])

    def test_dates_and_times(self):
        self.assertEqual(values("Op 29.10.2026 om 14.30 uur."), [29, 10, 2026, 14, 30])
        self.assertEqual(values("Van 2020-2024."), [2020, 2024])

    def test_digits_with_scale(self):
        self.assertEqual(values("Een tekort van 3,5 miljard euro en 2 mln mensen."), [3_500_000_000, 2_000_000])
        self.assertEqual(values("Ruim 10 duizend fans."), [10_000])


class DutchWordTests(unittest.TestCase):
    def test_compounds(self):
        cases = {
            "drie": 3, "achttien": 18, "eenentwintig": 21, "tweeëntwintig": 22,
            "honderd": 100, "tweehonderdvijfendertig": 235, "honderdduizend": 100_000,
            "negentienhonderdvijfenveertig": 1945, "vijfhonderdduizend": 500_000,
            "tweeduizendzesentwintig": 2026, "één": 1,
        }
        for word, expected in cases.items():
            self.assertEqual(parse_dutch_word(word), expected, word)

    def test_not_numbers(self):
        for word in ["een", "eerste", "honderden", "duizenden", "tiental", "dertigers", "en", "vieren"]:
            self.assertIsNone(parse_dutch_word(word), word)

    def test_in_sentences(self):
        self.assertEqual(values("Er zijn één of twee doden en een gewonde."), [1, 2])
        self.assertEqual(values("Drie mensen kregen twee miljoen euro."), [3, 2_000_000])
        self.assertEqual(values("Het kost een miljoen."), [1_000_000])
        self.assertEqual(extract_numbers("Het kost een miljoen.")[0]["t"], "een miljoen")
        self.assertEqual(values("twee miljoen vijfhonderdduizend"), [2_500_000])
        self.assertEqual(values("honderd duizend"), [100_000])

    def test_halves(self):
        self.assertEqual(values("anderhalf miljoen euro en anderhalf jaar"), [1_500_000, 1.5])
        self.assertEqual(values("bijna een half miljard"), [500_000_000])
        self.assertEqual(extract_numbers("bijna een half miljard")[0]["t"], "een half miljard")
        self.assertEqual(values("een half uur"), [])
        self.assertEqual(values("bijna 5 en een half miljard euro"), [5_500_000_000])
        self.assertEqual(values("twee en een half miljoen"), [2_500_000])
        self.assertEqual(values("3 en een half miljoen"), [3_500_000])

    def test_ten_is_dutch_not_english(self):
        self.assertEqual(values("Ten minste vier mensen ten noorden van Gent."), [4])


class EnglishWordTests(unittest.TestCase):
    def test_words(self):
        self.assertEqual(values("Three people and twenty-one dogs."), [3, 21])
        self.assertEqual(values("twenty one"), [21])
        self.assertEqual(values("two hundred and fifty"), [250])
        self.assertEqual(values("two million five hundred thousand"), [2_500_000])
        self.assertEqual(values("a thousand billion"), [1_000_000_000_000])


if __name__ == "__main__":
    unittest.main()
