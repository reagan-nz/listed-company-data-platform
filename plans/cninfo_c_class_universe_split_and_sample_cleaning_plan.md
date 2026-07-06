# C-class Universe Split and Sample Cleaning Plan

_Era C Phase 4 · 2026-07-06_

> **前置：** [195 active live summary](../outputs/validation/cninfo_c_class_scale_smoke_200_active_summary.md) · [BSE diagnosis](../outputs/validation/cninfo_c_class_scale_smoke_200_bse_diagnosis.md)  
> **本轮：** 只读派生样本 · **无 live** · **无 CNINFO** · 无 YAML backfill · 无 DB · 无 verified

---

## 1. 背景与动机

195-company active live smoke（`LIVE_PARTIAL`）+ BSE diagnosis 表明：

- **non-BSE** 主判定稳定（~97% pass）
- **BSE 并非整体不可用** — **920 层** scode 路径基本可用
- **83/87 旧代码层** 系统性 HTTP 500 / `9240002` → `legacy_code_incompatible`
- **839729 / 920729** 永顺生物同 orgid — legacy code mapping 问题
- **600065 / 600978 / 000405** 等异常样本 — 样本质量 issue，非 source 不可用证据

**策略转变：** 主 C-class scale gate **不再**将 `bse_legacy_83_87` 与 non-BSE 混算；下一阶段 **不是 blind 1000**，而是 **universe split + 清洗后扩样**。

---

## 2. Universe 分类规则

母本：`lab/eval_companies_c_class_smoke_200_active.yaml`（**195** 家）

| universe_id | 条件 | 派生文件 | 数量 |
|-------------|------|----------|------|
| `non_bse_active` | `board != bse`；非已知异常名单；195 live 主源未 6/6 全失败 | [eval_companies_c_class_smoke_195_non_bse_active.yaml](../lab/eval_companies_c_class_smoke_195_non_bse_active.yaml) | **172** |
| `bse_920_active` | `board == bse` 且 `stock_code` 以 **920** 开头；195 live 主源大部分通过 | [eval_companies_c_class_smoke_195_bse_920_active.yaml](../lab/eval_companies_c_class_smoke_195_bse_920_active.yaml) | **12** |
| `bse_legacy_83_87_hold` | `board == bse` 且前缀 **83/87**；195 live 主源 HTTP 500 / 9240002 | [eval_companies_c_class_smoke_195_bse_legacy_hold.yaml](../lab/eval_companies_c_class_smoke_195_bse_legacy_hold.yaml) | **8** |
| `abnormal_review` | ST/历史异常；195 live 主源 **6/6 全失败** | [eval_companies_c_class_smoke_195_abnormal_review.yaml](../lab/eval_companies_c_class_smoke_195_abnormal_review.yaml) | **3** |

**合计：** 172 + 12 + 8 + 3 = **195**

### 2.1 `non_bse_active`（172）

- 覆盖 sse_main 57 · szse_main 48 · chinext 45 · star 25（含 *ST 但 live 未 6/6 全败者，如 *ST东珠）
- **可进入** 1000-like planning 主宇宙候选
- 195 live 参考：主判定 pass ~97%

### 2.2 `bse_920_active`（12）

| stock_code | short_name | 195 live 主源 |
|------------|------------|---------------|
| 920023 | *ST田野 | 6/6 pass |
| 920035 | 精创电气 | 6/6 pass |
| 920050 | 爱舍伦 | 6/6 pass |
| 920145 | 恒合股份 | 6/6 pass |
| 920160 | 北矿检测 | 6/6 pass |
| 920186 | 中科仪 | 5/6 pass（top_float empty_but_valid） |
| 920339 | 恒太照明 | 6/6 pass |
| 920367 | 新赣江 | 6/6 pass |
| 920663 | 明阳科技 | 6/6 pass |
| 920729 | 永顺生物 | 6/6 pass（**保留**；剔除重复 839729） |
| 920866 | 绿亨科技 | 6/6 pass |
| 920957 | 汉维科技 | 6/6 pass |

- **单独 BSE 子 gate**；不并入 non-BSE 主 gate

### 2.3 `bse_legacy_83_87_hold`（8）— HOLD

| stock_code | short_name | hold_reason |
|------------|------------|-------------|
| 832317 | 观典防务 | legacy_code_incompatible · HTTP 500 |
| 832491 | 奥迪威 | legacy_code_incompatible · HTTP 500 |
| 832876 | 慧为智能 | legacy_code_incompatible · HTTP 500 / blocked |
| 833266 | 生物谷 | legacy_code_incompatible · HTTP 500 |
| 835174 | 五新隧装 | legacy_code_incompatible · HTTP 500 / blocked |
| 839680 | *ST广道 | legacy_code_incompatible · HTTP 500 |
| 839729 | 永顺生物 | legacy 重复代码 · 见 920729 |
| 870656 | 海昇药业 | legacy_code_incompatible · HTTP 500 |

