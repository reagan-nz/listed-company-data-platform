# CNINFO C-class — Snapshot exclusion prep · builder command draft
# PLAN ONLY · DO NOT RUN against production snapshot roots
# execute_production_snapshot_rebuild = false
# execute mode FORBIDDEN · exclusion-csv 仅 preparation dry-run

# --- Option A: 原始 universe + --exclusion-csv（未来 batch builder 接线）---
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --sample-file lab/eval_companies_c_class_fuller_market_slice1_200.yaml \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/ \
#   --exclusion-csv outputs/validation/cninfo_c_class_erad_snapshot_rebuild_dryrun/exclusion_reconcile.csv

# --- Option B: 本适配器已过滤 universe（当前离线可用 · 无 batch 接线依赖）---
# python3 lab/build_cninfo_c_class_snapshot_batch.py --dry-run \
#   --sample-file outputs/validation/cninfo_c_class_erad_snapshot_exclusion_prep_adapter/filtered_universe_included.yaml \
#   --harvest-root outputs/harvest/cninfo_c_class/fuller_market_slice1_200/ \
#   --output-root outputs/snapshot/cninfo_c_class/_mock_erad_rebuild_slice1_200_dryrun/

# 安全边界：
# - output-root 必须为 _mock_* 前缀
# - 禁止 863/phase3/phase35 生产 snapshot 根
# - 禁止 execute / approve-* 与本 draft 同用
