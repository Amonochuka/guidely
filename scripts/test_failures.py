"""Guidely failure-handling validation: exercises the four required error cases.

Run order matters:
  1. Stop the backend and wipe backend/data/faiss/ + backend/data/cache/.
  2. Start the backend normally.
  3. Run this script FIRST (it needs an empty store for the no-results case).
  4. Then run validate_guidely.py for the happy-path metrics.
"""
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE = os.environ.get("GUIDELY_BASE", "http://127.0.0.1:8000")
TEMP_PORT = os.environ.get("GUIDELY_TEMP_PORT", "8010")
TEMP_BASE = f"http://127.0.0.1:{TEMP_PORT}"
SAMPLE_DOCS = Path(__file__).resolve().parents[1] / "backend" / "data" / "sample-docs"
BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
REPORT_FILE = Path(__file__).resolve().parent / "guidely_failure_report.json"

client = httpx.Client(timeout=90)
results = []


def check(name, expected_status, response, detail_hint):
    body = {}
    try:
        body = response.json()
    except Exception:
        pass
    detail = str(body.get("detail", body))
    ok = response.status_code == expected_status and detail_hint.lower() in detail.lower()
    results.append({
        "case": name,
        "expected_status": expected_status,
        "actual_status": response.status_code,
        "detail": detail,
        "pass": ok,
    })
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: HTTP {response.status_code} -> {detail}")
    return ok


print("=== FAILURE CASE 1: empty query ===")
r = client.post(f"{BASE}/search/", json={"question": "   "})
check("empty_query", 400, r, "question")

print("\n=== FAILURE CASE 2: corrupted file upload ===")
corrupt = Path("/tmp/opencode/guidely-corrupted.pdf")
corrupt.parent.mkdir(parents=True, exist_ok=True)
corrupt.write_bytes(b"%PDF-1.4 corrupted-for-testing \x00\x01\x02 not a real pdf")
with corrupt.open("rb") as f:
    r = client.post(f"{BASE}/documents/upload", files={"file": (corrupt.name, f)})
check("corrupted_file", 400, r, "process")

print("\n=== FAILURE CASE 2b (extra): unsupported file type ===")
bogus = Path("/tmp/opencode/guidely-bogus.exe")
bogus.write_bytes(b"MZ not allowed")
with bogus.open("rb") as f:
    r = client.post(f"{BASE}/documents/upload", files={"file": (bogus.name, f)})
check("unsupported_file_type", 400, r, "allowed")

print("\n=== FAILURE CASE 3: no results found ===")
doc_count = client.get(f"{BASE}/documents/").json()["total_documents"]
if doc_count == 0:
    r = client.post(f"{BASE}/search/", json={"question": "What is the remote work policy?"})
    check("no_relevant_results", 404, r, "no documents")
else:
    results.append({"case": "no_relevant_results", "expected_status": 404,
                    "actual_status": None, "detail": "skipped: index not empty", "pass": False})
    print("  [SKIP] index already has documents; wipe data/faiss + data/cache and rerun")

print("\n=== Preparing missing-key case (indexing sample docs) ===")
for path in sorted(SAMPLE_DOCS.glob("*.txt")):
    with path.open("rb") as f:
        client.post(f"{BASE}/documents/upload", files={"file": (path.name, f)})
print("  sample docs indexed")

print("\n=== FAILURE CASE 4: missing model key (temporary no-key instance) ===")
env = dict(os.environ)
env["GEMINI_API_KEY"] = ""
proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "main:app", "--port", str(TEMP_PORT)],
    cwd=BACKEND_DIR, env=env,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)
temp_metrics = None
try:
    deadline = time.time() + 120
    up = False
    while time.time() < deadline:
        try:
            if client.get(f"{TEMP_BASE}/system/health").status_code == 200:
                up = True
                break
        except Exception:
            time.sleep(1)
    if up:
        r = client.post(f"{TEMP_BASE}/search/", json={"question": "How many annual leave days do we get?"})
        check("missing_model_key", 503, r, "GEMINI_API_KEY")
        temp_metrics = client.get(f"{TEMP_BASE}/system/metrics").json()
    else:
        results.append({"case": "missing_model_key", "expected_status": 503,
                        "actual_status": None, "detail": "temporary instance failed to start", "pass": False})
        print("  [FAIL] temporary instance did not become healthy in 120s")
finally:
    proc.terminate()
    proc.wait(timeout=15)

print("\n=== Merged failure metrics ===")
main_metrics = client.get(f"{BASE}/system/metrics").json()
merged = dict(main_metrics["failure_counts"])
if temp_metrics:
    for k, v in temp_metrics["failure_counts"].items():
        merged[k] = merged.get(k, 0) + v
merged_view = {
    "queries_served_on_main": main_metrics["queries_served"],
    "failure_counts_main": main_metrics["failure_counts"],
    "failure_counts_no_key_instance": temp_metrics["failure_counts"] if temp_metrics else {},
    "merged_failure_counts": merged,
}
print(json.dumps(merged_view, indent=2))

report = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "cases": results,
    "all_passed": all(c["pass"] for c in results),
    "metrics": merged_view,
}
REPORT_FILE.write_text(json.dumps(report, indent=2))
print(f"\nReport saved to {REPORT_FILE}")
print("ALL PASSED" if report["all_passed"] else "SOME CHECKS FAILED - see above")
