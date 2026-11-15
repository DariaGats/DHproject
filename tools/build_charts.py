#!/usr/bin/env python3
"""Draw the five charts of charts.html from data/endings.csv.

Every square is one story. Run from the project folder:
    python3 tools/build_charts.py
The script replaces what is between <!-- chart:N --> and <!-- /chart:N --> in charts.html.
"""
import csv
import re
import statistics as st
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "data" / "endings.csv", encoding="utf-8")))
for r in rows:
    for k in ("paragraphs", "words_last", "median_other", "dialogue_share_rest", "sentence_ending", "sentence_rest"):
        r[k] = float(r[k])
N = len(rows)

W, H = 500, 375
INK, SOFT, ACCENT, PALE = "#34271c", "#5a4636", "#86452a", "#b9a98f"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(v):
    return f"{v:g}" if float(v).is_integer() else f"{v:.1f}"


def svg(title, body):
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="t">{esc(title)}</title>{body}</svg>')


def tile(x, y, size, filled):
    if filled:
        return f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{ACCENT}"/>'
    return (f'<rect x="{x+1}" y="{y+1}" width="{size-2}" height="{size-2}" fill="none" '
            f'stroke="{INK}" stroke-width="2"/>')


def text(x, y, s, size=13, weight=400, fill=INK, anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def count_chart(title, n_yes, big, line1, line2, yes_label, no_label, bar_a, bar_b, unit):
    """25 squares (one for each story) and two bars with the typical values."""
    o = []
    size, gap, x0, y0 = 34, 6, 24, 22
    k = 0
    for row in range(5):
        for col in range(5):
            o.append(tile(x0 + col * (size + gap), y0 + row * (size + gap), size, k < n_yes))
            k += 1
    gx = x0 + 5 * (size + gap) + 18
    o.append(text(gx, y0 + 44, big, 44, 700, ACCENT))
    o.append(text(gx, y0 + 74, line1, 15, 400))
    o.append(text(gx, y0 + 94, line2, 15, 400))
    ly = y0 + 5 * (size + gap) + 8
    o.append(tile(x0, ly, 14, True))
    o.append(text(x0 + 22, ly + 12, yes_label, 12))
    o.append(tile(x0 + 230, ly, 14, False))
    o.append(text(x0 + 252, ly + 12, no_label, 12))
    # typical values
    by = 268
    top = max(bar_a[1], bar_b[1])
    scale = 195 / top
    for i, (label, v, col) in enumerate([bar_a + (PALE,), bar_b + (ACCENT,)]):
        y = by + i * 40
        o.append(text(x0, y + 14, label, 12, 400, SOFT))
        o.append(f'<rect x="{x0+150}" y="{y}" width="{v*scale:.1f}" height="22" fill="{col}"/>')
        o.append(text(x0 + 150 + v * scale + 8, y + 16, f"{fmt(v)} {unit}", 13, 600))
    return svg(title, "".join(o))


# ---- chart 1: length ------------------------------------------------------
n1 = sum(r["words_last"] < r["median_other"] for r in rows)
typ_last = st.median(r["words_last"] for r in rows)
typ_other = st.median(r["median_other"] for r in rows)
c1 = count_chart(
    "Chart 1. In " + str(n1) + " of " + str(N) + " stories the last paragraph is shorter than the typical paragraph of the story. "
    "The typical last paragraph has " + fmt(typ_last) + " words, the typical other paragraph " + fmt(typ_other) + ".",
    n1, f"{n1} of {N}", "stories have a shorter", "last paragraph",
    "last paragraph shorter", "not shorter",
    ("Typical other paragraph", typ_other), ("Typical last paragraph", typ_last), "words")

# ---- chart 2: sentence length -----------------------------------------------
n2 = sum(r["sentence_ending"] < r["sentence_rest"] for r in rows)
s_rest = st.median(r["sentence_rest"] for r in rows)
s_end = st.median(r["sentence_ending"] for r in rows)
c2 = count_chart(
    "Chart 2. In " + str(n2) + " of " + str(N) + " stories the sentences of the ending are shorter than those of the rest of the story. "
    "The typical sentence has " + fmt(s_end) + " words in the ending and " + fmt(s_rest) + " in the rest.",
    n2, f"{n2} of {N}", "stories have shorter", "sentences in the ending",
    "ending sentences shorter", "not shorter",
    ("Typical sentence, rest", s_rest), ("Typical sentence, ending", s_end), "words")

# ---- chart 3: voice -------------------------------------------------------
cnt = Counter(r["voice"] for r in rows)
order = [k for k, _ in cnt.most_common()]
names = {"dialogue": "Dialogue", "narration": "Narration", "quoted text": "Quoted text", "mixed": "Mixed"}
o = [text(24, 30, "Each square is the ending of one story.", 13, 400, SOFT)]
size, gap, x0, top, rowh = 24, 4, 128, 62, 62
for i, k in enumerate(order):
    y = top + i * rowh
    o.append(text(x0 - 14, y + 17, names.get(k, k), 14, 600, INK, "end"))
    for j in range(cnt[k]):
        o.append(tile(x0 + j * (size + gap), y, size, True))
    o.append(text(x0 + cnt[k] * (size + gap) + 6, y + 18, str(cnt[k]), 16, 700, ACCENT))
c3 = svg("Chart 3. Voice of the ending: " + ", ".join(f"{names.get(k, k).lower()} {cnt[k]}" for k in order) + f" (out of {N} stories).", "".join(o))

# ---- chart 4: sentence length and voice -----------------------------------
o = []
x0, top, rowh = 24, 58, 78
scale = 300 / 20
o.append(f'<rect x="{x0}" y="14" width="14" height="14" fill="{PALE}"/>')
o.append(text(x0 + 22, 26, "rest of the story", 12))
o.append(f'<rect x="{x0+160}" y="14" width="14" height="14" fill="{ACCENT}"/>')
o.append(text(x0 + 182, 26, "ending", 12))
o.append(text(x0 + 250, 26, "average words per sentence", 12, 400, SOFT))
groups = []
for i, k in enumerate(order):
    sel = [r for r in rows if r["voice"] == k]
    rest = st.mean(r["sentence_rest"] for r in sel)
    end = st.mean(r["sentence_ending"] for r in sel)
    groups.append((k, len(sel), rest, end))
    y = top + i * rowh
    o.append(text(x0, y + 4, f"{names.get(k, k)} ({len(sel)} endings)", 13, 600))
    o.append(f'<rect x="{x0}" y="{y+12}" width="{rest*scale:.1f}" height="20" fill="{PALE}"/>')
    o.append(text(x0 + rest * scale + 8, y + 27, fmt(round(rest, 1)), 13, 600))
    o.append(f'<rect x="{x0}" y="{y+36}" width="{end*scale:.1f}" height="20" fill="{ACCENT}"/>')
    o.append(text(x0 + end * scale + 8, y + 51, fmt(round(end, 1)), 13, 600))
c4 = svg("Chart 4. Average words per sentence in the rest of the story and in the ending, for each voice: " +
         "; ".join(f"{names.get(k, k).lower()} {a:.1f} and {b:.1f}" for k, n, a, b in groups) + ".", "".join(o))

# ---- chart 5: where the turning point comes ---------------------------------
tw = [r for r in rows if r["twist"] == "yes"]
n5 = len(tw)
early = sum(r["turning_point"].startswith("earlier") for r in tw)
o = []
size, gap, x0, y0 = 34, 6, 24, 22
for k in range(n5):
    o.append(tile(x0 + (k % 5) * (size + gap), y0 + (k // 5) * (size + gap), size, k < early))
gx = x0 + 5 * (size + gap) + 18
o.append(text(gx, y0 + 44, f"{early} of {n5}", 44, 700, ACCENT))
o.append(text(gx, y0 + 74, "stories with a twist have", 15))
o.append(text(gx, y0 + 94, "the turning point earlier", 15))
ly = y0 + 5 * (size + gap) + 8
o.append(tile(x0, ly, 14, True))
o.append(text(x0 + 22, ly + 12, "turning point before the last paragraph", 12))
o.append(tile(x0, ly + 26, 14, False))
o.append(text(x0 + 22, ly + 38, "turning point in the last paragraph", 12))
c5 = svg("Chart 5. In " + str(early) + " of the " + str(n5) + " stories with a twist, the turning point comes before the last paragraph; "
         "in the other " + str(n5 - early) + " it is in the last paragraph.", "".join(o))


# ---- alt text (approved by Daria; it replaces the generated titles) ------------
ALT = [
    "A grid of 25 squares, one for each story. Eighteen are filled: these stories have a last paragraph shorter than their typical paragraph. Two bars compare the typical other paragraph, 38.5 words, with the typical last paragraph, 22 words.",
    "A grid of 25 squares, one for each story. Thirteen are filled: these stories have shorter sentences in the ending. Two bars show the typical sentence in the rest of the story, 15.6 words, and in the ending, 15 words.",
    "Four rows of squares, one square for each ending: dialogue 12, narration 5, quoted text 4, mixed 4.",
    "Four pairs of bars, one pair for each voice, with the average sentence length in the rest of the story and in the ending. The ending has shorter sentences in dialogue, quoted text and mixed endings, and longer sentences in narration, 17.4 words against 15.1.",
    "A grid of 22 squares, one for each story with a twist. Twelve are filled: the turning point comes before the last paragraph. Ten are empty: the turning point is in the last paragraph.",
]
import html as _h
def _with_alt(svg_text, i):
    return re.sub(r"<title id=\"t\">.*?</title>", lambda m: '<title id="t">' + _h.escape(ALT[i], quote=False) + '</title>', svg_text, flags=re.S)
c1, c2, c3, c4, c5 = [_with_alt(c, i) for i, c in enumerate([c1, c2, c3, c4, c5])]
c1, c2, c3, c4, c5 = [c.replace('id="t"', f'id="t{i+1}"').replace('aria-labelledby="t"', f'aria-labelledby="t{i+1}"') for i, c in enumerate([c1, c2, c3, c4, c5])]

# ---- write into charts.html ------------------------------------------------
path = ROOT / "charts.html"
html = path.read_text(encoding="utf-8")
if "<!-- chart:1 -->" not in html:
    frames = list(re.finditer(r'<div class="chart-frame".*?</div>\s*', html, flags=re.S))
    assert len(frames) == 4, len(frames)  # chart 5 is added by hand once, with its markers
    for i, m in reversed(list(enumerate(frames, 1))):
        html = html[:m.start()] + f'<!-- chart:{i} --><!-- /chart:{i} -->\n          ' + html[m.end():]
for i, c in enumerate([c1, c2, c3, c4, c5], 1):
    html = re.sub(rf'<!-- chart:{i} -->.*?<!-- /chart:{i} -->', lambda m: f'<!-- chart:{i} -->{c}<!-- /chart:{i} -->', html, flags=re.S)
path.write_text(html, encoding="utf-8")
print("charts written:", N, "stories;", n1, "shorter last paragraph;", n2, "shorter ending sentences;", dict(cnt))
print("typical words last/other:", typ_last, typ_other, "| typical sentence end/rest:", s_end, s_rest)
