#!/usr/bin/env python3
"""Write the table of the 25 stories into stories.html from data/endings.csv.
Run from the project folder:  python3 -I tools/build_stories.py
Replaces what is between <!-- table --> and <!-- /table -->.
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "data" / "endings.csv", encoding="utf-8")))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def num(v):
    v = float(v)
    return f"{v:g}"


body = []
for i, r in enumerate(rows, 1):
    twist = "Yes" if r["twist"] == "yes" else "No"
    if r["story"] == "The Cop and the Anthem":
        twist = "Yes (borderline)"
    body.append(
        f'<tr id="{slug(r["story"])}"><td class="n">{i}</td><th scope="row">{esc(r["story"])}</th>'
        f'<td class="num">{num(r["paragraphs"])}</td>'
        f'<td class="num">{num(r["words_last"])}</td><td class="num">{num(r["median_other"])}</td>'
        f'<td>{"Yes" if r["last_shorter"] == "yes" else "No"}</td>'
        f'<td>{esc(r["voice"].capitalize())}</td><td>{twist}</td><td class="num">{r["tests"]}</td>'
        + (f'<td><a href="{r["voyant_url"]}" target="_blank" rel="noopener">Open</a></td></tr>' if r.get("voyant_url") else '<td>&ndash;</td></tr>'))

table = ('<table class="stories">'
         '<caption>The 25 stories of <cite>The Four Million</cite>, in the order of the book.</caption>'
         '<thead><tr><th scope="col">#</th><th scope="col">Story</th>'
         '<th scope="col">Paragraphs</th><th scope="col">Words in the last paragraph</th><th scope="col">Typical other paragraph (words)</th>'
         '<th scope="col">Last paragraph shorter?</th><th scope="col">Voice of the ending</th>'
         '<th scope="col">Twist</th><th scope="col">Tests passed (of 3)</th><th scope="col">Voyant</th></tr></thead>'
         '<tbody>' + "".join(body) + '</tbody></table>')

path = ROOT / "stories.html"
html = path.read_text(encoding="utf-8")
html = re.sub(r"<!-- table -->.*?<!-- /table -->", lambda m: f"<!-- table -->{table}<!-- /table -->", html, flags=re.S)
path.write_text(html, encoding="utf-8")
print("table written:", len(rows), "stories")
