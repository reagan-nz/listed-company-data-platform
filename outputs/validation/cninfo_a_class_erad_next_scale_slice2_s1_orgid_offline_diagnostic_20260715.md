# A-class Slice2 S1 — Offline org_id Root-Cause Diagnostic (Run 14)

_生成时间：2026-07-15_  
_性质：离线交叉证据 · **CNINFO = 0** · **无 live** · **无 universe 改写** · **NOT verified**_

---

## 1. Task

| 项 | 值 |
|----|-----|
| track | A |
| task | offline org_id diagnostic for AD2E578 / AD2E590 / AD2E598 |
| capability_gain_expected | true |
| CNINFO | 0 |
| while_peer_running | C native `--exclusion-csv` wiring（async） |

---

## 2. Observed failure pattern（slice2 S1 live，已有）

| case_id | code | name | live org_id | retrieval | CNINFO/case |
|---------|------|------|-------------|-----------|-------------|
| AD2E578 | 688605 | 先锋精科 | null | not_found | 3 |
| AD2E590 | 688688 | 蚂蚁集团 | null | not_found | 3 |
| AD2E598 | 688758 | 赛分科技 | null | not_found | 3 |

对照：同批 100 案中 **97** 案 `org_id` present 且可匹配；失败集与 `org_id=null` **完全重合**。

Runner 路径：`resolve_orgid`（topSearch）失败后直接 `not_found`，**不会**进入 periodic matching。

---

## 3. Offline cross-source orgId recovery（本包）

权威只读源（仓库内已有，非新 live）：

| code | name | offline orgId | source |
|------|------|---------------|--------|
| 688605 | 先锋精科 | **9900059045** | `outputs/validation/cninfo_report_p1_identity_mapping.csv` + `lab/eval_companies_full_market_2024.yaml` |
| 688688 | 蚂蚁集团 | **9900046315** | C-class `cninfo_c_class_retry_889_partial_fail_live_report.csv`（同码同名） |
| 688758 | 赛分科技 | **9900057459** | `lab/eval_companies_full_market_2024.yaml` |

---

## 4. Identity caveat adjudication（AD2E590）

| 问题 | 离线裁决 |
|------|----------|
| universe `688688` ↔ `蚂蚁集团` 是否身份错配？ | **否（offline_consistent）** |
| 依据 | C-class 既有 live/report 行对同一 `scode=688688` 使用名称「蚂蚁集团」且解析到 `orgId=9900046315` |
| 动作 | **不**改 slice2 universe；将 identity caveat 从「未裁决」升级为 **`offline_identity_consistent`** |

失败根因更应归类为：**A-path topSearch orgId 瞬时/路径失败**，而非公司身份错误。

---

## 5. Capability gain

```text
capability_gain = CAPABILITY_ADVANCED
failure_class_refined = org_id_topsearch_miss_with_known_offline_orgid
identity_caveat_ad2e590 = offline_identity_consistent
isolated_retry_hint = prefer_seeded_orgid_or_mapping_fallback_before_live_requery
```

- 三案均可在 **CNINFO=0** 下给出已知 orgId（侧轨映射）。
- 窄化后续 isolated retry：优先验证「映射 orgId + query」是否恢复匹配，而不是盲目重跑 topSearch。
- **不**宣称 bare PASS / verified / production_ready。
- **不** mutate slice2 live 根 / universe CSV。

---

## 6. Explicit non-actions

- 无 CNINFO live / 无 isolated retry 执行（本包仅诊断）
- 无 push
- 无 PDF / DB / RAG
- 不把 offline orgId 写回已封闭 live raw_metadata（避免污染 live 证据）

---

## 7. Artifacts

| 文件 | 用途 |
|------|------|
| 本报告 | 根因与裁决 |
| `cninfo_a_class_erad_next_scale_slice2_s1_orgid_offline_recovery_20260715.csv` | 三案恢复表 |

---

## 8. Async note（Run 14）

本 A-wave 在 **C 仍 EXECUTING**（native exclusion-csv）期间完成 VALIDATING→COMMIT 路径，用于证明 v4：一轨不阻塞他轨。
