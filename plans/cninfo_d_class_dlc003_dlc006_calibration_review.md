# CNINFO D 类 DLC003 / DLC006 Expectation Calibration — Detailed Review

_生成时间：2026-07-09_

> **性质：** 离线决策评审 only；**无 CNINFO** · **无 live** · **无 rerun** · **不是 schema failure 认定**

**关联输入：** [tiny live report](../outputs/validation/cninfo_d_class_tiny_live_validation/reports/d_class_tiny_live_report.csv) · [closure review](cninfo_d_class_phase1_tiny_live_closure_review.md) · [expectation calibration note](cninfo_d_class_phase1_expectation_calibration_note.md)

---

## 1. Objective

为 tiny live execution 中 **2** 个 expectation mismatch case（DLC003 · DLC006）准备人工决策包，明确：

- 观测与预期的差异性质
- 为何不是 schema / registry / quality policy 缺陷
- 各决策选项的风险与推荐默认
- v2 universe / rerun 的前置条件

**不修改** v1 execution report · **不重跑** probe · **不发明** replacement 公司代码。

---

## 2. Shared Interpretation

| 原则 | 说明 |
|------|------|
| 非 schema failure | endpoint HTTP 200 · JSON 可解析 · retrieval/quality 口径正确 |
| 非 registry failure | `liftBan/detail` · `shareholeder/detail` 与 registry 一致 |
| 主因 | **expectation mismatch / probe-window limitation** |
| v1 收口 | `d_class_phase1_tiny_live_closure_gate = PASS_WITH_CAVEAT` 保持 |

---

## 3. DLC003 — restricted_shares_unlock

### 3.1 Case Facts

| 项 | 值 |
|----|-----|
| case_id | DLC003 |
| company | 300009 安科生物 |
| component | restricted_shares_unlock |
| original expectation | `captured_normal` |
| observed | `empty_but_valid` · 0 company rows |
| endpoint | `https://www.cninfo.com.cn/data20/liftBan/detail` |
| CNINFO requests | **8** |

### 3.2 Probe Coverage

| tdate 探测 | 结果（公司级） |
|------------|----------------|
| 2026-06-08 | 0 rows |
| 2026-07-03 | 0 rows |
| 2025-12-31 | 0 rows |
| 2025-06-30 | 0 rows |
| 2024-12-31 | 0 rows |
| 2024-06-28 | 0 rows |
| 2023-12-29 | 0 rows |
| 2023-06-30 | 0 rows |

全市场在各日期可能有解禁行，但 **300009 在 8 个 tdate 内均无匹配行**。

### 3.3 Why Not Schema Failure

- API 返回结构符合 `data.records` 路径预期
- `retrieval_status=empty_but_valid` · `quality_status=pass` 与 [quality policy](cninfo_d_class_event_quality_policy.md) §4.4 一致
- field catalog / freeze v1 contract **无需修订**
- 其他组件（如 DLC004 captured）证明 pipeline 可产出 `found`

### 3.4 Why Valid Empty Behavior

解禁事件日历稀疏；公司在特定 `tdate` 窗口无解禁行是 **合法业务空态**，不应标为 `failed` 或 `http_error`。

### 3.5 Risk — Reclassify Too Early (Option A)

| 风险 | 说明 |
|------|------|
| 覆盖不足 | `restricted_shares_unlock` 组件在 tiny universe 中 **尚无** 成功 `captured_normal` 样本 |
| 回归盲区 | 若立即改为 `empty_but_valid`，未来 mapper 回归缺少 captured 路径验证 |
| 掩盖选股问题 | 可能是 300009 选股不当，而非组件常态为空 |

### 3.6 Risk — Extend Probes Too Broadly (Option B)

| 风险 | 说明 |
|------|------|
| CNINFO 负载 | 无界日期回溯导致请求数膨胀 |
| 非 tiny | 偏离 tiny live 样本定位 |
| 仍可能空 | 即使扩窗，300009 仍可能无事件 |

**缓解：** 限定最大 tdate 数 · 仅 v2 rerun 批准包内执行 · 与 Option C 并行准备。

### 3.7 Recommended Decision

