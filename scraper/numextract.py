"""Extract every number from a (mostly Dutch, sometimes English) piece of text.

Handles:
  * digits with Dutch or English separators: 12, 3,5, 10.000, 1.234,56, 1,234.56
  * negative numbers when the minus sign is detached from a preceding word: -5
  * Dutch number words, including compounds: drie, tweeëntwintig, negentienhonderdvijfenveertig
  * English number words: three, twenty-one, two hundred and fifty
  * scale words after a number: 3,5 miljoen, twee miljard, 5 million, honderd duizend
  * times like 14.30 uur, counted as two numbers (14 and 30)
  * anderhalf (1.5), and half before a scale word: een half miljard

Deliberately ignored: the Dutch article "een" (too ambiguous; "één" does count),
the English "ten" (a very common Dutch word), ordinal words (eerste, tweede) and
vague plurals (honderden, duizenden).
"""

import re

NL_UNITS = {
    "nul": 0, "een": 1, "één": 1, "eén": 1, "twee": 2, "drie": 3, "vier": 4,
    "vijf": 5, "zes": 6, "zeven": 7, "acht": 8, "negen": 9,
}
NL_TEENS = {
    "tien": 10, "elf": 11, "twaalf": 12, "dertien": 13, "veertien": 14,
    "vijftien": 15, "zestien": 16, "zeventien": 17, "achttien": 18, "negentien": 19,
}
NL_TENS = {
    "twintig": 20, "dertig": 30, "veertig": 40, "vijftig": 50,
    "zestig": 60, "zeventig": 70, "tachtig": 80, "negentig": 90,
}
NL_VALUES = {**NL_UNITS, **NL_TEENS, **NL_TENS, "honderd": 100, "duizend": 1000}


def _alt(words):
    # Longest first so "achttien" wins over "acht" + "tien".
    return "(?:" + "|".join(sorted(words, key=len, reverse=True)) + ")"


_U = _alt(k for k in NL_UNITS if k != "nul")
_B100 = f"(?:{_U}(?:en|ën){_alt(NL_TENS)}|{_alt(NL_TENS)}|{_alt(NL_TEENS)}|{_U})"
_B1000 = f"(?:{_B100}?honderd{_B100}?|{_B100})"
NL_COMPOUND = re.compile(f"(?:{_B1000}?duizend{_B1000}?|{_B1000})")
NL_TOKEN = re.compile(_alt(list(NL_VALUES) + ["en", "ën"]))

EN_UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
    "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
EN_TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

SCALES = {
    "honderd": 100, "hundred": 100,
    "duizend": 1_000, "thousand": 1_000,
    "miljoen": 1_000_000, "million": 1_000_000, "mln": 1_000_000,
    "miljard": 1_000_000_000, "billion": 1_000_000_000, "mld": 1_000_000_000, "mrd": 1_000_000_000,
    "biljoen": 1_000_000_000_000, "trillion": 1_000_000_000_000,
}
# Abbreviations only make sense right after digits ("3 mln"), never on their own.
ABBREVIATED_SCALES = {"mln", "mld", "mrd"}

TOKEN_RE = re.compile(
    r"(?P<num>(?:(?<![^\s(\[\"'“‘])[-−])?(?<!\w)\d+(?:[.,]\d+)*)"
    r"|(?P<word>[^\W\d_]+(?:-[^\W\d_]+)*)"
)
TIME_SUFFIX = re.compile(r"\s*(?:uur|u)\b", re.IGNORECASE)


def parse_dutch_word(word):
    """Value of a single Dutch number word (compound allowed), else None."""
    if word == "een" or not NL_COMPOUND.fullmatch(word):
        return None
    total = current = 0
    for tok in NL_TOKEN.findall(word):
        if tok in ("en", "ën"):
            continue
        value = NL_VALUES[tok]
        if value == 100:
            current = (current or 1) * 100
        elif value == 1000:
            total += (current or 1) * 1000
            current = 0
        else:
            current += value
    return total + current


def parse_english_word(word):
    if word in EN_UNITS:
        return EN_UNITS[word]
    if word in EN_TENS:
        return EN_TENS[word]
    parts = word.split("-")
    if len(parts) == 2 and parts[0] in EN_TENS and EN_UNITS.get(parts[1], 0) in range(1, 10):
        return EN_TENS[parts[0]] + EN_UNITS[parts[1]]
    return None


def _to_number(x):
    x = round(x, 6)
    return int(x) if x == int(x) else x


