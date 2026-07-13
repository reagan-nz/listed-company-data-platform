# Era D 执行计划（本地稳定抽取 · 不入库 · 四线并行）

_最后更新：2026-07-10_

> **前序：** [eraC_execution_plan.md](eraC_execution_plan.md)（A–F 分层验证 / 试点收口 · 基本收束）  
> **仓库导航：** [PROJECT_MAP.md](../PROJECT_MAP.md) · **当前进展：** [CURRENT_STATUS.md](../CURRENT_STATUS.md)  
> **权威分类：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)
>
> **Era D 只做本地稳定抽取与落盘**；**不研究 DB / MinIO / 产品入库**（延后到后续 Era）。  
> **可四线并行（A/B/C/D 各一 agent）**；单线内仍按 gate 顺序，不跳过 dry-run / 批准 / closure。
>
> **双 Era 并行（2026-07-10 起）：**
> - **B / C → 进入 Era D**（本地扩规模 / resume 硬化；不因 Case B 落地而停线）
> - **A / D → 继续收完 Era C 尾巴**（A3M017 boundary→commit；disclosure closure→boundary→commit）
> - 工作流不变：人发运行结果 → Prompt Manager 写下一条提示词
> - 四线仍互不踩对方 live 根；入库一律延后

---

## 0. Era D 完成定义

### 0.1 一句话

在 **不接库、不写 verified** 的前提下，把 A/B/C/D 的抽取做成：**可重复、可 resume、失败可隔离重试、产物稳定落在本地 `outputs/`**，规模从 Era C 试点抬到「接近全市场可用」的本地样本层。

### 0.2 验收（完整 Era D）

| 线 | 验收标准（本地 only） |
|----|----------------------|
| **C** | 约定 universe（优先 863 non-BSE 或 registry 批准集）本地 harvest + snapshot **可全量重跑 / resume**；清理不误删生产产物；QA/holdout 有闭环 |
| **A** | 定期报告 metadata + URL lineage 扩到 **数百级**（目标 200→500，视网络与 orgId 稳定性）；本地 raw_metadata + ledger 完整 |
| **B** | 公告 metadata + URL lineage 扩到 **数百级**（目标 200→500）；inventory/sidecar 不被测试清理误删 |
| **D** | **≥3 个组件** 完成 first-slice 以上扩样（每组件 ≥20 家或等价预算）；本地 live_snapshots + reports |
| **横切** | 本地目录约定、保留策略、批量 runner/resume、四线互不踩根；**无 DB/MinIO/RAG/verified** |

### 0.3 MVP（可先收一刀）

| 项 | MVP 标准 |
|----|----------|
| C | resume/cleanup 硬化 + 至少一轮更大 batch 或全量重跑演练（本地） |
| A | 扩到 **~200** metadata 本地稳定 |
| B | 扩到 **~200** metadata 本地稳定 |
| D | disclosure_schedule 收口入库文档级 commit（若需要）+ **再 1 个组件** 扩到 ≥20 或保持多切片 ≥10 |
| 横切 | 《本地产出目录与保留策略》文档 + 四线并行工作约定 |

### 0.4 明确不做（本 Era）

- PostgreSQL / MinIO / MongoDB / 任何产品入库
- PDF 正文下载 / 解析 / OCR / 章节抽取（除非另开人批子轨）
- `verified` / `production_ready` / 升级 `testing_stable_sample` 为产品结论
- 用混杂 `main` 强推远端；远端发布另议，不阻塞本地抽取

### 0.5 与 Era C / 全市场口径的关系

| 口径 | Era C 末 | Era D 目标末（估） |
|------|----------|-------------------|
| 试点收口（流程打通） | ~96–98% | 维持 / 归档 |
| **本地稳定抽取**（本 Era） | ~25–35% 起步 | **MVP ~55–65% · 完整 ~70–80%**（相对本 Era 定义） |
| 全市场稳定抽取+**入库** | ~28–35% | Era D 后预计 ~45–55%（仍无入库） |

---

## 1. 红线

- **不接** PostgreSQL / MinIO / MongoDB；不写 migration；不研究入库方案（可列「延后」一句，不展开）。
- **不下载 / 不解析** PDF 正文；不做 OCR / 章节抽取（除非用户对子轨显式批准）。
- **不写** `verified` / `production_ready`；不把 `PASS_WITH_CAVEAT` 写成裸 `PASS`。
- 不绕过登录/验证码/付费/权限；请求间 sleep；不用 BrowserUser。
- **四线并行时：** 各线只改本线 runner/outputs/plans；**禁止**互相改对方 live 根与已收口报告。
- 测试 cleanup **不得删除** 生产 live sidecar / snapshot / raw_metadata。
- 联网 live 必须显式人批；默认 dry-run / offline。
- 不 force push；不把混杂本地 `main` 当作发布载体（发布另轨）。

---

## 2. Phase 路线图

> Era C 早期是「严格单 Phase」；Era D 改为 **横切 Phase + 四线并行轨**。  
> **同一条线内**仍一次只推一个 gate；**线与线之间**可四 agent 并行。

| Phase | 内容 | 状态 | 主要产出 |
|---|---|---|---|
| **D0** | Era D 范围冻结 + 本地落盘约定 + 并行工作约定 | **进行中** | 本文件 · 本地目录策略 · 并行约定 |
| **D1** | 稳定性底座（resume / cleanup / 目录 / 预算帽） | 未开始 | hardening 包 · 测试 · 策略文档 |
| **D2-MVP** | 四线并行扩到 MVP 规模（见 §0.3） | 未开始 | 各线 expansion live + 本地产物 |
| **D3** | 完整验收规模（见 §0.2） | 未开始 | 近全市场 C + A/B 数百 + D 多组件扩样 |
| **D4** | Era D 收口（本地 only） | 未开始 | eraD closure summary · 明确「入库 = 下一 Era」 |

---

## 3. Phase D0 — 范围冻结与并行约定（当前）

### 3.1 继承自 Era C 的可用底座（不重做）

| 线 | 已具备（摘要） | Era D 起点 |
|----|----------------|------------|
| **A** | Phase 3 有效 **50/50**（含 A3M017 retry）；metadata + URL lineage；`bbc15c3` 历史保留 | 扩规模 + 本地稳定；retry 产物 boundary/commit 可并行收尾 |
| **B** | Phase 3 **100/100** · inventory **763/763** · 已在 `origin/main`（Case B） | 扩规模；10 network_error 可选；cleanup 硬化保持 |
| **C** | **863** harvest 经验 · Phase 3.5 **491** snapshot · holdout 9 closed-with-caveat · 已在 `origin/main` | resume/全量重跑硬化 + 更大/更稳本地 batch |
| **D** | known-event 收口 · margin_trading 5/5 · disclosure_schedule live 5/5 | closure/boundary 收尾 + 下一组件 + 扩样 |

### 3.2 本地落盘约定（D0 必须写清）

