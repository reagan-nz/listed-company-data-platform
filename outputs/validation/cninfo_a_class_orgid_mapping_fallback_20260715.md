# A-class Offline orgId Mapping Fallback（Run 15 / A-R15-01）

_生成时间：2026-07-15_  
_性质：离线能力增益 · **CNINFO = 0** · **无 live** · **无 slice2 live raw_metadata 改写** · **未 commit（Controller 负责）**_

---

## 1. Task

| 项 | 值 |
|----|-----|
| track | A |
| task_id | A-R15-01 |
| executor | a-class-executor |
| capability_gain_expected | true |
| CNINFO | 0 |
| live | no |
| commit | no（Controller） |

---

## 2. Objective

当 A-class topSearch 返回 `orgId=null` 时，提供**纯离线**映射回退，使已知码（至少 AD2E578/590/598）可解析到已恢复 orgId，**不调用 CNINFO**。

---

## 3. Inputs（只读 · 已提交证据）

| 路径 | 用途 |
|------|------|
| `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_offline_recovery_20260715.csv` | Run 14 三案恢复表（最高优先级） |
| `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_offline_diagnostic_20260715.md` | 根因诊断 |
| `outputs/validation/cninfo_report_p1_identity_mapping.csv` | 通用 identity 映射 |
| `lab/eval_companies_full_market_2024.yaml` | 全市场 orgid 索引 |

---

## 4. Deliverables

| 文件 | 说明 |
|------|------|
| `lab/cninfo_a_class_orgid_mapping_fallback.py` | 离线 lookup / resolve 模块 |
| `lab/test_cninfo_a_class_orgid_mapping_fallback.py` | 单元测试（10） |
| 本报告 | 证据包 |

**未修改**：共享 live runner、slice2 live raw_metadata、universe CSV。

---

## 5. API（离线）

```text
build_offline_orgid_index(...) -> OfflineOrgIdIndex
lookup_orgid(code)  -> OrgIdLookupResult   # 未命中 found=False + error
resolve_orgid(code) -> str                 # 未命中抛 OrgIdMappingMissError
```

优先级：`recovery_csv` > `identity_mapping` > `full_market_yaml`。

缺失码：**显式** `offline_orgid_not_found:<code>` / `OrgIdMappingMissError`；禁止静默伪造。

---

## 6. Anchor resolution（slice2 S1 三案）

| case_id | code | name | offline orgId | source layer |
|---------|------|------|---------------|--------------|
| AD2E578 | 688605 | 先锋精科 | 9900059045 | recovery_csv |
| AD2E590 | 688688 | 蚂蚁集团 | 9900046315 | recovery_csv |
| AD2E598 | 688758 | 赛分科技 | 9900057459 | recovery_csv |

烟测索引规模（含三层源）：`index_size=6124`，`sources=3`，`cninfo_calls=0`。

---

## 7. Test results

```text
command: python3 lab/test_cninfo_a_class_orgid_mapping_fallback.py -v
Ran 10 tests in ~1.3s
OK
CNINFO calls: 0
```

覆盖点：

- 三案 orgId 精确匹配
- recovery-only 层独立覆盖三案
- 缺失码显式 miss / raise
- `cninfo_calls` 恒为 0

---

## 8. Capability gain

```text
capability_gain = CAPABILITY_ADVANCED
capability_gain_claim = offline_orgid_mapping_fallback_helper_ready
failure_class_addressed = org_id_topsearch_miss_with_known_offline_orgid
cninfo_calls = 0
live = false
runner_hook = deferred（本包仅 offline helper + tests，未改 live runner）
```

- 新增可复用离线解析能力：topSearch null 时可先查映射，再决定是否 live 重试。
- **不**宣称 production_ready / verified PASS / 已接入 live path。
- **不** mutate 已封闭 live 证据。

---

## 9. Explicit non-actions

- 无 CNINFO live
- 无 push / 无 `git add .` / 无 commit
- 无 PDF / DB / MinIO / RAG
- 未改 slice2 live raw_metadata
- 未改共享 live runner（可选 hook 留待后续窄改）

---

## 10. ready_for_commit

| 项 | 值 |
|----|-----|
| ready_for_commit | **true** |
| allow-list（仅此三路径） | 见下 |

Allow-list paths：

1. `lab/cninfo_a_class_orgid_mapping_fallback.py`
2. `lab/test_cninfo_a_class_orgid_mapping_fallback.py`
3. `outputs/validation/cninfo_a_class_orgid_mapping_fallback_20260715.md`

---

## 11. Next（Controller）

1. Review allow-list 后 commit（Controller only）。
2. 若需 capability 接入：在 A-class resolve_orgid 失败路径增加**可选** offline fallback 调用（窄改 · 另开任务）。
3. A-R15-02：本包时间用于 helper 落地；未单独 promote 额外证据文件。
