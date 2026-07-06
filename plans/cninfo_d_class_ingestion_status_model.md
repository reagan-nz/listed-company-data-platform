# CNINFO D 类 Ingestion Status Model 草案

_最后更新：2026-07-05_

> **性质：** 状态机与枚举定义草案，指导 validation、未来采集与 registry 更新。  
> **关联：** [cninfo_d_class_source_registry_design.md](cninfo_d_class_source_registry_design.md) · [cninfo_d_class_schema_draft.md](cninfo_d_class_schema_draft.md)

---

## 1. 目的

Phase 2 验证产生了多层结论：source 是否可用、单次 fetch 是否成功、字段是否确认、schema 是否稳定。需要 **统一状态模型**，避免：

- 把 `empty_but_valid_response` 误判为 source 失败；
- 把正文关键词误判为 `blocked`；
- 把 `testing_stable_sample` 误写为 `verified`。

本模型定义四类状态：**source**、**fetch**、**field**、**schema stability**。

---

## 2. source status

描述 **source 作为数据入口** 的综合生命周期状态（registry `recommended_status`）。

| 值 | 含义 |
|----|------|
| `candidate` | endpoint 未确认；或仅 page 可达 |
| `testing` | 小样本 `sample_ok`；未完成稳定性复测 |
| `testing_stable_sample` | 多日期/多参数稳定性通过；field set / records path 稳定 |
| `testing_partial` | 部分用例 OK，部分失败或结构不一致 |
| `testing_needs_more_review` | 出现 schema_changed 或需人工裁定 |
| `blocked` | 确认需登录/验证码/付费，无法公开获取 |
| `deprecated` | endpoint 废弃或 CNINFO 改版不可用 |

### 禁止使用

| 值 | 说明 |
|----|------|
| ~~`verified`~~ | **Era C 红线：当前禁止使用** |

### 当前 10 源快照

| source_id | source status |
|-----------|---------------|
| disclosure_schedule | testing_stable_sample |
| restricted_shares_unlock | testing_stable_sample |
| block_trade | testing_stable_sample |
| margin_trading | testing_stable_sample |
| abnormal_trading | testing_stable_sample |
| equity_pledge | testing_stable_sample |
| shareholder_change | testing_stable_sample |
| executive_shareholding | testing_stable_sample |
| fund_industry_allocation | testing_stable_sample |
| shareholder_data | testing_stable_sample |

### config candidate（未验证）

| source_id | source status |
|-----------|---------------|
| ipo_query | candidate |
| szse_calendar | candidate |

---

## 3. fetch status

描述 **单次 HTTP 请求 / test case** 结果（validation CSV `validation_status`、未来采集 run）。

| 值 | 含义 |
|----|------|
| `success` | HTTP 200 + JSON 可解析 + records 有数据 + 结构符合预期 |
| `empty_but_valid_response` | HTTP 200 + JSON 可解析 + records path 稳定 + **records=0** |
| `http_error` | 非 200（如 500） |
| `parse_error` | 非 JSON 或 JSON 解析失败 |
| `blocked` | 确认权限拦截 |
| `timeout` | 请求超时 |
| `schema_changed` | records path 或 field set 相对 baseline 变化 |
| `unknown_error` | 网络异常等 |

### 与 validation 脚本对齐

| 脚本 validation_status | 映射 fetch status |
|------------------------|-------------------|
| `sample_ok` | `success` |
| `empty_but_valid_response` | `empty_but_valid_response` |
| `http_error` | `http_error` |
| `parse_error` | `parse_error` |
| `blocked` | `blocked` |
| `schema_changed` | `schema_changed` |
| `unknown_error` | `unknown_error` |

---

## 4. field status

描述 **单个 raw field** 语义确认程度（registry / `d_field_semantics.confirmation_status`）。

| 值 | 含义 |
|----|------|
| `ui_confirmed` | 人工 UI 表头对照通过 |
| `candidate` | 有候选语义，待 UI 或校验 |
| `not_visible_on_ui` | 接口返回，UI 明细无列 |
| `uncertain` | 多义或证据不足 |
| `internal_text` | 接口内部文本（如 equity_pledge F008V） |

**规则：** 仅 `ui_confirmed` 应进入标准 schema 主列映射；其余保留在 `raw_record_json`。

---

## 5. schema stability status

描述 **同一 source 跨多个 test case** 的结构稳定性（stability 跑次聚合）。

| 值 | 含义 |
|----|------|
| `stable_sample` | 所有主用例 success 或 empty_but_valid；path + field set 一致 |
| `partial_sample` | 混合 OK 与错误；或 field set 多签名 |
| `changed` | 出现 schema_changed |
| `unknown` | 未跑稳定性或未足够样本 |

### 与 source status 关系

| schema stability | 典型 source status |
|------------------|-------------------|
| `stable_sample` | `testing_stable_sample` |
| `partial_sample` | `testing_partial` |
| `changed` | `testing_needs_more_review` |
| `unknown` | `testing` 或 `candidate` |

