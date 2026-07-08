# CNINFO C-Class Registry Rename History Signoff Summary

_生成时间：2026-07-08_

> **性质：** rename history 人工 signoff 决策记录。**仅决策记录** · **不合并身份** · **未修改 registry candidate**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**Gate：** `registry_rename_history_signoff_gate = PASS`

---

# Overall

| 指标 | 值 |
|------|-----|
| rename_total | **15** |
| approved_rename_history | **10** |
| manual_identity_review | **5** |
| identity merge executed | **否** |

---

# Approved Rename History

以下 **10** 例批准为 `rename_history_candidate`（血缘元数据 only）：

| # | old_code → new_code | old_name → new_name | org_id |
|---|---------------------|---------------------|--------|
| 1 | 000022 → 001872 | 深赤湾A → 招商港口 | gssz0000022 |
| 2 | 000043 → 001914 | 中航善达 → 招商积余 | gssz0000043 |
| 3 | 000765 → 001267 | *ST华信 → 汇绿生态 | gssz0000765 |
| 4 | 300114 → 302132 | 中航电测 → 中航成飞 | 9900013408 |
| 5 | 430090 → 920090 | 同辉信息 → *ST同辉 | 9900020567 |
| 6 | 601268 → 601399 | *ST二重 → 国机重装 | 9900010450 |
| 7 | 601313 → 601360 | 江南嘉捷 → 三六零 | 9900021962 |
| 8 | 832023 → 920023 | 田野股份 → *ST田野 | gfbj0832023 |
| 9 | 833575 → 920575 | 康乐卫士 → *ST康乐 | gfbj0833575 |
| 10 | 835174 → 920174 | 五新隧装 → 五新智能 | gfbj0835174 |

**决策：** `approved_rename_history` · **policy：** `rename_history_candidate`

---

# Manual Identity Review

以下 **5** 例保持 `manual_identity_review`（未解析）：

| # | code 对 | 名称 | reason |
|---|---------|------|--------|
| 1 | 600087 → 601975 | 退市长油 → 招商南油 | historical_listing_transition |
| 2 | 688287 → 832317 | 退市观典 → 观典防务 | cross_market_transition |
| 3 | 839680 → 920680 | *ST广道 → 广道退 | delisting_status_change |
| 4 | 600631 ↔ 600827 | 百联股份 | same_name_code_change · needs_security_identity_review |
| 5 | 600637 ↔ 600832 | 东方明珠 | same_name_code_change · needs_security_identity_review |

**说明：** 以上**非**普通 rename 事件，涉及：

- 退市 / 重新上市（delisting / relisting）
- 跨市场过渡（科创板 ↔ 北交所）
- 退市状态变更
- 同名不同证券代码 / org_id 歧义

**决策：** `manual_identity_review` · **不 resolve**

---

# Registry Policy

| 项 | 政策 |
|----|------|
| **rename_history** | 血缘元数据（lineage metadata） |
| **不替代** | company identity |
| **不触发** | identity merge |
| **不修改** | registry candidate CSV |
| **不迁移** | harvest / snapshot 数据 |

```
rename_history signoff = 历史更名链记录候选
                      ≠ canonical identity 替换
                      ≠ 数据合并
```

---

# Gate

| 项 | 值 |
|----|-----|
| **registry_rename_history_signoff_gate** | **`PASS`** |

---

## 剩余冲突状态（rename 队列外）

| 队列 | 状态 |
|------|------|
| BSE legacy mapping | fast triage 完成 · 待 signoff |
| duplicate identity | 1 例 · 待 signoff |
| manual high risk（defer） | 241 例 · likely_safe_later |

rename 队列 **15/15** 已 signoff（10 approved · 5 manual unresolved）。

---

## 红线确认

- 无 CNINFO · 无 live · 无 harvest · **无 identity merge**
- 未修改 registry candidate · 非 production registry · 不写 verified

---

## eraC 章节

- 本节对应 **§7cn Registry Rename History Signoff**
- 上一节 §7cm Registry Conflict Fast Triage 已完成
