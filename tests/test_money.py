import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))

from money import find_money  # noqa: E402


def summary(text):
    return [(m["eur"], m["cur"], m["dir"]) for m in find_money(text)]


class MoneyTests(unittest.TestCase):
    def test_currencies(self):
        self.assertEqual(summary("Het kost 12 miljoen euro."), [(12_000_000, "EUR", "neutral")])
        self.assertEqual(summary("Een ticket van € 25."), [(25, "EUR", "neutral")])
        self.assertEqual(summary("Google is $10 miljard waard."), [(8_600_000_000, "USD", "neutral")])
        self.assertEqual(summary("Er waren 300 mensen en 4 euro's."), [(4, "EUR", "neutral")])

    def test_not_money(self):
        self.assertEqual(summary("Er vielen 4 doden bij 252 miljoen hectare."), [])

    def test_direction(self):
        self.assertEqual(summary("Bij de overval werd 2 miljoen euro gestolen."), [(2_000_000, "EUR", "lost")])
        self.assertEqual(summary("De actie heeft 40.000 euro opgehaald."), [(40_000, "EUR", "gained")])
        self.assertEqual(summary("Volkswagen leed een verlies van 1,5 miljard euro."), [(1_500_000_000, "EUR", "lost")])

    def test_nearest_signal_wins_and_sentences_are_separate(self):
        text = "Het bedrijf maakte winst. Maar 3 miljoen euro is verdwenen."
        self.assertEqual(summary(text), [(3_000_000, "EUR", "lost")])

    def test_no_false_signals_inside_other_words(self):
        self.assertEqual(summary("In de winter kost een woning 1.000 euro huur."), [(1000, "EUR", "neutral")])

    def test_repeats_are_listed_once(self):
        text = "Er is 5 miljoen euro gestolen. De politie zoekt de 5 miljoen euro die gestolen werd."
        self.assertEqual(summary(text), [(5_000_000, "EUR", "lost")])
        text = "Er zou 6,3 miljard dollar (ongeveer 5,4 miljard euro) zijn gestolen."
        self.assertEqual(summary(text), [(5_418_000_000, "USD", "lost")])


if __name__ == "__main__":
    unittest.main()
