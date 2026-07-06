# CNINFO B 类 Corpus Retrieval Script Skeleton Notes

_最后更新：2026-07-05_

> **脚本：** `lab/validate_cninfo_b_class_corpus_retrieval.py`  
> **设计：** [cninfo_b_class_corpus_retrieval_validation_design.md](cninfo_b_class_corpus_retrieval_validation_design.md)  
> **Ready-case：** [cninfo_b_class_retrieval_ready_case_rules.md](cninfo_b_class_retrieval_ready_case_rules.md)

---

## 1. 为什么先写 skeleton

B 类 non-periodic corpus（inquiry / meeting / general）尚无 live retrieval 证据。在实现 `hisAnnouncement/query` 之前，需要：

1. 明确 **只消费 ready case** 的入口
2. 定义 dry-run 输出字段与 exit code
3. 与 selector / intake / checklist 流程衔接

Skeleton 可在 **ready=0** 时安全运行，验证管线而不误发 CNINFO 请求。

---

## 2. 为什么只消费 ready cases

| 状态 | 脚本行为 |
|------|----------|
| `placeholder` | `skipped_placeholder`；`would_query=false` |
| `retired` | `skipped_retired` |
| `ready` + 字段完备 | `ready_for_future_live_validation`；`would_query=true`（dry-run 不执行） |
| `ready` + 缺字段 | `invalid_ready`；`would_query=false` |

21 条 placeholder **不会** 进入未来 query 循环。

---

## 3. dry-run 与 live mode 的边界

| 模式 | 行为 | 本阶段 |
|------|------|--------|
| **dry-run**（默认） | 校验 ready case；写 report；`query_executed=0` | ✅ 已实现 |
| **live** | 发起 CNINFO POST；解析 JSON；写 case_result | ❌ **未实现** |

`--no-dry-run` → exit 3 + `live mode not implemented`。

---

## 4. 当前不会请求 CNINFO

Skeleton **不包含：**

- `requests` / `urllib` 调用
- `hisAnnouncement/query` POST
- PDF 下载
- 任何网络 I/O

`query_status` 恒为 `not_executed_dry_run`（ready case 在 live 未实现时亦同）。

---

## 5. 后续实现 live request 前的条件

1. ≥3 条人工审核的 `case_status: ready` case
2. `select_cninfo_b_class_retrieval_ready_cases.py` → `invalid_ready=0`, `ready>0`
3. 本脚本 dry-run → `DRY_RUN_PASS`
4. 评审批准小样本 live 跑（sleep/timeout/公司池）
5. 在脚本内新增 `_execute_query(case)` **仅** 对 `ready_for_future_live_validation` 行调用
6. 仍 **不** 下载 PDF；只写 metadata 到 validation report

---

## 6. 不写 verified

- Live pass **不得** 写 `verified` 或自动升 `testing_stable_sample`（non-periodic）
- 报告使用 `case_result`: pass / fail / ambiguous / skipped
- registry `status.verified` 保持 `false`

---

## 7. Exit codes

| Code | 条件 |
|------|------|
| 0 | dry-run 完成；无 invalid_ready |
| 1 | 存在 `invalid_ready` |
| 2 | `--strict` 且 `ready_cases=0` |
| 3 | `--no-dry-run`（live 未实现） |

---

## 参考

| 文档 | 路径 |
|------|------|
| Dry-run summary | [cninfo_b_class_corpus_retrieval_dry_run_summary.md](../outputs/validation/cninfo_b_class_corpus_retrieval_dry_run_summary.md) |
| Intake template | [cninfo_b_class_ready_case_intake_template.md](cninfo_b_class_ready_case_intake_template.md) |
