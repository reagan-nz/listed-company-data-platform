# CNINFO C-Class Phase 3 Batch 500 Harvest Dry-Run Review Checklist

_生成时间：2026-07-09_

> Phase 3 batch 500 harvest dry-run 审查清单。**规划产物** · **dry-run 未执行**

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**batch_id：** `phase3_batch_500_001`

---

# Preflight（dry-run 执行前）

- [ ] 1. `company_count` = **500**
- [ ] 2. `planned_http_cases` = **3500**
- [ ] 3. `matrix_rows` = **5000**
- [ ] 4. no **863** overlap（already_in_c_class = 0）
- [ ] 5. no **Phase 2 smoke** overlap（200 codes = 0）
- [ ] 6. no **Phase 2 failure** overlap（12 codes = 0）
- [ ] 7. no **delisted** rows（listing_status = delisted count = 0）
- [ ] 8. no **退 / 退市 / *ST** name rows
- [ ] 9. no **BSE** rows
- [ ] 10. no **hold** rows
- [ ] 11. no **manual_review** rows
- [ ] 12. no **identity_conflict** rows
- [ ] 13. **security** observe-only（非 main gate 源）
- [ ] 14. **output root** isolated：`outputs/harvest/cninfo_c_class/phase3_batch_500_001/`
- [ ] 15. no **CNINFO** call during dry-run
- [ ] 16. no **harvest execution** during dry-run（raw/normalized = 0）
- [ ] 17. **live** requires explicit approval + runner flag extension

---

# Dry-Run Execution Review（未来执行后勾选）

- [ ] dry-run report CSV 行数 = **5000**
- [ ] dry-run summary 记录 companies = **500**
- [ ] validation summary gate 记录
- [ ] 863 主轨 mtime / 文件数未变
- [ ] Phase 2 `phase2_smoke_200/` 未写入
- [ ] `phase3_batch_500_001_harvest_dryrun_gate` = **PASS** 或 **PASS_WITH_CAVEAT**

---

# Live Boundary（始终）

- [ ] dry-run PASS **不**等于 live 批准
- [ ] `phase3_runner_approval_flag_required` = **true**
- [ ] `--approve-phase3-batch-500-harvest` 实现前 **禁止 live**

---

# References

- [dry-run plan](../../plans/cninfo_c_class_phase3_batch_500_001_harvest_dryrun_plan.md)
- [command checklist](../../plans/cninfo_c_class_phase3_batch_500_001_harvest_command_checklist.md)
- [expected case matrix](cninfo_c_class_phase3_batch_500_001_harvest_expected_case_matrix.csv)
- [batch YAML](../../lab/eval_companies_c_class_phase3_batch_500_001.yaml)

## 红线确认

- 未请求 CNINFO · 未 live · 未 harvest · 未 snapshot