| 根 | 用途 | 备注 |
|----|------|------|
| `outputs/validation/cninfo_*` | 验证 live / ledger / closure | 按线隔离目录名 |
| `outputs/harvest/cninfo_c_class/` | C harvest raw/normalized | 大文件；gitignore 策略保持 |
| `outputs/snapshot/` | C snapshot JSON | **默认不入库 git**；本地保留 |
| `lab/` · `plans/` · `schemas/` | runner / 计划 / schema | 可提交；与大产物分离 |

**保留策略原则：**

1. live 成功产物默认保留，直到该轨正式 closure + 人批清理。  
2. 测试临时目录必须与生产根分离。  
3. 禁止「全目录 rm」式 teardown 扫到生产 sidecar。

### 3.3 四 agent 并行约定

| Agent | 默认负责 | 禁止 |
|-------|----------|------|
| Agent-A | A-class 扩规模 / retry 收尾 | 改 B/C/D live 根 |
| Agent-B | B-class 扩规模 / network_error 可选轨 | 改 A/C/D live 根 |
| Agent-C | C-class resume / harvest / snapshot 本地稳定 | 改 A/B/D live 根 |
| Agent-D | D-class 组件扩样 | 改 A/B/C live 根 |

**共享文件（`CURRENT_STATUS.md` / `PROJECT_MAP.md` / `eraD_execution_plan.md`）：**

- 各 agent 只追加本线小节；冲突时人工合并。  
- 或由 Prompt Manager 统一收口 status（推荐）。

**Git：**

- 优先 **每线独立分支**（如 `a-class-erad-scale-200`），避免四线抢同一 working tree。  
- 远端发布仍可选；**不阻塞**本地抽取验收。

### 3.4 D0 产出清单

1. ✅ 本文件 `plans/eraD_execution_plan.md`（初版）  
2. ⬜ `plans/eraD_local_output_retention_policy.md`（本地保留/清理）  
3. ⬜ `plans/eraD_parallel_agent_work_agreement.md`（可与本 §3.3 合并精简）  
4. ⬜ 更新 `CURRENT_STATUS.md` / `PROJECT_MAP.md`：标注 Era D 启动、入库延后  

**D0 gate（建议）：** `era_d_scope_freeze_gate = READY_FOR_APPROVAL` → 人确认后 `PASS_WITH_CAVEAT`

---

## 4. Phase D1 — 稳定性底座（建议先于大规模 live）

每条线至少完成与本线相关的子集；可四线并行改各自 runner/测试。

| 项 | 内容 | 完成判据 |
|----|------|----------|
| D1.1 | 测试 cleanup 硬化（B 已有经验推广到 A/C/D） | 测试不得删生产 live/snapshot |
| D1.2 | resume / 断点续跑（C 优先；A/B 大批量后补） | dry-run + 文档说明 |
| D1.3 | 请求预算帽 / sleep / 隔离输出根 | 与现有 cap 一致并文档化 |
| D1.4 | 失败分流：network_error / needs_review / holdout | ledger 模板统一 |
| D1.5 | 本地磁盘与大文件提示（snapshot/harvest） | 策略文档，不接对象存储 |

**D1 gate：** `era_d_stability_foundation_gate = PASS_WITH_CAVEAT`（完成后）

---

## 5. Phase D2 — MVP 扩规模（四线并行）

### 5.1 建议目标（可调）

| 线 | MVP 目标 | 预估 CNINFO 量级（粗） | 依赖 |
|----|----------|------------------------|------|
| **C** | resume 硬化 + 863 或 491 重跑/补洞演练（本地） | 视缺口；可分日 | D1.2 |
| **A** | metadata 扩至 **~200** | 数百请求级（含 orgId） | 人批 live |
| **B** | metadata 扩至 **~200** | 数百请求级 | 人批 live |
| **D** | disclosure closure/boundary 收尾 + 下一组件 first-slice 或扩样 | 数十请求级 | 人批 live |

### 5.2 单线标准流水（与 Era C 相同纪律）

```text
planning (offline)
→ runner extension + dry-run (CNINFO=0)
→ live-path (offline, mock)
→ human approve live
→ isolated live
→ closure (offline)
→ commit boundary (offline)
→ commit (explicit paths only, optional)
→ （远端发布可选，不阻塞 Era D 验收）
```

### 5.3 MVP 完成定义

- 四线均达到 §0.3；  
- 全部产物在本地可定位；  
- 无 DB/MinIO；无 verified；  
- `era_d_mvp_gate = PASS_WITH_CAVEAT`

---

## 6. Phase D3 — 完整规模（本地近全市场）

| 线 | 完整目标 | 备注 |
|----|----------|------|
| **C** | 约定全量 universe 本地 harvest/snapshot 稳定可重跑 | 持 holdout 政策；不强制开 PDF |
| **A** | **~500** 或「非 BSE 活跃集」定期报告 metadata | 网络失败走隔离重试，不阻塞整轨 |
| **B** | **~500** 公告 metadata | 类别路由保持；PDF 仍默认关 |
| **D** | **≥3 组件** × 扩样（≥20/组件或总预算等价） | 不升级 disclosure→captured_normal 除非另批 |

**D3 gate：** `era_d_full_local_scale_gate = PASS_WITH_CAVEAT`

---

## 7. Phase D4 — Era D 收口

产出：

- `outputs/validation/era_d_closure_summary.md`
- `outputs/validation/era_d_local_artifact_index.md`（各线本地根索引）
- `outputs/validation/era_d_deferred_ingestion_notes.md`（**仅一页**：入库延后到下一 Era，不展开设计）

明确声明：

- Era D **不**包含入库；  
- 下一 Era（建议名 Era E）才启动 DB/MinIO/verified 研究。

**D4 gate：** `era_d_closure_gate = PASS_WITH_CAVEAT`

---

## 8. 工期与四 agent 并行（回答「会不会更快」）

### 8.1 参照

| 历史 | 条件 | 墙钟 |
|------|------|------|
| 全市场 24 年报抽取（你方经验） | **单 agent** | **约 1 周** |
| Era C 试点收口（A–D 流程） | 多线交错 + 大量 gate | 已基本完成 |

### 8.2 Era D 粗估（墙钟）

| 档位 | 单 agent 串行 | **四 agent 并行**（A/B/C/D） |
|------|---------------|------------------------------|
| **D0+D1** | 2–4 天 | **1–2 天** |
| **D2 MVP** | 1.5–3 周 | **约 3–7 天**（常接近「一周内」） |
| **D3 完整** | 4–8 周 | **约 1.5–3 周** |
| **D4 收口** | 1–2 天 | **0.5–1 天** |

### 8.3 结论（直接回答）

**会更快，而且 MVP 很有希望压到「一周左右墙钟」**——接近你当年单 agent 做全市场年报的量级，但内容换成「四线本地稳定扩规模」。

完整 Era D（近全市场 C + A/B 数百 + D 多组件）并行后大约 **两到三周**，仍可能短于串行的一两个月。

### 8.4 并行加速的上限（别按 ×4 线性）

