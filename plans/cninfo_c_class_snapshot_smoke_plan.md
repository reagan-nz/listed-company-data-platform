# CNINFO C-Class Snapshot Smoke Plan（10 家公司）

_生成时间：2026-07-08_

> **性质：** snapshot builder 扩展 smoke **规划 only**。本轮 **不执行** 10 家 batch build。

**前置：** [snapshot builder PoC](../lab/build_cninfo_c_class_company_snapshot.py) · demo **688750** PASS

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

---

## 1. 选择原则

| 原则 | 说明 |
|------|------|
| 不同 board | 主板 / 创业板 / 科创板 |
| 不同行业 | 金融 / 制造 / 有色 / 食品 / 医药 |
| 字段覆盖差异 | 完整 vs partial vs empty_but_valid |
| 完整公司 | harvest_status=complete 且多源齐全 |
| partial 公司 | executive empty / share_capital empty / dividend 少 |

---

## 2. 候选 10 家

| # | company_code | company_name | reason |
|---|--------------|--------------|--------|
| 1 | **688750** | 金天钛业 | **PoC demo**；科创板；有色金属；10 源齐全；已生成 snapshot |
| 2 | **000009** | 中国宝安 | 深交所主板；综合类；高管/股东/分红数据丰富；establishment_date patch 验证样本 |
| 3 | **601988** | 中国银行 | 上交所主板；金融业；normalized 覆盖评分高；大行代表 |
| 4 | **300009** | 安科生物 | 创业板；医药生物；与 688 板对照 |
| 5 | **000895** | 双汇发展 | 深交所主板；食品；dividend_history 事件多（36+）；分红模块压力 |
| 6 | **002267** | 陕天然气 | 深交所主板；**executive empty_but_valid**（jsonl 空）；partial 模块验证 |
| 7 | **601328** | 交通银行 | 上交所主板；金融；与 601988 同业对照 |
| 8 | **688981** | 中芯国际 | 科创板；半导体；大型科创板 second sample |
| 9 | **000550** | 江铃汽车 | 深交所主板；汽车；dividend 28 条；行业制造代表 |
| 10 | **301332** | 德尔玛 | 创业板；**executive empty_but_valid** + 较新上市；困难样本 |

---

## 3. 预期覆盖矩阵

| 维度 | 覆盖 |
|------|------|
| board | 主板 ×4 · 创业板 ×3 · 科创板 ×3 |
| industry | 金融 ×2 · 有色 ×1 · 食品 ×1 · 医药 ×1 · 汽车 ×1 · 综合 ×1 · 半导体 ×1 · 其他 ×1 |
| completeness | 高完整 ×7 · executive empty ×2 · dividend 丰富 ×2 |
| partial 行为 | empty_but_valid executive · source_partial share_capital（抽样观察） |

---

## 4. 执行方式（未来轮次）

```bash
# 规划命令（本轮不执行）
for code in 688750 000009 601988 300009 000895 002267 601328 688981 000550 301332; do
  python lab/build_cninfo_c_class_company_snapshot.py --write --company "$code"
done
```

**输出目录（规划）：** `outputs/snapshot/cninfo_c_class/company_snapshot_smoke/`

**验收：**

- 18 模块均存在
- `snapshot_status` 均为 `complete_with_caveat` 或 `partial`（无 blocked）
- partial / not_available 与 harvest quality 一致
- 无 schema 阻塞错误

---

## 5. Gate（规划）

```
snapshot_smoke_plan_gate = PASS
```

**本轮：** planning only · **无 batch 执行**

---

## 6. 红线

- 无 CNINFO · 无 harvest 重跑
- 不修改 raw / normalized / field_inventory
- 无 DB / MinIO / RAG · 无 verified
