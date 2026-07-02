# Era C 执行计划（A–F 分层验证 · Composer 可执行）

_最后更新：2026-07-02_

> **权威分类与验证口径：** [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)  
> **仓库导航：** [PROJECT_MAP.md](../PROJECT_MAP.md) · **当前进展：** [CURRENT_STATUS.md](../CURRENT_STATUS.md)
>
> **只在 Era C 范围内改动**；**不要同时展开所有 Phase**；红线见第 1 节。

---

## 0. Era C 完成定义（三层 + A–F 分层）

1. **穷尽式收集**：CNINFO 可见栏目/入口清单（A–F 分层表已覆盖官网观察版，可持续补漏）。
2. **分类**：每项归入 A–F 之一；A = 类年报 PDF 流，B–F = 非类年报路径。
3. **分层验证**：每层用**各自口径**验证完毕，状态回填分层表。

> `cninfo_capability_final_summary.md` 与 `cninfo_report_announcement_validation_summary.md` 均为**阶段快照**；A 类最终结论以 **Phase 1 coverage%** 为准。

---

## 1. 红线

- 不接 PostgreSQL / MinIO / MongoDB；不下载/解析 PDF 正文。
- 不绕过登录/验证码/付费/权限；请求间 sleep；不用 BrowserUser。
- `recommended_status` 只用 `candidate`/`testing`/`partial`/`postponed`/`rejected`，**不写 `verified`**。
- 不碰 Era A / Era B 代码；联网脚本本地手动跑。

---

## 2. Phase 路线图（严格顺序，一次只做一个 Phase）

| Phase | 内容 | 状态 | 主要产出 |
|---|---|---|---|
| **0** | 固化 A–F 分层表 + 统一验证口径 | **已完成** | [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md) |
| **1** | A 类：新建 `validate_cninfo_report_coverage.py`，per-company coverage% | **下一步** | `cninfo_report_coverage_validation{.csv,_summary.md}` |
| **2** | D 类：手动 DevTools 抓 endpoint → `cninfo_table_sources.yaml` → 表格验证脚本 | 待 Phase 1 后 | `cninfo_table_*_validation` |
| **3** | B 类：补官方 `category` 码；corpus + known-event 口径改造 | 待 Phase 2 后 | 更新 announcement category 验证 |
| **4** | C 类 F10 标签页；E 类可达性三态；F 类暂缓 | 待 Phase 3 后 | F10 / reachability summary |

---

## 3. Phase 0 — 已完成

- 新建 [cninfo_data_source_layered_inventory.md](cninfo_data_source_layered_inventory.md)：A–F 清单 + 每类分母/分子/成功指标。
- 更新 PROJECT_MAP、CURRENT_STATUS、本文件。
- 明确：旧 `368/780` 行计数**不能**作为 A 类最终 coverage 结论。

---

## 4. Phase 1 — 下一步（A 类 coverage 重算）

### 目标
用干净口径回答：**「每家 mapped 公司的每个期望报告期，到底找没找到？」**

### 任务
1. **新建** `lab/validate_cninfo_report_coverage.py`（不改旧 `validate_cninfo_report_announcements.py`，旧脚本标注 deprecated 参考）。
2. **分母**：mapped 公司（30 家）× 期望报告期（如 2023/2024 年报、半年报、Q1、Q3）。
3. **分子**：命中且 `pdf_url` 非空、`report_period` 与期望一致（非 `unknown`）；多 strategy 仅内部回退，**每期望报告一行**。
4. **输出**：coverage% 总计 + 按 report_type / board 拆分；`recommended_status` 据结果填 `testing` 或 `partial`。
5. **🧑 本地跑** → 回填分层表 A 类状态。

### Composer 提示词（Phase 1）
```
先读 PROJECT_MAP.md、plans/cninfo_data_source_layered_inventory.md、plans/eraC_execution_plan.md。
只做 Phase 1：新建 lab/validate_cninfo_report_coverage.py。
分母=mapped公司×期望报告期；分子=命中且pdf_url+report_period正确；每期望报告一行。
复用 validate_cninfo_report_announcements.py 的请求逻辑，不改旧脚本。
输出 outputs/validation/cninfo_report_coverage_validation.csv 和 _summary.md。
红线：不联网执行、不接数据库、不写 verified。
```

### 完成标准
- summary 顶部写明分母/分子定义与 coverage%。
- 能明确判断 A 类是否 `testing` 或 `partial`。

---

## 5. Phase 2 — D 类固定表格（Phase 1 后再做）

1. 🧑 浏览器 DevTools 抓 XHR（先做预约披露，再融资融券/大宗交易/限售解禁/公开信息）。
2. 写入 `config/cninfo_table_sources.yaml`。
3. 新建 `lab/validate_cninfo_table_sources.py`：字段可得性%。

**不要与 Phase 1 并行。**

---

## 6. Phase 3 — B 类事件公告（Phase 2 后再做）

1. 为 B 类清单补 CNINFO 官方 `category` 码到 `cninfo_announcement_categories.yaml`。
2. 改造 `validate_cninfo_announcement_categories.py`：corpus 口径 + known-event benchmark；**禁止**随机公司 success rate 作主指标。

---

## 7. Phase 4 — C / E / F（Phase 3 后再做）

- **C**：F10 orgId + 股本股东/治理/财务摘要标签页入口探测；字段可得性%。
- **E**：可达性三态脚本（公开 / 需登录 / 需权限），不采数据。
- **F**：仅记可达性，暂缓。

---

## 8. 便宜模型通用开场

```
这是 CNINFO Era C 项目。先读：
- PROJECT_MAP.md
- plans/cninfo_data_source_layered_inventory.md
- plans/eraC_execution_plan.md
当前 Phase：<填 0/1/2/3/4>。只做该 Phase，不要同时展开其他 Phase。
红线见 eraC_execution_plan 第 1 节。recommended_status 不写 verified。
我要做的是：<具体任务>
```

---

## 9. 旧任务清单（已 supersede，仅供参考）

以下任务基于旧「二分类 + success rate」口径，**不再作为当前主线**：

- ~~任务 0 穷尽收集 → 已并入 A–F 分层表~~
- ~~任务 A 完成 → 旧脚本保留，待 Phase 1 coverage 重算~~
- ~~任务 B/C 回填/总结 → 待 Phase 1 后用新口径更新~~

---

## 10. 额度作战（怎么挺到月底）

- 7/2–7/16：主用账号2，省着花；账号1 剩量只救火。
- 7/16 账号1 刷新：7/16–7/27 优先账号1。
- 7/27 账号2 刷新：7/27–7/31 用新账号2。
- **便宜模型干 80%**（写脚本、写文档）；**高级模型只干 Phase 规划/复盘/卡死**。
