# CNINFO C 类 Era D — Partial-6 Human-Review Summary

_生成时间：2026-07-10_

> **offline validation-only** · **CNINFO = 0** · **no production write** · **no auto-fix**

---

## 范围

6 家 863_primary `needs_human_review`（6/10 normalized · status CSV = complete）：

| company_code | company_name | present | missing | snapshot |
|--------------|--------------|---------|---------|----------|
| 002267 | 陕天然气 | 6/10 | 4 | yes |
| 002710 | 慈铭体检 | 6/10 | 4 | yes |
| 301333 | 诺思格 | 6/10 | 4 | yes |
| 301583 | 托伦斯 | 6/10 | 4 | yes |
| 601206 | 海尔施 | 6/10 | 4 | yes |
| 688688 | 蚂蚁集团 | 6/10 | 4 | yes |

**6/6** 均有 status 行 · **6/6** 863 full snapshot 存在。

---

## 按 likely_gap_class

| likely_gap_class | count |
|------------------|-------|
| **status_ledger_only** | **6** |
| true_harvest_gap | 0 |
| mapper_drop | 0 |
| subtree_mismatch | 0 |
| other | 0 |

**解读：** 磁盘仅 6 个 normalized 文件，但 `company_harvest_status.csv` 标 `complete`；缺失源多为 dividend/executive/share_capital/shareholders 等 **empty_but_valid 高发源**；863 snapshot 已生成 — **非 proven live 缺口**。

---

## 按 recommendation

| recommendation | count |
|----------------|-------|
| **accept_with_caveat** | **6** |
| offline_remap_only | 0 |
| defer | 0 |
| **needs_live_resume** | **0** |

---

## Live resume 结论

**No live resume is justified for any of the 6 companies.**

- **needs_live_resume = 0/6**
- 与 58 triage（live_needed 0/58）一致
- Option A HOLD · status-fix-8 apply 后 C-line 继续 offline 收口即可

---

## 产出物

| 文件 | 说明 |
|------|------|
| [source presence ledger](cninfo_c_class_erad_partial6_human_review/reports/partial6_source_presence_ledger.csv) | 6 行汇总 |
| [missing source matrix](cninfo_c_class_erad_partial6_human_review/reports/partial6_missing_source_matrix.csv) | 6×10 矩阵 |
| [human review packet](cninfo_c_class_erad_partial6_human_review/partial6_human_review_packet.md) | 逐公司段落 |
| Runner | `lab/run_cninfo_c_class_erad_partial6_human_review_scan.py` |

---

## Gate

```
c_class_erad_partial6_human_review_gate = PASS_OFFLINE
```

**NOT APPROVED live** · **NOT APPROVED auto-fix** · **NOT verified**

---

## 红线

No CNINFO · no live · no production write · no snapshot rebuild · Era D **not finished**
