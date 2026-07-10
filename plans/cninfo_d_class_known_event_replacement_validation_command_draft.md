# CNINFO D 类 Known Event Replacement Validation — Command Draft

_生成时间：2026-07-09_

> **状态：NOT APPROVED** — 未来命令草案 only · **本回合不执行** · **Do not execute**

---

## 1. Purpose

在用户显式批准且 candidate intake 校验通过后，对 DLC003R · DLC006R replacement cases 执行 isolated metadata/event validation，补全组件级 `captured_normal` 覆盖。

---

## 2. Prerequisites

- [x] `d_class_known_event_candidate_intake_gate = HUMAN_CANDIDATE_VALIDATED`
- [x] [candidate template](../outputs/validation/cninfo_d_class_known_event_replacement_candidate_template.csv) 中 `human_provided=true`
- [x] [filled replacement universe](../outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv) placeholders **已替换**为人工公司
- [x] [approval checklist](../outputs/validation/cninfo_d_class_known_event_replacement_approval_checklist.md) 准备完成（**approval_status = NOT_APPROVED**）
- [x] runner dry-run + live path 已实现（见 [live implementation summary](../outputs/validation/cninfo_d_class_known_event_replacement_live_implementation_summary.md)）
- [x] live-path tests **22/22 PASS**（mock CNINFO only）
- [x] calibrated / original universe **未修改**

---

## 3. Output Root（隔离）

```text
outputs/validation/cninfo_d_class_known_event_replacement_validation/
```

**禁止写入：**

- `outputs/validation/cninfo_d_class_tiny_live_validation/`（v1）
- `outputs/validation/cninfo_d_class_tiny_live_validation_v2/`（v2）

---

## 4. Universe

```text
outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv
```

| case_id | company | component | expected_behavior | include_in_future_validation |
|---------|---------|-----------|-------------------|------------------------------|
| DLC003R | 688671 碧兴物联 | restricted_shares_unlock | captured_normal | **yes** |
| DLC006R | 301259 艾布鲁 | shareholder_change | captured_normal | **yes** |
| DLC001/002/004/005/007 | baseline | various | reference only | **no** · 0 CNINFO |

| 规则 | 说明 |
|------|------|
| DLC003R · DLC006R | 仅 `candidate_validation_status=HUMAN_CANDIDATE_VALIDATED` 行可执行 |
| `*_CANDIDATE_REQUIRED` | **不存在于 filled universe** |
| DLC001/002/004/005/007 | baseline reference · **0 CNINFO** |
| invented company codes | **禁止** |

---

## 5. Approval Flag（占位）

```text
--approve-d-class-known-event-replacement-validation
```

无此 flag → runner **拒绝 live**。

**live 路径已实现** · **本回合未执行真实 live** · **需人工 approval 后方可执行**。

---

## 6. Proposed Command（NOT APPROVED · Do not execute）

```bash
cd listed_company_data_collector

python lab/run_cninfo_d_class_tiny_live_validation.py \
  --known-event-replacement \
  --live \
  --universe-csv outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_replacement_validation/ \
  --approve-d-class-known-event-replacement-validation
```

> **注：** live 路径已实现 · mock 测试 **22/22 PASS** · **本草案 NOT APPROVED · Do not execute**

---

## 7. Dry-run Command（未来 · NOT APPROVED · Do not execute）

```bash
python lab/run_cninfo_d_class_tiny_live_validation.py \
  --dry-run \
  --known-event-replacement \
  --universe-csv outputs/validation/cninfo_d_class_tiny_live_replacement_universe_filled.csv \
  --output-root outputs/validation/cninfo_d_class_known_event_replacement_validation/ \
  --cases DLC003R,DLC006R
```

预期：`cninfo_calls=0` · 输出 planned case list · preflight PASS · **不调用 CNINFO**

---

## 8. Explicit Exclusions

| 项 | 值 |
|----|-----|
| invented company codes | **no** |
| web lookup | **no** |
| only human-filled cases run | **yes** |
| DB write | **no** |
| MinIO write | **no** |
| RAG run | **no** |
| verified | **no** |
| production_ready | **no** |
| testing_stable_sample upgrade | **no** |
| harvest | **no** |
| v1/v2 execution report mutation | **no** |

---

## 9. Gate

```text
approval_status = NOT_APPROVED
d_class_known_event_replacement_validation_package_gate = READY_FOR_APPROVAL
```

（未来执行 gate — **本草案不设定为 PASS** · **不是 live_ready**）

**CNINFO calls（本回合）：0** · **web lookup = 0** · **live/rerun/harvest = 0**
