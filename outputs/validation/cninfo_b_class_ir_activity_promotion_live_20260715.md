# CNINFO B 类 B-FM-10 — IR Activity（集体接待日 + 开放日）Promotion Bounded Live

_生成时间：2026-07-15 · bounded live metadata · **无 commit** · **无 push**_

> **性质：** B-FM-05/06 晋升闭环续包 — `ir_activity_known_002/003` + `ir_activity_sample_001/002` live metadata  
> **不造** validation_design §7 FP · **不**触碰 A/C/D · **不**写 verified · **不**下载 PDF

---

## 1. 5-horizon 选择

| # | horizon | 候选 | 本任务 |
|---|---------|------|--------|
| 1 | bounded live | IR B-FM-05/06 新晋 4 条 | **执行** — 主路径 |
| 2 | harvest promotion | 更多 IR / regulatory placeholder | **推迟** — 无新边角证据 |
| 3 | routing edges | 更多 document_type | **推迟** — B-FM-04 已清 IR route |
| 4 | retrieval tooling | 非 live 工具扩展 | **推迟** — 本包优先闭合 IR live |
| 5 | fake §7 FP | 新造 FP lineage | **拒绝** — 禁止 |

---

## 2. Allow-list

| case_id | type | evidence |
|---------|------|----------|
| `ir_activity_known_002` | known-document | 吉林化纤 000420 · 「投资者网上集体接待日」 · 2025-05-19~22 · BD2E202 |
| `ir_activity_known_003` | known-document | 新乡化纤 000949 · 「投资者开放日」 · 2025-06-02~05 · BD2E232 |
| `ir_activity_sample_001` | category-sample | `投资者网上集体接待日` · 2025-05-08~22（全市场窗） |
| `ir_activity_sample_002` | category-sample | `投资者开放日` · 2025-06-01~05（全市场窗） |

排除：既有 ready（含活动记录表 known_001、警示函、CPA 等）、全部 placeholder、guard。

---

## 3. Validation

| 检查 | 结果 |
|------|------|
| `python lab/test_cninfo_b_class_ir_activity_promotion.py` | **5 OK**（B-FM-05 不回退） |
| `python lab/test_cninfo_b_class_ir_activity_open_day_promotion.py` | **4 OK**（B-FM-06 不回退） |
| `python lab/test_cninfo_b_class_ir_activity_promotion_live.py` | **3 OK** |
| `python lab/test_cninfo_b_class_category_routing_ir_activity_edge.py` | **8 OK**（不回退） |
| allow-list dry-run | **DRY_RUN_PASS** · ready=**4** · invalid_ready=0 · query=0 |
| bounded live | **LIVE_PASS** · pass=**4**/0/0 |

### Live 细节

| 项 | 值 |
|----|-----|
| allow-list | 仅 `ir_activity_known_002/003` + `ir_activity_sample_001/002` |
| CNINFO | **8**（2 topSearch + 6 query） |
| wall | **26.14 s** |
| PDF | **0** |

| case_id | matched | date | classification | result |
|---------|---------|------|----------------|--------|
| `ir_activity_known_002` | 关于参加2025年吉林辖区上市公司投资者网上集体接待日活动的公告 | 2025-05-20 | classified_correctly / investor_relations_activity | **pass** |
| `ir_activity_known_003` | 关于举办投资者开放日活动的公告 | 2025-06-03 | classified_correctly / investor_relations_activity | **pass** |
| `ir_activity_sample_001` | …投资者网上集体接待日活动的公告（窗内 30 hits） | 2025-05-21 | classified_correctly / investor_relations_activity | **pass** |
| `ir_activity_sample_002` | 关于举办投资者开放日活动的公告（窗内 1 hit） | 2025-06-03 | classified_correctly / investor_relations_activity | **pass** |

---

## 4. Capability Gain

- IR 集体接待日 known-document ready 经 **live metadata** 确认（标题/日期/pdf_url/路由）
- IR 开放日 known-document ready 经 **live metadata** 确认
- 两 category-sample ready 经全市场窗 **live metadata** 确认
- 闭合 B-FM-04 → B-FM-05/06 → B-FM-10 live 链路；**不**声称 B complete / verified / full-market %

---

## 5. Gate

```text
b_class_ir_activity_promotion_live_gate = LIVE_PASS
task_id = B-FM-10
cninfo_calls_this_package = 8
live_calls_this_package = 8
pdf_download = 0
allow_list = ir_activity_known_002 + ir_activity_known_003 + ir_activity_sample_001 + ir_activity_sample_002
fake_section7_fp = no
ready_for_commit = true
```

---

## 6. 产物

| 路径 | 用途 |
|------|------|
| `lab/test_cninfo_b_class_ir_activity_promotion_live.py` | allow-list + mock live 锁测 |
| `outputs/validation/cninfo_b_class_ir_activity_promotion_live_20260715/` | allow-list + live 证据包 |
| 本文件 | 任务报告 |

---

## 7. Return Block

| 字段 | 值 |
|------|-----|
| task | B-FM-10 IR activity promotion bounded live（known_002/003 + sample_001/002） |
| files | live 证据包 · `lab/test_cninfo_b_class_ir_activity_promotion_live.py` · 本报告 |
| CNINFO | **8** |
| allow-list | `ir_activity_known_002` + `ir_activity_known_003` + `ir_activity_sample_001` + `ir_activity_sample_002` |
| wall | offline tests + dry-run + live **26.14 s** |
| ready_for_commit | **true** |

---

## 8. 下一步（Controller）

1. 人工审阅后 **commit**（本包未 commit / 未 push）。
2. 可选：新 harvest 边角晋升 / routing；或 retrieval tooling（非 fake §7 FP）。
