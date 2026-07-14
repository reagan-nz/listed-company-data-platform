# CNINFO A 类 Era D Next-Scale — Universe Strategy

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Cumulative Target

| 阶段 | case_id 范围 | cohort | 与 scale-200 关系 |
|------|-------------|--------|-------------------|
| Era D scale-200（已完成 · committed **`41dc049`**） | AD2E001–AD2E200 | retained_phase3 + new_erad | **192/200 effective** · lineage-reference |
| **Next slice 1（本规划）** | **AD2E201–AD2E500** | **next_scale_slice1** | **+300 new** · 零 overlap |
| Future slice 2（占位） | AD2E501+ | next_scale_slice2+ | 500→non-BSE fuller · planning only |

**累计 lineage 目标（slice1 后）：500 家公司代码（200 已覆盖 + 300 新）**

---

## 2. Overlap Rules vs Committed 192/200 Effective

| 对照集 | 政策 | draft 结果 |
|--------|------|------------|
| AD2E001–200（全部 scale-200 universe） | **exclude rerun** · lineage-reference only | **0 overlap**（company_code） |
| 192 effective accepted | **不重跑** · 仅 cumulative 计数 | 引用 [effective accepted ledger](cninfo_a_class_erad_scale_200_effective_accepted_ledger.csv) |
| 8 unresolved final | **side-track only** · 不在 slice1 primary | **0 in slice1 universe** |
| Phase 1/2 tiny live | **exclude** | lint at runner stage |
| Phase 3 effective 50 | **exclude**（新片 company_code） | retained AD2E001–050 已在 scale-200 · 不重复 |
| A3M017 | **side-track** · Phase 3 production root untouched | reference-only |

**draft universe lint：** 300 rows · **prior_in_scale_200=no** · **company_code ∩ scale-200 = ∅**

---

## 3. Next Cohort Selection Rules

### 3.1 Include

| 规则 | 说明 |
|------|------|
| 公司代码唯一 | 与 A-class scale-200 **200 codes** + B-class next-scale slice1 **300 codes** **零 overlap** |
| 非 BSE | 排除北交所（`8xxxxx` / `4xxxxx` / `92xxxx`） |
| 非 ST | 名称含 `ST` / `*ST` 排除 |
| 市场分层 | SSE main / SZSE main / ChiNext / STAR 分层抽样（draft：**108 / 102 / 60 / 30**） |
| report_type | annual_report + quarterly_report_q1 混合（runner 扩展时落地 · 与 scale-200 new_erad 比例参照） |
| matching_logic | **v2**（延续 scale-200） |

### 3.2 Exclude / Hold

| 类型 | 政策 |
|------|------|
| scale-200 8 unresolved | **hold side-track** · retry_again=no · 不进入 slice1 |
| AD2E146 defer | filing-delay · 不进入 slice1 |
| matching_logic_miss（121/122/185） | optional offline raw_metadata review · **不阻塞** slice1 |
| BSE | 默认 exclude · fuller 阶段另轨 |
| abnormal / 退市 | 源池已清洗 · live 发现则 `hold_review` |

---

## 4. Phase 3 / A3M017 Policy

| 项 | 政策 |
|----|------|
| Phase 3 production root | **禁止 mutation** · `cninfo_a_class_phase3_50_company_expansion/` 只读 |
| A3M017 | **side-track** · isolated retry planning only · **NOT in slice1 universe** |
| retained_phase3 AD2E001–050 | 已在 scale-200 · **不重跑** · lineage-reference |

---

## 5. Cross-Class Sync（B / C Fuller Market）

| 对照 | 同步策略 |
|------|----------|
| B-class next-scale slice1（BD2E201–500） | **并行 +300** · 本 draft 从同一 non-BSE 889 池选取 **disjoint 300 codes** · overlap **0** |
| C-class fuller market（889 pool） | slice1 后剩余 ~**289** codes 可用于 A/B slice2 或 fuller 阶段 |
| 联合日 cap | 若 A+B slice1 live 同日执行 · 建议合计 CNINFO **≤500** · 错开 session |

**源池：** [lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml](../../lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml)（889 companies · offline derived · CNINFO **0**）

---

## 6. Draft Universe Reference

- [cninfo_a_class_erad_next_scale_candidate_universe_draft.csv](cninfo_a_class_erad_next_scale_candidate_universe_draft.csv)
- **300 rows** · AD2E201–AD2E500
- **overlap with 192/200 effective codes：0**
- **overlap with B next-scale slice1：0**

---

## 7. Validation Before Live（Future）

1. dry-run overlap lint：300 codes ∩ scale-200 = ∅ · ∩ B slice1 = ∅
2. dry-run request budget：≤720 planned requests
3. output-root guard：拒绝写入 scale-200 / failed_retry / Phase 3 / A3M017 根
4. human approval phrase（separate task）

**NOT verified** · **NOT production_ready**
