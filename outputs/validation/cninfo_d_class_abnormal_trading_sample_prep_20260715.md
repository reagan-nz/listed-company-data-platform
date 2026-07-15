# CNINFO D 类 abnormal_trading — Sample Prep（Tier-0 / Tier-1）

_生成时间：2026-07-15 · D-FM-03_

> **CNINFO = 0** · Tier-0 只读引用 · Tier-1 合成

## Tier-0（read-only）

| 路径 | 用途 |
|------|------|
| `fixtures/d_class/abnormal_trading/sample_raw.json` | 市场异动 raw 骨架（000004 国华退 · 退市整理期 · detail[]） |
| `lab/cninfo_d_class_mappers.py` `_map_abnormal_trading` | 映射先例 |
| `config/cninfo_d_class_source_registry_draft.yaml` `abnormal_trading` | registry 契约 |
| `schemas/d_class/d_company_event.schema.json` | 主事件 schema |
| `schemas/d_class/d_event_party_detail.schema.json` | detail[] **deferred** |

## Tier-1（synthetic · this task）

根目录：`fixtures/d_class/abnormal_trading_first_slice/`

| 文件 | case | scenario |
|------|------|----------|
| DAT001_needs_review_synthetic.json | DAT001 | needs_review |
| DAT002_found.json / DAT002_empty.json | DAT002 | captured / empty |
| DAT003_found.json / DAT003_empty.json | DAT003 | captured / empty |
| DAT004_found.json / DAT004_empty.json | DAT004 | captured / empty |
| DAT005_empty_but_valid_synthetic.json | DAT005 | empty_but_valid |

**禁止：** 301259 · 688671 · DLC006R · cninfo_called=true
