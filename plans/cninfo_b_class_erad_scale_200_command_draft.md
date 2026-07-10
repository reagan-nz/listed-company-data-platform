# CNINFO B 类 Era D ~200 Expansion — Command Draft

_生成时间：2026-07-10 · live path 已落地（mock tests）_

> **approval_status = NOT_APPROVED** · **approved_for_live = false**  
> dry-run **已实现** · live path **已实现** · **禁止未批真实 live**

---

## Dry-run（已实现 · 可执行）

```bash
cd listed_company_data_collector

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-200 \
  --universe-csv outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_scale_200/
```

（默认 `mode=dry_run`；亦可显式 `--dry-run`。）

**实测：** CNINFO **0** · planned_ok **200/200** · planned_request_count **400**

**Tests:**

```bash
python lab/test_cninfo_b_class_erad_scale_200_runner.py
```

---

## Live（路径已实现 · **NOT APPROVED — DO NOT RUN**）

```bash
# NOT APPROVED — DO NOT RUN without:
# I approve B-class Era D scale-200 live metadata validation.

python lab/run_cninfo_b_class_phase25_expansion_validation.py \
  --erad-b-scale-200 \
  --live \
  --universe-csv outputs/validation/cninfo_b_class_erad_scale_200_universe_draft.csv \
  --output-root outputs/validation/cninfo_b_class_erad_scale_200/ \
  --approve-b-class-erad-scale-200
```

> live path wired · mock tests **17/17 PASS** · 本任务**未执行**真实 live · 须人批后方可运行。

**Live-path tests:**

```bash
python lab/test_cninfo_b_class_erad_scale_200_live_path.py
```

---

## Flags

| Flag | Purpose |
|------|---------|
| `--erad-b-scale-200` | 启用 Era D 200-company expansion 模式 |
| `--approve-b-class-erad-scale-200` | live 执行人批门闩 |
| `--universe-csv` | 指向 Era D universe draft（须为 canonical path） |
| `--output-root` | 隔离输出根（须为 `cninfo_b_class_erad_scale_200/`） |

---

## Isolation Checks（已 enforce）

- 拒绝写入 `cninfo_b_class_phase3_100_*` 生产根（expansion / failed-retry / retry_v2 / EP002 precheck）
- 拒绝写入 A/C/D live 根
- retained cohort（BD2E001–100）：dry-run `reference_only` · live `live_refresh`（仅写 Era D 根）
- new cohort（BD2E101–200）：仅写 `cninfo_b_class_erad_scale_200/`
- request cap：**≤480**（dry-run planned **400**）

---

## Gates

```
b_class_erad_scale_200_runner_extension_gate = READY_FOR_APPROVAL
b_class_erad_scale_200_live_path_gate = READY_FOR_APPROVAL
```

Future live threshold：**≥180/200 acceptable** → `PASS_WITH_CAVEAT`

---

## Red Lines

- **无未批真实 live** · 本离线任务 **CNINFO = 0**
- **无 PDF/DB/MinIO/RAG/verified/production_ready**
- **无 Phase 3 生产根 mutation**