| 因素 | 影响 |
|------|------|
| **CNINFO 限流 / 网络** | 四线同时 live 可能互相抢配额 → 建议错峰或分日 live |
| **人批 gate** | live / commit 仍要你点批准 → 墙钟常卡在人，不卡在 agent 数 |
| **共享文件冲突** | `CURRENT_STATUS` / 公共 runner → 用分线分支 + Prompt Manager 收口 |
| **磁盘与大文件** | C snapshot/harvest 最大 → C 线单独机器/目录更稳 |
| **同文件改 runner** | A/B 若共用框架文件需串行合并 |

**经验法则：** 四 agent 对 **offline 规划/dry-run/closure/boundary** 接近 3–4×；对 **同时 live** 大约只有 1.5–2.5×。整体墙钟常见 **约 2–3×** 于单 agent，而不是满 4×。

### 8.5 推荐并行排期（第一周 MVP）

| 日 | Agent-A | Agent-B | Agent-C | Agent-D |
|----|---------|---------|---------|---------|
| D0 | 读 Era D 计划 / A 收尾 boundary | B 可选 network_error 规划 | C resume 硬化规划 | disclosure closure |
| 1 | A-200 planning+dry-run | B-200 planning+dry-run | C hardening 实现+测试 | disclosure boundary |
| 2 | A live-path | B live-path | C dry-run 重跑演练 | 下一组件 planning |
| 3 | **A live**（人批） | **B live**（人批，可错峰） | C 小补洞 live（人批） | 下一组件 dry-run |
| 4–5 | A closure | B closure | C QA/closure | 组件 live+closure |
| 6–7 | 缓冲 / 失败隔离重试 | 同左 | snapshot 保留检查 | D MVP 收口 |

---

## 9. 当前状态与下一步

### 9.1 当前

- Era C：试点收口基本完成（A/B/C 远端或本地证据已齐；D disclosure **`d37ce0a`** · margin **`116f875`**）。  
- **D 类 Era D：** next-component planning **完成**（primary **`block_trade`** · gate **`READY_FOR_APPROVAL`** · CNINFO **0**）。
- **C 类 Phase 3.5：** `a12d5fb`+`522c89b` on **`origin/main`** · Case B accepted · `phase35_clean_push_gate = PASS_WITH_CAVEAT` · **remote landing closed**。  
- **B 类 Phase 3：** `5f29ae6`+`cb6ffcb` on **`origin/main`** · Case B accepted · clean-push gate **`PASS_WITH_CAVEAT`** · **remote landing closed**。  
- Era D：本计划初版已写；**C 类 Era D Slice-C-EraD-01 cleanup hardening 完成**（[summary](../outputs/validation/cninfo_c_class_erad_cleanup_hardening_summary.md) · **35/35 PASS** · gate **`PASS_OFFLINE`**）；resume/stability 规划包 gate **`READY_FOR_APPROVAL`**；**D0 尚未人签**。  
- 进度（相对 Era D 定义）：**约 10–15%**（C 线 D1 硬化 offline 完成）。

### 9.2 下一步（双 Era 并行 · 现行）

| Agent | Era | 现行下一步 |
|-------|-----|------------|
| **B** | **D** | Human approve **explicit-path commit** · [boundary summary](../outputs/validation/cninfo_b_class_erad_scale_200_commit_boundary_summary.md) |
| **C** | **D** | C-class Era D **continues** · [slice1 live path](outputs/validation/cninfo_c_class_erad_fuller_market_slice1_live_path_summary.md) · gate **`READY_FOR_APPROVAL`** · 待人批 live |
| **A** | **C** | A3M017 isolated-retry **commit boundary**（offline）→ 再 commit |
| **D** | **C** | disclosure_schedule closure→boundary→commit **`d37ce0a`** → **Era D next-component planning**（**完成**） |

横切（可稍后）：

1. 人确认 Era D 范围（§0 + 红线 §1）→ `era_d_scope_freeze_gate`（不阻塞 B/C 先开规划包）  
2. 补 D0 保留策略短文档  
3. A/D 的 Era C 尾巴收完后，再切同一 agent 进 Era D（A→200；D→**block_trade** approval package）  
4. 入库相关 **一律不开**
5. **portrait_ontology 横切轨 P0–P3 已完成**（offline · 见 §9.10）· 不阻塞四线 live

### 9.10 横切 — portrait_ontology（2026-07-10）

> **offline complete** · **无 CNINFO** · **无 live** · **无 DB** · **无 verified**

| 项 | 内容 |
|----|------|
| ontology plan | [company_portrait_ontology_plan.md](company_portrait_ontology_plan.md) |
| module index | [company_portrait_module_index.csv](../outputs/validation/company_portrait_module_index.csv)（**18** 模块） |
| field catalog v0 | [company_portrait_field_catalog_v0.csv](../outputs/validation/company_portrait_field_catalog_v0.csv)（**715** 字段） |
| coverage matrix v0 | [company_portrait_coverage_matrix_v0.csv](../outputs/validation/company_portrait_coverage_matrix_v0.csv) |
| coverage summary | [company_portrait_coverage_summary.md](../outputs/validation/company_portrait_coverage_summary.md) |
| local layout | [company_portrait_local_layout.md](company_portrait_local_layout.md) |
| schemas | [schemas/portrait/](../schemas/portrait/)（fact_record · evidence_ref） |
| pilot | `outputs/portrait/companies/000009/` · [pilot summary](../outputs/validation/company_portrait_pilot_fill_summary.md)（**36** facts · **14** field_ids） |
| builder | `lab/build_company_portrait_ontology.py` · `lab/fill_company_portrait_pilot.py` |
| p0 catalog gate | **`portrait_p0_catalog_gate = PASS_OFFLINE`** |
| p1 coverage gate | **`portrait_p1_coverage_gate = PASS_OFFLINE`** |
| p2 schema gate | **`portrait_p2_schema_gate = PASS_OFFLINE`** |
| p3 pilot gate | **`portrait_p3_pilot_gate = PASS_OFFLINE`** |

**交付纪律（P4）：** 四线后续 closure/summary 建议追加一句「本批触及的 `field_id` 列表」；扩规模 live **不因 ontology 停**；ontology 用已有产物只读回填。

**下一步：** 用覆盖缺口指导 Era D 下一刀（优先补 M01 basic harvest 缺口）；全市场 portrait 批量生成 **延后**。

### 9.4 C 类 Era D — Resume / Stability（2026-07-10）

> **Option A HOLD signoff accepted** · **58 triage complete** · **C-line continues** · **Era D not finished** · **无 live** · **无 snapshot rebuild**

