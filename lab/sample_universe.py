"""Sample a stratified random subset of the A-share universe for held-out eval.

Fetches CNINFO's combined stock list (code + orgId + name), stratifies by board
via code prefix, and writes a companies YAML the eval harness can consume. orgId
is included so the harness can skip the (flaky) resolve step.

Deterministic via --seed so the held-out sample is reproducible.
"""

from __future__ import annotations

import argparse
import os
import random
import sys

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.probe_cninfo import _session  # noqa: E402

STOCK_LIST_URL = "http://www.cninfo.com.cn/new/data/szse_stock.json"

# board -> (exchange, code-prefix predicate). STAR/ChiNext kept distinct for strata.
def board_of(code: str) -> tuple[str, str]:
    if code.startswith("60"):
        return "SSE", "sse_main"
    if code.startswith("68"):
        return "SSE", "star"
    if code.startswith("00"):
        return "SZSE", "szse_main"
    if code.startswith("30"):
        return "SZSE", "chinext"
    if code[:2] in ("43", "83", "87", "92"):
        return "BSE", "bse"
    return "", ""


# Target counts per stratum (sums to ~200 at scale=1).
TARGETS = {"sse_main": 60, "star": 25, "szse_main": 50, "chinext": 45, "bse": 20}

_FIN_KW = ("银行", "证券", "保险", "期货", "信托", "再保险", "人寿", "财险", "金控", "金融", "资管", "基金")


def is_financial(name: str) -> bool:
    return any(k in (name or "") for k in _FIN_KW)


def main() -> int:
    ap = argparse.ArgumentParser(description="Stratified sampler of the A-share universe")
    ap.add_argument("--out", default=os.path.join(_PROJECT_ROOT, "lab", "eval_companies_200.yaml"))
    ap.add_argument("--seed", type=int, default=20260617)
    ap.add_argument("--scale", type=float, default=1.0,
                    help="multiply each stratum target (5 -> ~1000)")
    args = ap.parse_args()

    sess = _session(25)
    data = sess.get(STOCK_LIST_URL, timeout=25).json()
    universe = [x for x in data["stockList"] if x.get("category") == "A股"]

    by_stratum: dict[str, list] = {k: [] for k in TARGETS}
    for x in universe:
        code = str(x.get("code", ""))
        exch, stratum = board_of(code)
        if stratum in by_stratum:
            by_stratum[stratum].append({"code": code, "name": x.get("zwjc", ""),
                                        "orgid": x.get("orgId", ""), "exchange": exch})

    rng = random.Random(args.seed)
    picked = []
    for stratum, n in TARGETS.items():
        n = round(n * args.scale)
        pool = by_stratum[stratum]
        rng.shuffle(pool)
        picked.extend(pool[:min(n, len(pool))])

    companies = [{"short_name": p["name"], "stock_code": p["code"], "exchange": p["exchange"],
                  "orgid": p["orgid"], "board": board_of(p["code"])[1],
                  "financial": is_financial(p["name"])} for p in picked]
    with open(args.out, "w", encoding="utf-8") as fh:
        yaml.safe_dump({"companies": companies}, fh, allow_unicode=True, sort_keys=False)
    print(f"[sample] wrote {len(companies)} companies -> {args.out}")
    from collections import Counter
    print("[sample] strata:", dict(Counter(c["board"] for c in companies)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
