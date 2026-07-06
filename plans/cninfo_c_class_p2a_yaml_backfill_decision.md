# CNINFO C Class P2-A YAML Backfill Decision

_最后更新：2026-07-06_

> **P2 probe records：** [fixtures/c_class/probe/records/c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml)  
> **P2 probe plan：** [cninfo_c_class_p2_probe_plan.md](cninfo_c_class_p2_probe_plan.md)  
> **P1 backfill decision（对照）：** [cninfo_c_class_p1_yaml_backfill_decision.md](cninfo_c_class_p1_yaml_backfill_decision.md)  
> **Candidate YAML（待回填）：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)  
> **当前状态：** 决策文档已完成；**YAML 尚未修改**。

---

## 1. Decision summary

P2-A manual DevTools probe supports candidate YAML backfill for **four** C-class sources, but only to `recommended_status: testing`, `verified: false`.

| source_id | decision | max_status | verified | reason |
|-----------|----------|------------|----------|--------|
| `cninfo_executive_profile` | allow_yaml_backfill | testing | false | 3/3 endpoint_found on known-company sample; small sample only |
| `cninfo_share_capital_profile` | allow_yaml_backfill | testing | false | 3/3 endpoint_found on known-company sample; small sample only |
| `cninfo_top_shareholders_profile` | allow_yaml_backfill | testing | false | 3/3 endpoint_found on known-company sample; small sample only |
| `cninfo_top_float_shareholders_profile` | allow_yaml_backfill | testing | false | 3/3 endpoint_found on known-company sample; small sample only |

**本文件为决策草案，不自动执行回填。**

---

## 2. Probe evidence summary

| source_id | companies_tested | endpoint_found | blocked | schema_unexpected | records_path |
|-----------|------------------|----------------|---------|-------------------|--------------|
| `cninfo_executive_profile` | 3 | 3 | 0 | 0 | `data.records` |
| `cninfo_share_capital_profile` | 3 | 3 | 0 | 0 | `data.records` |
| `cninfo_top_shareholders_profile` | 3 | 3 | 0 | 0 | `data.records` |
| `cninfo_top_float_shareholders_profile` | 3 | 3 | 0 | 0 | `data.records` |

**Known companies：** 600000 浦发银行 · 300001 特锐德 · 688001 华兴源创。

**Observed：** HTTP 200, top-level `code=200`, `data.resultCode="200"`, `data.resultMsg="success"`, `data.records` non-empty. No blocked / login / captcha. No `schema_unexpected`. Cookie/SID/Authorization **not** stored in probe records.

---

## 3. Endpoint candidates

### cninfo_executive_profile

```yaml
url: "https://www.cninfo.com.cn/data20/companyOverview/getCompanyExecutives"
method: GET
params_template:
  scode: "{company_code}"
records_path: "data.records"
result_code_path: "data.resultCode"
headers_required_candidate:
  - Referer
```

**row_count observed：** 19 / 17 / 13（600000 / 300001 / 688001）

---

### cninfo_share_capital_profile

```yaml
url: "https://www.cninfo.com.cn/data20/stockholderCapital/getStockStructure"
method: GET
params_template:
  scode: "{company_code}"
records_path: "data.records"
result_code_path: "data.resultCode"
headers_required_candidate:
  - Referer
```

**row_count observed：** 5 / 5 / 5

---

### cninfo_top_shareholders_profile

```yaml
url: "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenStockholders"
method: GET
params_template:
  scode: "{company_code}"
records_path: "data.records"
result_code_path: "data.resultCode"
headers_required_candidate:
  - Referer
```

**row_count observed：** 50 / 50 / 50（≈ 5 reporting periods × 10 holders）

---

### cninfo_top_float_shareholders_profile

```yaml
url: "https://www.cninfo.com.cn/data20/stockholderCapital/getTopTenCirculatingStockholders"
method: GET
params_template:
  scode: "{company_code}"
records_path: "data.records"
result_code_path: "data.resultCode"
headers_required_candidate:
  - Referer
```

**row_count observed：** 50 / 50 / 50（shape very close to `getTopTenStockholders`)

