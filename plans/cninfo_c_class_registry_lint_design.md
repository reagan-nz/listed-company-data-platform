# CNINFO C 类 Registry Lint 设计

_最后更新：2026-07-05_

> **脚本：** `lab/lint_cninfo_c_class_registry.py`  
> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)  
> **JSON Schema：** [schemas/c_class/](../schemas/c_class/)

---

## 1. 目的

C 类 company profile 已具备 candidate YAML（10 source）、6 个 JSON Schema draft，但 **endpoint 尚未 probe**。

**Registry lint** 在 **本地、离线、无 CNINFO 请求** 前提下，检查 candidate YAML 与 schema 目录的 **内部一致性**，避免：

- `source_id` 重复或混入 B/D 类源；
- `verified` 误写入；
- `recommended_status` 超出允许枚举；
- `expected_fields` 缺失；
- schema 文件缺失。

Lint **不**代表 F10 字段可得性；**不** probe endpoint；**不写 verified**。

---

## 2. 输入

| 输入 | 路径 | 用途 |
|------|------|------|
| C 类 candidate registry | `config/cninfo_c_class_source_candidates.yaml` | source 定义、status、expected_fields |
| JSON Schema | `schemas/c_class/*.schema.json` | `source_status` / `fetch_status` enum 对照 |

**不读取：** CNINFO API、数据库、B/D registry（仅黑名单对照）。

---

## 3. Lint 规则（R001–R012）

| rule_id | severity | 检查 |
|---------|----------|------|
| R001 | FAIL | `sources[].source_id` 唯一 |
| R002 | FAIL | 所有 `source_layer` 必须为 `company_profile` |
| R003 | FAIL | 禁止 `verified: true`、`recommended_status: verified`、enum 含 `verified` |
| R004 | FAIL | `recommended_status` 仅允许 candidate / testing / testing_stable_sample / partial / blocked / deprecated |
| R005 | FAIL | 当前阶段所有 source 的 `recommended_status` 应为 `candidate` |
| R006 | INFO | `endpoint: null` 合法（尚未 probe）；全 null 时记 INFO，**不**记 FAIL |
| R007 | WARN/FAIL | `required_keys`：defaults 或每 source 须声明，且含 `company_code` 或 `org_id` |
| R008 | FAIL | 每个 source 须有非空 `expected_fields` |
| R009 | FAIL | `source_category` 仅允许 9 类 C 类 profile category |
| R010 | FAIL | `source_id` 必须以 `cninfo_` 开头 |
| R011 | FAIL | `schemas/c_class/` 须包含 6 个 schema 文件 |
| R012 | FAIL | 不得出现已知 B/D 类 `source_id`（如 `cninfo_periodic_report_pdf`、`margin_trading`） |

---

## 4. 输出

**CSV 字段：** `rule_id` · `severity` · `target` · `status` · `message` · `suggested_fix`

**severity：** `FAIL` · `WARN` · `INFO`

**stdout：** `SUMMARY  rules=12  sources=N  fail=0  warn=0  info=…  result=PASS`

---

## 5. 当前预期

| 项 | 预期 |
|----|------|
| endpoint | 全部 `null` → R006 INFO，**不** FAIL |
| recommended_status | 全部 `candidate` → R005 PASS |
| verified | 全部 `false` → R003 PASS |
| result | **PASS**（fail=0） |

---

## 6. 质量边界

- Lint PASS **不代表** CNINFO F10 可用。
- **不代表** endpoint 已确认或字段已 UI 验证。
- **不写 verified**。

---

## 7. 下一步

1. known-company fixture schema validation。
2. per-source DevTools probe → 回填 `endpoint`。
3. C 类 known-company profile validation 脚本（小样本，config 驱动）。

---

## 参考

| 文档 | 路径 |
|------|------|
| C 类 discovery 设计 | [cninfo_c_class_f10_source_discovery_design.md](cninfo_c_class_f10_source_discovery_design.md) |
| B 类 lint 设计（对照） | [cninfo_b_class_registry_lint_design.md](cninfo_b_class_registry_lint_design.md) |
