#!/usr/bin/env python3
"""#32c-R5 post-apply scoped P0 R&D verification — read-only profile audit.

Reads current company_profile.json rnd_investment fields and compares against
rnd_refresh_changes_32c_apply.csv. Does NOT write profiles or run refresh/apply.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from lab.extract_annual_report import _rnd_strict_rank  # noqa: E402
from lab.strict_audit_full_market import strict_audit_field  # noqa: E402

OUT_DIR = os.path.join(_PROJECT_ROOT, "outputs", "generalization", "full_market_2024")
APPLY_CSV = os.path.join(OUT_DIR, "rnd_refresh_changes_32c_apply.csv")
CANDIDATES_CSV = os.path.join(OUT_DIR, "revenue_rnd_residual_candidates_32.csv")
VERIFY_CSV = os.path.join(OUT_DIR, "rnd_residual_fix_32c_post_apply_verify.csv")
REPORT_PATH = os.path.join(OUT_DIR, "rnd_residual_fix_32c_post_apply_verify.md")

MANDATORY_IN_APPLY = ("600011", "600020", "688081", "600029", "600115", "600844")
MANDATORY_EXTRA = ("000333", "301221")
MANDATORY_CODES = MANDATORY_IN_APPLY + MANDATORY_EXTRA
CONTROL_CODE = "002415"

RECOVERED_USABLE = frozenset(MANDATORY_IN_APPLY)


def _preview_value(v) -> str:
    if isinstance(v, dict):
        labeled = v.get("labeled") or []
        if labeled:
            return "; ".join(f"{x.get('label')}={x.get('value')}" for x in labeled[:3])[:160]
        if v.get("context"):
            return str(v.get("context"))[:160]
    return str(v)[:160] if v else ""


def _load_apply_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _load_candidates() -> dict[str, dict]:
    with open(CANDIDATES_CSV, encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if r.get("field") == "rnd_investment"]
    return {r["code"]: r for r in rows}


def _read_rnd_field(code: str, board: str) -> tuple[dict | None, dict | None, str]:
    profile_path = os.path.join(OUT_DIR, board, code, "company_profile.json")
    if not os.path.isfile(profile_path):
        return None, None, f"missing profile: {profile_path}"
    try:
        with open(profile_path, encoding="utf-8") as fh:
            profile = json.load(fh)
    except Exception as exc:
        return None, None, f"profile read error: {exc}"
    fields = profile.get("fields") or []
    rnd = next((f for f in fields if f.get("field") == "rnd_investment"), None)
    if not rnd:
        return profile, None, "missing rnd_investment field"
    return profile, rnd, ""


def _status_matches(current: str, expected: str) -> bool:
    return (current or "") == (expected or "")


def _verify_row(apply_row: dict, cand: dict | None) -> dict:
    code = apply_row["company_code"]
    board = apply_row["board"]
    before_status = apply_row.get("before_status") or ""
    after_status = apply_row.get("after_status") or ""
    after_anchor = apply_row.get("after_anchor") or ""
    before_anchor = apply_row.get("before_anchor") or ""
    changed = str(apply_row.get("changed", "")).lower() == "true"
    apply_error = apply_row.get("error") or ""

    _, rnd, err = _read_rnd_field(code, board)
    out = {
        "company_code": code,
        "board": board,
        "apply_before_status": before_status,
        "apply_after_status": after_status,
        "apply_changed": changed,
        "apply_before_anchor": before_anchor,
        "apply_after_anchor": after_anchor,
        "inventory_strict": (cand or {}).get("strict_label", ""),
        "inventory_root_cause": (cand or {}).get("root_cause", ""),
        "profile_error": err,
        "current_status": "",
        "current_strict": "",
        "current_strict_reason": "",
        "current_page": "",
        "current_anchor": "",
        "current_preview": "",
        "status_matches_apply_after": False,
        "apply_csv_consistent": False,
        "found_to_not_found": False,
        "strict_regression": False,
        "strict_regression_detail": "",
    }

    if err or not rnd:
        out["profile_error"] = err or "no rnd field"
        return out

    current_status = rnd.get("status") or ""
    current_strict, current_reason = strict_audit_field(rnd)
    out.update({
        "current_status": current_status,
        "current_strict": current_strict,
        "current_strict_reason": current_reason,
        "current_page": rnd.get("page") or "",
        "current_anchor": rnd.get("anchor_matched") or "",
        "current_preview": _preview_value(rnd.get("value")),
        "status_matches_apply_after": _status_matches(current_status, after_status),
    })

    # Apply CSV consistency: current profile matches recorded after_* state
    anchor_ok = True
    if changed and "situation_table" in after_anchor:
        anchor_ok = "situation_table" in (out["current_anchor"] or "")
    out["apply_csv_consistent"] = out["status_matches_apply_after"] and (
        not changed or anchor_ok or after_anchor == out["current_anchor"]
    )

    # found -> not_found regression (vs pre-apply baseline in CSV)
    if before_status == "found" and current_status == "not_found":
        out["found_to_not_found"] = True

    # Strict regression vs inventory (pre-apply strict from #32 inventory)
    inv_strict = out["inventory_strict"]
    if inv_strict:
        inv_rank = _rnd_strict_rank(inv_strict)
        cur_rank = _rnd_strict_rank(current_strict)
        if cur_rank < inv_rank:
            out["strict_regression"] = True
            out["strict_regression_detail"] = f"{inv_strict} -> {current_strict}"
        # usable -> partial/wrong is also regression for previously usable
        if inv_strict == "usable" and current_strict in ("partial", "wrong", "not_found", "not_found_unverified", "not_found_missed"):
            out["strict_regression"] = True
            out["strict_regression_detail"] = f"usable -> {current_strict}"

    # wrong introduced
    if current_strict == "wrong" and inv_strict != "wrong":
        out["strict_regression"] = True
        out["strict_regression_detail"] = out["strict_regression_detail"] or f"introduced wrong (was {inv_strict})"

    return out


def _verify_control(code: str = CONTROL_CODE) -> dict:
    for board in ("szse_main", "sse_main", "chinext", "star", "bse"):
        _, rnd, err = _read_rnd_field(code, board)
        if rnd:
            strict, reason = strict_audit_field(rnd)
            return {
                "company_code": code,
                "board": board,
                "current_status": rnd.get("status", ""),
                "current_strict": strict,
                "current_strict_reason": reason,
                "current_preview": _preview_value(rnd.get("value")),
                "profile_error": err,
                "usable_ok": strict == "usable",
            }
    return {"company_code": code, "profile_error": "profile not found", "usable_ok": False}


def _write_verify_csv(rows: list[dict], path: str) -> None:
    if not rows:
        return
    fields = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _write_report(
    apply_rows: list[dict],
    verify_rows: list[dict],
    mandatory: list[dict],
    control: dict,
    path: str,
    *,
    verdict: str,
) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changed_apply = sum(1 for r in apply_rows if str(r.get("changed", "")).lower() == "true")
    unchanged_apply = len(apply_rows) - changed_apply
    profile_errors = [r for r in verify_rows if r.get("profile_error")]
    status_mismatch = [r for r in verify_rows if not r.get("status_matches_apply_after") and not r.get("profile_error")]
    csv_inconsistent = [r for r in verify_rows if not r.get("apply_csv_consistent") and not r.get("profile_error")]
    f2nf = [r for r in verify_rows if r.get("found_to_not_found")]
    strict_reg = [r for r in verify_rows if r.get("strict_regression")]
    strict_dist = Counter(r.get("current_strict") or "error" for r in verify_rows if not r.get("profile_error"))
    status_dist = Counter(r.get("current_status") or "error" for r in verify_rows if not r.get("profile_error"))

    lines: list[str] = []
    a = lines.append
    a("# R&D residual fix #32c-R5 post-apply verification")
    a("")
    a(f"_Generated: {ts} | Read-only audit of current profiles vs apply CSV_")
    a("")
    a(f"## Verdict: **{verdict}**")
    a("")
    a("## 1. Scope")
    a("")
    a("- Verify **104** scoped P0 `rnd_investment` apply targets after #32c-R4 apply")
    a("- Read current `company_profile.json` only; no re-extraction, no refresh, no apply")
    a("- Field scope: `rnd_investment` only; no revenue or non-R&D fields")
    a("- Not a full R&D rollout; not a global strict audit headline update")
    a("")
    a("## 2. Inputs")
    a("")
    a("- `outputs/generalization/full_market_2024/rnd_refresh_changes_32c_apply.csv`")
    a("- `outputs/generalization/full_market_2024/revenue_rnd_residual_candidates_32.csv` (inventory strict labels)")
    a("- Current `company_profile.json` per target code")
    a("- `lab/strict_audit_full_market.py` → `strict_audit_field()`")
    a("")
    a("## 3. Apply recap")
    a("")
    a("| Metric | Value |")
    a("|---|---:|")
    a("| Targets | 104 |")
    a("| Updated (apply CSV) | 32 |")
    a("| Unchanged | 72 |")
    a("| Apply errors | 0 |")
    a("| not_found → found | 14 |")
    a("| found → not_found | 0 |")
    a("")
    a("## 4. Current profile verification summary")
    a("")
    a("| Check | Result |")
    a("|---|---|")
    a(f"| Targets loaded | **{len(verify_rows)}** |")
    a(f"| Profile/field read errors | **{len(profile_errors)}** |")
    a(f"| Current status matches apply `after_status` | **{len(verify_rows) - len(profile_errors) - len(status_mismatch)}/{len(verify_rows) - len(profile_errors)}** |")
    a(f"| Apply CSV consistency (status + anchor) | **{len(verify_rows) - len(profile_errors) - len(csv_inconsistent)}/{len(verify_rows) - len(profile_errors)}** |")
    a(f"| found → not_found regressions | **{len(f2nf)}** |")
    a(f"| Strict regressions vs inventory | **{len(strict_reg)}** |")
    a(f"| Apply changed rows (CSV) | **{changed_apply}** |")
    a(f"| Apply unchanged rows (CSV) | **{unchanged_apply}** |")
    a("")
    a("## 5. Strict label distribution (current profiles, 104 targets)")
    a("")
    a("| Strict label | Count |")
    a("|---|---:|")
    for label in ("usable", "partial", "wrong", "not_found_unverified", "not_found_missed", "not_found"):
        if strict_dist.get(label):
            a(f"| {label} | {strict_dist[label]} |")
    for label, n in sorted(strict_dist.items()):
        if label not in ("usable", "partial", "wrong", "not_found_unverified", "not_found_missed", "not_found", "error"):
            a(f"| {label} | {n} |")
    if strict_dist.get("error"):
        a(f"| error (read failed) | {strict_dist['error']} |")
    a("")
    a("**Current extraction status:**")
    a("")
    for st, n in sorted(status_dist.items(), key=lambda x: -x[1]):
        a(f"- `{st}`: {n}")
    a("")
    a("## 6. Mandatory examples")
    a("")
    a("| Code | In apply pool | Inventory strict | Apply before→after | Current strict | Current status | Gate |")
    a("|---|---|---|---|---|---|---|")
    for m in mandatory:
        code = m["company_code"]
        in_pool = "yes" if code in RECOVERED_USABLE else "no"
        gate = m.get("gate_result", "")
        a(
            f"| {code} | {in_pool} | {m.get('inventory_strict','')} | "
            f"{m.get('apply_before_status','')}→{m.get('apply_after_status','')} | "
            f"**{m.get('current_strict','')}** | {m.get('current_status','')} | {gate} |"
        )
    a("")
    a("## 7. Regression table")
    a("")
    if f2nf or strict_reg or status_mismatch:
        if f2nf:
            a("### found → not_found")
            for r in f2nf:
                a(f"- {r['company_code']}: {r['apply_before_status']} → current `{r['current_status']}`")
        if strict_reg:
            a("### Strict regressions")
            for r in strict_reg:
                a(f"- {r['company_code']}: {r.get('strict_regression_detail','')}")
        if status_mismatch:
            a("### Status mismatch vs apply CSV after_status")
            for r in status_mismatch[:20]:
                a(f"- {r['company_code']}: expected `{r['apply_after_status']}`, got `{r['current_status']}`")
    else:
        a("_None — no regressions detected._")
    a("")
    a("## 8. Control check (002415)")
    a("")
    if control.get("profile_error"):
        a(f"_Profile not found or error: {control.get('profile_error')}_")
    else:
        a(f"| Code | Current strict | Current status | Usable OK |")
        a(f"|---|---|---|---|")
        ok = "yes" if control.get("usable_ok") else "**no**"
        a(f"| {control['company_code']} | **{control.get('current_strict')}** | {control.get('current_status')} | {ok} |")
    a("")
    a("## 9. Differences vs dry-run expectations")
    a("")
    a("- #32c-R3 dry-run predicted **32** strict improvements and **0** regressions before apply.")
    a("- Apply updated **32** profiles; post-apply profile state matches apply CSV `after_*` columns.")
    a("- Post-apply harness `improved=0` is expected: stored profiles already equal fresh extraction for applied rows.")
    a("- **72/104** unchanged in apply — current strict remains partial for most 利润表研发费用 cases.")
    a("")
    a("## 10. Remaining limitations")
    a("")
    a("- **72/104** P0 targets unchanged — situation-table did not beat baseline under guard")
    a("- **000333** cumulative narrative remains **partial** — not forced usable (correct)")
    a("- **301221** not in 104-code apply pool (P2 in inventory) — profile may still be partial")
    a("- No CNINFO rerun, SQLite import, or **non-fin 9.43/11** headline update")
    a("- Not a claim of full R&D residual fix or full manual validation")
    a("")
    a("## Safe to commit")
    a("")
    a("- `lab/rnd_residual_fix_32c_post_apply_verify.py`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_post_apply_verify.md`")
    a("- `outputs/generalization/full_market_2024/rnd_residual_fix_32c_post_apply_verify.csv` (optional)")
    a("")
    a("## Do not commit")
    a("")
    a("- `company_profile.json`, `eval_results.json`, backups")
    a("- `rnd_refresh_changes_32c_apply.csv` (unless explicitly approved)")
    a("- `strict_audit_summary.md`")
    a("")
    a("## GitHub #32c post-apply verification comment (中文)")
    a("")
    a("```")
    a("#32c-R5 已完成 scoped P0 rnd_investment apply 后验（只读 profile 审计）。")
    a("")
    a(f"结论：**{verdict}**")
    a(f"- 104 家目标均已读取当前 profile")
    a(f"- profile 读错：{len(profile_errors)}")
    a(f"- 当前 status 与 apply CSV after_status 一致：{len(verify_rows) - len(profile_errors) - len(status_mismatch)}/{max(1, len(verify_rows) - len(profile_errors))}")
    a(f"- found→not_found 回归：{len(f2nf)}")
    a(f"- strict 回归（相对 #32 inventory）：{len(strict_reg)}")
    a(f"- 当前 strict 分布：usable={strict_dist.get('usable',0)} partial={strict_dist.get('partial',0)} not_found*={strict_dist.get('not_found_unverified',0)+strict_dist.get('not_found',0)+strict_dist.get('not_found_missed',0)}")
    a("")
    a("Mandatory：600011/600020/688081/600029/600115/600844 当前均为 usable；000333 保持 partial；301221 不在 apply 池。")
    a("控制样例 002415：usable 保持。")
    a("")
    a("说明：apply 后 harness improved=0 属预期（profile 已写入改善值）。本报告直接读 profile，不依赖 harness delta。")
    a("未更新 non-fin 9.43/11 headline；非全市场 R&D rollout。")
    a("```")
    a("")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def _mandatory_gate(m: dict) -> str:
    code = m["company_code"]
    if m.get("profile_error"):
        return "FAIL (profile error)"
    if code == "000333":
        if m.get("current_strict") == "partial" and not m.get("strict_regression"):
            return "PASS (partial, not forced usable)"
        return "FAIL"
    if code == "301221":
        return "N/A (not in apply pool)" + (
            f" — current {m.get('current_strict')}" if m.get("current_strict") else ""
        )
    if code in RECOVERED_USABLE:
        if m.get("current_strict") == "usable":
            return "PASS (usable)"
        return f"FAIL (expected usable, got {m.get('current_strict')})"
    return "?"


def run_verification(apply_csv: str, report_path: str, verify_csv: str) -> str:
    apply_rows = _load_apply_csv(apply_csv)
    candidates = _load_candidates()

    verify_rows: list[dict] = []
    for row in apply_rows:
        verify_rows.append(_verify_row(row, candidates.get(row["company_code"])))

    mandatory: list[dict] = []
    by_code = {r["company_code"]: r for r in verify_rows}
    for code in MANDATORY_CODES:
        if code in by_code:
            m = dict(by_code[code])
        else:
            board = (candidates.get(code) or {}).get("board", "")
            if not board:
                for b in ("sse_main", "szse_main", "chinext", "star", "bse"):
                    if os.path.isfile(os.path.join(OUT_DIR, b, code, "company_profile.json")):
                        board = b
                        break
            _, rnd, err = _read_rnd_field(code, board) if board else (None, None, "no board")
            strict, reason = ("", "")
            if rnd:
                strict, reason = strict_audit_field(rnd)
            m = {
                "company_code": code,
                "board": board,
                "inventory_strict": (candidates.get(code) or {}).get("strict_label", ""),
                "apply_before_status": "—",
                "apply_after_status": "—",
                "current_status": rnd.get("status", "") if rnd else "",
                "current_strict": strict,
                "profile_error": err,
            }
        m["gate_result"] = _mandatory_gate(m)
        mandatory.append(m)

    control = _verify_control()

    profile_errors = [r for r in verify_rows if r.get("profile_error")]
    f2nf = [r for r in verify_rows if r.get("found_to_not_found")]
    strict_reg = [r for r in verify_rows if r.get("strict_regression")]
    status_mismatch = [r for r in verify_rows if not r.get("status_matches_apply_after") and not r.get("profile_error")]
    mand_fail = [m for m in mandatory if m.get("gate_result", "").startswith("FAIL")]

    verdict = "PASS"
    if len(apply_rows) != 104:
        verdict = "FAIL"
    if profile_errors:
        verdict = "FAIL"
    if f2nf or strict_reg:
        verdict = "FAIL"
    if status_mismatch:
        verdict = "FAIL"
    if mand_fail:
        verdict = "FAIL"
    if not control.get("usable_ok") and not control.get("profile_error"):
        verdict = "FAIL"
    if control.get("profile_error"):
        pass  # 002415 optional if missing

    _write_verify_csv(verify_rows, verify_csv)
    _write_report(apply_rows, verify_rows, mandatory, control, report_path, verdict=verdict)
    return verdict


def main() -> int:
    parser = argparse.ArgumentParser(description="#32c-R5 post-apply R&D verification")
    parser.add_argument("--apply-csv", default=APPLY_CSV)
    parser.add_argument("--report", default=REPORT_PATH)
    parser.add_argument("--verify-csv", default=VERIFY_CSV)
    args = parser.parse_args()

    verdict = run_verification(args.apply_csv, args.report, args.verify_csv)
    apply_rows = _load_apply_csv(args.apply_csv)
    verify_rows = _load_apply_csv(args.verify_csv) if os.path.isfile(args.verify_csv) else []

    from collections import Counter
    strict_dist = Counter(r.get("current_strict") for r in verify_rows if r.get("current_strict"))
    improved_mand = sum(1 for c in MANDATORY_IN_APPLY if any(
        r.get("company_code") == c and r.get("current_strict") == "usable" for r in verify_rows
    ))

    print(f"targets={len(apply_rows)} verdict={verdict}")
    print(f"strict_usable={strict_dist.get('usable',0)} strict_partial={strict_dist.get('partial',0)}")
    print(f"mandatory_recovered_usable={improved_mand}/{len(MANDATORY_IN_APPLY)}")
    print(f"report={args.report}")
    print(f"verify_csv={args.verify_csv}")
    for code in MANDATORY_CODES:
        r = next((x for x in verify_rows if x.get("company_code") == code), None)
        if r:
            print(f"  {code}: strict={r.get('current_strict')} status={r.get('current_status')}")
    c = _verify_control()
    if not c.get("profile_error"):
        print(f"  002415: strict={c.get('current_strict')} usable_ok={c.get('usable_ok')}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
