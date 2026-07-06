# CNINFO D 类 Priority-1 多日期小样本稳定性复测总结

- 生成时间：2026-07-05T06:56:42Z
- 脚本：`lab/validate_cninfo_table_sources_multidate.py`
- 配置：[config/cninfo_table_sources.yaml](../../config/cninfo_table_sources.yaml)
- 前置：[cninfo_table_sources_priority1_summary.md](cninfo_table_sources_priority1_summary.md)
- 字段语义 UI 对照：[cninfo_table_field_semantics_ui_check_summary.md](cninfo_table_field_semantics_ui_check_summary.md)
- 模式：**live 小样本**

---

## 1. 目的

在 priority-1 endpoint discovery 与 UI 字段语义对照完成后，验证 5 个 **testing** source
在多个日期 / 报告期下 **endpoint 可访问性**、**records JSON path**、**字段集合** 是否保持稳定。

这是 **多日期小样本** 稳定性复测，不是全量或长期稳定性验证；**不写 verified**。

## 2. 测试范围

| source_id | 测试用例 | 参数要点 |
|-----------|----------|----------|
| disclosure_schedule | 2 | `sectionTime=2025-12-31`, `2026-06-30`; market=szsh; pagesize=20; pagenum=1 |
| restricted_shares_unlock | 3 | `tdate=2026-06-08`, `2026-07-06`, `2026-07-03` |
| block_trade | 3 | `tdate=2026-07-03`, `2026-07-02`, `2026-07-01` |
| margin_trading | 2 + 2(aux) | detailList 默认请求 ×2；market summary `tdate=2026-07-02/01`（附属） |
| abnormal_trading | 3 | `sdate=edate` 2026-07-03 / 07-02 / 07-01; page=1; rows=30 |

- **total_test_cases**：**15**
- 每个用例 **仅请求一次**，不翻页、不循环长区间。

## 3. 总体结果

### validation_status

| validation_status | 数量 |
|-------------------|------|
| sample_ok | 12 |
| empty_but_valid_response | 1 |
| http_error | 2 |

### recommended_status_after_stability（按 source，主用例）

| recommended_status_after_stability | source 数 |
|----------------------------------|-----------|
| testing_stable_sample | 5 |

## 4. 分 source 结果

### disclosure_schedule

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |
|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|
| ds_section_2025_12_31 | 200 | 20 | prbookinfos | 10 | sample_ok | no |
| ds_section_2026_06_30 | 200 | 20 | prbookinfos | 10 | sample_ok | no |

- **schema 稳定**：是 （records_path: prbookinfos）

### restricted_shares_unlock

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |
|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|
| rsu_tdate_2026_06_08 | 200 | 6 | data.records | 7 | sample_ok | no |
| rsu_tdate_2026_07_06 | 200 | 7 | data.records | 7 | sample_ok | no |
| rsu_tdate_2026_07_03 | 200 | 9 | data.records | 7 | sample_ok | no |

- **schema 稳定**：是 （records_path: data.records）

### block_trade

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |
|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|
| bt_tdate_2026_07_03 | 200 | 0 | data.records | 0 | empty_but_valid_response | no |
| bt_tdate_2026_07_02 | 200 | 54 | data.records | 7 | sample_ok | no |
| bt_tdate_2026_07_01 | 200 | 66 | data.records | 7 | sample_ok | no |

- **schema 稳定**：是 （records_path: data.records）

### margin_trading

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |
|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|
| mt_detail_default_1 | 200 | 4374 | data.records | 15 | sample_ok | no |
| mt_detail_default_2 | 200 | 4374 | data.records | 15 | sample_ok | no |
| mt_market_2026_07_02 | 500 | — | — | — | http_error | n/a |
| mt_market_2026_07_01 | 500 | — | — | — | http_error | n/a |

- **schema 稳定**：是 （records_path: data.records）

### abnormal_trading

- **recommended_status_after_stability**：**testing_stable_sample**

| test_case_id | http_status | sample_rows | records_path | field_count | validation_status | field_set_changed |
|--------------|-------------|-------------|--------------|-------------|-------------------|-------------------|
| at_2026_07_03 | 200 | 30 | marketList | 9 | sample_ok | no |
| at_2026_07_02 | 200 | 30 | marketList | 9 | sample_ok | no |
| at_2026_07_01 | 200 | 30 | marketList | 9 | sample_ok | no |

- **schema 稳定**：是 （records_path: marketList）

## 5. 发现的问题

### 空结果但结构正常（empty_but_valid_response）
- `block_trade` / `bt_tdate_2026_07_03`：records=0，records_path=`data.records`

- 本次 **未发现** 主用例 `schema_changed`。

### margin_trading 附属接口 HTTP 500

- `mt_market_2026_07_02` / `mt_market_2026_07_01`：`marginTrading/market?tdate=` 返回 **HTTP 500**。
- 该接口为 **附属观察**，非 detailList 主 source；**不影响** detailList 主用例 `testing_stable_sample` 判定。

### margin_trading 限制

- `detailList` 主接口 **不显式传 date**（`params_location=none`）；稳定性复测主要看 **两次默认请求返回结构是否一致**。
- 页面上方 `marginTrading/market?tdate=` 为 **市场汇总** 附属接口，字段语义与 detailList 不同，**不作主 source**。

## 6. 结论

- 本次为 **多日期小样本** 稳定性复测，覆盖 5 个 priority-1 testing source，**不是**全市场或长期稳定性验证。
- **不写 verified**；通过复测最多标记为 **testing_stable_sample**。
- **空结果不等于接口不可用**：`empty_but_valid_response` 表示 HTTP 200 + JSON 可解析 + records path 稳定，仅当日无数据。
- 单日期失败 **不直接否定** source，需在 summary 中结合其他日期综合判断。

## 7. 下一步

1. 对 **testing_stable_sample** source 建立 future schema draft（仍非 verified）。
2. 对 **testing_partial** source 补充日期或页面确认（如 margin_trading 日期参数、空日期解释）。
3. 进入 **priority-2 source discovery**（shareholder_change、equity_pledge 等）。
4. **暂不入库、不全量抓取**。

## 8. 边界

- 不修改原 `cninfo_table_sources_validation.csv`
- 不登录、不绕过验证码/付费；timeout ≈10s；请求间 sleep
- 不写 **verified**
