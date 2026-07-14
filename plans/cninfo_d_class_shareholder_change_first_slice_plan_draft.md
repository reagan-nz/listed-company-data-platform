# CNINFO D 类 shareholder_change First-Slice Plan Draft

_生成时间：2026-07-13_

> **性质：** Era D 离线第一切片草案 only · **CNINFO calls = 0** · **无 live** · **approval_status = NOT_APPROVED**

---

## 1. Component Definition

| 项 | 值 |
|----|-----|
| component | `shareholder_change` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（metadata only） |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| registry path | `shareholder_change/shareholeder/detail`（[registry draft](../config/cninfo_d_class_source_registry_draft.yaml)） |
| query mode | **`type_inc` + `tdate_daily`**（first-slice sketch · 单 `type=inc`） |
| method | POST |
| params_location | query |
| records_path | `data.records` |
| date_param | **`tdate`**（公告日锚点 · 全宇宙共享） |
| type_param | **`type=inc`**（增持模式 · first-slice 默认；`desc` 留待扩展） |

### Endpoint Notes

- **主端点：** `shareholeder/detail` — CNINFO 注册拼写为 **`shareholeder`**（**不修正** path）
- **公司过滤：** 响应行以 `SECCODE` / `SECNAME` 匹配 universe `company_code`
- **模式：** `type=inc`（增持）或 `type=desc`（减持 · **不是** `dec`）
- **first-slice 简化：** 全宇宙共享 `type=inc` + 单一 `tdate` · 每案预期 **1** 请求
- **字段映射（registry）：** `F002V` shareholder_name · `F004N` share_change_amount · `F005N` share_change_ratio_percent · `F007V` share_change_price
- **Phase1 先例：** DLC006（000550 江铃汽车）→ dry-run **`captured_normal`** 规划口径 · calibrated live **`empty_but_valid`** on sparse anchor

---

## 2. Approval Status

| 项 | 值 |
|----|-----|
| component approval phrase | **I approve D-class shareholder_change as the next Era D component.** |
| approval status | **NOT APPROVED** |
| live approval | **NOT APPROVED** |
| runner approval | **NOT APPROVED**（`--shareholder-change-first-slice` **未实现**） |

---

## 3. Universe Sketch

| 项 | 值 |
|----|-----|
| universe size | **5** companies |
| case_id scheme | **DSC001–DSC005** |
| sketch CSV | [cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv](../outputs/validation/cninfo_d_class_shareholder_change_first_slice_universe_draft_sketch.csv) |
| formal universe | **锁定于后续 approval package** |

### Proposed Anchor `tdate` Policy（离线文档化）

- 全案例共享 **单一** `tdate = 2026-07-03`
- 全案例共享 **`type = inc`**
- 依据：registry `default_params`（`type: inc` · `tdate: 2026-07-03`）
- **本任务不调用 CNINFO** 验证该日是否有增减持行；稀疏日零行属 **可接受** 结果

### Exclusions (primary cases)

| 排除 | 原因 |
|------|------|
| **688671**（DLC003R 碧兴物联） | known-event 主案例 · **不作第一切片主案例** |
| **301259**（DLC006R 艾布鲁） | known-event 主案例 · DLC006R gap baggage · **不作第一切片主案例** |

DSC001 引用 DLC006（000550 江铃汽车）Phase1 先例，使用 **独立 DSC case_id** · **不是** DLC006R 代理。

---

## 4. Expected Behavior Mix（吸收 RSU / block_trade / equity_pledge 教训）

| 语义 | 说明 |
|------|------|
| `empty_but_valid` | 公司级零行 · 稀疏查询日合法空态 |
| `captured_normal_or_empty_but_valid` | **默认推荐** — found 或 empty 均可 acceptable |
| `captured_normal_or_needs_review` | found 可接受；字段映射不确定时 `needs_review` + ledger caveat |

**禁止：**

- sole `captured_normal_candidate` 绑定可能稀疏的单一 anchor（DBT002 教训）
- 单独 fragile `captured_normal_or_needs_review` 无混排（DEP004 教训）
- disclosure-only 证据升级为 captured_normal（DLC006R 教训）

---

## 5. Proposed Universe Rows（sketch）

| case_id | company_code | company_name | market | expected_behavior | notes |
|---------|--------------|--------------|--------|-------------------|-------|
| DSC001 | 000550 | 江铃汽车 | szse_main | captured_normal_or_empty_but_valid | DLC006 precedent; distinct DSC case_id |
| DSC002 | 000895 | 双汇发展 | szse_main | captured_normal_or_empty_but_valid | SZSE active; cross-slice reuse |
| DSC003 | 600000 | 浦发银行 | sse_main | captured_normal_or_empty_but_valid | SSE financial |
| DSC004 | 002415 | 海康威视 | szse_main | captured_normal_or_needs_review | field mapping review if found |
| DSC005 | 601988 | 中国银行 | sse_main | empty_but_valid | sparse-day control; board diversity |

---

## 6. Request Budget (future live)

| 项 | 值 |
|----|-----|
| per-case requests | **≤ 4**（单 type+tdate 预期 1 · 余量保留） |
| total cap | **≤ 20** CNINFO requests |
| planned (5-case) | **~5**（单请求/案） |
| early_stop | per-case 命中公司行后停止（若实现） |
| sleep default | 0.6s（与 prior slices 一致 · 未来 live 规划值） |

---

## 7. Success Criteria (future live)

| 项 | 标准 |
|----|------|
| acceptable threshold | **≥ 3/5** cases acceptable |
| execution gate | **`PASS_WITH_CAVEAT`**（若 ≥3/5）· **不是 bare PASS** |
| scope | metadata / structured-table only |
| raw lineage | retain snapshot JSON · no DB/MinIO/RAG |

**不使用：** PASS · verified · production_ready · testing_stable_sample

---

## 8. Output Root & Flags（future）

| 项 | 值 |
|----|-----|
| output root | `outputs/validation/cninfo_d_class_shareholder_change_first_slice/` |
| mode flag | `--shareholder-change-first-slice` |
| approval flag | `--approve-d-class-shareholder-change-first-slice` |

**本任务不实现 runner extension。**

---

## 9. Closed Tracks（不得重开）

| Track | Commit / Gate |
|-------|---------------|
| equity_pledge | **`85abad0`** · `PASS_WITH_CAVEAT` · **NOT pushed** |
| restricted_shares_unlock | **`aa087b5`** · `PASS_WITH_CAVEAT` · **NOT pushed** |
| block_trade | **`403472d`** · `PASS_WITH_CAVEAT` · **NOT verified** |
| margin_trading | **`116f875`** |
| disclosure_schedule | **`d37ce0a`** |
| known-event | **`389cd9c`** |

---

## 10. Next Step

Human approve component → **shareholder_change first-slice approval package**（formal universe · checklist · command draft · **无 CNINFO**）
