# CNINFO D 类 Priority-2 多参数稳定性复测总结

- 生成时间：2026-07-05T07:29:52Z
- 脚本：`lab/validate_cninfo_table_sources_priority2_stability.py`
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- 前置：[cninfo_table_sources_priority2_current_summary.md](cninfo_table_sources_priority2_current_summary.md)
- 字段语义 UI 对照：[cninfo_table_field_semantics_priority2.md](cninfo_table_field_semantics_priority2.md)
- 模式：**live 小样本**

---

## 1. 目的

本阶段验证 priority-2 五个 **testing** source 在多个日期 / 参数组合下
**endpoint 可访问性**、**records JSON path**、**字段集合** 是否保持稳定。

这是 **多参数小样本** 稳定性复测，不是全量或长期稳定性验证；**不写 verified**。

## 2. 测试范围

| source_id | 测试用例数 | 参数要点 |
|-----------|------------|----------|
| equity_pledge | 3 | `tdate=2026-07-03`, `2026-07-02`, `2026-07-01` |
| shareholder_change | 3 | `type=inc,tdate=2026-07-03`; `type=desc`; `type=desc,tdate=2026-07-03` |
| executive_shareholding | 3 | `oneMonth+b`; `threeMonth+b`; `oneMonth+s` |
| fund_industry_allocation | 3 | 默认请求；`rdate=20260331`; `rdate=20251231` |
| shareholder_data | 3 | `rdate=20260331`, `20251231`, `20250930` |

- **total_test_cases**：**15**
- 每个用例 **仅请求一次**，不翻页、不循环长区间。

## 3. 总体结果

### validation_status

| validation_status | 数量 |
|-------------------|------|
| sample_ok | 13 |
| empty_but_valid_response | 2 |

### recommended_status_after_stability（按 source）

| recommended_status_after_stability | source 数 |
|----------------------------------|-----------|
| testing_stable_sample | 5 |

## 4. 分 source 结果

### equity_pledge

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | field_count | records_path | validation_status | field_set_changed |
|--------------|-------------|-------------|-------------|--------------|-------------------|-------------------|
| ep_tdate_2026_07_03 | 200 | 0 | 0 | data.records | empty_but_valid_response | no |
| ep_tdate_2026_07_02 | 200 | 68 | 10 | data.records | sample_ok | no |
| ep_tdate_2026_07_01 | 200 | 82 | 10 | data.records | sample_ok | no |

- **records path 稳定**：是 （data.records）
- **field set 稳定**：是

### shareholder_change

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | field_count | records_path | validation_status | field_set_changed |
|--------------|-------------|-------------|-------------|--------------|-------------------|-------------------|
| sc_inc_tdate_2026_07_03 | 200 | 3 | 8 | data.records | sample_ok | no |
| sc_desc_no_tdate | 200 | 16 | 8 | data.records | sample_ok | no |
| sc_desc_tdate_2026_07_03 | 200 | 16 | 8 | data.records | sample_ok | no |

- **records path 稳定**：是 （data.records）
- **field set 稳定**：是

### executive_shareholding

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | field_count | records_path | validation_status | field_set_changed |
|--------------|-------------|-------------|-------------|--------------|-------------------|-------------------|
| esh_oneMonth_varyType_b | 200 | 842 | 16 | data.records | sample_ok | no |
| esh_threeMonth_varyType_b | 200 | 1862 | 16 | data.records | sample_ok | no |
| esh_oneMonth_varyType_s | 200 | 824 | 16 | data.records | sample_ok | no |

- **records path 稳定**：是 （data.records）
- **field set 稳定**：是

### fund_industry_allocation

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | field_count | records_path | validation_status | field_set_changed |
|--------------|-------------|-------------|-------------|--------------|-------------------|-------------------|
| fia_default | 200 | 19 | 6 | data.records | sample_ok | no |
| fia_rdate_20260331 | 200 | 19 | 6 | data.records | sample_ok | no |
| fia_rdate_20251231 | 200 | 0 | 0 | data.records | empty_but_valid_response | no |

