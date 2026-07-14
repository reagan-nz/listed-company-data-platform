# 公司画像试点填充摘要（000009）

_生成时间：2026-07-10T07:36:37Z_

## 试点公司

- company_code：**000009**（中国宝安）
- 产出目录：`outputs/portrait/companies/000009/`

## 填充统计

- fact 条数：**36**
- evidence_ref 条数：**13**
- 覆盖矩阵回写行数：**1**

## 按模块

| 模块 | fact 条数 | 状态 |
|------|-----------|------|
| M01 | 3 | testing/partial |
| M07 | 8 | testing/partial |
| M08 | 10 | testing/partial |
| M09 | 15 | testing/partial |

## 映射缺口

- M01 缺少 `company_basic_profile` normalized 文件，身份字段仅能从股本/高管交叉填充
- M01 法定代表人、注册地址、上市日期等需补 basic harvest
- M04 财务数值未填（保持 not_modeled，等 PDF 闸门）
- M13/M14 未填（依赖 B/D 轨道产物）

## Gate

- `portrait_p3_pilot_gate` — 每条 fact 均有 evidence_ref_id
- 无 live · 无 PDF · 无 DB · 无 `verified`
