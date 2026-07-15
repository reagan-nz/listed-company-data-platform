# CNINFO B 类 Category Routing Offline Validation Summary

_生成时间：2026-07-15（离线 title routing validation）_

## 1. 目的

本次为 **离线 title routing validation**：根据 `cninfo_announcement_categories.yaml` 规则
对 benchmark 标题做 `route_to` / `document_type` 预测，**不请求 CNINFO**，**不代表** corpus coverage。
**不写 verified。**

## 2. 输入

| 文件 | 路径 |
|------|------|
| Category routing YAML | `config/cninfo_announcement_categories.yaml` |
| Known-document benchmark | `fixtures/b_class/known_documents/known_document_benchmark.yaml` |
| 脚本 | `lab/validate_cninfo_b_class_category_routing.py` |

## 3. 总体结果

| 指标 | 数值 |
|------|------|
| total_benchmarks | **30** |
| route_match_count | **30** |
| route_mismatch_count | **0** |
| document_type_match_count | **30** |
| ambiguous_count | **1** |
| periodic_false_positive_caught_count | **13** / **13** |

**总体结论：** **PASS**

## 4. 分类型结果

### `periodic_report`

- total: **4**
- route_match: **4** / **4**

### `inquiry_reply`

- total: **3**
- route_match: **3** / **3**

### `meeting_notice`

- total: **3**
- route_match: **3** / **3**

### `general_announcement`

- total: **6**
- route_match: **6** / **6**

### `false_positive_guard`

- total: **13**
- route_match: **13** / **13**

## 5. 错误案例

_无 route_mismatch 或 document_type_mismatch。_

## 6. 结论

- 新 routing 规则 **可用于** B 类 corpus title classification 草案（离线 benchmark 层面）。
- 这 **不是** CNINFO retrieval coverage，**不**代表 PDF 可下载或语料非空。
- **不写 verified**；`category_code` 仍为 null。

## 7. 下一步

1. 加真实 known-document benchmark（公司代码 + 日期，仍可不联网先做结构）。
2. Probe 官方 CNINFO `category` code 填入 YAML。
3. Seed Phase 1 found reports 为 B 类 document fixtures。
4. 后续再做 corpus retrieval validation（known-document + category-sample）。

## 附录

详见 [cninfo_b_class_category_routing_report.csv](cninfo_b_class_category_routing_report.csv)。
