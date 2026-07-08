# CNINFO C-Class Registry Candidate Quality Summary

_生成时间：2026-07-08T08:52:30Z_

> **性质：** registry candidate 离线 QA 摘要。**非 production registry** · **未修改 candidate CSV**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

# Overall

| 指标 | 值 |
|------|-----|
| candidate_count | **6124** |
| high_confidence | **863** |
| medium_confidence | **46** |
| low_confidence | **5215** |
| QA report 行数 | **767** |

---

# Identity Quality

| 指标 | 值 |
|------|-----|
| missing identity 行数 | **0** |
| missing_rate | **0.0** |
| duplicate findings | **508** |
| org_id conflict 组 | **259** |
| org_id conflict 影响公司数 | **518** |
| flagged conflict 行 | **518** |

### missing 字段分布

| field | count |
|-------|-------|
| — | 0 |

### duplicate 分类

| classification | count |
|----------------|-------|
| duplicate_identity | 1 |
| needs_manual_review | 241 |
| possible_legacy_mapping | 251 |
| possible_rename | 15 |

### org_id conflict 说明

案例：839729 / 920729 — 同 org_id `gfbj0839729`，不同 security identity；conflict_status=review_required；不自动合并

---

# Universe Lineage

| 切片 | candidate 行数 | 预期 |
|------|----------------|------|
| 863 active | **863** | 863 |
| 26 hold | **26** | 26 |
| BSE 920 | **12** | 12 |
| BSE legacy | **8** | 8 |
| 6124 baseline 填充 | **5215** | ~5215 |
| missing_lineage | **0** | 0 |
| unexpected_records | **0** | 0 |

---

# Confidence Review

| level | count | 说明 |
|-------|-------|------|
| high | **863** | 863 validated C-class（harvest_863_yaml + snapshot enrichment） |
| medium | **46** | hold / BSE / org_id conflict 等特殊案例 |
| low | **5215** | Era B baseline only（full_market_2024 填充） |

**政策：** 本轮不升级 confidence。

---

# Decision

| 项 | 值 |
|----|-----|
| **registry_candidate_quality_gate** | **`PASS_WITH_CAVEAT`** |

---

## Caveats

- rename_history 未填充
- BSE legacy 映射未 probe
- org_id conflict 须人工 review（不自动合并）
- 无 CNINFO 在线 enrichment

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 未修改 candidate CSV
- 无 raw / normalized / snapshot 修改 · 非 production registry
