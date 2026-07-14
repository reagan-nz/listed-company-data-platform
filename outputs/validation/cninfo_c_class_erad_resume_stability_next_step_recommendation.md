# CNINFO C 类 Era D Resume / Stability 下一步建议

_生成时间：2026-07-10_

---

## Primary recommendation

**Proceed to Slice-C-EraD-01 implementation:** C-class resume/cleanup hardening + protected-root regression tests (offline only).

---

## Option comparison

| Option | 描述 | 推荐 |
|--------|------|------|
| **A（推荐）** | Slice-C-EraD-01：硬化 `tearDown`/cleanup · 补 `test_cleanup_refuses_production_*` · 对齐 protected roots CSV | **Primary** |
| B | 863 harvest resume audit dry-run only | 次选 · 在 A 之后 |
| C | 491 snapshot rebuild readiness dry-run | 延后至 D2 · 需 `approved_for_snapshot_rebuild` |
| D | 直接 863 full harvest live 重跑 | **不推荐** · 跳过 D1 |

---

## Recommended sequence

1. Human review planning package → approve `c_class_erad_resume_stability_planning_gate`（in-session phrase if required later）  
2. Switch to branch `c-class-erad-resume`（避免与 `b-class-phase3-clean-push` 混树）  
3. Implement cleanup hardening in C-class test files（`test_cninfo_c_class_phase35_expanded_snapshot_builder.py` 等审计清单）  
4. Run offline pytest suites · CNINFO **0**  
5. Write `cninfo_c_class_erad_cleanup_hardening_summary.md` + gate `c_class_erad_cleanup_hardening_gate`  
6. **Only then** open Slice-C-EraD-02（863 harvest resume audit dry-run）if needed

---

## Do not do next

- Live harvest  
- Rebuild 491/863 snapshot JSON  
- Promote C35R016 or reopen holdouts  
- Push mixed local `main`  
- Mutate A/B/D outputs

---

## Coordination notes

| 线 | 备注 |
|----|------|
| **C（本轨）** | Era D planning **started** · Phase 3.5 remote landing **closed** |
| **B** | `b-class-phase3-clean-push` / Case B on `origin/main` — separate track; do not mix commits |
| **A / D** | Still finishing Era C tail per [eraD_execution_plan.md](../../plans/eraD_execution_plan.md) §9.2 |

---

## Gate after planning approval

| Gate | Value now | After human approve planning |
|------|-----------|------------------------------|
| `c_class_erad_resume_stability_planning_gate` | `READY_FOR_APPROVAL` | `PASS_WITH_CAVEAT`（规划收口） |
| `phase35_clean_push_gate` | `PASS_WITH_CAVEAT` | **unchanged** |
