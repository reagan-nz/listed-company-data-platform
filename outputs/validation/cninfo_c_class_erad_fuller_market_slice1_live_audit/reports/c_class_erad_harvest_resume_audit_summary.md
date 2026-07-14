# C-Class Era D Harvest Resume Audit Summary

_generated_at: 2026-07-13T03:40:28Z_

> **offline dry-run only** · **CNINFO = 0** · **production harvest read-only**

## Scan scope

- **harvest_root:** `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/`
- **audit_mode:** `dry_run`

### Subtrees scanned

- `863_primary` → `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/harvest/cninfo_c_class/fuller_market_slice1_200` (status_csv=yes)

## Resume state counts (863_primary)

| resume_state | count |
|--------------|-------|
| complete | 93 |
| partial | 7 |
| missing | 0 |
| needs_review | 100 |
| unknown | 0 |

## Resume state counts (all subtrees)

| resume_state | count |
|--------------|-------|
| complete | 93 |
| partial | 7 |
| missing | 0 |
| needs_review | 100 |
| unknown | 0 |

- **total report rows:** 200

## State mapping

| resume_state | 判定规则 |
|--------------|----------|
| complete | `company_harvest_status=complete` 且 normalized 源齐全 |
| partial | `partial`/`failed` 或源缺口但有部分文件 |
| missing | 无 status 行且无 normalized 文件 |
| needs_review | 磁盘有文件但无 status 行；或 complete 与源计数不一致 |
| unknown | 非 863 universe 且无数据 |

## Live resume recommendation

- **hold** for 863_primary when complete dominates and gaps are needs_review/missing only
- **deferred_targeted_live_after_approval** for partial/missing (separate Slice-C-EraD-02b)
- **no snapshot rebuild** in this slice

## Red lines

No CNINFO · no live harvest · no production root writes · holdout policy unchanged
