"""Write a YAML of ALL A-share companies (no sampling) for full-market eval."""

from __future__ import annotations

import os
import sys
from collections import Counter

import yaml

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.probe_cninfo import _session  # noqa: E402
from lab.sample_universe import STOCK_LIST_URL, board_of, is_financial  # noqa: E402


def main() -> int:
    out = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(_PROJECT_ROOT, "lab", "eval_companies_full_market_2024.yaml")
    )
    sess = _session(25)
    data = sess.get(STOCK_LIST_URL, timeout=25).json()
    universe = [x for x in data["stockList"] if x.get("category") == "A股"]

    companies = []
    for x in universe:
        code = str(x.get("code", ""))
        exch, board = board_of(code)
        if not board:
            continue
        companies.append({
            "short_name": x.get("zwjc", ""),
            "stock_code": code,
            "exchange": exch,
            "orgid": x.get("orgId", ""),
            "board": board,
            "financial": is_financial(x.get("zwjc", "")),
        })

    with open(out, "w", encoding="utf-8") as fh:
        yaml.safe_dump({"companies": companies}, fh, allow_unicode=True, sort_keys=False)

    boards = Counter(c["board"] for c in companies)
    fin = sum(1 for c in companies if c["financial"])
    print(f"[full_market] wrote {len(companies)} companies -> {out}")
    print("[full_market] boards:", dict(boards))
    print("[full_market] financial:", fin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
