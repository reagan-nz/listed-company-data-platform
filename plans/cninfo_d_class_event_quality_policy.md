# CNINFO D 类 Event Quality Policy（Phase 1）

_最后更新：2026-07-09_

> **性质：** 设计口径 only；不调用 CNINFO；不入库。  
> **关联：** [cninfo_d_class_event_object_schema.md](cninfo_d_class_event_object_schema.md) · [cninfo_d_class_phase1_schema_freeze_review.md](cninfo_d_class_phase1_schema_freeze_review.md)

---

## 1. Purpose

定义 D-class Phase 1 **market_event** 的质量与检索状态口径，尤其区分：

- 真实数据缺失（**合法空态**）
- 字段语义不确定（**caveat / needs_review**）
- 源或请求失败（**failed / blocked**）

**不写 verified**；**不升级** testing_stable_sample。

---

## 2. Status Dimensions

### 2.1 retrieval_status（检索层）

描述 **HTTP/API 检索** 结果，挂在 harvest run 或 envelope `lineage` 扩展字段。

| 值 | 含义 | 典型场景 |
|----|------|----------|
| `found` | HTTP 200 · 结构符合预期 · 有 ≥1 条业务记录 | 正常命中 |
| `not_found` | HTTP 200 · 结构符合预期 · **零条**业务记录 | 见 §4 合法空态 |
| `empty_but_valid` | 同 `not_found`，但源策略认定空列表为**合法业务空态** | 当日无大宗交易等 |
| `http_error` | 非 2xx 或 CNINFO 业务错误码 | 500 · 9240002 等 |
| `blocked` | 权限/验证码/频率封禁 | 不绕过 |

**原则：** `empty_but_valid` ⊂ 语义上属于「检索成功但无行」；与 `http_error` **互斥**。

---

### 2.2 quality_status（记录/产品层）

描述 **单条 market_event 或组件 payload** 的产品可用性。

| 值 | 含义 | 下游 |
|----|------|------|
| `pass` | required 字段齐全 · 映射 confidence high | 可进 timeline |
| `caveat` | 可用但有已知缺口（单位 medium · recommended 缺失） | 可进 timeline，带 flag |
| `needs_review` | 需人工判定（映射歧义 · 非标准值） | 进 review queue |
| `blocked` | 不可用于产品（源 blocked · 结构损坏） | 不进 timeline |

**与 event_status 关系：**

| event_status | 默认 quality_status |
|--------------|---------------------|
| `captured` | pass 或 caveat |
| `empty_but_valid` | pass（空态记录）或 caveat |
| `failed` | blocked 或 needs_review |
| `pending` | —（未完成） |

---

### 2.3 lineage_status（血缘层）

描述 **来源追溯与挂接** 状态（lineage 对象或扩展）。

| 值 | 含义 |
|----|------|
| `discovered` | 已从 CNINFO 捕获 raw 行；尚未挂接 B-class 证据 |
| `linked` | 已关联 B-class `event_document_link`（**Phase 1 不实现**） |
| `needs_review` | raw 行存在但映射/哈希异常 |
| `stale` | 同一 event_id 有更新 raw 行待 reconcile（**Phase 1 仅文档化**） |

Phase 1 默认：**discovered**。

---

### 2.4 event_status（信封层）

| 值 | 含义 |
|----|------|
| `captured` | 至少一条业务字段已从 raw 映射 |
| `empty_but_valid` | 检索成功但无业务行，或行级空态合法 |
| `failed` | 检索或映射失败 |
| `pending` | dry-run / 未执行 |

---

## 3. Composite Decision Flow

```
API request
    │
    ├─ http_error / blocked ──► retrieval_status=http_error|blocked
    │                              event_status=failed
    │                              quality_status=blocked|needs_review
    │
    └─ HTTP 200 + valid JSON
            │
            ├─ records.length = 0 ──► retrieval_status=empty_but_valid
            │                          event_status=empty_but_valid
            │                          quality_status=pass (见 §4)
            │
            └─ records.length > 0 ──► per-row mapping
                    │
                    ├─ required 齐全 + high confidence ──► quality_status=pass
                    ├─ required 齐全 + medium confidence ──► quality_status=caveat
                    └─ required 缺失 / 解析失败 ──► quality_status=needs_review
```

