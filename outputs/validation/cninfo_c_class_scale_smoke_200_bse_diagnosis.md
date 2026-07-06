# CNINFO C-Class 200 Active Smoke — BSE Failure Diagnosis

_生成时间：2026-07-06_

## 1. 执行摘要

基于 [cninfo_c_class_scale_smoke_200_active_report.csv](cninfo_c_class_scale_smoke_200_active_report.csv)（195 家 · 1365 live cases · **未新增 CNINFO 请求**）。

| 指标 | 全样本 | BSE (20) | 非 BSE (175) |
|------|--------|----------|--------------|
| 主判定 pass | 1101 | 71 | 1030 |
| 主判定 fail | 69 | 49 | 20 |
| 主判定 pass% | 94.1% | 59.2% | 98.1% |

**核心结论：** BSE 失败高度集中于 **83xxxx / 87xxxx** 旧代码（HTTP 500 · `json_code=9240002`）；**92xxxx** 新代码 11/12 家主源全过。非 BSE 整体稳定（~97–100% pass），失败主要为 **3 家 *ST/异常上市状态** + **1 家股东空表**。

## 2. Failure cases 提取

共 **69** 条 `case_result=fail`，已导出 [cninfo_c_class_scale_smoke_200_failure_cases.csv](cninfo_c_class_scale_smoke_200_failure_cases.csv)。

| retrieval_status | count |
|------------------|-------|
| `blocked` | 4 |
| `empty_but_valid_response` | 3 |
| `http_error` | 62 |

## 3. Company-level failure clustering

- **主判定 6/6 全失败：** 11 家
- **仅股东源 empty_but_valid：** 2 家
- **其他部分失败：** 0 家

### 3.1 主判定 6/6 全失败

| code | name | board | 备注 |
|------|------|-------|------|
| `000405` | ST鑫光 | `szse_main` | 名称含 ST · HTTP 500 / 9240002 |
| `600065` | *ST联谊 | `sse_main` | 名称含 ST · HTTP 500 / 9240002 |
| `600978` | *ST宜生 | `sse_main` | 名称含 ST · HTTP 500 / 9240002 |
| `832317` | 观典防务 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `832491` | 奥迪威 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `832876` | 慧为智能 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `833266` | 生物谷 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `835174` | 五新隧装 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `839680` | *ST广道 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `839729` | 永顺生物 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |
| `870656` | 海昇药业 | `bse` | BSE 旧代码 · HTTP 500 / 9240002 |

### 3.2 仅股东源 empty_but_valid

| code | name | board | failed sources |
|------|------|-------|----------------|
| `688797` | 臻宝科技 | `star` | cninfo_top_float_shareholders_profile;cninfo_top_shareholders_profile |
| `920186` | 中科仪 | `bse` | cninfo_top_float_shareholders_profile |

## 4. BSE-specific diagnosis（20 家）

### 4.1 代码前缀分层

| 前缀 | 家数 | 主源表现 | 推断 |
|------|------|----------|------|
| **83xxxx** | 7 | 7/7 · **6/6 全失败** | 旧三板/迁移前代码；`getCompany*` scode 路径不兼容 |
| **87xxxx** | 1 | 1/1 · **6/6 全失败** | 同上 |
| **92xxxx** | 12 | 11/12 全过；1 家仅 top_float empty | 当前 CNINFO C-class scode 路径对 **920** 有效 |

### 4.2 BSE 主源矩阵（6 主判定）