- **records path 稳定**：是 （data.records）
- **field set 稳定**：是

### shareholder_data

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | field_count | records_path | validation_status | field_set_changed |
|--------------|-------------|-------------|-------------|--------------|-------------------|-------------------|
| sd_rdate_20260331 | 200 | 5255 | 9 | data.records | sample_ok | no |
| sd_rdate_20251231 | 200 | 5211 | 9 | data.records | sample_ok | no |
| sd_rdate_20250930 | 200 | 5204 | 9 | data.records | sample_ok | no |

- **records path 稳定**：是 （data.records）
- **field set 稳定**：是

## 5. 分层说明

### company-level source

- `equity_pledge` — 股权质押
- `shareholder_change` — 股东增减持（inc / desc）
- `executive_shareholding` — 高管持股变动明细
- `shareholder_data` — 股东人数 / 人均持股定期数据

### industry-level aggregate

- `fund_industry_allocation` — 基金行业配置（行业级聚合表）
- **不要**将 `fund_industry_allocation` 归入 company event schema
- 稳定性判断 **不要求** `company_code_available=yes`

## 6. 发现的问题

### 空结果但结构正常（empty_but_valid_response）
- `equity_pledge` / `ep_tdate_2026_07_03`：records=0，records_path=`data.records`
- `fund_industry_allocation` / `fia_rdate_20251231`：records=0，records_path=`data.records`

- 本次 **未发现** `schema_changed`。

### 参数敏感性观察

- **equity_pledge**：`tdate=2026-07-03` 返回 **0** 行（`empty_but_valid_response`）；`2026-07-02` **68** 行、`2026-07-01` **82** 行，字段 10 列稳定。接口对交易日敏感，空日不等于结构异常。
- **shareholder_change**：`type=desc` 不传 `tdate` 与 `type=desc,tdate=2026-07-03` 均 **16** 行、8 字段一致；`type=inc,tdate=2026-07-03` **3** 行。`type=desc` 稳定，勿用 `type=dec`。
- **executive_shareholding**：`oneMonth+varyType=b` **842** 行；`threeMonth+b` **1862** 行；`oneMonth+varyType=s` **824** 行。三种组合均 HTTP 200、16 字段、`data.records` 稳定；`varyType=s` 接口支持，语义待 UI 确认。
- **fund_industry_allocation**：默认与 `rdate=20260331` 均 **19** 行；`rdate=20251231` **0** 行（`empty_but_valid_response`）。`rdate` 可传但部分报告期无数据。
- **shareholder_data**：`rdate=20260331` **5255**、`20251231` **5211**、`20250930` **5204** 行，9 字段稳定；行数随报告期变化属预期。

## 7. 结论

- 本次为 **多参数小样本** 稳定性复测，覆盖 5 个 priority-2 testing source。
- **不写 verified**；通过复测最多标记为 **testing_stable_sample**。
- 该阶段仍 **不是** 生产化验证或全市场稳定性结论。
- **空结果不等于接口不可用**：`empty_but_valid_response` 表示 HTTP 200 + JSON 可解析 + records path 稳定。

### 各 source 稳定性判定

- **equity_pledge** → `testing_stable_sample`
- **shareholder_change** → `testing_stable_sample`
- **executive_shareholding** → `testing_stable_sample`
- **fund_industry_allocation** → `testing_stable_sample`
- **shareholder_data** → `testing_stable_sample`

## 8. 下一步

1. 若五源稳定，priority-2 当前批次可收口。
2. 进入下一批 discovery：`ipo_query`、`szse_calendar`、`executive_shareholding_summary`、`fund_stock_holding`。
3. **暂不入库、不全量抓取**；不写 verified。

## 9. 边界

- 不修改原 `cninfo_table_sources_validation.csv`
- 不修改 priority-1 summary
- 不登录、不绕过验证码/付费；timeout ≈10s；请求间 sleep
- 不写 **verified**
