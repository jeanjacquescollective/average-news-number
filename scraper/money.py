"""Find amounts of money in a text and decide whether they are lost or gained.

An amount is a number right after a currency sign (€ 5, $3 miljard) or right before
a currency word (5 miljoen euro, 3 dollar). Every amount gets a direction:

  1. the signal word closest to it in the same sentence:
       "Bij de overval werd 2 miljoen euro gestolen"     -> lost   (gestolen)
       "De speurders namen 330.430 euro in beslag"       -> gained (beslag)
  2. otherwise a signal word in the headline (the first line of the text):
       "Dendervallei krijgt Europees geld" ... "8,45 miljoen euro uit het LIFE-programma"
  3. otherwise the majority of signal words in the whole article;
  4. otherwise gained: money that is mentioned without anything lost.

"how" records which step decided: "sentence", "title", "article" or "default".
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

# Signal words. "word" matches exactly, "stem*" also matches longer words, and
# "*part*" matches inside compounds too (geboortepremie, inbeslagname).
LOST = [
    # stolen, gone, lost
    "gestolen", "stal", "stalen", "steelt", "stelen", "diefstal*", "buit", "overval*", "inbraak",
    "inbrekers", "verduisterd", "verduistering*", "verdwenen", "verdwijnt", "verloren", "*verlies*",
    "verliest", "kwijt", "kwijtgeraakt", "losgeld", "afgeperst", "afpersing*", "smeergeld", "ontvreemd",
    "gehackt", "hack", "hackers", "cyberaanval*",
    # fraud, damage, debt, failure
    "fraude*", "fraudeur*", "opgelicht", "oplichting*", "oplichter*", "witwas*", "verspild",
    "verspilling*", "geflopt", "failliet", "faillissement*", "schuld", "schulden*", "*tekort*",
    "schade*", "*boete*", "riskeert", "dreigt",
    # paying out, falling
    "kost", "kostte", "kosten", "kostprijs", "*belasting*", "*taks*", "*heffing*", "duurder",
    "daalde", "daalt", "gedaald", "daling*", "zakte", "gezakt", "kelderde", "gekelderd", "verdampt",
    "afgeschreven", "afschrijving*", "crash*",
    "stolen", "loss", "losses", "lost", "missing", "fraud", "damage*", "debt*", "deficit*", "wiped",
    "scam*", "theft", "robbery", "embezzle*", "fined", "penalty", "costs", "cost",
]
GAINED = [
    # seized, found, recovered
    "*beslag*", "gevonden", "teruggevonden", "aangetroffen", "stootte", "stuitte", "ontdekt",
    "teruggekregen", "terugbetaald", "teruggestort", "terugbetaling*", "gerecupereerd", "recupereert",
    # received, raised, won, earned
    "krijgt", "kreeg", "kregen", "gekregen", "ontvangt", "ontving", "ontvangen", "wint", "won",
    "gewonnen", "verdient", "verdiend", "verdienen", "*winst*", "opbrengst*", "opgebracht",
    "opgehaald", "ingezameld", "inzameling*", "jackpot*", "prijzengeld*", "erfenis*", "schenking*",
    "geschonken", "gedoneerd", "donatie*", "dividend*",
    # budgets, funding, support, payouts
    "*budget*", "investe*", "financier*", "financiering*", "steun*", "*subsidie*", "*premie*",
    "toelage*", "uitkering*", "toegekend", "uitgekeerd", "vrijgemaakt", "bespaard", "*besparing*",
    "meevaller*", "overschot*", "waard", "waarde",
    "profit*", "gain", "gains", "gained", "raised", "earned", "saved", "surplus*", "windfall*",
    "donated", "seized", "recovered", "budget*", "funding", "invest*",
]


def _signal_re(words):
    parts = []
    for w in words:
        core = re.escape(w.strip("*"))
        parts.append((r"\w*" if w.startswith("*") else r"\b") + core + (r"\w*" if w.endswith("*") else r"\b"))
    return re.compile("|".join(parts), re.IGNORECASE)


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


def _signals(text, span):
    """(direction, match) for every signal word inside span."""
    return [(direction, m) for direction, pattern in SIGNALS for m in pattern.finditer(text, *span)]


def _direction(text, sentence, start, end):
    """(direction, signal word, how) for the amount at start..end; see the module docstring."""
    found = _signals(text, sentence)
    if found:
        direction, m = min(found, key=lambda s: max(s[1].start() - end, start - s[1].end(), 0))
        return direction, m.group(0), "sentence"
    title_end = text.find("\n") if "\n" in text else len(text)
    found = _signals(text, (0, title_end))
    if found:
        return found[0][0], found[0][1].group(0), "title"
    found = _signals(text, (0, len(text)))
    lost = sum(1 for direction, _ in found if direction == "lost")
    gained = len(found) - lost
    if lost != gained:
        direction = "lost" if lost > gained else "gained"
        return direction, next(m.group(0) for d, m in found if d == direction), "article"
    return "gained", None, "default"


def find_money(text):
    """List of amounts: {"eur", "t", "cur", "dir", "kw", "how", "ctx"}; a repeated amount is listed once."""
    found = []
    for number in find_numbers(text):
        currency = _currency(text, number)
        if not currency or number["v"] <= 0:
            continue
        code, start, end = currency
        sentence = _sentence(text, start, end)
        direction, signal, how = _direction(text, sentence, start, end)
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
            "how": how,
            "ctx": context if len(context) <= 300 else context[:297] + "…",
        })
    return found
