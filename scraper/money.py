"""Find amounts of money in a text and guess whether they were lost or gained.

An amount is a number right after a currency sign (€ 5, $3 miljard) or right before
a currency word (5 miljoen euro, 3 dollar). Its direction comes from the signal word
closest to it in the same sentence:

    "Bij de overval werd 2 miljoen euro gestolen"    -> lost    (gestolen)
    "De actie heeft 40.000 euro opgehaald"           -> gained  (opgehaald)
    "Het nieuwe zwembad kost 12 miljoen euro"        -> neutral (no signal word)

Amounts in other currencies are converted to euro at fixed, approximate rates.
"""

import re

from numextract import find_numbers

RATES_TO_EUR = {"EUR": 1.0, "USD": 0.86, "GBP": 1.15, "CHF": 1.07, "JPY": 0.0057, "CNY": 0.12}

WORD_CURRENCIES = {
    "euro": "EUR", "eur": "EUR", "dollar": "USD", "usd": "USD", "pond": "GBP", "ponden": "GBP",
    "pound": "GBP", "frank": "CHF", "yen": "JPY", "yuan": "CNY", "renminbi": "CNY",
}
SIGN_CURRENCIES = {"€": "EUR", "$": "USD", "£": "GBP", "¥": "JPY", "eur": "EUR", "usd": "USD", "gbp": "GBP", "chf": "CHF"}
CURRENCY_AFTER = re.compile(
    r"\s*(?:amerikaanse |britse |zwitserse )?(" + "|".join(WORD_CURRENCIES) + r")(?:'?s)?\b", re.IGNORECASE
)
CURRENCY_BEFORE = re.compile(r"(€|\$|£|¥|\beur|\busd|\bgbp|\bchf)\s?$", re.IGNORECASE)

# Exact words; a trailing * also matches longer words starting with the stem.
LOST = [
    "gestolen", "stal", "steelt", "stelen", "diefstal*", "buit", "overval*", "inbraak", "inbrekers",
    "verduisterd", "verduistering*", "verdwenen", "verdwijnt", "verloren", "verlies*", "verliest",
    "kwijt", "kwijtgeraakt", "tekort*", "schuld", "schulden*", "schade*", "fraude*", "fraudeur*",
    "opgelicht", "oplichting*", "oplichter*", "witwas*", "verspild", "verspilling*", "geflopt",
    "failliet", "faillissement*", "boete*", "verdampt", "kelderde", "gekelderd", "afgeschreven",
    "afschrijving*", "miljardenverlies*", "miljoenenverlies*", "losgeld", "afgeperst", "afpersing*",
    "smeergeld", "ontvreemd",
    "stolen", "loss", "losses", "lost", "missing", "fraud", "damage*", "debt*", "deficit*", "wiped",
    "scam*", "theft", "robbery", "embezzle*",
]
GAINED = [
    "winst*", "wint", "won", "gewonnen", "verdient", "verdiend", "verdienen", "opbrengst*",
    "opgebracht", "opgehaald", "ingezameld", "inzameling*", "gevonden", "teruggevonden",
    "teruggekregen", "terugbetaald", "teruggestort", "terugbetaling*", "bespaard", "besparing*",
    "meevaller*", "overschot*", "jackpot*", "prijzengeld*", "erfenis*", "schenking*", "geschonken",
    "gedoneerd", "donatie*", "subsidie*", "toegekend", "uitgekeerd", "dividend*", "recordwinst*",
    "profit*", "gain", "gains", "gained", "raised", "earned", "saved", "surplus*", "windfall*", "donated",
]


def _signal_re(words):
    parts = [re.escape(w[:-1]) + r"\w*" if w.endswith("*") else re.escape(w) + r"\b" for w in words]
    return re.compile(r"\b(?:" + "|".join(parts) + ")", re.IGNORECASE)


SIGNALS = [("lost", _signal_re(LOST)), ("gained", _signal_re(GAINED))]
SENTENCE_END = re.compile(r"(?<=[.!?…])[\"”'’]?\s+|\n+")


def _currency(text, number):
    """(currency code, start, end) of the amount including its currency, or None."""
    after = CURRENCY_AFTER.match(text, number["end"])
    if after:
        return WORD_CURRENCIES[after.group(1).lower()], number["start"], after.end()
    before = CURRENCY_BEFORE.search(text, max(0, number["start"] - 4), number["start"])
    if before:
        return SIGN_CURRENCIES[before.group(1).lower()], before.start(), number["end"]
    return None


def _sentence(text, start, end):
    left = max((m.end() for m in SENTENCE_END.finditer(text, 0, start)), default=0)
    right = SENTENCE_END.search(text, end)
    return left, right.start() if right else len(text)


def _direction(text, sentence, start, end):
    """("lost" | "gained" | "neutral", signal word), from the signal word closest to the amount."""
    best = None
    for direction, pattern in SIGNALS:
        for m in pattern.finditer(text, *sentence):
            distance = max(m.start() - end, start - m.end(), 0)
            if best is None or distance < best[0]:
                best = (distance, direction, m.group(0))
    return (best[1], best[2]) if best else ("neutral", None)


def find_money(text):
    """List of amounts: {"eur", "t", "cur", "dir", "kw", "ctx"}; a repeated amount is listed once."""
    found = []
    for number in find_numbers(text):
        currency = _currency(text, number)
        if not currency or number["v"] <= 0:
            continue
        code, start, end = currency
        sentence = _sentence(text, start, end)
        direction, signal = _direction(text, sentence, start, end)
        eur = round(number["v"] * RATES_TO_EUR[code], 2)
        if any(f["dir"] == direction and abs(f["eur"] - eur) <= 0.1 * max(f["eur"], eur) for f in found):
            continue  # the same amount again: repeated, rounded, or in another currency
        context = re.sub(r"\s+", " ", text[sentence[0]:sentence[1]]).strip()
        found.append({
            "eur": int(eur) if eur == int(eur) else eur,
            "t": text[start:end].strip(),
            "cur": code,
            "dir": direction,
            "kw": signal,
            "ctx": context if len(context) <= 300 else context[:297] + "…",
        })
    return found
