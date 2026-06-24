#!/usr/bin/env bash
# Full-market 2024 sequential batch run + merge + db_import.
# VPN must be OFF. Do not run batches in parallel.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$PWD"

mkdir -p outputs/generalization/full_market_2024

for board in bse star szse_main chinext sse_main; do
  echo "=== START ${board} $(date) ==="
  .venv/bin/python lab/eval_generalize.py \
    --companies "lab/batch_${board}_2024.yaml" \
    --out "outputs/generalization/full_market_2024/${board}" \
    --throttle 1.5 \
    2>&1 | tee "outputs/generalization/full_market_2024/batch_${board}.log"
  echo "=== DONE ${board} $(date) ==="
  df -h .
done

.venv/bin/python lab/merge_full_market_batches.py \
  --out-dir outputs/generalization/full_market_2024

.venv/bin/python lab/db_init.py

.venv/bin/python lab/db_import.py \
  --eval-dir outputs/generalization/full_market_2024 \
  --companies-yaml lab/eval_companies_full_market_2024.yaml \
  --run-name full_market_2024 \
  --limit 0

.venv/bin/python - <<'PY'
import json
import statistics
from collections import Counter

rs = json.load(open("outputs/generalization/full_market_2024/eval_results.json", encoding="utf-8"))
status = Counter(r["status"] for r in rs)
ok = [r for r in rs if r["status"] == "ok"]
nonfin = [r for r in ok if not r.get("financial")]
fin = [r for r in ok if r.get("financial")]
print("status:", dict(status))
print(f"ok={len(ok)} nonfin={len(nonfin)} fin={len(fin)}")
if nonfin:
    print(f"nonfin plausible mean: {statistics.mean(r['plausible'] for r in nonfin):.3f}/11")
for f in ("rnd_investment", "revenue_by_region", "revenue_by_segment"):
    if nonfin:
        p = sum(1 for r in nonfin if r.get("fields", {}).get(f, {}).get("plausible"))
        print(f"{f}: {p}/{len(nonfin)} ({100*p/len(nonfin):.1f}%)")
print("financial subtypes:", dict(Counter(r.get("schema_profile", "?") for r in fin)))
PY

sqlite3 outputs/db/listed_companies_v1.db \
  "SELECT run_name, COUNT(*) FROM evaluation_result GROUP BY run_name;"

echo "=== FULL MARKET 2024 COMPLETE $(date) ==="