def parse_digits(raw):
    """Turn a digit string with separators into one or more numbers."""
    sign = -1 if raw[0] in "-−" else 1
    s = raw.lstrip("-−")
    if "." in s and "," in s:
        if re.fullmatch(r"\d{1,3}(?:\.\d{3})+,\d+", s):  # Dutch 1.234,5
            return [sign * float(s.replace(".", "").replace(",", "."))]
        if re.fullmatch(r"\d{1,3}(?:,\d{3})+\.\d+", s):  # English 1,234.5
            return [sign * float(s.replace(",", ""))]
        return [int(p) for p in re.split(r"[.,]", s)]
    for sep in (".", ","):
        if sep in s:
            groups = s.split(sep)
            if len(groups) == 2 and not (sep == "." and len(groups[1]) == 3):
                return [sign * float(groups[0] + "." + groups[1])]  # decimal
            if all(len(g) == 3 for g in groups[1:]) and len(groups[0]) <= 3:
                return [sign * int("".join(groups))]  # thousands separators
            return [int(g) for g in groups]  # something like a date: 29.10.2026
    return [sign * int(s)]


def _classify(m):
    """(kind, value) for a token: kind is 'digits', 'word', 'scale', 'and' or None."""
    if m.group("num"):
        return "digits", None
    word = m.group("word").lower()
    if word in SCALES:
        return "scale", SCALES[word]
    if word == "and":
        return "and", None
    if word == "anderhalf":
        return "word", 1.5
    value = parse_dutch_word(word)
    if value is None and word != "ten":
        value = parse_english_word(word)
    return ("word", value) if value is not None else (None, word)


def extract_numbers(text):
    """Return a list of {"v": value, "t": original text} for every number in text."""
    return [{"v": n["v"], "t": n["t"]} for n in find_numbers(text)]


def find_numbers(text):
    """Like extract_numbers, plus the "start" and "end" offset of each number in text."""
    tokens = [(m, *_classify(m)) for m in TOKEN_RE.finditer(text)]
    results = []
    i = 0
    while i < len(tokens):
        m, kind, value = tokens[i]
        start, end = m.start(), m.end()
        open_english_tens = False

        if kind == "digits":
            raw = m.group("num")
            if re.fullmatch(r"\d{1,2}\.\d{2}", raw) and TIME_SUFFIX.match(text, end):
                results.extend({"v": int(part), "t": raw, "start": start, "end": end} for part in raw.split("."))
                i += 1
                continue
            values = parse_digits(raw)
            if len(values) > 1:
                results.extend({"v": _to_number(v), "t": raw, "start": start, "end": end} for v in values)
                i += 1
                continue
            current, from_words, j = values[0], False, i + 1
        elif kind == "word":
            current, from_words, j = value, True, i + 1
            open_english_tens = m.group("word").lower() in EN_TENS
        elif kind == "scale" and m.group("word").lower() not in ABBREVIATED_SCALES:
            # A bare scale word ("miljoen euro") counts as one of it; "een miljoen" too,
            # and "(een) half miljard" as half of it.
            current = 1
            for back in (1, 2):
                prev = tokens[i - back] if i >= back else None
                if not (prev and text[prev[0].end():start].isspace()):
                    break
                if prev[2] == "half" and back == 1:
                    current, start = 0.5, prev[0].start()
                elif prev[2] in ("een", "a"):
                    start = prev[0].start()
                    break
                else:
                    break
            # "5 en een half miljard": the 5 was already emitted on its own; fold it in.
            before = re.fullmatch(r"(.*?)\s+en\s+", text[:start], re.DOTALL)
            if current == 0.5 and before and results and results[-1]["end"] == len(before.group(1)):
                whole = results.pop()
                current, start = whole["v"] + 0.5, whole["start"]
            from_words, j, end = True, i, m.start()
        else:
            i += 1
            continue

        total = biggest_scale = last_scale = 0
        while j < len(tokens):
            nm, nkind, nvalue = tokens[j]
            if text[end:nm.start()].strip():
                break
            if nkind == "scale":
                if nvalue >= 1000:
                    if nvalue > biggest_scale:
                        total = (total + current) * nvalue
                    else:
                        total += (current or 1) * nvalue
                    current, biggest_scale = 0, nvalue
                else:
                    current = (current or 1) * nvalue
                last_scale = nvalue
            elif from_words and nkind == "word" and last_scale and nvalue < last_scale:
                current += nvalue  # "twee miljoen vijfhonderdduizend"
            elif open_english_tens and nkind == "word" and nm.group("word").lower() in EN_UNITS                     and 0 < nvalue < 10:
                current += nvalue  # "twenty one"
            elif from_words and nkind == "and" and last_scale and j + 1 < len(tokens)                     and tokens[j + 1][1] == "word":
                pass  # "two hundred and fifty"
            else:
                break
            open_english_tens = False
            end = nm.end()
            j += 1

        results.append({"v": _to_number(total + current), "t": text[start:end], "start": start, "end": end})
        i = max(j, i + 1)
    return results
