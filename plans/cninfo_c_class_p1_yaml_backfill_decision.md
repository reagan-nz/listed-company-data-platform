# CNINFO C 类 P1 YAML Backfill Decision

_最后更新：2026-07-06_

> **Probe review：** [cninfo_c_class_p1_probe_review.md](cninfo_c_class_p1_probe_review.md)  
> **Candidate YAML（待回填）：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)  
> **当前状态：** 决策文档已完成；**YAML 尚未修改**。

---

## 1. 目的

说明 P1 probe 审查后，哪些 source **可以**在下一批人工编辑中回填 `endpoint` / `params` / `records_path`，哪些 **暂缓**。

**本文件为决策草案，不自动执行回填。**

---

## 2. 建议回填

### cninfo_company_basic_profile

**建议：** 可以回填 endpoint；`recommended_status` **最多** `testing`。

```yaml
# 建议回填字段（草案 — 尚未写入 YAML）
endpoint: "https://www.cninfo.com.cn/data20/companyOverview/getCompanyIntroduction"
method: GET
params_template:
  scode: "{company_code}"
records_path: "data.records[0]"
sub_records:
  basic_information_path: "data.records[0].basicInformation[0]"
  listing_information_path: "data.records[0].listingInformation[0]"
known_caveats:
  - "600000 returned empty basicInformation/listingInformation"
  - "field semantics candidate-level; see basic_profile_field_mapping_draft"
recommended_status: testing
verified: false
```

**依据：** 2/3 `endpoint_found` + 1/3 `empty_but_valid_response`；endpoint 结构稳定。

---

### cninfo_company_security_profile

**建议：** 可以回填 endpoint；`recommended_status` **最多** `testing`。

```yaml
# 建议回填字段（草案 — 尚未写入 YAML）
endpoint: "https://www.cninfo.com.cn/new/newInterface/marketOverview"
method: GET
params_template:
  secCode: "{company_code}"
  orgId: "{org_id}"
  secType: "szshe"
records_path: "$"
known_caveats:
  - "secType value needs broader board validation (主板/创业板/科创板)"
  - "sshk/szhk semantics candidate-level"
recommended_status: testing
verified: false
```

**依据：** 3/3 `endpoint_found`；marketOverview 行为一致。

---

## 3. 建议暂缓

### cninfo_company_industry_profile

**原因：**

- 未发现独立 HTTP endpoint。
- 行业相关字段已在 `getCompanyIntroduction.basicInformation[0]` 中观察到：
  - `F032V` — 行业名称
  - `MARKET` — 板块
  - `F044V` — 指数/板块标签

**建议：**

| 项 | 值 |
|----|-----|
| `recommended_status` | 保持 **`candidate`** |
| `endpoint` | **不回填**（保持 `null`） |
| `derived_from_candidate` | `cninfo_company_basic_profile`（逻辑派生，可在 notes 或后续 registry 扩展字段中声明） |
| probe_status | 保持 **`needs_more_probe`** 直至派生策略在 validation script 中落地 |

**不单独回填 endpoint。**

---

## 4. 不回填项

### getHeadStripData（security_profile annex）

| 项 | 决策 |
|----|------|
| 是否作为独立 source | **否** |
| 角色 | `cninfo_company_security_profile` 的 **annex candidate** |
| 原因 | FxxxN 字段语义未确认；避免过早标准化或误入 `share_capital_profile` |
| 证据位置 | probe YAML `security_profile_annex` 块 |

**暂不作为独立 source 回填 candidate YAML。**

可在 `cninfo_company_security_profile.notes` 中追加 annex URL 引用（回填 basic/security 时可选）。

---

## 5. 回填前 checklist

执行 YAML 编辑前必须完成：

- [ ] [cninfo_c_class_p1_probe_review.md](cninfo_c_class_p1_probe_review.md) 已阅读并认可
- [ ] 本决策文档已与 probe records 交叉核对
- [ ] [cninfo_c_class_probe_checklist.md](cninfo_c_class_probe_checklist.md) **§4 回填前检查** 逐项通过
- [ ] **`verified` 保持 `false`**
- [ ] **`recommended_status` 不高于 `testing`**
- [ ] caveat 写入对应 source `notes`
- [ ] **未修改** Phase 1 / B / D 类文件
- [ ] 回填后计划重跑 `lab/lint_cninfo_c_class_registry.py`

---

## 6. 回填后下一步

1. **人工更新** `config/cninfo_c_class_source_candidates.yaml`（basic + security 两项）。
2. **重跑** `lab/lint_cninfo_c_class_registry.py`；确认 endpoint 非 null 后 lint 行为符合预期。
3. **建立** C 类 known-company **live validation script**（config 驱动，仅 3 家公司）。
4. **验证** 600000 empty 态、300001/688001 非空态、marketOverview 字段稳定性。
5. **可选：** 用 live 样本更新 offline fixtures / field mapping draft。
6. **不入库**；**不写 verified**；**不扩全市场**。

---

## 决策摘要

| source_id | 回填 endpoint | recommended_status（回填后） | 备注 |
|-----------|---------------|------------------------------|------|
| `cninfo_company_basic_profile` | **是** | `testing` | 600000 empty caveat |
| `cninfo_company_security_profile` | **是** | `testing` | secType / sshk/szhk caveat |
| `cninfo_company_industry_profile` | **否** | `candidate` | derived_from basic |
| `getHeadStripData` | **否** | — | security annex only |

**当前批次：** 决策已完成；**YAML 未回填**（等待 checklist 批准后单独 PR）。