| 项 | 内容 |
|----|------|
| plan | [cninfo_c_class_erad_resume_stability_plan.md](cninfo_c_class_erad_resume_stability_plan.md) |
| Option A signoff | [cninfo_c_class_erad_option_a_hold_signoff.md](cninfo_c_class_erad_option_a_hold_signoff.md) · **ACCEPTED** |
| 58 triage | [triage summary](../outputs/validation/cninfo_c_class_erad_needs_review_58_triage_summary.md) · live_needed **0/58** |
| retention | [local retention policy](../../plans/cninfo_c_class_erad_local_retention_policy.md) · [artifact index](../outputs/validation/cninfo_c_class_erad_local_artifact_index.md) |
| protected roots | [cninfo_c_class_erad_protected_output_roots.csv](../outputs/validation/cninfo_c_class_erad_protected_output_roots.csv)（**12** rows） |
| approval | [readiness checklist](../outputs/validation/cninfo_c_class_erad_snapshot_rebuild_readiness_checklist.md) · **`ACCEPTED_HOLD`** |
| Phase 3.5 remote | **closed** on `origin/main`（`a12d5fb`+`522c89b`） |
| holdout | **9** closed-with-caveat · no promotion |
| cleanup hardening gate | **`PASS_OFFLINE`** |
| harvest resume audit gate | **`PASS_OFFLINE`** |
| snapshot rebuild readiness gate | **`PASS_WITH_CAVEAT`**（Option A HOLD） |
| option A hold signoff gate | **`PASS_WITH_CAVEAT`** |
| needs_review triage gate | **`PASS_OFFLINE`** |
| status-fix-8 gate | **`PASS_OFFLINE`** |
| status-fix-8 apply gate | **`PASS_WITH_CAVEAT`**（**8/8 appended** · backup on disk） |
| partial-6 human-review gate | **`PASS_OFFLINE`**（needs_live_resume **0/6**） |
| local retention gate | **`PASS_OFFLINE`**（ED-002 policy + index） |
| post-fix8 harvest audit gate | **`PASS_OFFLINE`**（**813+50** · Δ needs_review **−8**） |
| needs_review 50 closure gate | **`PASS_OFFLINE`**（live_needed **0/50** · scale-ready **863/863**） |
| fuller-market planning gate | **`READY_FOR_APPROVAL`**（slice1 **+200** CE1E001–200 · **NOT APPROVED live**） |
| slice1 dry-run prep gate | **`PASS_OFFLINE`**（YAML **200** · harvest dry-run **1400** HTTP · CNINFO **0**） |
| slice1 live path gate | **`READY_FOR_APPROVAL`**（`_run_live_fuller_market_slice1` · tests **12/12** · **NOT executed live**） |

**approved_for_snapshot_rebuild = false** · **approved_for_live_resume = false**

**下一步：** 人批 slice1 live harvest（verbatim 短语）· 执行 session 1 `--limit 100` · Era D **not finished**

---

### 9.5 B 类 Era D — ~200 Metadata Expansion（2026-07-10）

> **explicit-path commit complete** · **198/200 caveat** · **NOT pushed** · **NOT verified**

| 项 | 内容 |
|----|------|
| effective | **198/200** · unresolved **2**（BD2E090/BD2E092 · `network_error`） |
| commit | **`e738fa9`** · **30 files** · [commit status](../outputs/validation/cninfo_b_class_erad_scale_200_commit_status.md) |
| excluded bulk | raw_metadata **200** · quality **200**（local-only · not committed） |
| commit gate | **`b_class_erad_scale_200_commit_gate = PASS_WITH_CAVEAT`** |
| closure gate | **`PASS_WITH_CAVEAT`** |
| unresolved ledger | [ledger](../outputs/validation/cninfo_b_class_erad_scale_200_unresolved_case_ledger.csv) |

**下一步：** human-approved push（separate phrase）· optional BD2E090/BD2E092 retry（deferred）· **next-scale planning complete**

---

### 9.5a B 类 Era D — Next-Scale Slice1 Merge Closure（2026-07-10）

> **merge closure complete** · **300/300 effective** · cumulative **498** · **NOT verified** · **NOT pushed**

| 项 | 内容 |
|----|------|
| live | S1+S2 **300/300** · CNINFO **600** · [execution summary](../outputs/validation/cninfo_b_class_erad_next_scale_slice1_live_execution_summary.md) |
| merge closure | [summary](../outputs/validation/cninfo_b_class_erad_next_scale_slice1_merge_closure_summary.md) · effective **300/300** · edge **9** |
| cumulative | scale-200 **198** + slice1 **300** → **498** toward ~500 |
| execution gate | **`b_class_erad_next_scale_slice1_execution_gate = PASS_WITH_CAVEAT`** |
| merge closure gate | **`b_class_erad_next_scale_slice1_merge_closure_gate = PASS_WITH_CAVEAT`** |
| commit boundary gate | **`b_class_erad_next_scale_slice1_commit_boundary_gate = READY_FOR_COMMIT_REVIEW`** |
| scale-200 lineage | **198/200** · **no rerun** · BD2E090/092 side-track only |

**下一步：** human approve slice1 explicit-path commit · or hold closed-with-caveat

---

### 9.6 A 类 Era D — ~200 Metadata Expansion（2026-07-10）

> **explicit-path commit complete** · **`41dc049`** · effective **192/200** · unresolved **8** · **NOT pushed**

| 项 | 内容 |
|----|------|
| plan | [cninfo_a_class_erad_scale_200_plan.md](cninfo_a_class_erad_scale_200_plan.md) |
| live execution | [execution summary](../outputs/validation/cninfo_a_class_erad_scale_200_execution_summary.md) · **192/200** · CNINFO **423** |
| execution gate | **`a_class_erad_scale_200_execution_gate = PASS_WITH_CAVEAT`** |
| merge closure gate | **`a_class_erad_scale_200_merge_closure_gate = PASS_WITH_CAVEAT`** |
| explicit-path commit | **`41dc049`** · **47 files** |
| commit gate | **`a_class_erad_scale_200_commit_gate = PASS_WITH_CAVEAT`** |
| track status | **CLOSED with caveat** · bulk raw_metadata local-only |

**下一步：** see §9.6a next-scale planning

---

### 9.6a A 类 Era D — Next-Scale Planning + Slice1 Runner + Live Path（2026-07-10）

> **runner + dry-run + live-path mock complete** · slice1 **+300** · CNINFO **0** in tests · **NOT APPROVED live**

| 项 | 内容 |
|----|------|
| plan | [cninfo_a_class_erad_next_scale_plan.md](cninfo_a_class_erad_next_scale_plan.md) |
| primary path | **C) staged 200→500→fuller + daily caps** |
| universe strategy | [strategy](../outputs/validation/cninfo_a_class_erad_next_scale_universe_strategy.md) |
| candidate universe | [draft](../outputs/validation/cninfo_a_class_erad_next_scale_candidate_universe_draft.csv) · **300** rows · AD2E201–500 |
| request budget | [budget](../outputs/validation/cninfo_a_class_erad_next_scale_request_budget.md) · est **~630** · cap **≤720** |
| overlap vs scale-200 | **0** |
| overlap vs B slice1 | **0** |
| planning gate | **`a_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL`** |
| runner | `--erad-a-scale-500-slice1` · [runner extension summary](../outputs/validation/cninfo_a_class_erad_next_scale_slice1_runner_extension_summary.md) |
| dry-run | **300/300 planned_ok** · **600** planned requests · CNINFO **0** |
| slice1 runner gate | **`a_class_erad_next_scale_slice1_runner_extension_gate = READY_FOR_APPROVAL`** |
| live path | [summary](../outputs/validation/cninfo_a_class_erad_next_scale_slice1_live_path_summary.md) · mock **17/17 PASS** · `--case-range` wired |
| slice1 live-path gate | **`a_class_erad_next_scale_slice1_live_path_gate = READY_FOR_APPROVAL`** |
| output root | `cninfo_a_class_erad_next_scale_slice1/` |
| acceptance threshold | **≥270/300** → `PASS_WITH_CAVEAT` |

