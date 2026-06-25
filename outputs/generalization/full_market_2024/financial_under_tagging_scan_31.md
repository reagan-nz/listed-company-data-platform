# Financial under-tagging scan #31

## 1. Scope and guardrails

- **Task:** Read-only inventory of companies in `full_market_2024` that appear financial-like but have `financial != true` in YAML.
- **Universe:** 6,124 companies in `lab/eval_companies_full_market_2024.yaml`; 87 marked `financial: true`; **6,037 non-financial** scanned.
- **Inputs inspected (read-only):**
  - `lab/eval_companies_full_market_2024.yaml`
  - `outputs/generalization/full_market_2024/eval_results.json`
  - `outputs/generalization/full_market_2024/{board}/{code}/company_profile.json`
  - `docs/financial_company_schema.md` (reference)
  - `#30g` over-tag report: `financial_subtype_review_30g.md`
- **Not done:** YAML edits, code edits, extraction, apply, CNINFO, SQLite, audit population rebuild, commits.
- **Guardrails applied:**
  - Do **not** classify on `投资` alone.
  - Do **not** treat industrial companies with finance subsidiaries as financial unless finance is dominant.
  - Do **not** auto-retag `金融街`-style real-estate names (see `#30g` `000402`).
  - Do **not** use `eval_results.suggested_profile` as a primary signal (1,872 non-fin rows score `bank` — mostly noise).
  - Pair `#31` under-tags with `#30g` over-tags in one human review batch before any YAML change.

## 2. Scan method

### 2.1 Primary heuristic (disclosure-first)

For each YAML company with `financial: false`, load stored `company_profile.json` and concatenate:

- `main_business_segments`
- `industry_discussion`
- `mda`
- `revenue_by_segment`
- `major_products`

Apply dominant-business regex patterns:

| Pattern family | Candidate type |
|---|---|
| Securities core / 证券子公司 | broker |
| 多元金融 / 产业金融 / 类金融 | financial_holding |
| Dominant leasing / 飞机租赁 | leasing |
| Trust license / 信托业务 | trust |
| 期货经纪 | futures |
| 典当 / 担保 / 小贷 / 保理 | specialty_finance |
| 吸收公众存款 / 商业银行 | bank |
| 原保险保费 / 保险服务收入 | insurer |

### 2.2 Secondary heuristic (name-only, manual add)

Short-name keyword scan on non-financial universe for: 银行, 保险, 证券, 信托, 期货, 租赁, 资本, 金控.

Only **6 name hits** (all 资本/租赁); most true under-tags (e.g. 中国人保, 申万宏源) **do not** contain finance keywords in `short_name`. Name-only is insufficient alone.

### 2.3 Manual curation pass

Automated hits were reviewed against disclosure text. Known false-positive classes were downgraded:

- Fintech / financial-IT vendors (恒生电子, 安硕信息, 中科软, …)
- Industrial / utility with finance mentions (辽宁成大, 哈投股份, 中国铁建, …)
- Shipping/container industrial leasing (中远海发)
- Real-estate developers with finance wording (万科A)
- Name collisions (宏源药业)
- Missing profile / delisted edge cases

### 2.4 Outputs

- `financial_under_tagging_candidates_31.csv` — 53 curated rows
- This report

## 3. Candidate summary table

| Confidence | Count | Interpretation |
|---|---:|---|
| **High** | 11 | Clear financial institution / dominant finance ops; strong YAML under-tag |
| **Medium** | 10 | Financial holding, mixed ops, or specialty finance needing subtype review |
| **Low** | 32 | Keyword-only or vendor/industrial false positives; document only |
| **Total** | **53** | From 6,037 non-financial universe |

### By candidate type (high + medium only)

| Type | High | Medium |
|---|---:|---:|
| insurer | 4 | 0 |
| broker | 4 | 0 |
| bank | 1 | 0 |
| trust | 1 | 2 |
| leasing | 1 | 0 |
| financial_holding | 0 | 7 |
| specialty_finance | 0 | 1 |

### Notable YAML inconsistency

Three major listed insurers sit adjacent in YAML with mixed flags:

| Code | Name | YAML `financial` |
|---|---|---|
| `601628` | 中国人寿 | `true` |
| `601336` | 新华保险 | `true` |
| `601318` | 中国平安 | **`false`** ← under-tag |
| `601319` | 中国人保 | **`false`** ← under-tag |
| `601601` | 中国太保 | **`false`** ← under-tag |

This suggests the financial flag was applied inconsistently rather than a systematic sector omission.

## 4. High-confidence candidates

