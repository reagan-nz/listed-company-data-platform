# CNINFO D 类 DLC006R — Disclosure Evidence Reconciliation Note

_生成时间：2026-07-10_

> **性质：** Option C 离线披露证据谱系注记 only · **无 CNINFO** · **无 promotion** · **不是 verified**

**人工决策：** Option A + Option C · disclosure **单独保留** · **不** promote 至 `captured_normal`

---

## 1. What Human Disclosure Evidence Says

| 项 | 值 |
|----|-----|
| company | **301259** 艾布鲁 |
| component | `shareholder_change` |
| anchor_date | **2024-07-16** |
| evidence_label | `shareholder_change_announcement` |
| description | 艾布鲁披露《简式权益变动报告书（一）》（CNINFO 简式权益变动报告书），正诚2号持股由 8,385,000 股、5.3750% 变为 7,799,900 股、4.9999%，不再是公司持股 5%以上股东 |
| source | human intake · CNINFO finalpage 引用（离线记录） |

---

## 2. Why It Matters

- 证明 **人工已知** 该公司在 anchor 日附近存在权益变动披露事件
- 支持 known-event replacement 候选 intake 校验（`HUMAN_CANDIDATE_VALIDATED`）
- 为下游审计提供 **披露谱系** 参考 — **非** 组件探针命中证明

---

## 3. Why It Is Not Structured Component Capture

| 证据轨 | 来源 | 可否等同 structured capture |
|--------|------|----------------------------|
| human disclosure | intake 描述 · PDF 引用 | **否** |
| metadata probe | `shareholeder/detail` API 公司级行 | **是**（仅当命中） |

DLC006R metadata 探针：**31** requests · **0** company-level rows → structured component **unresolved**

---

## 4. Why It Cannot Override empty_but_valid_after_budget

- runner 判定基于 API 返回的公司级 JSON 行数 · **非** 披露文本
- `empty_but_valid` 表示 endpoint 合法响应但无匹配公司行 — quality policy 允许
- 人工披露 **不改变** retrieval_status / record_count / acceptable 字段
- **禁止** 用披露内容覆盖 `empty_but_valid_after_budget`

---

## 5. Conceptual Storage as Separate Lineage Evidence

```text
human_evidence_track/
  DLC006R/
    evidence_type: shareholder_change_announcement
    event_date: 2024-07-16
    description: (intake text)
    lineage_role: separate_disclosure_reference_only
    promotes_captured_normal: false

structured_component_track/
  DLC006R/
    status: unresolved_empty_but_valid_after_budget
    metadata_probe_total: 31
    record_count: 0
```

两轨 **并行保留** · **不 merge**

---

## 6. Allowed Wording

- human disclosure evidence exists
- disclosure lineage retained separately
- structured shareholder_change component unresolved
- component gap accepted with caveat
- accepted_component_gap_with_separate_disclosure_evidence

---

## 7. Forbidden Wording

- captured_normal（针对 DLC006R structured component）
- verified
- production_ready
- structured component successfully captured
- disclosure evidence proves component capture
- merge disclosure into structured event
- testing_stable_sample

---

## 8. Gate Reference

| gate | 值 |
|------|-----|
| final_closure_gate | **PASS_WITH_CAVEAT** |
| DLC006R captured_normal_allowed | **no** |
| execution gates | **FAIL_REVIEW_REQUIRED**（保持） |

**CNINFO calls（本回合）：0**
