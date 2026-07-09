# CNINFO C-Class Phase 3 Batch 500 Success-Subset Snapshot Build Expected QA

_生成时间：2026-07-09_

> Build 完成后预期 QA 口径（**本轮 build 未执行**）。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# 1. Build Scope Expectations

| 项 | 预期 |
|----|------|
| `company_count` | **491** |
| `excluded_code_count` in output | **0**（9 家 caveat 不得出现） |
| `snapshot_json_count` | **491**（或 ≤491 若 QA 再排除 partial） |
| `planned_modules` | **18** per company |

---

# 2. Isolation Expectations

| 项 | 预期 |
|----|------|
| `full_snapshot_modified` | **false** |
| `phase2_snapshot_modified` | **false** |
| `harvest_normalized_modified` | **false** |
| `harvest_raw_modified` | **false** |
| `cninfo_calls` | **0** |

---

# 3. Excluded Code Verification

以下 **9** 家代码在 snapshot output 中 **必须 absent**：

`600102` `600270` `600317` `600625` `600627` `600705` `600840` `601028` `601989`

| 检查 | 方法 | 预期 |
|------|------|------|
| YAML absent | universe YAML diff | **9/9 absent** |
| JSON absent | glob `phase3_batch_500_001_success/*.json` | **0** files for excluded codes |
| status CSV absent | company_snapshot_status.csv | **0** rows for excluded codes |

---

# 4. Module Quality Expectations

| 指标 | 预期 |
|------|------|
| module coverage | 18 模块均有 status |
| basic available | ≥ majority complete |
| derived from basic | contact · business_scope · industry |
| security | observe-only · 不阻塞主 gate |
| partial flags | `complete_with_caveat` 允许（harvest partial 行） |

---

# 5. Status Distribution (expected after build)

| status | 说明 |
|--------|------|
| `complete` | 主路径成功 |
| `complete_with_caveat` | partial harvest / module partial |
| `failed` | build 失败（须 error CSV 记录） |
| `pending` | build 后应为 **0** |

---

# 6. QA Artifacts (future)

| 产物 | 路径 |
|------|------|
| build report | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_build_report.csv` |
| build summary | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_build_summary.md` |
| build QA summary | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_build_qa_summary.md` |
| completeness report | `outputs/validation/cninfo_c_class_phase3_batch_500_success_snapshot_completeness_report.csv` |

---

# 7. Gate Expectations (future build)

| gate | 预期 |
|------|------|
| `phase3_batch_500_success_snapshot_build_gate` | `PASS` or `PASS_WITH_CAVEAT` |
| C-class status | 保持 `SNAPSHOT_GENERATED_QA_REVIEW` until explicit promotion |

---

# 8. Current State (pre-build)

| 项 | 值 |
|----|-----|
| snapshot JSON | **0** |
| build executed | **false** |
| CNINFO calls | **0** |
| approval gate | `READY_FOR_APPROVAL` |

---

# 9. Red Lines

- **no verified**
- **no DB / MinIO / RAG**
- **no identity merge**
