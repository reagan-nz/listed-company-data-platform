# CNINFO C-Class Registry Candidate Refresh Execution Plan

_生成时间：2026-07-08_

> **性质：** Phase 1 registry candidate refresh **未来实现**执行计划。**本轮不实现脚本** · **不生成 refreshed CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：**
- [refresh plan](cninfo_c_class_registry_candidate_refresh_plan.md)
- [refresh action matrix](../outputs/validation/cninfo_c_class_registry_candidate_refresh_action_matrix.csv)
- [reconciliation result](../outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv)

---

# 1. 未来脚本

| 项 | 值 |
|----|-----|
| **脚本名** | `lab/refresh_cninfo_c_class_company_registry_candidate.py` |
| **默认模式** | **dry-run only**（打印统计 · 不写文件） |
| **写入模式** | `--write` 显式批准后才 emit refreshed candidate |
| **网络** | **无 CNINFO** · **无 live** |

---

# 2. 输入 / 输出

## 2.1 输入

| 文件 | 路径 | 行数 |
|------|------|------|
| candidate draft | `outputs/validation/cninfo_c_class_company_registry_candidate_draft.csv` | 6124 |
| reconciliation result | `outputs/validation/cninfo_c_class_full_market_universe_reconciliation_result.csv` | 6124 |
| identity decision ledger | `outputs/validation/cninfo_c_class_registry_identity_decision_ledger.csv` | 267 |

## 2.2 输出（`--write` 时）

| 文件 | 路径 |
|------|------|
| refreshed candidate | `outputs/validation/cninfo_c_class_company_registry_candidate_refreshed.csv` |
| refresh summary | `outputs/validation/cninfo_c_class_registry_candidate_refresh_summary.md` |

## 2.3 Join 逻辑

```python
# 伪代码 — 本轮不实现
for row in candidate_draft:
    recon = reconciliation_by_code[row.company_code]
  row.reconciliation_classification = recon.classification
    row.refresh_action = ACTION_MATRIX[recon.classification].refresh_action
    row.refresh_confidence = ACTION_MATRIX[recon.classification].confidence
    row.requires_manual_review = ACTION_MATRIX[recon.classification].manual_review
    row.harvest_support_status = ACTION_MATRIX[recon.classification].harvest_status
    row.snapshot_support_status = ACTION_MATRIX[recon.classification].snapshot_status
    row.lineage_note = f"recon={recon.reconciliation_id}; {recon.notes}"
    # 24 base 字段：除 support/confidence/hold 外保持不变
```

---

# 3. Safety Controls

| 控制 | 说明 |
|------|------|
| default dry-run | 无 `--write` 不创建/覆盖 refreshed CSV |
| no CNINFO | 脚本无 HTTP / 无 live 依赖 |
| no merge | `merge_executed` 恒 false；不合并 code 行 |
| no registry implementation | 不写 DB · 不建表 |
| 863 preservation | already_in_c_class 行 confidence 不得降级 |
| conflict isolation | identity_conflict / manual_review 不得标为 candidate_supported |
| ledger cross-check | refresh 后抽样核对 ledger 267 条一致性 |

---

# 4. 执行步骤（未来）

| Step | 动作 | 产出 |
|------|------|------|
| 1 | load candidate_draft + reconciliation + ledger | 内存 join |
| 2 | apply action matrix per classification | 6124 refreshed rows |
| 3 | validate invariants（863 high · 26 hold · 0 not_found） | validation report |
| 4 | dry-run print counts | stdout stats |
| 5 | `--write` emit CSV + summary | refreshed 产物 |
| 6 | run tests | 5/5 PASS gate |

---

# 5. 测试计划

**脚本：** `lab/test_cninfo_c_class_registry_candidate_refresh.py`（未来）

| # | Case | 断言 |
|---|------|------|
| 1 | **classification mapping** | 8 类 classification → refresh_action 一一对应 |
| 2 | **confidence mapping** | already_in_c_class=high · matched_active=low · conflict=review |
| 3 | **manual review preservation** | needs_manual_review 16 行 requires_manual_review=true |
| 4 | **BSE hold preservation** | matched_bse_legacy_hold 242 行 harvest=legacy_hold |
| 5 | **863 high-confidence preservation** | already_in_c_class 863 行 confidence=high 且未降级 |

**期望：** 5/5 PASS

---

# 6. Gate（未来执行后）

| Gate | 条件 |
|------|------|
| `registry_candidate_refresh_dryrun_gate` | dry-run 统计与 action matrix 一致 |
| `registry_candidate_refresh_gate` | `--write` 后 6124 行完整 · 不变量通过 · test 5/5 |

---

# 7. 后续阶段衔接

| 阶段 | 输入 | 说明 |
|------|------|------|
| Phase 2 smoke | refreshed CSV 中 `matched_active` 抽样 | 100–200 家 |
| Phased manifest | `full_market_phased_universe_manifest.yaml` | 从 refreshed 派生 |
| Registry Layer 2 | 产品决策后 | implementation still deferred |

---

# 8. 红线

未来实现时 **禁止：**

- CNINFO / live / harvest / snapshot
- registry implementation / DB / MinIO / RAG
- identity merge
- raw / normalized / field_inventory 修改
- verified / testing_stable_sample

**本轮：** 脚本 **未创建** · refreshed CSV **未生成**