**下一步：** human approve slice1 live（exact phrase）· or hold until scheduled

---

### 9.7 D 类 Era D — Next-Component Planning（2026-07-10）

> **offline planning complete** · **无 CNINFO** · **无 live** · **无 runner** · **Era C finish-up closed**

| 项 | 内容 |
|----|------|
| plan | [cninfo_d_class_erad_next_component_planning.md](cninfo_d_class_erad_next_component_planning.md) |
| candidate matrix | [cninfo_d_class_erad_next_component_candidate_matrix.csv](../outputs/validation/cninfo_d_class_erad_next_component_candidate_matrix.csv) |
| recommendation | [cninfo_d_class_erad_next_component_recommendation.md](../outputs/validation/cninfo_d_class_erad_next_component_recommendation.md) |
| planning summary | [cninfo_d_class_erad_next_component_planning_summary.md](../outputs/validation/cninfo_d_class_erad_next_component_planning_summary.md) |
| Era C closed | margin_trading **`116f875`** · disclosure_schedule **`d37ce0a`** · known-event **`PASS_WITH_CAVEAT`** |
| primary component | **`block_trade`** |
| runner-up | **`restricted_shares_unlock`** |
| exclude | **688671** · **301259** |
| first-slice size | **5**（proposed DBT001–DBT005） |
| output root (proposed) | `cninfo_d_class_block_trade_first_slice/` |
| planning gate | **`d_class_erad_next_component_planning_gate = READY_FOR_APPROVAL`** |
| CNINFO（本回合） | **0** |

**下一步：** block_trade first-slice **approval package**（offline · universe + checklist · **无 runner**）

---

### 9.8 D 类 block_trade First-Slice Approval Package（2026-07-10）

> **offline approval package only** · **无 CNINFO** · **无 live** · **无 runner** · **NOT APPROVED**

| 项 | 内容 |
|----|------|
| plan | [cninfo_d_class_block_trade_first_slice_plan.md](cninfo_d_class_block_trade_first_slice_plan.md) |
| universe | [cninfo_d_class_block_trade_first_slice_universe_draft.csv](../outputs/validation/cninfo_d_class_block_trade_first_slice_universe_draft.csv)（**5** 行 · DBT001–DBT005） |
| approval checklist | [cninfo_d_class_block_trade_first_slice_approval_checklist.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_checklist.md) |
| command draft | [cninfo_d_class_block_trade_first_slice_command_draft.md](cninfo_d_class_block_trade_first_slice_command_draft.md) |
| approval summary | [cninfo_d_class_block_trade_first_slice_approval_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_summary.md) |
| endpoint | `ints/statistics` · `tdate_daily` · anchor **2026-07-03** |
| exclude | **688671** · **301259** |
| closed tracks | margin **`116f875`** · disclosure **`d37ce0a`** · known-event **`PASS_WITH_CAVEAT`** |
| approval gate | **`d_class_block_trade_first_slice_approval_gate = READY_FOR_APPROVAL`** |
| approval_status | **NOT_APPROVED** · **approved_for_live = false** |
| CNINFO（本回合） | **0** |

**下一步：** block_trade first-slice **runner extension + dry-run**（offline · CNINFO **0**）

---

### 9.9 D 类 block_trade First-Slice Runner Extension + Dry-run（2026-07-10）

> **offline runner extension + dry-run only** · **无 CNINFO** · **无 live** · **NOT APPROVED**

| 项 | 内容 |
|----|------|
| runner | `lab/run_cninfo_d_class_tiny_live_validation.py`（`--block-trade-first-slice`） |
| tests | `lab/test_cninfo_d_class_block_trade_first_slice_runner.py`（**19/19 PASS**） |
| extension summary | [cninfo_d_class_block_trade_first_slice_runner_extension_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_runner_extension_summary.md) |
| dry-run | **5/5 planned_ok** · planned **5** · CNINFO **0** |
| live path | **implemented offline**（§9.11 · mock only） |
| runner extension gate | **`d_class_block_trade_first_slice_runner_extension_gate = READY_FOR_APPROVAL`** |
| approval gate | **`READY_FOR_APPROVAL`** · **NOT APPROVED** |

**下一步：** live-path offline implementation（mock only）

---

### 9.11 D 类 block_trade First-Slice Live Path（2026-07-10）

> **offline live-path implementation** · **mock CNINFO only** · **无 production live** · **NOT APPROVED**

| 项 | 内容 |
|----|------|
| runner | `execute_block_trade_first_slice_live()` in `lab/run_cninfo_d_class_tiny_live_validation.py` |
| tests | `lab/test_cninfo_d_class_block_trade_first_slice_live_path.py`（**18/18 PASS**） |
| runner tests | `lab/test_cninfo_d_class_block_trade_first_slice_runner.py`（**19/19 PASS**） |
| live-path summary | [cninfo_d_class_block_trade_first_slice_live_path_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_live_path_summary.md) |
| dry-run reconfirm | **5/5 planned_ok** · CNINFO **0** |
| production live report | **NOT CREATED** |
| live-path gate | **`d_class_block_trade_first_slice_live_path_gate = READY_FOR_APPROVAL`** |
| approval_status | **NOT_APPROVED** · **approved_for_live = false** |

**下一步：** human approval phrase → isolated live execution（**do not run now**）

---

### 9.12 D 类 block_trade First-Slice Isolated Live（2026-07-10）

> **human-approved isolated live** · CNINFO **5** · **NOT verified** · **NOT production_ready**

| 项 | 内容 |
|----|------|
| approval | phrase received · **`APPROVED_FOR_THIS_LIVE_ONLY`** |
| CNINFO requests | **5**（cap ≤ **20**） |
| acceptable | **4/5** |
| execution gate | **`d_class_block_trade_first_slice_execution_gate = PASS_WITH_CAVEAT`** |
| caveat | **DBT002** expectation_mismatch（sparse-day empty on 2026-07-03） |
| isolated live summary | [cninfo_d_class_block_trade_first_slice_isolated_live_validation_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_isolated_live_validation_summary.md) |
| closure gate | **`d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT`** |
| closed tracks | **untouched** |

**下一步：** human-approved explicit-path commit（separate phrase）

---

### 9.13 D 类 block_trade First-Slice Closure Review（2026-07-10）

> **offline closure only** · CNINFO **0** · **无 live rerun** · **NOT verified**