---

## 6. empty_but_valid_response 解释

**定义：** 同时满足：

1. HTTP **200**
2. 响应为 **可解析 JSON**
3. **records path 稳定**（如 `data.records` 存在且路径不变）
4. **records 数组长度为 0**

**含义：** 该日期/参数下 **无业务数据**，不是 endpoint 故障。

### Phase 2 观测实例

| source | test case | 说明 |
|--------|-----------|------|
| block_trade | tdate=2026-07-03 | 非交易日或无大宗交易 |
| equity_pledge | tdate=2026-07-03 | 当日无质押公告 |
| fund_industry_allocation | rdate=20251231 | 该报告期无行业配置数据 |

**聚合规则：** 若同一 source 其他 test case 为 `success` 且 field set 一致，source 仍可标 `testing_stable_sample`。

---

## 7. blocked 判断原则

### 应判 blocked

- 响应明确要求登录、验证码、付费权限；
- HTTP 403 / 401 且业务上不可公开访问；
- 跳转商业 API 域名且无法匿名访问。

### 不应误判 blocked

| 情况 | 正确处理 |
|------|----------|
| JSON `code=200` 且 `data.records` 有数据 | **success**，即使 body 其他位置含「商业」等词 |
| HTML 页面脚本文案含关键词 | 若 API JSON 正常，**不**判 blocked |
| 空 records | `empty_but_valid_response`，非 blocked |

**实现参考：** `validate_cninfo_table_sources.py` 在 `code=200` 且 records 非空时 **跳过** 正文 blocked 关键词检测。

---

## 8. 状态流转图

### source status 流转（文字）

```
candidate
  ├─(endpoint discovery + sample_ok)──> testing
  ├─(权限拦截)────────────────────────> blocked
  └─(长期未用)────────────────────────> deprecated

testing
  ├─(稳定性通过)──────────────────────> testing_stable_sample
  ├─(部分用例失败)────────────────────> testing_partial
  ├─(schema_changed)──────────────────> testing_needs_more_review
  └─(权限拦截)──────────────────────> blocked

testing_stable_sample
  ├─(CNINFO 改版不可用)──────────────> deprecated
  └─(结构漂移)──────────────────────> testing_needs_more_review

testing_partial / testing_needs_more_review
  └─(补充验证通过)──────────────────> testing_stable_sample
```

### fetch status 不直接升级 source

单次 `empty_but_valid_response` **不**降级 source；需结合多 case 聚合（见 §5）。

### verified 不在流转图中

**任何状态不得流转到 `verified`**（当前 Era C 禁止）。

---

## 9. 当前 10 源状态快照

| source_id | source status | schema stability | 典型 fetch 结果 | field 语义 |
|-----------|---------------|------------------|-----------------|------------|
| disclosure_schedule | testing_stable_sample | stable_sample | success | 多数 ui_confirmed；latest_time candidate |
| restricted_shares_unlock | testing_stable_sample | stable_sample | success | ui_confirmed |
| block_trade | testing_stable_sample | stable_sample | success + empty_but_valid | ui_confirmed |
| margin_trading | testing_stable_sample | stable_sample | success | mixed；F003N 等 candidate |
| abnormal_trading | testing_stable_sample | stable_sample | success | ui_confirmed + detail 嵌套 |
| equity_pledge | testing_stable_sample | stable_sample | success + empty_but_valid | F008V internal_text |
| shareholder_change | testing_stable_sample | stable_sample | success（inc/desc） | ui_confirmed |
| executive_shareholding | testing_stable_sample | stable_sample | success（3 modes） | 11 ui_confirmed + not_visible/uncertain |
| fund_industry_allocation | testing_stable_sample | stable_sample | success + empty_but_valid | ui_confirmed |
| shareholder_data | testing_stable_sample | stable_sample | success（3 rdate） | ui_confirmed |

### 稳定性跑次汇总

| 批次 | total cases | success | empty_but_valid | schema_changed | blocked |
|------|-------------|---------|-----------------|----------------|---------|
| Priority-1 multidate | 15 | 12 | 1 | 0 | 0 |
| Priority-2 multi-param | 15 | 13 | 2 | 0 | 0 |

---

## 10. 后续使用

| 场景 | 使用方式 |
|------|----------|
| validation 脚本输出 | fetch status → 写入 `d_source_validation_run` |
| registry 更新 | 聚合 fetch + schema stability → source status |
| 采集调度 | 仅 `testing_stable_sample` source 进入 pilot fetch |
| 告警 | `schema_changed` / 连续 `http_error` 触发 drift review |
| 产品展示 | field status 控制哪些列可对用户可见 |

**当前：** 状态仅文档化 + 与现有 CSV/MD 对齐；**不**实现状态机服务。

---

## 11. 边界

- 不入库；不写 migration
- 不写 **verified**
- `testing_stable_sample` ≠ 生产就绪 ≠ 全市场稳定
