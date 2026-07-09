# CNINFO C-Class Phase 2 Smoke Closure Review

_生成时间：2026-07-09_

> 离线 closure review。**无 CNINFO** · **无 live** · **无 harvest rerun** · **无 snapshot rebuild**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# 1. Phase 2 Objective

Phase 2 验证 C-class 能否在原始 **863** 家已验证 universe 之外，通过受控 **200** 家公司 smoke batch 完成扩源闭环。

目标不是全市场覆盖，而是验证：

- matched_active 候选池选股与隔离规则是否可用
- isolated output-root live harvest 是否可执行
- harvest QA 能否识别并分流 all-direct-failure 公司
- snapshot builder 扩展（`--harvest-root` / `--output-dir`）能否对干净子集离线构建 JSON
- snapshot QA 能否复用 863 模式并校正 status 追踪

---

# 2. Execution Summary

| Stage | Input count | Output count | Gate | Notes |
|-------|-------------|--------------|------|-------|
| universe selection | matched_active pool **4647** | selected **200** | `phase2_smoke_universe_selection_gate = PASS` | 无 already_in_c_class / hold / BSE / identity_conflict / manual_review 混入 |
| harvest | **200** companies | raw **1400** · normalized **1928** | terminal smoke **PASS** | **1400** HTTP（200×7 live sources）；observe-only security 另计 |
| harvest QA | **200** harvested | **188** usable · **12** all-direct-failure | `phase2_smoke_live_harvest_qa_gate = PASS_WITH_CAVEAT` | 失败集中于 delisted/inactive；**9240002** 占全部 http_error |
| snapshot subset | **200** harvested | **188** include · **12** exclude | design gate **DESIGN_COMPLETE** | 排除 12 家 all-direct-failure；不纳入首批 snapshot |
| snapshot build | **188** subset | **188** JSON · failed **0** | `phase2_smoke_188_snapshot_build_gate = PASS_WITH_CAVEAT` | 输出隔离于 `phase2_smoke_188/`；`full/` 未触碰 |
| snapshot QA | **188** JSON | **188** valid JSON | `phase2_smoke_188_snapshot_qa_gate = PASS_WITH_CAVEAT` | status CSV 从 dry-run `pending` 校正为 `reviewed` |

---

# 3. Key Results

| 指标 | 结果 |
|------|------|
| smoke universe selected | **200** |
| live harvest executed | **200** companies · **1400** HTTP |
| harvest usable companies | **188**（6 direct sources 可用） |
| all-direct-failure excluded | **12** |
| snapshot subset | **188** |
| snapshots built | **188** JSON · failed **0** |
| valid JSON after QA | **188** |
| snapshot_status | **188** × `complete_with_caveat` |
| output isolation | harvest → `phase2_smoke_200/` · snapshot → `phase2_smoke_188/` · `full/` **863** 未变 |

---

# 4. Caveats

## 4.1 12 家 all-direct-failure 公司

| company_code | company_name | 特征 |
|--------------|--------------|------|
| 000038 | 大通退 | delisted |
| 000616 | *ST海投 | ST / inactive pattern |
| 000956 | 中原退市 | delisted |
| 002087 | 新纺退 | delisted |
| 002231 | *ST奥维 | ST / inactive pattern |
| 300023 | 宝德退 | delisted |
| 300356 | 光一退 | delisted |
| 600005 | 武钢股份 | legacy / inactive |
| 600290 | *ST华仪 | ST / inactive pattern |
| 600634 | 退市富控 | delisted |
| 600646 | ST国嘉 | ST / inactive pattern |
| 600696 | 退市岩石 | delisted |

其中 **7** 家 selection YAML 标记 `listing_status=delisted`；**5** 家为 ST/退市/legacy 名称但选股时仍为 `listed`。

## 4.2 9240002 集中

- 全部 **70** 条 `http_error` 使用 business_code **9240002**
- 与 delisted/inactive 公司高度共现；非 broad active-listing outage

## 4.3 Normalized 覆盖率

- normalized files: **1928** / expected max **2000**（**72** missing = 12×6 direct source gaps）
- derived sources（contact / business / industry / security）对 **200** 家均写入