| 项 | 内容 |
|----|------|
| acceptable | **4/5** |
| sparse-day empty | **5/5** on `tdate=2026-07-03` |
| caveat | **DBT002** `expectation_mismatch_on_sparse_day`（non-blocking） |
| closure gate | **`d_class_block_trade_first_slice_closure_gate = PASS_WITH_CAVEAT`** |
| closure summary | [cninfo_d_class_block_trade_first_slice_closure_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_closure_summary.md) |
| closure decision | [cninfo_d_class_block_trade_first_slice_closure_decision.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_closure_decision.md) |
| unresolved ledger | [cninfo_d_class_block_trade_first_slice_unresolved_case_ledger.csv](../outputs/validation/cninfo_d_class_block_trade_first_slice_unresolved_case_ledger.csv) |
| CNINFO（本回合） | **0** |

**下一步：** human-approved explicit-path commit（separate phrase）

---

### 9.14 D 类 block_trade First-Slice Commit Boundary Review（2026-07-10）

> **offline boundary only** · CNINFO **0** · **无 commit** · **NOT verified**

| 项 | 内容 |
|----|------|
| safe-to-commit | **~27** explicit paths |
| do-not-commit | live_snapshots JSON · unrelated track roots · category blocks |
| DBT002 caveat | **retained** · `expectation_mismatch_on_sparse_day` |
| boundary gate | **`d_class_block_trade_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW`** |
| boundary summary | [cninfo_d_class_block_trade_first_slice_commit_boundary_summary.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_commit_boundary_summary.md) |
| CNINFO（本回合） | **0** |

**下一步：** human-approved explicit-path commit（separate phrase · **not in this task**）

---

### 9.15 D 类 block_trade First-Slice Explicit-Path Commit（2026-07-10）

> **human-approved commit** · **28 files** · **NOT pushed** · **NOT verified**

| 项 | 内容 |
|----|------|
| commit | **`403472d`** |
| files | **28** explicit paths |
| live_snapshots | **not committed** |
| DBT002 caveat | **retained** |
| commit gate | **`d_class_block_trade_first_slice_commit_gate = PASS_WITH_CAVEAT`** |
| commit status | [cninfo_d_class_block_trade_first_slice_commit_status.md](../outputs/validation/cninfo_d_class_block_trade_first_slice_commit_status.md) |

**下一步：** Era D next-component planning refresh（**`restricted_shares_unlock`** · planning only）

---

### 9.16 D 类 Era D Next-Component Planning Refresh（2026-07-10）

> **offline planning refresh only** · CNINFO **0** · **无 live** · **无 commit**

| 项 | 内容 |
|----|------|
| trigger | block_trade commit **`403472d`** · closed tracks unchanged |
| primary | **`restricted_shares_unlock`** |
| runner-up | `equity_pledge` |
| matrix v2 | [cninfo_d_class_erad_next_component_candidate_matrix_v2.csv](../outputs/validation/cninfo_d_class_erad_next_component_candidate_matrix_v2.csv) |
| RSU sketch | [cninfo_d_class_restricted_shares_unlock_first_slice_plan_draft.md](cninfo_d_class_restricted_shares_unlock_first_slice_plan_draft.md) |
| refresh gate | **`d_class_erad_next_component_planning_refresh_gate = PASS_WITH_CAVEAT`**（human chose RSU） |
| CNINFO（本回合） | **0** |

**下一步：** restricted_shares_unlock first-slice approval package → runner extension + dry-run

---

### 9.17 D 类 restricted_shares_unlock First-Slice Approval Package（2026-07-10）

> **offline approval package only** · CNINFO **0** · **无 live** · **无 runner** · **无 commit**

| 项 | 内容 |
|----|------|
| human approval | **I approve D-class restricted_shares_unlock as the next Era D component.** |
| universe | **5** rows · DRU001–DRU005 · anchor **`tdate=2026-06-08`** |
| endpoint | `liftBan/detail` |
| approval gate | **`d_class_restricted_shares_unlock_first_slice_approval_gate = READY_FOR_APPROVAL`** |
| live / runner | dry-run **done** · live **NOT IMPLEMENTED** |
| CNINFO（本回合） | **0** |

**下一步：** live-path implementation（offline · mock only）

---

### 9.18 D 类 restricted_shares_unlock First-Slice Runner Extension + Dry-run（2026-07-10）

> **runner extension + dry-run only** · CNINFO **0** · **无 live**

| 项 | 内容 |
|----|------|
| dry-run | **5/5 planned_ok** · planned **20** |
| tests | **20/20 PASS** |
| live path | **not implemented**（stub） |
| extension gate | **`d_class_restricted_shares_unlock_first_slice_runner_extension_gate = READY_FOR_APPROVAL`** |
| CNINFO（本回合） | **0** |

**下一步：** live-path implementation（offline · mock only）

---

### 9.19 D 类 restricted_shares_unlock First-Slice Live-Path Implementation（2026-07-10）

> **live-path offline implementation + mock tests only** · CNINFO **0**（本任务）· **无 real live**

| 项 | 内容 |
|----|------|
| live function | `execute_restricted_shares_unlock_first_slice_live()` |
| stub removed | **yes** |
| tests | **22/22 PASS**（mock CNINFO） |
| runner tests | **20/20 PASS**（retained） |
| live-path gate | **`d_class_restricted_shares_unlock_first_slice_live_path_gate = READY_FOR_APPROVAL`** |
| CNINFO（本回合） | **0** |

**下一步：** human approve phrase → isolated live validation

---

### 9.20 D 类 restricted_shares_unlock First-Slice Isolated Live（2026-07-10）

> **human-approved isolated live** · **NOT verified** · **无 commit** · **无 push**

| 项 | 内容 |
|----|------|
| approval | **I approve D-class restricted_shares_unlock first-slice live validation.** |
| CNINFO | **15** |
| acceptable | **5/5** |
| sparse-day empty | **5/5** |
| execution gate | **`d_class_restricted_shares_unlock_first_slice_execution_gate = PASS_WITH_CAVEAT`** |
| outcome ledger | [cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_per_case_outcome_ledger.csv) |

**下一步：** closure / commit-boundary package（offline）— **已完成** §9.21

---

### 9.21 D 类 restricted_shares_unlock First-Slice Closure + Commit Boundary（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT verified** · **无 commit** · **无 push**

| 项 | 内容 |
|----|------|
| closure gate | **`d_class_restricted_shares_unlock_first_slice_closure_gate = PASS_WITH_CAVEAT`** |
| boundary gate | **`d_class_restricted_shares_unlock_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW`** |
| approval_status_for_commit | **NOT_APPROVED** |
| acceptable | **5/5** · empty_but_valid **×5** · sparse anchor **2026-06-08** |
| safe-to-commit | **~32** explicit paths |
| closure review | [cninfo_d_class_restricted_shares_unlock_first_slice_closure_review.md](cninfo_d_class_restricted_shares_unlock_first_slice_closure_review.md) |
| boundary review | [cninfo_d_class_restricted_shares_unlock_first_slice_commit_boundary_review.md](cninfo_d_class_restricted_shares_unlock_first_slice_commit_boundary_review.md) |
| post-closure | [cninfo_d_class_restricted_shares_unlock_first_slice_post_closure_next_step_recommendation.md](../outputs/validation/cninfo_d_class_restricted_shares_unlock_first_slice_post_closure_next_step_recommendation.md) |

