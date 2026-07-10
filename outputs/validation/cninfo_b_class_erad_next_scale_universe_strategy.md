# CNINFO B 类 Era D Next-Scale — Universe Strategy

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Cumulative Target

| 阶段 | case_id 范围 | cohort | 与 scale-200 关系 |
|------|-------------|--------|-------------------|
| Era D scale-200（已完成） | BD2E001–BD2E200 | retained_phase3 + new_expansion | **198/200 effective** · lineage-reference |
| **Next slice 1（本规划）** | **BD2E201–BD2E500** | **next_scale_slice1** | **+300 new** · 零 overlap |
| Future slice 2（占位） | BD2E501+ | next_scale_slice2+ | 500→non-BSE fuller · planning only |

**累计 lineage 目标（slice1 后）：500 家公司代码（200 已覆盖 + 300 新）**

---

## 2. Next Cohort Selection Rules

### 2.1 Include

| 规则 | 说明 |
|------|------|
| 公司代码唯一 | 与 Phase 1/2/2.5/3 + Era D 200 **零 overlap** |
| 非 BSE | 排除北交所（`8xxxxx` / `4xxxxx` / `92xxxx`）— 与历史 B 轨一致 |
| 非 ST | 名称含 `ST` / `*ST` 排除 |
| 市场分层 | SSE / SZSE / ChiNext / STAR 分层抽样（draft：**108 / 112 / 50 / 30**） |
| announcement 路由 | 50% periodic_report（EP001+EP004）· 50% general_announcement（EP001+EP005）— runner 扩展时落地 |
| 金融子集 | 名称含银行/证券/保险等 → EP002 候选（draft 现 **5** 家 · runner 阶段可补强） |

### 2.2 Overlap Matrix

| 对照集 | 政策 | prior_overlap 值 |
|--------|------|------------------|
| Phase 1 tiny live | **exclude** | `phase1` if hit |
| Phase 2 expansion | **exclude** | `phase2` if hit |
| Phase 2.5 expansion | **exclude** | `phase25` if hit |
| Phase 3 effective 100 | **exclude**（新片） | `phase3` if hit |
| Era D scale-200（BD2E001–200） | **exclude rerun** · lineage-reference only | `erad_scale_200` if hit |
| A/C/D live 根 | **禁止写入** · 只读参照 | n/a |

**draft universe：** 全部 `prior_overlap=none`（275 prior B-class codes 已排除）

### 2.3 Lineage Reference（不重跑）

| 项 | 政策 |
|----|------|
| BD2E001–200（198 effective） | 仅作 cumulative lineage 计数与 report 交叉引用 |
| BD2E090 · BD2E092 | **optional side-track** · 不阻塞 next-scale slice1 |
| Phase 3 production roots | **禁止 mutation** · `cninfo_b_class_phase3_*` 只读 |

---

## 3. Exclude / Hold Policies

### 3.1 Persistent network_error

| 场景 | 政策 |
|------|------|
| scale-200 unresolved（BD2E090/092） | **hold** in unresolved ledger · optional isolated retry（separate approval） |
| next-scale slice1 新失败 | 入 slice1 unresolved ledger · **不 rollback** 已成功 case · 不阻塞 slice2 规划 |
| 同一 company_code 重复 network_error ≥2 次 | **hold_deferred** · 移出下一批候选 · 保留 sidecar 若有 |

### 3.2 Other Holds

| 类型 | 政策 |
|------|------|
| ST / 退市 / 停牌极端 | 规划阶段排除 · live 发现则 `hold_review` |
| BSE | 默认 exclude · fuller 阶段另轨 |
| Phase 3 已 accepted sidecar | 新片 **不覆盖** · 新根隔离 |

---

## 4. Draft Universe Reference

- [cninfo_b_class_erad_next_scale_candidate_universe_draft.csv](cninfo_b_class_erad_next_scale_candidate_universe_draft.csv)
- **300 rows** · BD2E201–BD2E500
- 源池：`lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（离线派生 · CNINFO **0**）

---

## 5. Validation Before Live（Future）

1. dry-run overlap lint：确认 300 codes ∩ prior B-class = ∅
2. dry-run request budget：≤720 planned requests
3. output-root guard：拒绝写入 scale-200 / Phase 3 根
4. human approval phrase（separate task）

**NOT verified** · **NOT production_ready**
