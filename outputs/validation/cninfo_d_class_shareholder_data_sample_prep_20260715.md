# CNINFO D 类 shareholder_data — Sample Prep（Tier-0 / Tier-1）

_生成时间：2026-07-15 · D-FM-07_

> **CNINFO = 0** · Tier-0 只读引用 · Tier-1 合成

## Tier-0（read-only）

| 路径 | 用途 |
|------|------|
| `fixtures/d_class/shareholder_data/sample_raw.json` | 股东数据 raw 骨架（000001 平安银行 · rdate=20260331） |
| `lab/cninfo_d_class_mappers.py` `map_to_company_metric_periodic` | 1 raw → 6 metrics |
| `config/cninfo_d_class_source_registry_draft.yaml` `shareholder_data` | registry 契约 |
| `schemas/d_class/d_company_metric_periodic.schema.json` | 周期指标 schema |

## Tier-1（synthetic · this task）

根目录：`fixtures/d_class/shareholder_data_first_slice/`

| 文件 | case | scenario |
|------|------|----------|
| DSD001_found.json | DSD001 | captured（Tier0 cite） |
| DSD002_found.json / DSD002_empty.json | DSD002 | captured / empty |
| DSD003_found.json / DSD003_empty.json | DSD003 | captured / empty |
| DSD003_records_filtered_empty.json | DSD003 | SECCODE filter → empty_but_valid |
| DSD004_found.json / DSD004_empty.json | DSD004 | captured / empty |
| DSD005_empty_but_valid_synthetic.json | DSD005 | empty_but_valid |

**禁止：** 301259 · 688671 · DLC006R · cninfo_called=true
