# CNINFO B 类 Era D Fuller Next-Slice — Universe Strategy

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Cumulative Target

| 阶段 | case_id 范围 | cohort | 与 prior B 关系 |
|------|-------------|--------|-----------------|
| Era D scale-200（已完成） | BD2E001–BD2E200 | retained_phase3 + new_expansion | **198/200 effective** · lineage-reference |
| Next-scale slice1（已完成） | BD2E201–BD2E500 | next_scale_slice1 | **300/300 effective** · lineage-reference |
| **Fuller slice2（本规划）** | **BD2E501–BD2E800** | **fuller_next_slice2** | **+300 new** · 零 overlap |
| Future slice3+（占位） | BD2E801+ | fuller_next_slice3+ | toward non-BSE active remainder |

**累计 lineage（slice2 后规划目标）：~798 effective**（498 已 effective + 300 新片）

---

## 2. Overlap Rules vs BD2E001–500 Effective 498

| 对照集 | 政策 | `prior_in_scale_200_or_slice1` |
|--------|------|--------------------------------|
| BD2E001–200（198 effective） | **exclude rerun** · lineage-reference only | `erad_scale_200` if hit → **reject** |
| BD2E201–500（300 effective） | **exclude rerun** · lineage-reference only | `erad_slice1` if hit → **reject** |
| BD2E090 · BD2E092 | **side-track only** · **not in primary slice2** | optional retry 另轨 · 不占用 slice2 名额 |
| Phase 1/2/2.5/3 B-class | **exclude** | `phase*` if hit → **reject** |
| A/C/D live 根 | **禁止写入** · 只读参照 | n/a |

**draft universe：** 全部 `prior_in_scale_200_or_slice1=none` · company_code ∩ prior B cumulative **500 codes** = **∅**

---

## 3. Next Cohort Selection Rules

### 3.1 Include

| 规则 | 说明 |
|------|------|
| 公司代码唯一 | 与 B cumulative 500 + Phase 历史 **零 overlap** |
| 非 BSE | 排除北交所（`8xxxxx` / `4xxxxx` / `92xxxx`） |
| 非 ST / 退市 | 名称含 `ST` / `*ST` / `退` 排除 |
| 市场分层 | 从 smoke 889 池有序取样 · draft strata 见 planning summary |
| announcement 路由 | ~50% periodic_report · ~50% general_announcement（runner 阶段落地） |
| 金融子集 | 名称含银行/证券/保险 → EP002 候选（runner 阶段） |

### 3.2 Source Pool

- 母本：`lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml`（**889** active non-BSE）
- 排除：B scale-200 **200** + slice1 **300** + C fuller slice1 **200**（registry 去重后）
- 可用候选（离线派生）：**~478** · draft 取前 **300**（full prior B + slice1 exclusion）

---

## 4. Sync Notes vs A Next-Scale / C Fuller-Market

| 轨 | 当前状态 | 与 B fuller slice2 关系 |
|----|----------|------------------------|
| **A next-scale** | AD2E201–500 slice1 planning/live 并行轨 | 共享 non-BSE 方向 · **company_code 须交叉 lint** · 不共享 output root |
| **C fuller-market** | CE1E001–200 slice1 draft · 863+200 目标 | C harvest 轨 · B metadata-only · **零 overlap 政策一致** · C 200 codes 已从 B draft 池排除 |
| **B cumulative** | 498 effective · commit `350cdda` | slice2 **仅新增** · 不重跑 498 |

**协调原则：** 三轨可并行规划 · live 须错开 CNINFO 高峰 · 日合计 cap 参照 request budget。

---

## 5. BSE / ST / 退 / Holdout Handling

| 类型 | 政策 |
|------|------|
| BSE | 规划阶段 **exclude** · fuller 终局另轨或 registry refresh 后评估 |
| ST / *ST | **exclude** from primary slice2 draft |
| 退市 / 名称后缀「退」 | **exclude** |
| 26 hold（C 轨） | B slice2 **不主动纳入** holdout 公司 · 与 C Option A HOLD 一致 |
| network_error（090/092） | **hold** · side-track · 不进入 slice2 primary universe |

---

## 6. Draft Universe Reference

- [cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv](cninfo_b_class_erad_fuller_next_slice_candidate_universe_draft.csv)
- **300 rows** · BD2E501–BD2E800
- CNINFO **0** · overlap lint **0** vs B cumulative 500

---

## 7. Validation Before Live（Future）

1. dry-run overlap lint：300 codes ∩ prior B = ∅
2. dry-run overlap lint vs A/C parallel universes
3. dry-run request budget：≤720 planned requests
4. output-root guard：拒绝写入 scale-200 / slice1 / Phase 3 根
5. human approval phrase（separate task）

**NOT verified** · **NOT production_ready**