| code | name | basic | dividend | executive | share_cap | top_sh | top_float |
|------|------|-------|----------|-----------|-----------|--------|-----------|
| `832317` | 观典防务 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) |
| `832491` | 奥迪威 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) |
| `832876` | 慧为智能 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(blocked) | F(http_error) |
| `833266` | 生物谷 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) |
| `835174` | 五新隧装 | F(http_error) | F(http_error) | F(blocked) | F(http_error) | F(http_error) | F(http_error) |
| `839680` | *ST广道 | F(http_error) | F(http_error) | F(blocked) | F(http_error) | F(http_error) | F(http_error) |
| `839729` | 永顺生物 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) |
| `870656` | 海昇药业 | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) | F(http_error) |
| `920023` | *ST田野 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920035` | 精创电气 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920050` | 爱舍伦 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920145` | 恒合股份 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920160` | 北矿检测 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920186` | 中科仪 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | F(empty_but_valid_response) |
| `920339` | 恒太照明 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920367` | 新赣江 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920663` | 明阳科技 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920729` | 永顺生物 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920866` | 绿亨科技 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |
| `920957` | 汉维科技 | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) | P(endpoint_found) |

### 4.3 6/6 主源失败（BSE · 8 家）

- `832317` 观典防务（prefix `83`）
- `832491` 奥迪威（prefix `83`）
- `832876` 慧为智能（prefix `83`）
- `833266` 生物谷（prefix `83`）
- `835174` 五新隧装（prefix `83`）
- `839680` *ST广道（prefix `83`）
- `839729` 永顺生物（prefix `83`）
- `870656` 海昇药业（prefix `87`）

### 4.4 主源全过（BSE · 11 家，92xxxx）

- `920023` *ST田野
- `920035` 精创电气
- `920050` 爱舍伦
- `920145` 恒合股份
- `920160` 北矿检测
- `920339` 恒太照明
- `920367` 新赣江
- `920663` 明阳科技
- `920729` 永顺生物
- `920866` 绿亨科技
- `920957` 汉维科技

### 4.5 仅 top_float empty_but_valid

- `920186` 中科仪 — HTTP 200 · records=[]（符合 §6 股东 empty 口径，非 endpoint 不可用）

### 4.6 *ST / 名称异常

- `839680` *ST广道 — 83xxxx · 6/6 fail（HTTP 500）
- `920023` *ST田野 — 92xxxx · **6/6 pass**（*ST 不必然失败，与代码代际相关）

### 4.7 orgId / 重复公司可疑

- **`永顺生物` 重复：** `839729`（6/6 fail）与 `920729`（6/6 pass）共用 **同一 orgid `gfbj0839729`** — 样本需清洗，旧代码应剔除或映射至 920 代码

| orgid | codes |
|-------|-------|
| `gfbj0839729` | 839729 永顺生物, 920729 永顺生物 |

## 5. 跨板块对比（主判定 6 源）

| board | sample | cases | pass | fail | reachability% | http_error | empty_but_valid | blocked | valid_empty |
|-------|--------|-------|------|------|---------------|------------|-----------------|---------|-------------|
| `bse` | 20 | 120 | 71 | 49 | 60.0% | 45 | 1 | 3 | 0 |
| `chinext` | 45 | 270 | 270 | 0 | 100.0% | 0 | 0 | 0 | 0 |
| `sse_main` | 57 | 342 | 330 | 12 | 96.5% | 12 | 0 | 0 | 0 |
| `star` | 25 | 150 | 148 | 2 | 100.0% | 0 | 2 | 0 | 3 |
| `szse_main` | 48 | 288 | 282 | 6 | 97.9% | 5 | 0 | 1 | 0 |

**非 BSE 合计：** 175 家 · 1050 主判定 cases · pass **98.1%** · fail 20 · http_error 17 · blocked 1

## 6. Summary 模板修正说明

已对 [cninfo_c_class_scale_smoke_200_active_summary.md](cninfo_c_class_scale_smoke_200_active_summary.md) 做以下修正：

- Caveats：`30-company` → **195-company active sample**
- 「与上一轮含退市样本对比」标注为 **historical reference only**，不作为 200 live gate 依据

## 7. 下一步建议

### 7.1 是否将 BSE 从主 C-class scale gate 拆出？

**是（建议 split）。** 在 scode-only 统一路径下，BSE **旧代码层（83/87）与 920 层行为不一致**；应用 **BSE-920 active 子宇宙**（~12 家）单独 gate，旧代码层标记为 `legacy_code_incompatible` 而非 endpoint 失败。

### 7.2 非 BSE 是否可进入 1000-like sample planning？

**CONDITIONAL YES。** 非 BSE 主判定 pass **98.1%**；需先清洗样本中 **600065 / 600978 / 000405** 等 ST·异常状态公司（与 30 轮退市问题同类），再扩样。chinext **100%** pass 可作为扩样主力层之一。

### 7.3 dividend_history YAML backfill

- **non-BSE universe：GO（决策层）** — reachability 高 · valid_empty 可解释 · blocked/429 极低
- **full mixed universe（含 BSE 83/87）：HOLD** — 混合宇宙拉低 gate，且 dividend 与 basic 同受旧代码 500 影响
- **执行仍暂缓**（无 YAML 写入本轮）

### 7.4 是否需要 BSE-specific endpoint / parameter？

**需要 targeted probe，不是全量重跑。** 假设：83/87 代码需不同 base URL、market 参数或 orgId+secCode 组合（类似 security `marketOverview`）。建议 **20 家 BSE 定向 DevTools probe**（每代码 1–2 请求），而非 195 全量重跑。

### 7.5 样本清洗

1. 剔除 **839729**（保留 **920729** 永顺生物）及同类 legacy 重复
2. 评估剔除 ***ST联谊 / *ST宜生 / ST鑫光***（HTTP 500，非 C-class 可扩展性信号）
3. 将 **920186 top_float empty** 按 §6 口径计 reachable

## 8. 红线

本轮仅只读 CSV/MD 分析 · **无 live** · **无 CNINFO** · 无 YAML backfill · 无 verified · 无 DB
