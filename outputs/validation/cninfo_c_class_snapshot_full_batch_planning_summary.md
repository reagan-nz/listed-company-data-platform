# CNINFO C-Class Snapshot Full Batch Planning Summary

_生成时间：2026-07-08_

> 863 家公司 snapshot full batch **规划摘要**。**本轮不执行 batch** · **无 CNINFO** · **normalized 只读**

**C-class 状态：** `HARVEST_COMPLETED_QA_ONGOING`

**Full batch plan：** [cninfo_c_class_snapshot_full_batch_plan.md](../../plans/cninfo_c_class_snapshot_full_batch_plan.md)

---

## 1. Snapshot Smoke 结论

| 项 | 结果 |
|----|------|
| 样本 | **10** 家（SSE/SZSE/ChiNext/STAR 覆盖） |
| snapshot_status | complete_with_caveat = **10** |
| failed | **0** |
| gate | **`snapshot_smoke_gate = PASS_WITH_CAVEAT`** |
| 18 模块 | 结构稳定，可泛化至 863 |
| schema issues | 4 条跨公司字段漂移（002267 partial · 688750 event_timeline），**非阻塞** |
| demo / smoke | 未互相覆盖 |

**结论：** builder PoC + smoke runner 路径已验证；可进入 full batch **规划**，执行需单独批准。

---

## 2. 10 家 → 863 家风险变化

| 维度 | smoke 10 | 863 full batch | 风险变化 |
|------|----------|----------------|----------|
| 板块覆盖 | 4 板块各 2–4 家 | 4 板块 125–281 家 | 低 — 结构已验证 |
| executive empty | 2/10 partial | **~9/863**（harvest QA） | 低 — 已知 empty_but_valid |
| share_capital empty | 1/10 financial partial | **~10/863** | 低 — 已知 |
| dividend empty | 3/10 partial | **~38/863** valid_empty | 中 — partial 率上升，非 failed |
| shareholder partial | 10/10 | **~863/863** | 无新变化 — 设计为 source_partial |
| technology not_available | 10/10 | **863/863** | 无变化 — 预期 |
| 磁盘 / 耗时 | <1 MB · <1 min | **~500–900 MB** · **15–45 min** | 运维注意 |
| status CSV 缺口 | 未暴露 | 10 家无 harvest_status 行 | 低 — 用 normalized 存在性兜底 |

**总体：** 风险从「schema 未知」降为「规模 + 已知 partial 放大」；无新增源类阻塞。

---

## 3. 预计问题

### 3.1 schema drift

- 数组模块 item 键因 `scope` / `dividend_parse_status` / empty 源略有差异（smoke 已观测）。
- 863 上 cross_company drift 检测噪音可能增大；建议 batch summary **抽样** 而非全量 hard-fail。

### 3.2 empty_but_valid

| 源 | harvest 计数 | snapshot 影响 |
|----|-------------|---------------|
| executive | 9 | executive_profile → partial |
| share_capital | 10 | financial_snapshot · capital_action → partial |
| top_shareholders | 15 | shareholder_profile → partial |
| top_float_shareholders | 18 | shareholder_profile → partial |
| dividend valid_empty | 38 | dividend_profile · event_timeline → partial |

**政策：** 不判 failed；与 QA `PASS_WITH_CAVEAT` 一致。

### 3.3 module missing

- `technology_profile`：**863** 家 `not_available`（无源，不补齐）。
- `market_behavior` · `investor_relation`：**863** 家预期 `partial`（observe_only / 与 organization 重叠）。

### 3.4 field alias

- 已知 alias 已在 builder 处理：`dividend_plan_text_raw` · `main_business` · `company_introduction` · `secCode` 等。
- 863 规模下 alias 遗漏若存在，表现为单公司 field 缺失 + module partial，**不**预期系统性 failed。

---

## 4. 是否建议 Full Batch

**建议：批准后在离线环境执行 full batch。**

| 项 | 判定 |
|----|------|
| 架构 | 18 模块稳定 |
| Builder | smoke 10 零 failed |
| Universe | 863 已 harvest，normalized 就绪 |
| 阻塞项 | **无** |
| 保留项 | partial / caveat 为产品预期，非 gate 失败 |

```
snapshot_full_batch_gate = PASS_WITH_CAVEAT
```

**说明：** 与 smoke gate 一致；`complete_with_caveat` 为 863 家预期主流 snapshot_status，**不**代表 batch 失败。

---

## 5. Builder 变更分析

```
builder_change_required: no
```

| 项 | 结论 |
|----|------|
| `build_snapshot()` | 单公司无状态，smoke 10 已复用 |
| 阻塞修改 | **不需要**改 `lab/build_cninfo_c_class_company_snapshot.py` |
| 执行层 | 需新建 **batch runner**（泛化 `run_cninfo_c_class_snapshot_smoke_10.py`） |

### 可选增强（非阻塞，执行前可议）

| issue | impact | recommended_fix |
|-------|--------|-----------------|
| 无 `metadata` 顶层块 | full plan 与 PoC 结构略异 | batch runner 写 JSON 前注入 `metadata`；或 builder 增加可选 `metadata` 参数 |
| 无 batch CLI | 无法单脚本跑 863 | 新建 `lab/run_cninfo_c_class_snapshot_full_batch.py` |
| `detect_schema_issues` 过简 | 863 难发现系统性问题 | batch runner 增加 cross_company drift 抽样 |
| 无 `failed` snapshot_status | basic 缺失时仍可能抛异常 | batch runner `try/except` + status CSV（不改 core builder） |

---

## 6. 执行清单（待批准，本轮不做）

1. 实现 `run_cninfo_c_class_snapshot_full_batch.py`
2. 初始化 `company_snapshot_status.csv`（863 行 pending）
3. `--write --universe harvest_863_non_bse --out-dir full/ --resume`
4. 生成 `snapshot_quality_summary.md` + gate 判定
5. 更新 `CURRENT_STATUS.md` / `eraC_execution_plan.md`

---

## 7. 红线确认

- 未请求 CNINFO · 未重跑 harvest · **未执行** full batch
- raw / normalized / field_inventory **未修改**
- 未入库 / MinIO / RAG · 未写 verified · 未升级 testing_stable_sample
