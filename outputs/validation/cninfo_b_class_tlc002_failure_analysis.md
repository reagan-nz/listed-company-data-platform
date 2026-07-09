# TLC002 Failure Analysis — B-class Tiny Live Validation

_生成时间：2026-07-09_

> **性质：** 离线 QA 分诊；**无 CNINFO** · **无 live 重跑** · **未修改** raw_metadata / quality 产物

---

## Case Summary

| 项 | 值 |
|----|------|
| case_id | **TLC002** |
| company_code | **300009** |
| company_name | 安科生物 |
| source_type | `cninfo_general_announcement_pdf` |
| universe endpoint_scope | EP001 · EP005 |
| reported endpoint_id | EP005（primary） |
| failure stage | **EP002** `topSearch/query`（orgId 解析） |
| retrieval_status | `network_error` |
| quality_status | `needs_review` |
| error_type | `network_error` |
| notes | EP002 orgId resolution failed |

---

## Failure Category

**`transient_network_error_at_ep002_orgid_resolution`**

子类：`infrastructure_transient`（非 schema · 非公司身份不可解析）

### 依据

1. **同次 tiny live 运行中 4/5 成功** — TLC001/003/004/005 均 `found` + `quality_status=pass`，说明 EP001/EP002 链路在当次批次整体可用。
2. **TLC002 在首次 live 执行中曾成功** — 同 runner 首轮对 300009 返回公告「关于第3期员工持股计划非交易过户完成的公告」，`retrieval_status=found`；失败出现在后续重跑/测试覆盖后的第二次执行，属间歇性失败模式。
3. **C-class 对 300009 有成功 harvest 记录** — `cninfo_c_class_harvest_dryrun_report.csv` 显示多家 profile 源 `proceed_testing` / `direct_fetch`，证明该 `company_code` 在 CNINFO 侧可识别，非退市/ST/身份缺口样本。
4. **错误类型为 `network_error` 而非 `empty_response`** — runner 在 EP002 阶段因 HTTP 非 2xx、超时或异常返回 `network_error`；若 orgId 逻辑错误或公司不存在，预期为 `empty_response` 或稳定 `not_found`，与观测不符。
5. **EP001 被正确跳过** — `announcement_id` 为空 · `raw_announcement=null` · CNINFO 总请求 **8**（4×EP002 + 4×EP001）= TLC002 仅发起 **1** 次 EP002 后终止，符合「orgId 失败则不猜测、不继续 EP001」的 freeze v1 口径。

---

## Endpoint Logic vs Transient Network

| 假设 | 结论 |
|------|------|
| endpoint 逻辑问题 | **不太可能** — 同 runner 对其他创业板（688981）及同批次案例成功；EP002→EP001 顺序与 corpus retrieval 一致 |
| 瞬态网络问题 | **最可能** — `network_error` 标签 · 同 code 历史成功 · 单次失败孤立 |

### EP002 与 universe 声明

TLC002 universe 行仅列 `EP001;EP005`，runner 隐式调用 EP002 作 orgId helper（与 [live approval plan](../../plans/cninfo_b_class_phase1_live_validation_approval_plan.md) 及 freeze v1 endpoint catalog 一致）。**这不是 TLC002 独有配置错误**，而是 Phase 1 标准检索链。

---

## Report Inspection（Task 2）

来源：[cninfo_b_class_tiny_live_validation_report.csv](cninfo_b_class_tiny_live_validation_report.csv)

| 检查项 | 结果 |
|--------|------|
| request sequence | TLC002：**EP002 only**（1 req）→ 失败 → **EP001 skipped** |
| endpoint attempted | EP002（orgId）；EP005 为报告 primary endpoint_id，未到达 EP001 查询阶段 |
| error type | `network_error` |
| EP001 skipped correctly | **yes** — 无 announcement 字段填充 |
| lineage fields valid | **yes（失败态）** — `lineage_status=needs_review` · 无伪造 `discovered` · 无 `verified` |

### 与成功 case 对比

| case | EP002→EP001 | announcement_id | quality_status |
|------|-------------|-----------------|----------------|
| TLC001 | 成功 | 1222894646 | pass |
| TLC002 | **EP002 fail** | （空） | needs_review |
| TLC004 | 成功 | 1223973920 | pass |

---

## Retry Recommendation

| 项 | 建议 |
|----|------|
| 自动重试 | **否** — 须人工批准后再跑 isolated retry |
| 人工决策 | **retry_candidate** — 后续可用相同 schema / 相同 universe 行单独补跑 TLC002 |
| 重试条件 | C-class Phase 3 无并发 harvest 压力 · sleep ≥0.6s · 单 case limit |
| 预期结果 | 高概率 `found`（基于历史同 code 成功） |

---

## Schema Freeze Impact

| 项 | 影响 |
|----|------|
| phase1_freeze_v1 field catalog | **无影响** |
| 15 required fields | **无变更需求** |
| endpoint catalog EP001–EP005 | **无变更需求** |
| quality_status 规则 | **无影响** — `needs_review` 对 network_error 为预期行为 |

**结论：schema freeze 不受影响。**

---

## Artifacts Referenced（只读）

- [TLC002 raw_metadata](cninfo_b_class_tiny_live_validation/raw_metadata/TLC002_EP005.json)
- [TLC002 quality](cninfo_b_class_tiny_live_validation/quality/TLC002.json)
- [tiny live summary](cninfo_b_class_tiny_live_validation_summary.md)

**本轮未修改上述产物。**
