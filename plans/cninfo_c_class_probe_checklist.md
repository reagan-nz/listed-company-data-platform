# CNINFO C 类 Probe Checklist

_最后更新：2026-07-05_

> **Probe Plan：** [cninfo_c_class_devtools_probe_plan.md](cninfo_c_class_devtools_probe_plan.md)  
> **记录模板：** [fixtures/c_class/probe/c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml)  
> **Candidate YAML：** [config/cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml)

人工 DevTools probe 时使用本清单。**每探一个 source × 一家公司** 走一遍；回填 YAML 前再完成 §4。

---

## 1. Probe 前检查

在打开 CNINFO F10 页面之前确认：

- [ ] `source_id` 存在于 [cninfo_c_class_source_candidates.yaml](../config/cninfo_c_class_source_candidates.yaml) 的 `sources[]`
- [ ] `company_code` 已从 known-company 列表选取（600000 / 300001 / 688001 之一）
- [ ] `org_id` 已查或计划在 probe 中确认（topSearch / identity mapping）
- [ ] 本 source **仅选 1–3 家公司**，非全市场
- [ ] 已复制 [c_class_probe_record_template.yaml](../fixtures/c_class/probe/c_class_probe_record_template.yaml) 或准备等价记录行
- [ ] 已准备记录 **request URL / params / response 片段**（截图或本地 JSON 文件）
- [ ] 确认 **不下载 PDF**、**不入库**、**不写 verified**
- [ ] 确认 **不登录**、**不绕验证码**；请求间隔 ≥ 0.6s
- [ ] candidate YAML 的 `endpoint` / `recommended_status` **本轮不修改**

---

## 2. DevTools 检查项

在浏览器 DevTools → Network 中：

- [ ] 切换到目标 F10 标签页后，Network **能看到新 request**
- [ ] 目标 request 为 **JSON / XHR**（`Content-Type: application/json` 或类似）
- [ ] 已排除静态资源（`.js` / `.css` / 图片）与无关 analytics
- [ ] `params` 中是否包含 `stockCode` / `orgId` / `companyCode` / `scode` 等（记录实际键名）
- [ ] response body 是否有 **`data` / `records` / `list` / `result`** 等数组或对象容器
- [ ] 数组元素字段能否对应 candidate `expected_fields` 与 [schemas/c_class/](../schemas/c_class/) 逻辑字段
- [ ] 是否依赖 **Referer** 或特定 **Origin**（记入 `headers_required_candidate`，**不记 Cookie**）
- [ ] 是否存在 **分页**（`pageNum` / `pageSize` / `total`）；若有多页，notes 说明是否只需第一页
- [ ] **board / market 差异**：同一 API 在 600000 vs 300001 vs 688001 上 params 是否不同
- [ ] 是否同一 endpoint 服务多个 `source_id`（若共享，notes 标明，避免重复回填）

---

## 3. Response 质量检查

对选中的 API response：

- [ ] HTTP 状态 **200**（非 200 记 `blocked` 或 `endpoint_not_found`）
- [ ] 响应体含 **业务数据**（非纯 `{code:0,msg:ok}` 空壳）
- [ ] **空响应** 时：结构是否仍合法 → 可标 `empty_but_valid_response`
- [ ] 同一 source 在第二家公司上 **字段名是否稳定**（`schema_unknown` 若漂移大）
- [ ] 返回中的公司代码 / 名称与 probe 的 `company_code` / `company_name` **一致**
- [ ] 排除 **HTML 页面** 误当作 JSON API（`Content-Type: text/html` → 非 endpoint）
- [ ] `row_count` 与页面展示行数 **大致一致**（股东/高管等列表）
- [ ] 敏感字段（身份证、手机号全量）**不写入 Git**；probe record 仅保留字段名

---

## 4. 回填前检查

在编辑 `cninfo_c_class_source_candidates.yaml` 之前（**单独步骤，需人工批准**）：

- [ ] 同一 `source_id` **至少 1 家公司** `probe_status=endpoint_found`（建议 3 家）
- [ ] `endpoint`（request_url）在多家公司上 **可复述** 或差异已文档化
- [ ] `records_path` **明确**且 probe 人可独立验证
- [ ] `sample_fields` 已保存（probe record 或本地 JSON）
- [ ] `raw_record_json` 样本可保留供 mapper / fixture 使用
- [ ] `recommended_status` 拟改为 **`testing` 及以下**（非 `testing_stable_sample` / `verified`）
- [ ] `verified` **仍为 false**
- [ ] 已重读 [cninfo_c_class_devtools_probe_plan.md](cninfo_c_class_devtools_probe_plan.md) §7 红线
- [ ] 计划重跑 `lab/lint_cninfo_c_class_registry.py`
- [ ] **未**修改 Phase 1 / B / D 类配置与 fixtures

---

## 5. 快速判定表

| 观察 | 建议 probe_status |
|------|-------------------|
| 清晰 JSON API + 有数据 + 字段可映射 | `endpoint_found` |
| 无 XHR / 仅 HTML 渲染 | `endpoint_not_found` |
| 200 + 合法 JSON + 空数组 | `empty_but_valid_response` |
| 403 / 429 / 验证码 / 需登录 | `blocked` |
| 有数据但字段对不上 schema | `schema_unknown` |
| 只探了 1 家 / 分页未确认 | `needs_more_probe` |

---

## 6. 记录归档

- 单次 probe 输出：**一条** `probe_records[]` 条目（或独立 YAML 文件，如 `c_class_probe_records_600000_basic.yaml`）。
- 模板文件 `c_class_probe_record_template.yaml` **保持 `template_only`**，不写入真实证据。
- 真实 probe 记录建议路径：`fixtures/c_class/probe/records/`（执行 probe 时创建；**本轮不预填真实数据**）。
