# 公司画像本地目录与证据指针约定

_最后更新：2026-07-10_

> 本阶段 **只规范、不入库**；portrait 产物只读引用既有 `outputs/harvest|validation|snapshot`，不改写 Phase 3 生产根。

## 根目录

```text
outputs/portrait/companies/<company_code>/
  facts.jsonl            # 事实层：每行一条 fact_record
  coverage.json          # 该公司按模块状态摘要
  evidence_index.jsonl   # 每行一条 evidence_ref
```

## company_id 策略

- 主键固定为 **company_code**（如 `000009`）。
- `org_id` 作为 M01 身份字段写入 facts，不另造第二主键。
- 曾用名、代码变更只进 M01 变更史字段，不分裂实体。

## fact_record 字段

见 [`schemas/portrait/fact_record.schema.json`](../schemas/portrait/fact_record.schema.json)。

关键字段：

```text
company_id, field_id, module_id, value, value_shape,
as_of | period, source_track, source_rank,
evidence_ref_id, conflict_flag, status, collected_at
```

## evidence_ref 字段

见 [`schemas/portrait/evidence_ref.schema.json`](../schemas/portrait/evidence_ref.schema.json)。

关键字段：

```text
evidence_ref_id, source_path, source_url, sha256, fetched_at, note
```

## 冲突与版本（模块十七）

- 同 `field_id` 允许多条 fact，靠 `source_rank` + `as_of/period` 取当前值。
- 冲突写 `conflict_flag=yes`，不静默合并。
- 禁止本阶段写 `verified`。

## 与四线产物关系

| 轨道 | evidence_root_hint 示例 |
|------|-------------------------|
| C | `outputs/harvest/cninfo_c_class/normalized/<profile>/` |
| A | `outputs/validation/cninfo_a_class_*/raw_metadata/` |
| B | `outputs/validation/cninfo_b_class_*/raw_metadata/` |
| D | `outputs/validation/cninfo_d_class_*/` |

## Gate

- `portrait_p2_schema_gate` — fact/evidence schema 自校验通过
- `portrait_p3_pilot_gate` — 试点公司每条 fact 均有 evidence_ref

## 红线

无 DB/MinIO · 无 PDF 解析默认 · 无 `verified` · 生产根只读
