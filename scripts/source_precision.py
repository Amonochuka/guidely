"""Source-precision spot-check: verifies rank-1 snippets against cited files."""
import json
import os
from pathlib import Path

import httpx

BASE = os.environ.get("GUIDELY_BASE", "http://127.0.0.1:8000")
SAMPLE_DOCS = Path(__file__).resolve().parents[1] / "backend" / "data" / "sample-docs"
REPORT_FILE = Path(__file__).resolve().parent / "guidely_source_precision.json"

QUERIES = [
    "How many annual-leave days do full-time employees receive?",
    "How far in advance should I request annual leave?",
    "Is multi-factor authentication required for the company VPN?",
    "When must a lost company device be reported?",
    "What counts as a severity-one support incident?",
    "What details belong in an escalated incident ticket?",
    "What should I complete in my first week?",
    "What is the annual learning budget?",
    "When must expense claims be submitted?",
    "What is the domestic business-travel meal allowance?",
]

client = httpx.Client(timeout=90)
results = []
aligned = 0

for q in QUERIES:
    r = client.post(f"{BASE}/search/", json={"question": q})
    body = r.json()
    src = body["sources"][0]
    fname, snippet = src["filename"], src["snippet"]
    doc_text = " ".join((SAMPLE_DOCS / fname).read_text(errors="ignore").split())
    ok = snippet in doc_text
    aligned += ok
    results.append({
        "question": q,
        "cited_file": fname,
        "rank": src["rank"],
        "similarity_score": src["similarity_score"],
        "snippet_in_cited_file": ok,
    })
    print(f"  [{'PASS' if ok else 'FAIL'}] {fname} #{src['rank']} "
          f"({src['similarity_score']}) :: {q}")

print(f"\nSOURCE PRECISION = {aligned}/{len(results)} = "
      f"{aligned / len(results) * 100:.0f}%  (target >= 80%)")

REPORT_FILE.write_text(json.dumps({
    "checked": len(results),
    "aligned": aligned,
    "precision": round(aligned / len(results), 2),
    "target": 0.8,
    "results": results,
}, indent=2))
print(f"Report saved to {REPORT_FILE}")
