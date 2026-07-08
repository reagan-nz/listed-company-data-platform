# CNINFO C-Class dividend_history Mapper Test Summary

_生成时间：2026-07-08_

## Run mode

**fixture-only**（无 CNINFO 请求）

## Result: **10/10 PASS**

| case_id | description | result |
|---------|-------------|--------|
| `case_1_cash_only` | 纯现金分红 | **PASS** |
| `case_2_cash_and_stock` | 现金 + 送股 | **PASS** |
| `case_3_cash_and_transfer` | 现金 + 转增 | **PASS** |
| `case_4_empty_records` | 空分红记录 valid_empty | **PASS** |
| `case_5_unparseable_text` | 无法解析文本 | **PASS** |
| `case_6_ten_shares_cash_fullwidth_tax` | 10股派1元（含税） | **PASS** |
| `case_7_ten_shares_cash_halfwidth_tax` | 10股派0.5元(含税) | **PASS** |
| `case_8_per_ten_shares_cash` | 每10股派2元（含税） | **PASS** |
| `case_9_per_ten_shares_cash_bonus_long` | 每10股派发现金红利3元（含税） | **PASS** |
| `case_10_ten_shares_cash_stock_transfer` | 10股派1元（含税），送1股，转增2股 | **PASS** |

## Details

### `case_1_cash_only` — 纯现金分红

- **result:** PASS
- all checks passed

### `case_2_cash_and_stock` — 现金 + 送股

- **result:** PASS
- all checks passed

### `case_3_cash_and_transfer` — 现金 + 转增

- **result:** PASS
- all checks passed

### `case_4_empty_records` — 空分红记录 valid_empty

- **result:** PASS
- all checks passed

### `case_5_unparseable_text` — 无法解析文本

- **result:** PASS
- all checks passed

### `case_6_ten_shares_cash_fullwidth_tax` — 10股派1元（含税）

- **result:** PASS
- all checks passed

### `case_7_ten_shares_cash_halfwidth_tax` — 10股派0.5元(含税)

- **result:** PASS
- all checks passed

### `case_8_per_ten_shares_cash` — 每10股派2元（含税）

- **result:** PASS
- all checks passed

### `case_9_per_ten_shares_cash_bonus_long` — 每10股派发现金红利3元（含税）

- **result:** PASS
- all checks passed

### `case_10_ten_shares_cash_stock_transfer` — 10股派1元（含税），送1股，转增2股

- **result:** PASS
- all checks passed

## Caveats

- mapper 实现：`lab/cninfo_c_class_mappers.py` · `map_dividend_history()`
- harvest 入口：`lab/harvest_cninfo_c_class.py`（import）
- **no verified** · **no harvest execution**
