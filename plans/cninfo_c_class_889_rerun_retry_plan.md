# CNINFO C-Class 889 Rerun — Partial-Fail Targeted Retry Plan（Era C Phase 4）

_生成时间：2026-07-07_

> **目的：** 基于 [889 rerun diagnosis](../outputs/validation/cninfo_c_class_889_non_bse_rerun_diagnosis.md) 派生 **all6 hold** 与 **partial-fail targeted retry** 子集；**本轮仅 plan + dry-run/preflight**；**不跑 live**；**不请求 CNINFO**；**非 verified**；**非 testing_stable_sample**。

**前置：** [889 rerun plan](cninfo_c_class_889_non_bse_rerun_plan.md) · [889 rerun diagnosis](../outputs/validation/cninfo_c_class_889_non_bse_rerun_diagnosis.md)

---

## 一、Why 26 家 All6 Hold（不直接 retry）

| 维度 | 说明 |
|------|------|
| 规模 | **26** 家 · 六主源 **6/6 全失败** |
| 与 stable 200 十二家 | **无重叠**（十二家已在 stable rerun 中恢复） |
| 主因 | **HTTP 500 / `json_code=9240002`**（非 schema_unexpected） |
| 名称特征 | 多为 *ST / 退市 / 重组残留（如宏源证券、中银绒业等） |
| 判定 | **sample_quality_or_status_review** — 非 runner/parser 缺陷 |
| 决策 | **hold_no_retry** — 不清洗母本、不扩样本剔除 |

**为何不 retry：**

1. 全源同时失败且以服务端 500/9240002 为主，retry 大概率重复失败，浪费配额。
2. 与 stable 200 已验证的「限流/backoff 可恢复」模式不同；此处更像 **标的上市状态 / CNINFO 侧不可用**。
3. 保留在 hold 子集便于审计与后续人工 status review，**不阻塞** partial-fail retry 主线。

**样本：** `lab/eval_companies_c_class_889_rerun_all6_hold.yaml`（**26** 家）

---

## 二、Why Partial-Fail 需要 Targeted Retry

| 维度 | 说明 |
|------|------|
| 规模 | **41** 家（1–4 主源 fail，排除 26 家 all6） |
| 模式 | 单源 fail **26** · 多源 partial **15** |
| 与 stable 200 | 含 stable 200 十二家中已恢复的 **4** 家 chinext partial（executive+share empty_but_valid） |
| 主因分布 | http_error · blocked · empty_but_valid（executive/share） |
| 预期收益 | 隔离 **瞬时 HTTP/DNS**（如 688750）与 **合法空 records 语义确认**；验证 backoff 在子集是否足够 |

**为何不 rerun 889 全量：**

- 889 主宇宙 **97%+** 主源 reachability 已达成；剩余 fail 集中在 **67** 家公司级簇。
- 全量重跑成本高、对 harvest 决策增益有限；**targeted retry** 更精准。

**样本：** `lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml`（**41** 家）

### retry_priority 规则（已写入 YAML）

| 优先级 | 条件 | 本批数量 |
|--------|------|----------|
| **high** | blocked / http_error 涉及 basic · dividend · top_sh · top_float | **4** |
| **medium** | executive / share_capital partial fail；或 empty_but_valid 仅涉及 executive+share | **37** |
| **low** | empty_but_valid 仍判 fail、需语义确认 | **0**（本批无独立 low 簇） |

### Board 分布（partial-fail retry）

| board | count |
|-------|-------|
| chinext | **36** |
| star | **2** |
| szse_main | **2** |
| sse_main | **1** |

---

## 三、本轮红线

| 项 | 状态 |
|----|------|
| 889 全量重跑 | **不做** |
| C-class harvest | **暂停** |
| live CNINFO | **不做**（本轮） |
| YAML backfill | **不执行** |
| 入库 / verified | **不做** |
| testing_stable_sample 升级 | **不做** |
| 新 endpoint discovery | **不做** |
| runner pacing 调整 | **暂不调**（90001/429 已吸收；9240002 非 pacing 主因） |

---

## 四、样本 Preflight（partial-fail retry）

| 检查项 | 预期 | dry-run 结果 |
|--------|------|--------------|
| company_count | **41** | **41** ✓ |
| 与 26 家 all6 hold 重叠 | **0** | **0** ✓ |
| planned cases | **41 × 7 = 287** | **287** ✓ |
| CNINFO 请求 | **0** | **0** ✓ |
| pre_dryrun_validation | PASS | **PASS** ✓ |

**命令：**

```bash
python lab/validate_cninfo_c_class_scale_smoke.py --dry-run \
  --sample-file lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml
```

**输出：**

- [dryrun_report.csv](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_dryrun_report.csv)
- [dryrun_summary.md](../outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_dryrun_summary.md)

---

## 五、Planned Live（待人工批准）

| 维度 | 数量 |
|------|------|
| companies | **41** |
| sources per company | **7**（6 主判定 + security observe） |
| **total cases** | **287** |
| 预计 HTTP 请求 | **287**（live 时） |

**Live 命令（未执行）：**

```bash
python lab/validate_cninfo_c_class_scale_smoke.py --live \
  --sample-file lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml
```

**预期输出命名：**

- `outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_live_report.csv`
- `outputs/validation/cninfo_c_class_889_rerun_partial_fail_retry_live_summary.md`

---

## 六、Post-Retry Gate（规划）

1. **partial-fail retry live** 完成后做 post-live diagnosis（同 889 rerun 口径）。
2. 若 residual fail 可解释（empty_but_valid 集中、个别 DNS 瞬态）→ 评估是否 **恢复 harvest 规划**。
3. 26 家 all6 hold **维持 hold**；不自动回流 partial retry。
4. dividend_history YAML backfill 仍为 **GO（决策 only）** — retry 后再评估是否执行。

---

## 七、相关文件

| 类型 | 路径 |
|------|------|
| all6 hold 样本 | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` |
| partial-fail retry 样本 | `lab/eval_companies_c_class_889_rerun_partial_fail_retry.yaml` |
| 母本 | `lab/eval_companies_c_class_smoke_1000_non_bse_candidate.yaml` |
| diagnosis | `outputs/validation/cninfo_c_class_889_non_bse_rerun_diagnosis.md` |
| failure cases | `outputs/validation/cninfo_c_class_889_non_bse_rerun_failure_cases.csv` |
| runner | `lab/validate_cninfo_c_class_scale_smoke.py` |

---

## 八、决策摘要

| 问题 | 决策 |
|------|------|
| 26 家 all6 是否 retry？ | **否** — hold_no_retry |
| 41 家 partial-fail 是否 retry？ | **是（待批准 live）** |
| 本轮是否跑 live？ | **否** — dry-run only |
| harvest？ | **暂停** — targeted retry 后再定 |
| pacing？ | **暂不调** |

**下一步：** **等待人工批准**后执行 partial-fail targeted retry `--live`。