**默认推荐：Option B 或 C，不立即 Option A。**

| 优先级 | 选项 | 理由 |
|--------|------|------|
| 1（并列） | **C** | 人工选定 **已知解禁事件** 公司 · 保持 `captured_normal` 预期 |
| 1（并列） | **B** | 在 v2 runner 中扩展有限 date window · 对原 300009 或 replacement 再探 |
| 3 | **A** | 仅当确认该组件 tiny 层 **仅需** empty 路径验证时再考虑 |

---

## 4. DLC006 — shareholder_change

### 4.1 Case Facts

| 项 | 值 |
|----|-----|
| case_id | DLC006 |
| company | 000550 江铃汽车 |
| component | shareholder_change |
| original expectation | `captured_normal` |
| observed | `empty_but_valid` · 0 company rows |
| endpoint | `https://www.cninfo.com.cn/data20/shareholeder/detail` |
| CNINFO requests | **5** |

### 4.2 Probe Coverage

| 参数 | 结果（公司级） |
|------|----------------|
| `type=desc` | 0 rows（全市场 ~28 行） |
| `type=inc` · tdate=2026-07-03 | 0 rows |
| `type=inc` · tdate=2025-12-31 | 0 rows |
| `type=inc` · tdate=2025-06-30 | 0 rows |
| `type=desc` · tdate=2026-07-03 | 0 rows |

### 4.3 Why Not Schema Failure

- inc/desc 双 mode API 均 HTTP 200
- 全市场有行证明 endpoint 非空壳
- `empty_but_valid` + `pass` 符合 quality policy §4.3（mode 级空态）
- shareholder_change 字段映射 **未因本 case 失败**

### 4.4 Why Valid Empty Behavior

股东增减持事件低频；000550 在探测窗口内无 inc/desc 行属 **合法空态**。

### 4.5 Risk — Reclassify Too Early (Option A)

| 风险 | 说明 |
|------|------|
| 覆盖不足 | 组件 **尚无** tiny live `captured_normal` 命中 |
| mode 混淆 | inc 空 ≠ desc 空；单一 case 改 empty 不能代表双 mode 语义 |
| 弱化 captured 测试 | 失去 shareholder_change captured 路径的 live 证据 |

### 4.6 Risk — Extend Probes Too Broadly (Option B)

| 风险 | 说明 |
|------|------|
| 请求膨胀 | 多 mode × 多日期组合 |
| 非 tiny | 需 cap 在批准包内 |
| 选股依赖 | 扩探不能替代 **已知事件** 公司（Option C） |

### 4.7 Recommended Decision

**默认推荐：Option B 或 C，不立即 Option A。**

| 优先级 | 选项 | 理由 |
|--------|------|------|
| 1（并列） | **C** | 人工选定 **已知增减持事件** 公司 |
| 1（并列） | **B** | v2 扩展有限 mode/date 探测 |
| 3 | **A** | 待至少一个 captured_normal 样本存在后再评估 |

---

## 5. Cross-case Recommendation Summary

| case | 推荐默认 | 不推荐立即 |
|------|----------|------------|
| DLC003 | **B 或 C** | **A** |
| DLC006 | **B 或 C** | **A** |

**理由（共同）：** 各组件应先获得至少 **1** 个 `captured_normal` tiny live 证据，再考虑将 expectation 稳定为 `empty_but_valid`。

---

## 6. v1 Artifact Preservation

| 项 | 政策 |
|----|------|
| execution report | **不修改** |
| live snapshots | **不修改** |
| universe v1 CSV | **保留** |
| v2 draft | 占位符 only · [universe v2 draft](../outputs/validation/cninfo_d_class_phase1_tiny_live_universe_v2_draft.csv) |

---

## 7. Gate

```text
d_class_dlc003_dlc006_calibration_gate = READY_FOR_HUMAN_DECISION
```

**不是 PASS** · **不是 approved** · **不是 live_ready** · **不是 verified**

---

## 8. Red Lines（本回合）

- No CNINFO · No live · No rerun · No harvest
- No invented company codes · No web lookup
- No DB / MinIO / RAG · No verified · No production_ready
