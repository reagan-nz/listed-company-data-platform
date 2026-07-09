# CNINFO D 类 Phase 1 — Universe Expectation Calibration Note

_生成时间：2026-07-09_

> **性质：** 离线决策记录 only；**不修改** universe CSV · **不重跑** live · **不是 schema failure 认定**

**关联：** [tiny live closure review](cninfo_d_class_phase1_tiny_live_closure_review.md) · [closure summary](../outputs/validation/cninfo_d_class_phase1_tiny_live_closure_summary.md)

---

## 1. Purpose

记录 DLC003 / DLC006 在 tiny live execution 中的 **expected_behavior 与观测结果不一致** 问题，供后续人工选择校准路径。

**共同结论：** API 可用 · 质量口径正确 · **probe 窗口 / universe 选股与预期不匹配**。

---

## 2. DLC003 — restricted_shares_unlock

| 项 | 内容 |
|----|------|
| case_id | DLC003 |
| company | 300009 安科生物 |
| universe 预期 | `captured_normal` |
| 观测 | `empty_but_valid` · 0 rows · **8** tdate probes |
| endpoint | `data20/liftBan/detail` |
| CNINFO requests（本 case） | 8 |

### 观测说明

- 各探测日期 API 返回 HTTP 200 · JSON 结构正常
- 全市场可能有解禁行，但 **300009 在探测日期集合内无公司级行**
- `retrieval_status=empty_but_valid` · `quality_status=pass` 符合 [quality policy](cninfo_d_class_event_quality_policy.md) §4.4

### 决策选项

| 选项 | 描述 | 影响 |
|------|------|------|
| **A** | 将 `expected_behavior` 重分类为 `empty_but_valid` | universe CSV 修订 · 与 live 观测对齐 |
| **B** | 未来回合扩展 date window probing（更多 tdate / 日历回溯） | runner 增强 · 可能找到 captured 行 |
| **C** | 替换 universe case 为 **已知有解禁事件** 的公司代码 | 新 tiny case · 保持 captured_normal 预期 |

### 推荐（本回合）

**不视为 schema failure。** 记为 **universe expectation mismatch / probe-window limitation**；选项 **A 或 C** 供人工后续选择，**本回合不执行**。

---

## 3. DLC006 — shareholder_change

| 项 | 内容 |
|----|------|
| case_id | DLC006 |
| company | 000550 江铃汽车 |
| universe 预期 | `captured_normal` |
| 观测 | `empty_but_valid` · 0 rows · **5** mode probes |
| endpoint | `data20/shareholeder/detail` |
| CNINFO requests（本 case） | 5 |

### 探测模式

- `type=desc`（无 tdate）
- `type=inc` + tdate=2026-07-03 / 2025-12-31 / 2025-06-30
- `type=desc` + tdate=2026-07-03

### 观测说明

- API 返回全市场增减持行（desc 模式约 28 行）
- **000550 在所有探测参数下无公司级匹配行**
- 合法空态语义正确 · 与 `captured_normal` 预期不符

### 决策选项

| 选项 | 描述 | 影响 |
|------|------|------|
| **A** | 将 `expected_behavior` 重分类为 `empty_but_valid` | universe CSV 修订 |
| **B** | 未来回合扩展 mode/date probing（更长历史 inc/desc） | runner 增强 |
| **C** | 替换 universe case 为 **已知有增减持事件** 的公司代码 | 新 tiny case |

### 推荐（本回合）

**不视为 schema failure。** 记为 **universe expectation mismatch / probe-window limitation**；选项 **A 或 C** 供人工后续选择，**本回合不执行**。

---

## 4. Cross-case Summary

| 类型 | cases | 处理 |
|------|-------|------|
| 预期命中 acceptable | DLC001 · DLC002 · DLC004 · DLC005 · DLC007 | closure 确认 |
| 预期不符 · API 正常 | DLC003 · DLC006 | 本文档记录 · 非 schema 修订 |
| 需未来校准 | DLC003 · DLC006 | 人工选择 A/B/C |

---

## 5. Non-actions（本回合红线）

- 不修改 [cninfo_d_class_phase1_tiny_live_universe.csv](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe.csv)
- 不修改 execution report 行
- 不 rerun CNINFO
- 不写 verified · 不标 production_ready
