# CNINFO A 类 Era D ~200 Metadata Expansion Plan

_生成时间：2026-07-10_

> **性质：** Era D 本地扩规模规划 · **离线 only** · **NOT APPROVED** · **不是 verified** · **不是 production_ready**
>
> **Era 归属：** A 类 **进入 Era D**（Era C 已收口 · A3M017 commit **`cb9f3fc`** · post-retry **50/50 effective**）。本包 **不调用 CNINFO** · **不 live** · **不实现 runner**。

**Historical commits（本任务不 amend）：**

- **`bbc15c3`** — Phase 3 50-company 历史 **49/50**（A3M017 caveat 保留为历史）
- **`cb9f3fc`** — A3M017 isolated-retry + post-retry closure（**50/50 effective**）

**Remote publish of `cb9f3fc`：** 本任务 **out of scope**（另轨人决）。

---

## 1. Goal

在 **matching_logic v2 不变**、**metadata + URL lineage only** 的前提下，将 A-class 定期报告 metadata 本地稳定抽取从 Phase 3 **post-retry effective 50/50** 扩至 **~200** 家公司：

- **50 retained** — Phase 3 post-retry effective accepted cohort（AD2E001–AD2E050 · `phase3_overlap=yes` by design）
- **150 new** — 与 Phase 1 / Phase 2 effective 20 / Phase 3 **零公司代码重叠** 的新扩样（AD2E051–AD2E200）
- 独立输出根：`outputs/validation/cninfo_a_class_erad_scale_200/`
- **Era D 本地 only** — 不入库 · 不写 verified · 不升级 testing_stable_sample

---

## 2. Universe Design Choice

| 方案 | 本包选择 |
|------|----------|
| 200 全新公司 | **否** |
| **50 retained + 150 new = 200** | **是** |

**理由：**

1. Phase 3 已在本地收口 **50/50 effective**（`cb9f3fc`）；retained 50 保留有效 accepted 基线与 lineage 连续性。
2. 新增 150 家专测 Era D 扩规模与 orgId / matching 稳定性，与 Phase 1/2/3 **零 overlap**（new cohort）。
3. 与 Era D MVP（A 线 ~200 metadata）及 [eraD_execution_plan.md](eraD_execution_plan.md) §0.3 对齐。

---

## 3. Overlap Policy

| 对照 | 政策 |
|------|------|
| Phase 3 post-retry effective 50 | **50 retained** — `phase3_overlap=yes`（by design · 非 silent overlap） |
| Phase 1 tiny live（5） | **0 overlap** on new 150 — excluded at selection |
| Phase 2 effective 20 | **0 overlap** on new 150 — excluded at selection |
| Phase 3（new cohort） | **0 overlap** on new 150 |
| A3M017 isolated-retry root | **只读参照** · 不重跑 · 不写入 |
| Phase 3 expansion root / bbc15c3 blobs | **禁止 rewrite** · 只读参照 |
| B / C / D live 根 | **禁止写入** |
| 北交所（BSE） | 默认 **排除** |

完整 overlap 见 [universe draft](../outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv)。

---

## 4. Report Type / Period Policy

| cohort | report_type mix | expected_period |
|--------|-----------------|-----------------|
| retained 50 | **preserve Phase 3 mix**（annual 20 · semi 10 · q1 10 · q3 10） | 与 Phase 3 一致 |
| new 150 | **annual_report 主导**（120 annual · 10 semi · 10 q1 · 10 q3） | 2024-12-31 / 2024-06-30 / 2024-03-31 / 2024-09-30 |

**title matching：** v2 · `expected_title_keywords` / `excluded_title_keywords` 与 Phase 3 口径一致。

**红线：** metadata + pdf_url/adjunct_url lineage only · **无 PDF 下载/解析/OCR/章节抽取**

---

## 5. orgId_resolution Risk Note（A3M017 History）

| 项 | 说明 |
|----|------|
| A3M017 | Phase 3 live `network_error` at `orgId_resolution` · 后由 isolated retry 恢复 |
| Era D 200 含义 | 扩规模时 orgId 解析仍为首要网络风险点 |
| 规划对策 | conservative request cap · sleep ≥1.0s · 可选 isolated retry 轨（仿 A3M017 · 单独 gate） |
| 本包 | **不执行 retry** · 仅文档化 |

---

## 6. Output Root

```
outputs/validation/cninfo_a_class_erad_scale_200/
├── reports/          # dry-run / live report CSV+MD
├── raw_metadata/     # per-case CNINFO metadata snapshot JSON
└── (optional ledgers)
```

**隔离要求：**

- **不得**写入 Phase 1 / Phase 2 / Phase 3 expansion / A3M017 retry 生产根
- **不得**触碰 B / C / D live 根
- **不得** rewrite `bbc15c3` / `cb9f3fc` committed blobs
- 测试 mock 输出必须在 `_mock_*` 子目录

---

## 7. Request Cap Proposal（Conservative）

| 项 | 估值 |
|----|------|
| universe size | **200** |
| per-case baseline（orgId + announcement query） | **~2** CNINFO |
| planned_request_count_total（dry-run 上限） | **≤480**（200×2 + 20% orgId buffer） |
| live 执行建议 sleep | **≥1.0s** between CNINFO calls（live 阶段；本包不执行） |
| 单日 live 批次建议 | **≤100** cases 单批；200 全量需分批 + 人批 |
| A3M017 lesson | 保留 isolated retry 规划口 · 不 silent drop network failures |

---

## 8. Success Criteria（Future Live）

本规划包 **不执行 live**；以下为后续 live 收口建议：

| 指标 | 阈值 | Gate 建议 |
|------|------|-----------|
| acceptable / executed | **≥180/200（90%）** | `PASS_WITH_CAVEAT` |
| acceptable / executed | **≥190/200（95%）** | `PASS_WITH_CAVEAT` + 更小 caveat |
| acceptable / executed | **<180/200** | `FAIL_REVIEW_REQUIRED` |
| orgId_resolution network_error | 参考 A3M017 | 文档化 · 可选 isolated retry |
| PDF / DB / MinIO / RAG | **0** | 红线 |

**永不使用裸 `PASS`。**

---

## 9. Planned CLI Flags（document only · 未实现）

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-200 \
  --dry-run \
  --universe-csv outputs/validation/cninfo_a_class_erad_scale_200_universe_draft.csv \
  --output-root outputs/validation/cninfo_a_class_erad_scale_200/
```

Live（**NOT APPROVED**）需额外：

```bash
  --live \
  --approve-a-class-erad-scale-200
```

---

## 10. Era D Local-Only Note

- 本 Era D 200 轨为 **本地稳定抽取** · **不入库**
- **不写 verified / production_ready**
- 远端 cherry-pick / publish（含 `cb9f3fc`）为 **独立 later decision** · 不阻塞本地规划

---

## 11. Planning Gate

```text
a_class_erad_scale_200_planning_gate = READY_FOR_APPROVAL
```

**下一步：** runner extension + dry-run（offline · CNINFO **0**）