- **不进入** 主 C-class scale gate
- **不进入** 1000-like 主宇宙
- 后续：**BSE legacy targeted DevTools / code mapping probe**（小样本，非 195 重跑）

### 2.4 `abnormal_review`（3）

| stock_code | short_name | board | review_reason |
|------------|------------|-------|---------------|
| 600065 | *ST联谊 | sse_main | 6/6 主源 fail · HTTP 500 |
| 600978 | *ST宜生 | sse_main | 6/6 主源 fail · HTTP 500 |
| 000405 | ST鑫光 | szse_main | 6/6 主源 fail · HTTP 500 / blocked |

- **不判定** direct source 不可用
- **不进入** 主 gate 分母
- 样本质量 review；扩 1000 前应从母本剔除或单独标注

---

## 3. 当前策略（执行口径）

| 决策 | 说明 |
|------|------|
| 主 gate 混算 | **停止** 将 `bse_legacy_83_87` 与 non-BSE 混算 |
| non-BSE | **可进入** 1000-like planning（清洗后从 `eval_companies_1000` 等母本派生） |
| BSE 920 | **子 universe 单独 gate** |
| BSE 83/87 | **HOLD** · targeted probe · 不做全量 live 重跑 |
| abnormal_review | **不进入** 主 gate |
| security_profile | **observe-only**（延续） |
| shareholder empty_but_valid | 按 [200 plan](cninfo_c_class_scale_smoke_200_plan.md) §6 统计 |

---

## 4. Dividend backfill 决策口径

| 宇宙 | YAML backfill 决策 | 执行 |
|------|-------------------|------|
| **non-BSE universe** | **GO（仅决策）** — 195 live 表现支持 historical dividend endpoint |
| **mixed full universe（含 BSE 83/87）** | **HOLD** |
| **bse_920_active** | 待 BSE 子 gate 稳定后再决策 |
| **执行** | **本轮不执行 YAML backfill** |

**命名：** 若未来 backfill，使用 **`dividend_history`**（或等价），**避免** `dividend_financing` 语义过宽；caveat：**historical dividend only**。

---

## 5. 1000-like planning 前置条件

进入 1000-like sample 派生前须满足：

1. **剔除** 退市名 / `abnormal_review` 三家 / `bse_legacy_hold` 八家
2. **剔除** legacy 重复（839729，保留 920729）
3. **BSE 83/87 不进入** 主 universe 分母
4. **BSE 920 单列** 子宇宙文件或 stratum 标记
5. **股东源** `empty_but_valid` 按 §6 口径（reachable ≠ non_empty）
6. **security_profile** observe-only，不绑定主 gate
7. **不写 verified** · **不升级 testing_stable_sample**
8. 从现有 `lab/eval_companies_1000.yaml` **离线过滤**派生，**不联网**补样本

**建议主宇宙起点：** `non_bse_active`（172）+ 从 `eval_companies_1000` 同规则过滤扩样。

---

## 6. 清洗规则（可复用于 1000 母本）

```text
EXCLUDE if:
  - short_name 含「退市」
  - short_name 以「退」结尾
  - stock_code in abnormal_review explicit list (live 6/6 fail ST set)
  - board == bse AND stock_code matches ^83|^87
  - duplicate legacy BSE code when 920 counterpart exists (same orgid)

HOLD (separate file, not in main gate):
  - bse_legacy_83_87

SPLIT:
  - bse AND stock_code matches ^920 → bse_920_active

MAINLINE:
  - board != bse AND passes EXCLUDE rules → non_bse_active
```

---

## 7. 下一步

| 优先级 | 动作 |
|--------|------|
| 1 | 从 `eval_companies_1000.yaml` 离线派生 **non_bse_active ~1000** 候选（同清洗规则） |
| 2 | **BSE legacy targeted probe**（8 家 hold 池，DevTools only，非 live smoke 全量） |
| 3 | 可选：对 `non_bse_active` 172 跑定向 dry-run / 小规模 spot live（需批准） |
| 4 | dividend_history backfill **决策文档更新**（仍不执行 YAML） |

---

## 8. 红线

- 不跑 live · 不请求 CNINFO
- 不 YAML backfill · 不入库 · 不写 verified
- 不升级 testing_stable_sample
- 不新增大规模 endpoint discovery
- 不改 B / D / Phase 1 文件

---

## 9. 参考

- [cninfo_c_class_scale_smoke_200_plan.md](cninfo_c_class_scale_smoke_200_plan.md)
- [cninfo_c_class_scale_smoke_200_bse_diagnosis.md](../outputs/validation/cninfo_c_class_scale_smoke_200_bse_diagnosis.md)
- [cninfo_c_class_scale_smoke_200_failure_cases.csv](../outputs/validation/cninfo_c_class_scale_smoke_200_failure_cases.csv)