---

## 4. Candidate field mappings

### executive_profile

| Raw field | Candidate semantic |
|-----------|-------------------|
| F002V | executive_name |
| F009V | position_titles |
| F010V | gender |
| F012V | birth_year |
| F017V | education |
| F005N | shareholding_quantity_candidate |
| F012N | compensation_candidate |
| SEQID | row_sequence_id |
| F001V | person_id_candidate |

---

### share_capital_profile

| Raw field | Candidate semantic |
|-----------|-------------------|
| VARYDATE | change_date_or_report_date |
| F002V | change_reason_or_source |
| F021N | total_share_capital_candidate |
| F022N | circulating_share_capital_candidate |
| F023N | restricted_share_candidate |
| F024N | unrestricted_share_candidate |
| F028N | change_amount_candidate |
| F003N | total_capital_candidate |

---

### top_shareholders_profile and top_float_shareholders_profile

| Raw field | Candidate semantic |
|-----------|-------------------|
| F001D | report_date |
| F002V | shareholder_name |
| F003N | holding_amount_candidate |
| F004N | holding_ratio_percent_candidate |
| F005N | rank |
| F006V | share_type |
| F007V | change_status_or_change_amount_candidate |

**Note：** `top_float_shareholders` uses the same field shape; distinguish by `shareholder_scope: top_float_shareholder` in registry / mapper, not by different API fields.

---

## 5. Caveats

- **3 known-company sample only**（600000 / 300001 / 688001）；非全市场验证。
- **Not full-market validation**；不得据此声称全 A 股可用。
- **Field units** for `FxxxN` numeric fields are **not fully confirmed**（UI 对照待补）。
- **F005N / F012N** in executive records remain **candidate-level**（持股数量 / 薪酬语义与单位待确认）。
- **F003N** in shareholder records likely holding amount but **unit requires confirmation**.
- **F007V** may be textual status（如 未变 / 新进）or numeric-looking change value；保持 candidate-level。
- **F017V** education may be **null** on some executive rows（688001 observed）。
- **No source is verified**；`verified` 必须保持 `false`。
- **Do not write `testing_stable_sample`** without separate approval。
- **No database ingestion**；不写 migration。

---

## 6. Backfill permission

### Approved next step

- Update [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) for the **four P2-A sources**
- Set `recommended_status: testing`
- Keep `verified: false`
- Add `endpoint` / `sample_observation` / `known_caveats` per source
- Rerun `lab/lint_cninfo_c_class_registry.py`

### Not approved

| 项 | 状态 |
|----|------|
| `verified: true` | **禁止** |
| `testing_stable_sample` | **禁止**（本轮） |
| Database ingestion | **禁止** |
| Full-market claims | **禁止** |
| Mapper implementation **before** YAML backfill | **不建议**（先 YAML + lint，再 mapper draft） |

---

## 7. Next step

**Next step is C-class P2-A YAML backfill v1**, followed by registry lint.

Suggested sequence（单独批次，需 checklist 批准）：

1. 人工更新 `cninfo_c_class_source_candidates.yaml`（executive + share_capital + top_shareholders + top_float_shareholders）。
2. 重跑 `lab/lint_cninfo_c_class_registry.py`。
3. 扩展 `validate_cninfo_c_class_live_sources.py` 或新建 P2 live validation v1（仅 3 家 × 4 源，受控请求）。
4. 再起草 per-source mapper + fixture + schema validation（仿 P1 basic/security 路径）。
5. **不入库**；**不写 verified**；**不扩全市场**。

---

## 参考

| 文档 | 路径 |
|------|------|
| P2 probe records | [c_class_p2_probe_records.yaml](../fixtures/c_class/probe/records/c_class_p2_probe_records.yaml) |
| P2 checklist §6 | [cninfo_c_class_p2_probe_checklist.md](cninfo_c_class_p2_probe_checklist.md) |
| JSON Schema | [schemas/c_class/](../schemas/c_class/)（`c_executive_profile`, `c_share_capital_profile`, `c_shareholder_profile`） |
