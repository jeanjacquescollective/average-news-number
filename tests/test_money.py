import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scraper"))

from money import find_money  # noqa: E402


def summary(text):
    return [(m["eur"], m["cur"], m["dir"]) for m in find_money(text)]


def directions(text):
    return [(m["t"], m["dir"], m["how"]) for m in find_money(text)]


class MoneyTests(unittest.TestCase):
    def test_currencies(self):
        self.assertEqual(summary("Een ticket van € 25."), [(25, "EUR", "gained")])
        self.assertEqual(summary("Google is $10 miljard waard."), [(8_600_000_000, "USD", "gained")])
        self.assertEqual(summary("Er waren 300 mensen en 4 euro's."), [(4, "EUR", "gained")])

    def test_not_money(self):
        self.assertEqual(summary("Er vielen 4 doden bij 252 miljoen hectare."), [])

    def test_direction_from_the_sentence(self):
        self.assertEqual(summary("Bij de overval werd 2 miljoen euro gestolen."), [(2_000_000, "EUR", "lost")])
        self.assertEqual(summary("De actie heeft 40.000 euro opgehaald."), [(40_000, "EUR", "gained")])
        self.assertEqual(summary("Volkswagen leed een verlies van 1,5 miljard euro."), [(1_500_000_000, "EUR", "lost")])
        self.assertEqual(summary("Het kost 12 miljoen euro."), [(12_000_000, "EUR", "lost")])

    def test_real_sentences(self):
        cases = {
            "Daarnaast namen de speurders nog 330.430 euro cash, meerdere luxehorloges en 2,7 kilo cocaïne in beslag.": "gained",
            "Het totale budget daarvoor is bijna 26 miljoen euro, en Europa betaalt daarvan een kleine 9 miljoen.": "gained",
            "Als hij zich daar niet aan houdt, riskeert hij 50.000 tot 250.000 euro te moeten betalen.": "lost",
            "In hun hotelkamer stootte de politie op honderd gouden munten voor een totale waarde van 116.522 euro.": "gained",
            "Hij had op enkele maanden tijd meer dan 100.000 euro gekregen van de broer.": "gained",
            "De waarde van bitcoin ging met ruim 4 procent omlaag en daalde tot onder 78.000 dollar.": "lost",
        }
        for text, expected in cases.items():
            self.assertEqual([m["dir"] for m in find_money(text)], [expected], text)

    def test_falls_back_to_the_headline(self):
        text = "Herstel van de Dendervallei krijgt Europees geld\nDaarvan komt 8,45 miljoen euro uit het LIFE-programma."
        self.assertEqual(directions(text), [("8,45 miljoen euro", "gained", "title")])
        text = "Raad van State fluit regering terug over beperking geboortepremie\nDat startbedrag bedraagt 1.310 euro."
        self.assertEqual(directions(text), [("1.310 euro", "gained", "title")])

    def test_falls_back_to_the_article_then_default(self):
        text = "Grote zaak in Gent\nDe dader werd gevat. Het ging om 5.000 euro. Er werd ook geld gestolen en verduisterd."
        self.assertEqual(directions(text), [("5.000 euro", "lost", "article")])
        self.assertEqual(directions("Nieuw zwembad\nHet zwembad opent met 300 euro in de kassa."), [("300 euro", "gained", "default")])

    def test_nearest_signal_wins_and_sentences_are_separate(self):
        text = "Het bedrijf maakte winst. Maar 3 miljoen euro is verdwenen."
        self.assertEqual(summary(text), [(3_000_000, "EUR", "lost")])

    def test_no_false_signals_inside_other_words(self):
        self.assertEqual(directions("In de winter huurt men een woning voor 1.000 euro."), [("1.000 euro", "gained", "default")])

    def test_repeats_are_listed_once(self):
        text = "Er is 5 miljoen euro gestolen. De politie zoekt de 5 miljoen euro die gestolen werd."
        self.assertEqual(summary(text), [(5_000_000, "EUR", "lost")])
        text = "Er zou 6,3 miljard dollar (ongeveer 5,4 miljard euro) zijn gestolen."
        self.assertEqual(summary(text), [(5_418_000_000, "USD", "lost")])


if __name__ == "__main__":
    unittest.main()
