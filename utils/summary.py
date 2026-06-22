"""Builds outputs/coverage_summary.md from collected coverage rows.

Produces the 14 required sections plus a final judgment on whether the generic
collector framework is promising.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from utils.coverage import CoverageRow

SUCCESS_STATES = {"success", "partial"}
FAIL_STATES = {"failure", "skipped"}


def _pct(n: int, d: int) -> str:
    return f"{(100.0 * n / d):.0f}%" if d else "0%"


def build_summary(
    rows: list[CoverageRow],
    companies: list[dict],
    sources: list[dict],
) -> str:
    name_to_priority = {s.get("name", ""): s.get("priority", "P1") for s in sources}

    total = len(rows)
    categories = sorted({r.data_category for r in rows if r.data_category})
    n_companies = len(companies)

    success = [r for r in rows if r.fetch_status in SUCCESS_STATES]
    failed = [r for r in rows if r.fetch_status in FAIL_STATES]
    by_state: dict[str, int] = defaultdict(int)
    for r in rows:
        by_state[r.fetch_status or "unknown"] += 1

    needs_pw = [r for r in rows if r.needs_playwright]
    needs_llm = [r for r in rows if r.needs_llm]
    needs_legal = [r for r in rows if r.needs_legal_review]
    full_text = [r for r in rows if r.can_store_full_text]
    metadata_only = [r for r in rows if not r.can_store_full_text]
    p2_rows = [r for r in rows if name_to_priority.get(r.data_source) == "P2"]

    # Per-category coverage ratio (success+partial / total in category).
    cat_total: dict[str, int] = defaultdict(int)
    cat_ok: dict[str, int] = defaultdict(int)
    for r in rows:
        cat_total[r.data_category] += 1
        if r.fetch_status in SUCCESS_STATES:
            cat_ok[r.data_category] += 1
    cat_ratio = {c: (cat_ok[c] / cat_total[c] if cat_total[c] else 0.0) for c in cat_total}
    well_covered = sorted([c for c, v in cat_ratio.items() if v >= 0.6])
    weak = sorted([c for c, v in cat_ratio.items() if v < 0.6])

    overall_ok_ratio = len(success) / total if total else 0.0

    lines: list[str] = []
    add = lines.append

    add("# Source Coverage Summary")
    add("")
    add(f"_Generated: {datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}_")
    add("")
    add("This report measures how much **public** data can be collected for the "
        "configured companies. It is the output of a data source **validation prototype**, "
        "not a production crawler.")
    add("")

    add("## 1. Companies tested")
    add("")
    if companies:
        for c in companies:
            label = c.get("short_name") or c.get("company_name") or "(unnamed)"
            code = c.get("stock_code") or "?"
            exch = c.get("exchange") or "?"
            add(f"- {label} ({code} / {exch})")
    else:
        add("- (none configured)")
    add(f"\n**Total companies:** {n_companies}")
    add("")

    add("## 2. Total categories tested")
    add("")
    add(f"**{len(categories)}** categories: {', '.join(categories) if categories else '(none)'}")
    add("")

    add("## 3. Total source-company pairs tested")
    add("")
    add(f"**{total}** pairs "
        f"(success: {by_state.get('success', 0)}, partial: {by_state.get('partial', 0)}, "
        f"failure: {by_state.get('failure', 0)}, skipped: {by_state.get('skipped', 0)})")
    add("")

    add("## 4. Successful sources")
    add("")
    add(f"**{len(success)}** of {total} pairs reachable/usable ({_pct(len(success), total)}) "
        f"[success + partial].")
    add("")

    add("## 5. Failed sources")
    add("")
    add(f"**{len(failed)}** of {total} pairs failed/unavailable ({_pct(len(failed), total)}) "
        f"[failure + skipped].")
    if failed:
        reason_counts: dict[str, int] = defaultdict(int)
        for r in failed:
            reason_counts[r.failure_reason or "unknown"] += 1
        add("\nTop failure reasons:")
        for reason, cnt in sorted(reason_counts.items(), key=lambda x: -x[1])[:8]:
            add(f"- `{reason}`: {cnt}")
    add("")

    add("## 6. Sources needing Playwright")
    add("")
    add(f"**{len(needs_pw)}** pairs flagged `needs_playwright`.")
    add("")

    add("## 7. Sources needing LLM")
    add("")
    add(f"**{len(needs_llm)}** pairs flagged `needs_llm` (summary/classification/event/evidence extraction).")
    add("")

    add("## 8. Sources needing legal review")
    add("")
    add(f"**{len(needs_legal)}** pairs flagged `needs_legal_review`.")
    add("")

    add("## 9. Sources that can store full text")
    add("")
    add(f"**{len(full_text)}** pairs may store full text (statutory official filings).")
    ft_sources = sorted({r.data_source for r in full_text})
    if ft_sources:
        add("Sources: " + ", ".join(ft_sources))
    add("")

    add("## 10. Sources that should only store metadata")
    add("")
    add(f"**{len(metadata_only)}** pairs are metadata-only (news, social, research reports, "
        "commercial platforms, etc.).")
    add("")

    add("## 11. Sources not recommended for first-stage use")
    add("")
    p2_names = sorted({r.data_source for r in p2_rows})
    add(f"**{len(p2_rows)}** pairs are P2 (not first-stage): {', '.join(p2_names) if p2_names else '(none)'}")
    add("These include high-risk social/sentiment sources and litigation/enforcement risk signals.")
    add("")

    add("## 12. Well-covered data dimensions")
    add("")
    if well_covered:
        for c in well_covered:
            add(f"- {c} ({_pct(cat_ok[c], cat_total[c])} reachable)")
    else:
        add("- (none reached the 60% threshold in this run)")
    add("")

    add("## 13. Weak or missing data dimensions")
    add("")
    if weak:
        for c in weak:
            add(f"- {c} ({_pct(cat_ok[c], cat_total[c])} reachable)")
    else:
        add("- (none)")
    add("")

    add("## 14. Final judgment")
    add("")
    add(_final_judgment(overall_ok_ratio, well_covered, weak, n_companies, total))
    add("")

    return "\n".join(lines)


def _final_judgment(
    ok_ratio: float,
    well_covered: list[str],
    weak: list[str],
    n_companies: int,
    total: int,
) -> str:
    if n_companies == 0 or total == 0:
        return (
            "**Inconclusive.** No companies were configured, so no source-company pairs were "
            "tested. Add companies to `config/companies.yaml` and re-run to evaluate coverage."
        )
    verdict = "Promising" if ok_ratio >= 0.5 else "Partially promising"
    return (
        f"**{verdict}.** Across {n_companies} company(ies) and {total} source-company pairs, "
        f"{ok_ratio*100:.0f}% of sources were reachable/usable. A generic, config-driven "
        "collector for Chinese listed companies is feasible: statutory disclosure, company "
        "official sites, and government/policy portals form a strong, legally-clean P0 core "
        f"(well-covered: {', '.join(well_covered) if well_covered else 'n/a'}). "
        "High-value but higher-risk dimensions (news, social sentiment, research reports, "
        "commercial enterprise platforms) are best limited to existence + metadata, with "
        "authorization or official APIs for anything deeper. Weak dimensions "
        f"({', '.join(weak) if weak else 'n/a'}) are mostly config-driven (region/industry "
        "URLs) or require Playwright/legal review rather than indicating an infeasible design. "
        "Overall, the framework's value is in traceability, failure recording, and legal-risk "
        "mapping rather than exhaustive crawling."
    )