---

## 4. 合法空态（empty_but_valid）

以下场景 **不是** endpoint 失败，**不是** `failed`，**不是** blocked：

### 4.1 无交易记录（block_trade）

- 条件：`tdate` 当日 API 返回 `data.records = []` · HTTP 200
- retrieval_status: `empty_but_valid`
- event_status: `empty_but_valid`
- quality_status: `pass`
- 说明：该公司当日无大宗交易是正常业务结果

### 4.2 无质押记录（equity_pledge）

- 条件：查询日无股权质押行
- 同上口径
- 可与公司级「无质押」筛选共存

### 4.3 无股东增减持（shareholder_change）

- 条件：`type=inc` 或 `type=desc` 返回空列表
- **须分 mode 记录**（inc 空 ≠ desc 空）
- empty_but_valid 按 **query_mode** 粒度，不混为一谈

### 4.4 无限售解禁（restricted_shares_unlock）

- 条件：`tdate` 当日无解禁行
- 合法空态；解禁日历稀疏

### 4.5 其他组件

| 组件 | 空态说明 |
|------|----------|
| margin_trading | detailList 通常全市场行；**公司级过滤后空** → empty_but_valid |
| disclosure_schedule | 某 sectionTime 下公司无预约行 → empty_but_valid |
| executive_shareholding | timeMark 窗口内无变动 → empty_but_valid |

---

## 5. needs_review 触发条件

| 场景 | 示例 |
|------|------|
| 单位不确定 | margin F00xN 万元/元歧义 |
| 非标准日期 | unlock_date 无法解析 |
| 映射冲突 | pledge_ratio 多字段候选不一致 |
| future 字段请求 | 产品要求 buyer 但 API 无字段 |
| 信封与 payload 不一致 | company_code 不匹配 |

---

## 6. failed 触发条件

| 场景 | 示例 |
|------|------|
| HTTP 非成功 | 5xx · 429 · timeout |
| JSON 结构变化 | records_path 缺失 |
| 必填映射失败 | required 字段无法从 raw 派生且非合法空态 |
| 权限/封禁 | blocked 源 |

**注意：** 合法空态 **不得** 标为 `failed`。

---

## 7. Phase 1 记录策略

### 7.1 有事件行

生成完整 `market_event` + component payload；`event_status=captured`。

### 7.2 合法空态

可选两种产品策略（signoff 时二选一，默认 **A**）：

| 策略 | 行为 |
|------|------|
| **A（推荐）** | 写 **run-level** 空态标记 + 可选 synthetic `empty_but_valid` 占位 event（无 payload 数值字段） |
| **B** | 仅 run-level 统计，不生成 per-company event 行 |

Phase 1 fixture 采用策略 A 示例：`empty_but_valid_fixture.json`（implementation 回合创建）。

### 7.3 失败

写 `quality/company_event_status.csv`（未来 harvest）或 validation report；**不** 伪造 payload。

---

## 8. 与 C-class / B-class 的边界

| 层 | 空态含义 |
|----|----------|
| C-class shareholder_profile | top-N snapshot 空 → `empty_but_valid_response`（profile 口径） |
| D-class shareholder_change | 事件流空 → 本节 §4.3 |
| B-class document | 公告 not_found ≠ D-class 市场行为空态 |

**禁止** 用 C-class profile 空结果推断 D-class event 空态。

---

## 9. QA 汇总字段（未来 harvest quality 层）

| 字段 | 说明 |
|------|------|
| `empty_but_valid_count` | 合法空态次数 |
| `needs_review_count` | 待审 |
| `failed_count` | 真失败 |
| `caveat_count` | 带 caveat 行数 |

Phase 1 **不生成** harvest quality 文件；仅政策文档化。

---

## 10. Red Lines

- **No verified**
- **No testing_stable_sample upgrade**
- **empty_but_valid ≠ failed**
- **No CNINFO**（本政策仅设计）
