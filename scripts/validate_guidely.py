"""Guidely validation session: runs the README testing workflow end-to-end."""
import concurrent.futures
import json
import os
import time
from pathlib import Path

import httpx

BASE = os.environ.get("GUIDELY_BASE", "http://127.0.0.1:8000")
SAMPLE_DOCS = Path(__file__).resolve().parents[1] / "backend" / "data" / "sample-docs"

QUERIES = [
    ("How many annual-leave days do full-time employees receive?", "employee-handbook.txt"),
    ("How far in advance should I request annual leave?", "employee-handbook.txt"),
    ("How many remote-working days are allowed each week?", "employee-handbook.txt"),
    ("When is a medical note required for sick leave?", "employee-handbook.txt"),
    ("Is multi-factor authentication required for the company VPN?", "it-security-policy.txt"),
    ("When must a lost company device be reported?", "it-security-policy.txt"),
    ("Can I send customer records to my personal email?", "it-security-policy.txt"),
    ("What counts as a severity-one support incident?", "customer-support-guide.txt"),
    ("How quickly must severity-one incidents be acknowledged?", "customer-support-guide.txt"),
    ("What details belong in an escalated incident ticket?", "customer-support-guide.txt"),
    ("What should I complete in my first week?", "new-hire-onboarding.txt"),
    ("What is the annual learning budget?", "new-hire-onboarding.txt"),
    ("How long is the standard probation period?", "new-hire-onboarding.txt"),
    ("When must expense claims be submitted?", "expense-faq.txt"),
    ("What is the domestic business-travel meal allowance?", "expense-faq.txt"),
]

client = httpx.Client(timeout=90)


def upload(path: Path):
    start = time.perf_counter()
    with path.open("rb") as f:
        r = client.post(f"{BASE}/documents/upload",
                        files={"file": (path.name, f)})
    return path.name, r.status_code, time.perf_counter() - start, r.json()


print("=== STEP 1: initial indexing of 5 sample docs ===")
t0 = time.perf_counter()
for name in sorted(SAMPLE_DOCS.glob("*.txt")):
    fname, code, secs, body = upload(name)
    print(f"  {code} {secs:5.2f}s {fname} -> {body.get('message', body)}")
print(f"  TOTAL INDEXING TIME: {time.perf_counter() - t0:.2f}s")

print("\n=== STEP 2: re-upload unchanged docs (cache effectiveness) ===")
for name in sorted(SAMPLE_DOCS.glob("*.txt")):
    fname, code, secs, body = upload(name)
    print(f"  {code} {fname} -> {body.get('message', body)}")

print("\n=== STEP 3: 15 validation queries ===")
passes = 0
answers_log = []
for q, expected in QUERIES:
    start = time.perf_counter()
    try:
        r = client.post(f"{BASE}/search/", json={"question": q})
        elapsed = time.perf_counter() - start
        body = r.json()
        src_files = [s["filename"] for s in body.get("sources", [])]
        hit = expected in src_files
        passes += hit
        answers_log.append((q, expected, body.get("answer", ""), src_files))
        print(f"  [{'PASS' if hit else 'FAIL'}] {elapsed:5.2f}s {q}")
        print(f"         expected={expected} got={src_files}")
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"  [ERROR] {elapsed:5.2f}s {q} -> {e}")
        answers_log.append((q, expected, f"<request failed: {e}>", []))

print(f"\n  RETRIEVAL@3 = {passes}/15 = {passes / 15 * 100:.0f}%  (target >= 80%)")

print("\n=== STEP 4: /system/metrics ===")
m = client.get(f"{BASE}/system/metrics").json()
print(json.dumps(m, indent=2))

Path(__file__).resolve().parent.joinpath("guidely_answers.json").write_text(
    json.dumps(answers_log, indent=2))
print("Answers saved to scripts/guidely_answers.json for manual review.")
