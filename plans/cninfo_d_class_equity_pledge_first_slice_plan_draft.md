# CNINFO D 类 equity_pledge First-Slice Plan Draft

_生成时间：2026-07-10_

> **性质：** Era D 离线第一切片草案 only · **CNINFO calls = 0** · **无 live** · **approval_status = NOT_APPROVED**

---

## 1. Component Definition

| 项 | 值 |
|----|-----|
| component | `equity_pledge` |
| source_layer | `company_event` |
| target_logical_table | `d_company_event`（metadata only） |
| endpoint | `https://www.cninfo.com.cn/data20/equityPledge/list` |
| registry path | `equity_pledge/equityPledge/list`（[registry draft](../config/cninfo_d_class_source_registry_draft.yaml)） |
| query mode | **`tdate_daily`** |
| method | POST |
| params_location | query |
| records_path | `data.records` |
| date_param | **`tdate`**（公告日锚点 · 全宇宙共享） |

### Endpoint Notes

- **主端点：** `equityPledge/list` — 按 `tdate` 返回当日股权质押记录列表
- **公司过滤：** 响应行以 `SECCODE` / `SECNAME` 匹配 universe `company_code`
- **单 tdate 模式：** 无 RSU-style multi-probe 窗口；每案预期 **1** 请求（cap 设计仍保留 per-case ≤4 余量）
- **字段映射（registry）：** `F001V` pledgor · `F003V` pledgee · `F006N` pledged_shares · `F007N` pledge_ratio · `F018N` cumulative_pledge_ratio
- **Phase1 先例：** DLC005（688981 中芯国际）→ calibrated **`empty_but_valid`**（稀疏查询日合法零行）

---

## 2. Approval Status

| 项 | 值 |
|----|-----|
| component approval phrase | **I approve D-class equity_pledge as the next Era D component.** |
| approval status | **NOT APPROVED** |
| live approval | **NOT APPROVED** |
| runner approval | **NOT APPROVED**（`--equity-pledge-first-slice` **未实现**） |

---

## 3. Universe Sketch

| 项 | 值 |
|----|-----|
| universe size | **5** companies |
| case_id scheme | **DEP001–DEP005** |
| sketch CSV | [cninfo_d_class_equity_pledge_first_slice_universe_draft_sketch.csv](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_universe_draft_sketch.csv) |
| formal universe | **锁定于后续 approval package** |

### Proposed Anchor `tdate` Policy（离线文档化）

- 全案例共享 **单一** `tdate = 2026-07-03`
- 依据：registry `default_params.tdate` 与 Phase1 registry `empty_but_valid_notes`（该日 records=0 先例）
- **本任务不调用 CNINFO** 验证该日是否有质押行；稀疏日零行属 **可接受** 结果

### Exclusions (primary cases)

| 排除 | 原因 |
|------|------|
| **688671**（DLC003R 碧兴物联） | known-event 主案例 · **不作第一切片主案例** |
| **301259**（DLC006R 艾布鲁） | known-event 主案例 · **不作第一切片主案例** |

DEP001 引用 DLC005（688981 中芯国际）Phase1 **acceptable · empty_but_valid** 先例，使用 **独立 DEP case_id**。

---

## 4. Expected Behavior Mix（吸收 RSU / block_trade 教训）

| 语义 | 说明 |
|------|------|
| `empty_but_valid` | 公司级零行 · 稀疏查询日合法空态（DLC005 先例） |
| `captured_normal_or_empty_but_valid` | **默认推荐** — found 或 empty 均可 acceptable |
| `captured_normal_or_needs_review` | found 可接受；字段映射不确定时 `needs_review` + ledger caveat |

**禁止：** sole `captured_normal_candidate` 绑定可能稀疏的单一 anchor（block_trade DBT002 · RSU 规划教训）。

---

## 5. Request Budget (future live)

| 项 | 值 |
|----|-----|
| per-case requests | **≤ 4**（单 tdate 预期 1 · 余量保留） |
| total cap | **≤ 20** CNINFO requests |
| planned (5-case) | **~5**（单请求/案） |
| early_stop | per-case 命中公司行后停止（若实现） |
| sleep default | 0.6s（与 prior slices 一致 · 未来 live 规划值） |

---

## 6. Success Criteria (future live)

| 项 | 标准 |
|----|------|
| acceptable threshold | **≥ 3/5** cases acceptable |
| execution gate | **`PASS_WITH_CAVEAT`**（若 ≥3/5）· **不是 bare PASS** |
| scope | metadata / structured-table only |
| raw lineage | retain snapshot JSON · no DB/MinIO/RAG |

**不使用：** PASS · verified · production_ready · testing_stable_sample

---

## 7. Output Root & Flags（future）

| 项 | 值 |
|----|-----|
| output root | `outputs/validation/cninfo_d_class_equity_pledge_first_slice/` |
| mode flag | `--equity-pledge-first-slice` |
| approval flag | `--approve-d-class-equity-pledge-first-slice` |

**本任务不实现 runner extension。**

---

## 8. Closed Tracks（不得重开）

| Track | Commit / Gate |
|-------|---------------|
| restricted_shares_unlock | **`aa087b5`** · `PASS_WITH_CAVEAT` · **NOT pushed** |
| block_trade | **`403472d`** · `PASS_WITH_CAVEAT` · **NOT verified** |
| margin_trading | **`116f875`** |
| disclosure_schedule | **`d37ce0a`** |
| known-event | **`389cd9c`** |

---

## 9. Next Step

Human approve component → **equity_pledge first-slice approval package**（formal universe · checklist · command draft · **无 CNINFO**）