These companies have dominant financial-institution disclosures and stored `schema_profile=industrial`. Recommended for YAML `financial: true` **after** human sign-off and subtype assignment.

| Code | Name | Board | Type | Key evidence |
|---|---|---|---|---|
| `601318` | 中国平安 | sse_main | insurer | Insurance/financial conglomerate; peers `601628`/`601336` already tagged |
| `601319` | 中国人保 | sse_main | insurer | Insurance service income; industry discussion is insurance sector |
| `601601` | 中国太保 | sse_main | insurer | Segment table: 太保寿险 / 太保产险 |
| `000627` | *ST天茂 | szse_main | insurer | Holding company; operating business is insurance subsidiaries |
| `002839` | 张家港行 | szse_main | bank | Commercial bank scope; banking MD&A |
| `000563` | 陕国投A | szse_main | trust | Trust license and trust business scope |
| `000166` | 申万宏源 | szse_main | broker | Securities business as core operating segment |
| `600095` | 湘财股份 | sse_main | broker | Operating business dominated by 湘财证券 |
| `600621` | 华鑫股份 | sse_main | broker | Operating business via 华鑫证券 |
| `300059` | 东方财富 | chinext | broker | Licensed securities/futures brokerage (internet platform model) |
| `000415` | 渤海租赁 | szse_main | leasing | Dominant aircraft/container leasing |

**Suggested subtype mapping (for later YAML/schema work, not applied here):**

- Insurers → `insurer` profile (same as `601628`, `601336`)
- `002839` → `bank`
- `000563` → `trust` / `other_financial` pending trust schema maturity
- Broker holdings → `broker` (parent may need holding note like `#30g` `600318`)
- `000415` → `other_financial` / leasing bucket

## 5. Medium-confidence / human-review candidates

| Code | Name | Type | Why medium |
|---|---|---|---|
| `600061` | 国投资本 | financial_holding | Multi-financial platform (securities/trust/fund/futures) |
| `600390` | 五矿资本 | financial_holding | 央企产业金融; trust/futures/insurance exposure |
| `000617` | 中油资本 | financial_holding | Bank/trust/insurance/leasing subsidiaries |
| `002423` | 中粮资本 | financial_holding | Capital platform with trust/futures/insurance |
| `000987` | 越秀资本 | financial_holding | Historically diversified finance; now mixed with new-energy assets |
| `600705` | 中航产融 | financial_holding | Aviation industry financial holding platform |
| `600517` | 国网英大 | trust | Trust/finance exposure; confirm dominant segment |
| `600120` | 浙江东方 | trust | Trust/finance exposure; confirm dominant segment |
| `000532` | 华金资本 | financial_holding | Name-only add; no disclosure pattern hit in stored profile |
| `600830` | 香溢融通 | specialty_finance | Core 担保/典当/融资租赁; also trade segment — similar to `#30g` `600318` pattern |

**Human review questions for medium bucket:**

1. Is finance the **reporting** identity or just a subsidiary block inside an industrial parent?
2. Which `schema_profile` fits: `other_financial`, `trust`, `broker`, or mixed holding?
3. Should specialty-finance (`600830`) use the same schema as `#30g` `600318` (diversified / other_financial)?

## 6. False-positive patterns

| Pattern | Example codes | Why not financial |
|---|---|---|
| **Fintech / financial IT vendor** | `600570`, `002657`, `300380`, `300468`, `300541`, `300561`, `603927`, `688590` | Serves banks/insurers; disclosure mentions client industries |
| **Industrial + finance wording** | `600739`, `600868`, `600704`, `601186` | Core business is biopharma, coal, supply-chain, construction |
| **Utility + futures mention** | `600864` | Power/heat utility dominant |
| **Infrastructure + finance subsidiary** | `600548`, `600820`, `600834` | Toll-road / metro / construction operators |
| **Real estate + 多元金融** | `000002` | Developer; finance is investment/subsidiary context |
| **Shipping / container leasing** | `601866` | Industrial shipping with leased assets; not FI schema |
| **Name collision** | `301246` 宏源药业 | Pharma; “宏源” ≠ 申万宏源 |
| **Specialty finance keyword in non-core line** | `000828`, `600611`, `600997` | 小贷/担保 appears in passing, not dominant business |
| **Delisted / ST edge** | `000416`, `002808`, `600599` | Distressed or delisted; defer |
| **eval_results `suggested_profile=bank` noise** | ~1,872 non-fin rows | Text-scoring artifact; **not** used for this scan |

## 7. Recommended action

**Close #31 as inventory + human review gate.** Do not auto-apply YAML changes from this scan.

