# CNINFO D 类 fund_industry_allocation — Sample Prep（Tier-0 / Tier-1）

_生成时间：2026-07-15 · D-FM-11_

> **CNINFO = 0** · Tier-0 只读引用 · Tier-1 合成

## Tier-0（read-only）

| 路径 | 用途 |
|------|------|
| `fixtures/d_class/fund_industry_allocation/sample_raw.json` | 基金行业配置 raw 骨架（C26 · default） |
| `lab/cninfo_d_class_mappers.py` `map_to_industry_aggregate` | 1 raw → 3 metrics |
| `config/cninfo_d_class_source_registry_draft.yaml` `fund_industry_allocation` | registry 契约 · company_code_available=false |
| `schemas/d_class/d_industry_aggregate.schema.json` | 行业聚合 schema |

## Tier-1（synthetic · this task）

根目录：`fixtures/d_class/fund_industry_allocation_first_slice/`

| 文件 | case | scenario |
|------|------|----------|
| DFIA001_found.json | DFIA001 | captured（Tier0 cite · C26 · default） |
| DFIA002_found.json | DFIA002 | captured（default 全行业截面非空 · sample C27） |
| DFIA003_found.json | DFIA003 | captured（rdate=20260331 截面非空 · sample C27） |
| DFIA004_found.json / DFIA004_empty.json | DFIA004 | captured / empty（rdate · C26） |
| DFIA004_industry_filtered_empty.json | DFIA004 | F001V filter → empty_but_valid |
| DFIA005_empty_but_valid_synthetic.json | DFIA005 | empty_but_valid（rdate=20251231） |

**禁止：** 301259 · 688671 · DLC006R · cninfo_called=true · company_code 写入 metric 行