**下一步：** human-approved explicit-path commit — **已完成** §9.22

---

### 9.22 D 类 restricted_shares_unlock First-Slice Explicit-Path Commit（2026-07-10）

> **explicit-path commit only** · **NOT pushed** · **NOT verified** · CNINFO **0**

| 项 | 内容 |
|----|------|
| approval | **I approve D-class restricted_shares_unlock first-slice explicit-path commit.** |
| commit | **`aa087b5`** · **32 files** |
| commit gate | **`d_class_restricted_shares_unlock_first_slice_commit_gate = PASS_WITH_CAVEAT`** |
| acceptable | **5/5** · empty_but_valid **×5** · sparse anchor **2026-06-08** |
| live_snapshots | **not committed**（5 JSON · local-only） |
| push | **no** |

**下一步：** **`equity_pledge`** next-component planning package — **已完成** §9.23

---

### 9.23 D 类 equity_pledge Next-Component Planning（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT verified** · **无 runner** · **无 commit** · **无 push**

| 项 | 内容 |
|----|------|
| planning gate | **`d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT`** |
| primary | **`equity_pledge`** |
| runner-up | **`shareholder_change`** |
| first-slice sketch | **5** · DEP001–DEP005 · anchor **`tdate=2026-07-03`**（offline only） |
| threshold | **≥ 3/5 acceptable** → `PASS_WITH_CAVEAT` |
| planning plan | [cninfo_d_class_equity_pledge_next_component_planning.md](cninfo_d_class_equity_pledge_next_component_planning.md) |
| first-slice draft | [cninfo_d_class_equity_pledge_first_slice_plan_draft.md](cninfo_d_class_equity_pledge_first_slice_plan_draft.md) |
| next step | [cninfo_d_class_equity_pledge_next_component_next_step_recommendation.md](../outputs/validation/cninfo_d_class_equity_pledge_next_component_next_step_recommendation.md) |

**下一步：** human approve component → equity_pledge first-slice approval package — **已完成** §9.24

---

### 9.24 D 类 equity_pledge First-Slice Approval Package（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT APPROVED for live** · **无 runner** · **无 commit**

| 项 | 内容 |
|----|------|
| component approval | **I approve D-class equity_pledge as the next Era D component.** |
| planning gate | **`d_class_equity_pledge_next_component_planning_gate = PASS_WITH_CAVEAT`** |
| approval gate | **`d_class_equity_pledge_first_slice_approval_gate = READY_FOR_APPROVAL`** |
| universe | **5** · DEP001–DEP005 · anchor **`tdate=2026-07-03`** |
| expectation mix | 1 `empty_but_valid` · 3 `captured_normal_or_empty_but_valid` · 1 `captured_normal_or_needs_review` |
| formal plan | [cninfo_d_class_equity_pledge_first_slice_plan.md](cninfo_d_class_equity_pledge_first_slice_plan.md) |
| next step | [cninfo_d_class_equity_pledge_first_slice_next_step_recommendation.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_next_step_recommendation.md) |

**下一步：** equity_pledge first-slice runner extension + dry-run — **已完成** §9.25

---

### 9.25 D 类 equity_pledge First-Slice Runner Extension + Dry-run（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT APPROVED for live** · live path **stub**

| 项 | 内容 |
|----|------|
| runner extension gate | **`d_class_equity_pledge_first_slice_runner_extension_gate = READY_FOR_APPROVAL`** |
| dry-run | **5/5 planned_ok** · planned **5** · CNINFO **0** |
| tests | **20/20 PASS** |
| live stub | `equity_pledge_first_slice_live_not_implemented` |
| extension summary | [cninfo_d_class_equity_pledge_first_slice_runner_extension_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_runner_extension_summary.md) |

**下一步：** equity_pledge first-slice live-path implementation — **已完成** §9.26

---

### 9.26 D 类 equity_pledge First-Slice Live-Path Implementation（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT APPROVED for live** · mock tests only

| 项 | 内容 |
|----|------|
| live-path gate | **`d_class_equity_pledge_first_slice_live_path_gate = READY_FOR_APPROVAL`** |
| live entry | `execute_equity_pledge_first_slice_live()` |
| tests | live-path **22/22** · runner **20/20** |
| dry-run reconfirm | **5/5 planned_ok** · planned **5** · CNINFO **0** |
| stub removed | `equity_pledge_first_slice_live_not_implemented` |
| live-path summary | [cninfo_d_class_equity_pledge_first_slice_live_path_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_path_summary.md) |

**下一步：** human approve isolated live — **已完成** §9.27

---

### 9.27 D 类 equity_pledge First-Slice Isolated Live Validation（2026-07-10）

> **human-approved** · **NOT verified** · **NOT production_ready** · **无 commit**

| 项 | 内容 |
|----|------|
| approval | **I approve D-class equity_pledge first-slice live validation.** |
| CNINFO requests | **5** |
| acceptable | **4/5** |
| executed | **5/5** |
| sparse-day empty | **5/5** |
| execution gate | **`PASS_WITH_CAVEAT`** |
| caveat | DEP004 `captured_normal_or_needs_review` + sparse-day `empty_but_valid` → expectation_mismatch |
| execution summary | [cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_live_execution_summary.md) |

**下一步：** equity_pledge first-slice closure / commit-boundary package — **已完成** §9.28

---

### 9.28 D 类 equity_pledge First-Slice Closure + Commit Boundary（2026-07-10）

> **offline only** · **CNINFO = 0** · **NOT verified** · **无 commit**

| 项 | 内容 |
|----|------|
| closure gate | **`d_class_equity_pledge_first_slice_closure_gate = PASS_WITH_CAVEAT`** |
| boundary gate | **`d_class_equity_pledge_first_slice_commit_boundary_gate = READY_FOR_COMMIT_REVIEW`** |
| acceptable | **4/5** · sparse-day empty **5/5** |
| caveat | DEP004 `expectation_mismatch_on_sparse_day` · non-blocking |
| safe-to-commit | **~33** explicit paths |
| closure summary | [cninfo_d_class_equity_pledge_first_slice_closure_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_closure_summary.md) |
| boundary summary | [cninfo_d_class_equity_pledge_first_slice_commit_boundary_summary.md](../outputs/validation/cninfo_d_class_equity_pledge_first_slice_commit_boundary_summary.md) |

**下一步：** human approve explicit-path commit with phrase **I approve D-class equity_pledge first-slice explicit-path commit.**

---

### 9.3 与「先本地、后入库」的对齐

| 现在做 | 以后做（非 Era D） |
|--------|-------------------|
| 稳定抽取、扩规模、本地保存 | DB / MinIO / verified / 产品入库 |
| gate / ledger / resume / cleanup | migration / 对象存储生命周期 |

---

## 10. 任务总表（初版 · 将随执行勾选）