### Proposed human review batch (combine with #30g)

| Direction | Codes | Action |
|---|---|---|
| **Under-tag (high)** | `601318`, `601319`, `601601`, `000627`, `002839`, `000563`, `000166`, `600095`, `600621`, `300059`, `000415` | Approve `financial: true` + assign subtype |
| **Under-tag (medium)** | `600061`, `600390`, `000617`, `002423`, `000987`, `600705`, `600517`, `600120`, `000532`, `600830` | Review dominant business + subtype |
| **Over-tag (#30g)** | `000402`, `600816`, `600318` | Review remove/downgrade broker/bank subtype |

### Priority order

1. **Tier A:** `601318`, `601319`, `601601`, `002839`, `000563` — flagship FIs with clear disclosures
2. **Tier B:** broker holdings `000166`, `600095`, `600621`, `300059`
3. **Tier C:** capital platforms + specialty finance (medium bucket + `#30g` trio)

## 8. Validation plan if YAML retag is approved

For **selected codes only** (not full-market re-run):

1. Update `lab/eval_companies_full_market_2024.yaml` — set `financial: true` and document intended subtype in review notes.
2. Re-extract **only** approved companies (CNINFO PDF → `company_profile.json`).
3. Re-run **strict financial audit** only for those companies (`lab/strict_audit_financial_full_market.py`).
4. Compare before/after:
   - Field applicability (`found` / `partial` / `not_found`)
   - Strict audit labels (`usable` / `partial` / `MISSED`)
   - `schema_profile` resolution vs intended subtype
5. **Do not** merge financial metric deltas into non-fin `9.43/11` headline without explicit methodology update.
6. For over-tags (`000402`): validate **removal** improves industrial-field applicability before flipping `financial: false`.

## 9. Safe-to-commit / do-not-commit list

### Safe to commit (this task only)

- `outputs/generalization/full_market_2024/financial_under_tagging_scan_31.md`
- `outputs/generalization/full_market_2024/financial_under_tagging_candidates_31.csv`

### Do not commit from this task

- Any YAML changes (`eval_companies_full_market_2024.yaml`)
- Any code / audit script changes
- Any `company_profile.json` re-extraction outputs
- Any `eval_results.json` regeneration
- Any `financial_audit_population.csv` / audit summary rebuild
- Prior uncommitted `#30` docs unless separately approved

## 10. GitHub #31 progress comment (中文)

---

**#31 金融欠标扫描 — 只读盘点完成**

**范围：** `full_market_2024` 共 6124 家，其中 YAML `financial:true` 87 家；对剩余 **6037** 家非金融公司做披露优先扫描 + 人工复核。

**方法：**
- 读取 `company_profile.json` 中主营业务/行业讨论/MD&A/分板块收入等字段
- 匹配银行/券商/保险/信托/租赁/类金融等主导业务模式
- 排除金融科技软件商、工业+金融措辞、基建/地产子公司金融表述等误报
- **未使用** `eval_results.suggested_profile`（非金融样本中 1872 家被噪声标为 bank）

**结果：**
- 候选 **53** 家（高 11 / 中 10 / 低 32）
- 交付物：
  - `financial_under_tagging_scan_31.md`
  - `financial_under_tagging_candidates_31.csv`

**高置信欠标（建议人工确认后改 YAML）：**
- 保险：`601318` 中国平安、`601319` 中国人保、`601601` 中国太保、`000627` *ST天茂（与已标 `601628`/`601336` 并列，YAML 不一致明显）
- 银行：`002839` 张家港行
- 信托：`000563` 陕国投A
- 券商：`000166` 申万宏源、`600095` 湘财股份、`600621` 华鑫股份、`300059` 东方财富
- 租赁：`000415` 渤海租赁

**中置信（需.subtype 人工判定）：** 国投资本/五矿资本/中油资本/中粮资本/越秀资本/中航产融/国网英大/浙江东方/华金资本/香溢融通 等

**常见误报：** 恒生电子、安硕信息、中科软等金融 IT；辽宁成大、哈投股份、中远海发、万科A 等

**建议：** 本 issue **以盘点 + 人工复核门禁关闭**，不自动改 YAML。下一步与 **#30g 过标**（`000402`/`600816`/`600318`）合并人工批次，批准后再按 validation plan 定点 re-extract + strict audit。

**未改动：** YAML / 代码 / profile / eval / audit population / 无 commit

---

## Appendix: Full candidate list (high + medium)

See `financial_under_tagging_candidates_31.csv` for all 53 rows including low-confidence false positives.
