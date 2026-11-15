#!/usr/bin/env python3
"""Write the data of the "Test the ending" page into test-the-ending.html.

Reads data/endings.csv (twist, tests, reason for students) and
data/last_paragraphs.json (the last five paragraphs of each story).
Run from the project folder:  python3 -I tools/build_demo.py
Replaces what is between // data:start and // data:end.
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "data" / "endings.csv", encoding="utf-8")))
last = json.load(open(ROOT / "data" / "last_paragraphs.json", encoding="utf-8"))

data = []
for r in rows:
    p = last[r["story"]]
    data.append({"title": r["story"], "n": p["n"], "twist": r["twist"], "tests": int(r["tests"]),
                 "reason": r["reason_students"], "last": p["last"]})

block = "// data:start\nvar DATA = " + json.dumps(data, ensure_ascii=False) + ";\n// data:end"
path = ROOT / "test-the-ending.html"
html = path.read_text(encoding="utf-8")
html = re.sub(r"// data:start.*?// data:end", lambda m: block, html, flags=re.S)
path.write_text(html, encoding="utf-8")
print("demo data written:", len(data), "stories")