| ID | 任务 | 线 | Phase | 状态 |
|----|------|----|-------|------|
| ED-001 | Era D 执行计划初版 | 横切 | D0 | **完成**（本文件） |
| ED-002 | 本地产出保留策略文档 | 横切 | D0 | 未开始 |
| ED-003 | CURRENT_STATUS / PROJECT_MAP 标注 Era D 启动 | 横切 | D0 | **部分完成**（C 线 Era D 规划已标注） |
| ED-004 | 人签 scope freeze | 横切 | D0 | 未开始 |
| ED-005 | cleanup / resume 硬化（分线） | A/B/C/D | D1 | 未开始 |
| ED-006 | A-class ~200 expansion 规划包 | A | D2 | **完成** · runner+dry-run **完成**（[summary](../outputs/validation/cninfo_a_class_erad_scale_200_runner_extension_summary.md) · **200/200** · tests **27/27** · gate **`READY_FOR_APPROVAL`**) |
| ED-007 | B-class ~200 expansion 规划包 | B | D2 | **完成**（planning gate **`READY_FOR_APPROVAL`**） |
| ED-008 | C-class resume/全量演练规划 | C | D1/D2 | **规划完成** · [plan](cninfo_c_class_erad_resume_stability_plan.md) · gate **`READY_FOR_APPROVAL`** |
| ED-009 | D-class disclosure closure→boundary 收尾 | D | D2 | **完成**（commit **`d37ce0a`** · **5/5** · gate **`PASS_WITH_CAVEAT`**） |
| ED-010 | D-class 下一组件规划 | D | D2 | **完成**（[plan](cninfo_d_class_erad_next_component_planning.md) · primary **`block_trade`** · gate **`READY_FOR_APPROVAL`**） |
| ED-011 | D-class block_trade first-slice approval package | D | D2 | **完成**（[summary](../outputs/validation/cninfo_d_class_block_trade_first_slice_approval_summary.md) · universe **5** · gate **`READY_FOR_APPROVAL`** · **NOT APPROVED** · **无 live**） |
| ED-011b | D-class block_trade first-slice runner + dry-run | D | D2 | **完成**（§9.9 · dry-run **5/5** · tests **19/19** · extension gate **`READY_FOR_APPROVAL`** · **无 live**） |
| ED-011c | D-class block_trade first-slice live path | D | D2 | **完成**（§9.11 · tests **18/18** · mock only） |
| ED-011d | D-class block_trade first-slice isolated live | D | D2 | **完成**（§9.12 · CNINFO **5** · **4/5** · execution gate **`PASS_WITH_CAVEAT`** · **无 commit**） |
| ED-011e | D-class block_trade first-slice closure review | D | D2 | **完成**（§9.13 · **4/5** · closure gate **`PASS_WITH_CAVEAT`** · CNINFO **0** · **无 commit**） |
| ED-011f | D-class block_trade first-slice commit boundary review | D | D2 | **完成**（§9.14 · safe **~27** · boundary gate **`READY_FOR_COMMIT_REVIEW`**） |
| ED-011g | D-class block_trade first-slice explicit-path commit | D | D2 | **完成**（§9.15 · commit **`403472d`** · **28 files** · gate **`PASS_WITH_CAVEAT`** · **无 push** · **NOT verified**） |
| ED-012 | D-class Era D next-component planning refresh | D | D2 | **完成**（§9.16 · primary **`restricted_shares_unlock`** · refresh gate **`PASS_WITH_CAVEAT`** · CNINFO **0**） |
| ED-013 | D-class restricted_shares_unlock first-slice approval package | D | D2 | **完成**（§9.17 · universe **5** · approval gate **`READY_FOR_APPROVAL`** · **NOT APPROVED live**） |
| ED-013b | D-class restricted_shares_unlock first-slice runner + dry-run | D | D2 | **完成**（§9.18 · dry-run **5/5** · planned **20** · tests **20/20** · extension gate **`READY_FOR_APPROVAL`** · **无 live**） |
| ED-013c | D-class restricted_shares_unlock first-slice live path | D | D2 | **完成**（§9.19 · tests **22/22** · mock only · live-path gate **`READY_FOR_APPROVAL`**） |
| ED-013d | D-class restricted_shares_unlock first-slice isolated live | D | D2 | **完成**（§9.20 · CNINFO **15** · **5/5** · execution gate **`PASS_WITH_CAVEAT`** · **无 commit**） |
| ED-013e | D-class restricted_shares_unlock first-slice closure review | D | D2 | **完成**（§9.21 · **5/5** · closure gate **`PASS_WITH_CAVEAT`** · CNINFO **0** · **无 commit**） |
| ED-013f | D-class restricted_shares_unlock first-slice commit boundary review | D | D2 | **完成**（§9.21 · safe **~32** · boundary gate **`READY_FOR_COMMIT_REVIEW`** · **NOT_APPROVED**） |
| ED-013g | D-class restricted_shares_unlock first-slice explicit-path commit | D | D2 | **完成**（§9.22 · commit **`aa087b5`** · **32 files** · gate **`PASS_WITH_CAVEAT`** · **无 push** · **NOT verified**） |
| ED-015 | D-class equity_pledge next-component planning | D | D2 | **完成**（§9.23 · primary **`equity_pledge`** · planning gate **`PASS_WITH_CAVEAT`** · CNINFO **0**） |
| ED-016 | D-class equity_pledge first-slice approval package | D | D2 | **完成**（§9.24 · universe **5** · approval gate **`READY_FOR_APPROVAL`** · **NOT APPROVED live**） |
| ED-016b | D-class equity_pledge first-slice runner + dry-run | D | D2 | **完成**（§9.25 · dry-run **5/5** · planned **5** · tests **20/20** · extension gate **`READY_FOR_APPROVAL`** · **无 live**） |
| ED-016c | D-class equity_pledge first-slice live-path | D | D2 | **完成**（§9.26 · live-path **22/22** · runner **20/20** · live-path gate **`READY_FOR_APPROVAL`** · mock only · CNINFO **0**） |
| ED-016d | D-class equity_pledge first-slice isolated live | D | D2 | **完成**（§9.27 · CNINFO **5** · acceptable **4/5** · execution gate **`PASS_WITH_CAVEAT`** · **无 commit**） |
| ED-016e | D-class equity_pledge first-slice closure + commit boundary | D | D2 | **完成**（§9.28 · closure **`PASS_WITH_CAVEAT`** · boundary **`READY_FOR_COMMIT_REVIEW`** · safe **~33** · CNINFO **0** · **无 commit**） |
| ED-014 | portrait_ontology P0–P3（catalog + coverage + schema + pilot） | 横切 | D0/D2 | **完成**（§9.10 · **715** fields · pilot **000009** · gates **`PASS_OFFLINE`** · **无 live**） |
| ED-012 | MVP 四线 closure 汇总 | 横切 | D2 | 未开始 |
| ED-012 | D3 完整规模（分线） | A/B/C/D | D3 | 未开始 |
| ED-013 | Era D 收口 + 入库延后声明 | 横切 | D4 | 未开始 |

---

## 11. 红线确认（页脚）

No DB · No MinIO · No MongoDB · No PDF download/parse（默认）· No OCR · No extraction · No RAG · No verified · No production_ready · No bare PASS · 四线不互踩 live 根 · live 必须人批 · 入库延后到后续 Era
