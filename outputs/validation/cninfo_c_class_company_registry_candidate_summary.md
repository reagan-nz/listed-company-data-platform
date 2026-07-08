# CNINFO C-Class Company Registry Candidate Summary

_生成时间：2026-07-08T08:41:52Z_

> **性质：** `company_registry_candidate` 离线派生摘要。**非 production registry**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

---

## Universe

| 切片 | 输入规模 |
|------|----------|
| active universe（863 harvest） | **863** |
| hold universe（26 all6 hold） | **26** |
| BSE universe（920 + legacy） | **20**（920=12 · legacy=8） |
| Era B baseline（6124） | **6124** |

---

## Candidate statistics

| 指标 | 值 |
|------|-----|
| candidate 行数 | **6124** |
| identity conflict（org_id 组） | **259** |
| identity conflict 行数 | **518** |
| hold 行数 | **34** |
| legacy code 相关行数 | **9** |

### source 分布

| source | 行数 |
|--------|------|
| `full_market_2024` | 5215 |
| `harvest_863_yaml` | 863 |
| `hold_26_yaml` | 26 |
| `bse_920_yaml` | 12 |
| `bse_legacy_yaml` | 8 |

---

## Confidence distribution

| confidence | 行数 |
|------------|------|
| high | **863** |
| medium | **46** |
| low | **5215** |

---

## Caveats

- rename_history 未填充（默认 `[]`）
- BSE legacy 映射未 probe 验证（仅文档与 YAML duplicate_of）
- org_id conflict 须人工 review（不自动合并）
- 无 CNINFO 在线 enrichment

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · 无 snapshot rebuild
- 未修改 raw / normalized / field_inventory / snapshot JSON
- 非 production registry · 不写 verified
