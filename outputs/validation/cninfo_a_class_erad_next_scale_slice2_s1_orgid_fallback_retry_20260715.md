# A-class Slice2 S1 orgId Fallback Isolated Retry（A-R16-01）

_生成时间：2026-07-15_  
_性质：能力接入 + 授权 live 孤立重试 · **无 PDF** · **不是 verified** · **不是 production_ready**_

---

## 1. Task

| 项 | 值 |
|----|-----|
| task_id | **A-R16-01** |
| track | A |
| executor | a-class-executor |
| scope | `erad_a_scale_500_slice2`（已授权） |
| CNINFO budget | ≤12 |
| closed S1 live root mutate | **no**（live 证据 SHA 未变） |

## 2. Wall clock

| 项 | 值 |
|----|-----|
| wall_start | 2026-07-15 16:04:35 +0800 |
| wall_end | 2026-07-15 16:05:20 +0800 |
| duration | ~45s |

## 3. Capability wiring

| 项 | 路径 / 行为 |
|----|-------------|
| offline helper | `lab/cninfo_a_class_orgid_mapping_fallback.py` |
| live hook | `lab/run_cninfo_a_class_tiny_live_metadata_validation.py` → `resolve_orgid` |
| 行为 | topSearch 优先；失败后离线 lookup；未命中显式 miss，保留 topSearch 错误，禁止静默伪造 |
| runner 扩展 | `lab/run_cninfo_a_class_phase2_metadata_expansion.py` 识别 3 案 retry universe + 独立 output root；CNINFO cap=12；禁止写封闭 S1 live 根 |

## 4. Isolated universe

| case_id | code | name | cohort |
|---------|------|------|--------|
| AD2E578 | 688605 | 先锋精科 | next_scale_slice2 |
| AD2E590 | 688688 | 蚂蚁集团 | next_scale_slice2 |
| AD2E598 | 688758 | 赛分科技 | next_scale_slice2 |

- universe: `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry_universe.csv`
- output root: `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry/`

## 5. Live command

```bash
python lab/run_cninfo_a_class_phase2_metadata_expansion.py \
  --erad-a-scale-500-slice2 \
  --approve-a-class-erad-scale-500-slice2 \
  --universe-csv outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry_universe.csv \
  --output-root outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry \
  --live
```

## 6. CNINFO counts and case outcomes

| 指标 | 值 |
|------|-----|
| CNINFO total | **9**（cap ≤12） |
| orgid_offline_fallback_hits | 0（本轮 topSearch 均返回 orgId） |
| orgid_offline_fallback_misses | 0 |
| acceptable | 0 / 3 |
| execution gate | `FAIL_REVIEW_REQUIRED` |

| case_id | code | org_id（live） | offline expected | fallback used | retrieval | CNINFO/case |
|---------|------|----------------|------------------|---------------|-----------|-------------|
| AD2E578 | 688605 | **9900059045** | 9900059045 | no（topSearch hit） | not_found | 3 |
| AD2E590 | 688688 | **9900046315** | 9900046315 | no（topSearch hit） | not_found | 3 |
| AD2E598 | 688758 | **9900057459** | 9900057459 | no（topSearch hit） | not_found | 3 |

共同 notes：`records=0; last_err=ok` — orgId 已解析，但 hisAnnouncement 无 v2 可匹配定期报告。

## 7. Failure-class refinement

```text
prior_class   = org_id_topsearch_miss_with_known_offline_orgid
live_observed = org_id_resolved_but_periodic_matching_empty
capability_gain = live_orgid_fallback_hook_wired + isolated_retry_executed
```

- 本轮证明：正确 orgId（与离线恢复表一致）仍不足以恢复三案匹配。
- Hook 仍为能力收益：topSearch 再 miss 时可用离线映射继续 query，不再在 resolve 阶段硬停。
- **不**宣称 bare PASS / verified / production_ready。

## 8. Tests

```text
python lab/test_cninfo_a_class_orgid_fallback_hook.py     → 10/10 OK
python lab/test_cninfo_a_class_orgid_mapping_fallback.py → 10/10 OK
python lab/test_cninfo_a_class_erad_next_scale_slice2_runner.py → 20/20 OK
python lab/test_cninfo_a_class_erad_next_scale_slice2_live_path.py → 19/19 OK
```

## 9. Isolation / safety

| 检查 | 结果 |
|------|------|
| 封闭 S1 live raw_metadata AD2E578/590/598 | **unchanged**（mtime 仍为 session2；SHA 一致） |
| 封闭 S1 live report CSV | **unchanged** |
| 写入仅发生在 | `.../cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry/` |
| PDF / DB / MinIO / RAG | no |
| commit / push | **not performed** |

## 10. Allow-list for commit（A-R16-01 only）

1. `lab/run_cninfo_a_class_tiny_live_metadata_validation.py`
2. `lab/run_cninfo_a_class_phase2_metadata_expansion.py`
3. `lab/test_cninfo_a_class_orgid_fallback_hook.py`
4. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry_universe.csv`
5. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry/`（整根）
6. `outputs/validation/cninfo_a_class_erad_next_scale_slice2_s1_orgid_fallback_retry_20260715.md`（本文件）

**Exclude：** C-class / 其他 track 改动；S1 console logs；slice1/scale200 dryrun churn。

## 11. Gates / next

```text
capability_gain = CAPABILITY_ADVANCED
ready_for_commit = yes   # hook + tests + isolated live evidence；不含 push
next_hint = matching/empty-announcement triage for AD2E578/590/598 under known orgId
            （日期窗 / keyword / column — 另开任务；不得 mutate 封闭 S1 live）
```
