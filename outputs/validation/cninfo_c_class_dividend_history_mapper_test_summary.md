# CNINFO C-Class dividend_history Mapper Test Summary

_生成时间：2026-07-07_

## Run mode

**fixture-only**（无 CNINFO 请求）

## Result: **5/5 PASS**

| case_id | description | result |
|---------|-------------|--------|
| `case_1_cash_only` | 纯现金分红 | **PASS** |
| `case_2_cash_and_stock` | 现金 + 送股 | **PASS** |
| `case_3_cash_and_transfer` | 现金 + 转增 | **PASS** |
| `case_4_empty_records` | 空分红记录 valid_empty | **PASS** |
| `case_5_unparseable_text` | 无法解析文本 | **PASS** |

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

## Caveats

- mapper 实现：`lab/cninfo_c_class_mappers.py` · `map_dividend_history()`
- harvest 入口：`lab/harvest_cninfo_c_class.py`（import）
- **no verified** · **no harvest execution**
