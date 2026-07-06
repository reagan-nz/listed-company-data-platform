# CNINFO B 类 Registry Lint Summary

## 1. 目的

本地 **registry / category routing / JSON Schema / fixture** 一致性检查。
**不请求 CNINFO**；不下载/解析 PDF；不写 verified。

## 2. 输入

| 来源 | 路径 |
|------|------|
| B 类 registry | `config/cninfo_b_class_source_registry_draft.yaml` |
| Category routing | `config/cninfo_announcement_categories.yaml` |
| Schemas | `schemas/b_class/` |
| Fixtures | `fixtures/b_class/` |
| 脚本 | `lab/lint_cninfo_b_class_registry.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_rules | **23** |
| fail | **0** |
| warn | **0** |
| info | **0** |
| result | **PASS** |

## 4. 重点检查结果

- **source_layer**：全部须为 `document_corpus`（R002）
- **verified**：全部须为 `false`；禁止 `verified` enum（R003/R009）
- **route_to**：category YAML 中 `source_id` 须匹配 registry（R008）
- **fixture source_id**：document fixture 须在 registry 内（R014）
- **non-periodic source**：inquiry/meeting/general 保持 `candidate`（R007/R012）
- **periodic source**：`cninfo_periodic_report_pdf` = `testing_stable_sample`（R007）

## 5. 问题清单

_无 FAIL / WARN。_

## 6. 质量边界

- Lint **PASS** 不代表 CNINFO coverage%。
- 不代表 PDF 已下载或已解析。
- 不代表 source **verified**。
- offline title fixture 的 `found` 仅表示 benchmark 路由。

## 7. 下一步

1. Corpus retrieval validation 小样本设计。
2. Known-document benchmark 替换为真实样本。
3. Probe 官方 `category_code`。
4. 允许请求后补 `pdf_url` 与 raw_file。

## 附录

详见 [cninfo_b_class_registry_lint_report.csv](cninfo_b_class_registry_lint_report.csv)。