## 4.4 Snapshot 全量 complete_with_caveat

- **188/188** `complete_with_caveat`；无 `complete` 纯绿快照
- 与 863 batch 策略一致：caveat 层为预期默认态

## 4.5 预期模块缺口（与 863 QA 模式一致）

| 模块 | 188 家模式 | 说明 |
|------|-----------|------|
| technology_profile | 188 × not_available | 无 RD 源，预期 |
| shareholder_profile | 188 × partial | top-N 源 partial |
| capital_action_profile | 188 × partial | share_capital partial |
| risk_profile | 188 × partial | security observe_only |
| market_behavior | 188 × partial | security observe_only |
| investor_relation | 188 × partial | 与 organization 重叠 |
| dividend_profile | 182 available · 6 partial | valid_empty 合法 |

## 4.6 Quality flags

- **4945** 条 quality flags（`field_missing` **4929** · severity **info** 为主）
- 与 863 full snapshot QA 同类模式；非 Phase 2 特有阻塞

---

# 5. Decision

```
phase2_smoke_closure_gate = PASS_WITH_CAVEAT
```

**理由：**

1. Pipeline 成功扩展到非 863 新样本（**188** 家干净子集端到端可用）
2. **12** 家失败集中且可解释（delisted/inactive / **9240002**），未出现广泛 active-listing outage
3. Snapshot 生成对干净子集 **188/188** 成功；QA **188/188** 有效 JSON
4. Harvest / snapshot output-root 隔离通过；`full/` 与主轨 harvest 未 breach
5. Builder extension、dry-run、build、QA、status 校正全链路完成

**Caveat 保留：** smoke 选股仍纳入 **7** 家 delisted 行（selection 时已知）；Phase 3 须加强 delisted/inactive 预筛。

---

# 6. What Phase 2 Does NOT Prove

Phase 2 **不证明**以下命题：

- **全市场稳定性** — 仅 200 家 smoke，非 6124 matched_active 全量
- **BSE 覆盖** — smoke pool 排除 BSE；BSE legacy 仍 HOLD
- **legacy / hold / manual review 队列消解** — 26 all6 hold、72 QA queue flags 未在本轮处理
- **6124 全量 harvest 授权** — 未批准、未执行
- **verified / testing_stable_sample 升级** — 未发生
- **registry 生产实现** — 仅 candidate 规划，无 merge

---

# 7. Recommended Next Phase

**推荐：Phase 3 batch expansion planning**

| 项 | 建议 |
|----|------|
| batch size | **500** companies per batch |
| candidate pool | **matched_active** only |
| exclusions | already_in_c_class · hold · BSE · BSE legacy · identity_conflict · manual_review · delisted/inactive caveat candidates（若可识别） |
| safeguards | output-root isolation · explicit approval · dry-run before live · harvest QA before snapshot · snapshot only clean subset |
| first deliverable | Phase 3 batch expansion **planning** document（非 live 执行） |

**不推荐：** 在 closure review 完成前启动 full 500 live batch。

---

# 8. References

- [selection summary](../outputs/validation/cninfo_c_class_phase2_smoke_200_selection_summary.md)
- [live harvest QA summary](../outputs/validation/cninfo_c_class_phase2_smoke_200_live_harvest_qa_summary.md)
- [snapshot build QA summary](../outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_build_qa_summary.md)
- [snapshot QA summary](../outputs/validation/cninfo_c_class_phase2_smoke_188_snapshot_qa_summary.md)
- [closure metrics](../outputs/validation/cninfo_c_class_phase2_smoke_closure_metrics.csv)
- [excluded company caveat ledger](../outputs/validation/cninfo_c_class_phase2_smoke_excluded_company_caveat_ledger.csv)
- [Phase 3 readiness summary](../outputs/validation/cninfo_c_class_phase3_batch_readiness_summary.md)

## 红线确认

- 未请求 CNINFO · 未 live · 未重跑 harvest · 未 rebuild snapshot
- raw / normalized / field_inventory / snapshot JSON **未修改**
- 未入库 / MinIO / RAG / registry / verified
