# Era C 执行计划（1.5 天可完成 + 便宜模型可接手）

_最后更新：2026-07-02_

> **这份文件是给"未来的你 + 便宜/换代 AI 模型"用的执行清单。** 目标：在有限的高级模型额度下，**靠这份计划 + 便宜模型**把 Era C（CNINFO 数据源能力研究）做到一个完整、能交差的状态。
>
> 先读 [PROJECT_MAP.md](../PROJECT_MAP.md) 和 [CURRENT_STATUS.md](../CURRENT_STATUS.md) 再动手。**只在 Era C 范围内改动**：`lab/validate_cninfo_*.py`、`config/cninfo_*.yaml`、`outputs/validation/`、`plans/cninfo_data_source_value_inventory.md`。

---

## 0. Era C "完成"的定义（先对齐终点）

核心思路（按此推进，别缩窄）：**先把巨潮上"所有能看到、以及觉得可能获取"的数据/信息穷尽式地收集成一份清单 → 再分类成「类年报」和「完全不是年报」两大类 → 类年报沿已跑通的路径做扎实 → 再逐个研究非类年报怎么拿。** 所以 Era C 分三层，全部达成才算完成：

### 第 1 层：穷尽式收集清单（尚未完成，这是当前重点）
- 目标：把 CNINFO **每一个栏目/入口/页面/接口**都走一遍，记录"这里能看到什么、可能能拿到什么"，宁可多列也不要漏。
- 现状：`plans/cninfo_data_source_value_inventory.md` 第 3 节已有一份栏目清单，但**不保证穷尽**——需要真的去网站逐栏目核对、补齐遗漏（如公告全部子类型、F10 各标签页、专题页等）。
- 完成标准：清单覆盖到"再逛巨潮也基本发现不了新栏目"的程度。

### 第 2 层：分类（部分完成）
- 把清单里每一项明确打上标签：**类年报**（定期披露 + 标题稳定 + 有 PDF：年报/半年报/季报/业绩预告/业绩快报/招股书等）｜**非类年报**（公告事件流、F10 结构化字段、股本股东、风险监管、分红治理、互动易、市场行为等）。
- 现状：盘点表第 4 节有按数据类型的分类，但需按"类年报 / 非类年报"这个二分口径重新对齐并补全。

### 第 3 层：验证（仅"类年报"这一条完成，非类年报绝大多数未做）
- 类年报路径：✅ 年报/半年报/季报检索 + 报告期解析已跑通（`validate_cninfo_report_announcements.py`）。
- 非类年报：❌ 除少数 P0（最新公告、PDF 元数据、F10）做过小样本外，**大部分栏目尚未验证**——这是 Era C 剩下的主要工作量。

> 诚实结论：`cninfo_capability_final_summary.md` 只是"到今天为止"的阶段快照，**不代表 Era C 已完成**。真正完成需要第 1 层清单穷尽 + 第 3 层把非类年报逐个验证掉。

---

## 1. 红线（任何模型都必须遵守）

- 不接 PostgreSQL / MinIO / MongoDB。
- 不绕过登录/验证码/付费/权限；请求之间 sleep（脚本里已有 `SLEEP_SECONDS`）。
- 不做大规模抓取；不下载/解析 PDF 正文。
- `recommended_status` 只用 `candidate`/`testing`/`partial`，**不写 `verified`**。
- 不碰 Era A / Era B 代码（见 PROJECT_MAP）。
- 联网脚本**本地手动跑**（你自己关 VPN 跑），AI 只负责改代码/看结果/写文档，不需要它联网。

---

## 2. 任务清单（按顺序，每个都是小单元）

> 每个任务标了【谁做】：🧑 你自己（跑脚本/本地操作）｜🤖便宜 你 + 便宜模型（改代码/写文档）｜⭐高级 值得用高级模型（判断/复盘/卡住时）。

### 任务 0 —【🧑 + 🤖便宜】穷尽式收集 CNINFO 清单（当前重点，最先做）
- 🧑 你自己逐栏目逛一遍巨潮（首页导航、个股页各标签、信息披露/公告搜索、F10、专题页等），把"能看到什么、可能能拿到什么"随手记下来（栏目名 + 入口 URL + 看到的字段/内容）。
- 🤖便宜模型把你记的整理进 `plans/cninfo_data_source_value_inventory.md` 第 3 节清单，补齐遗漏项，并给每项打上「类年报 / 非类年报」标签。
- 完成标准：再逛也基本发现不了新栏目；每项都有二分类标签。
- 提示词见第 5 节【模板 0】。

### 任务 A —【已完成】类年报检索 + 报告期解析
- 脚本：`lab/validate_cninfo_report_announcements.py`
- 产物：`outputs/validation/cninfo_report_announcement_validation{.csv,_summary.md}`
- 结论：年报/半年报/季报可检索；`report_period` 解析 332/780（其余为 failed 行占位 unknown）。
- ✅ 无需再做，除非要扩展报告类型（见任务 D）。

### 任务 B —【🤖便宜】把类年报结论回填盘点表
- 目标：编辑 `plans/cninfo_data_source_value_inventory.md`，把"半年报""季报"两行的"当前状态"从`候选 / 待验证`改为 `testing / partial`，并在第 8 节补一行类年报验证结果（引用 `cninfo_report_announcement_validation_summary.md` 的数字：success 368/780、annual 98 / semi 55 / Q1 113 / Q3 102）。
- 完成标准：盘点表里类年报三项状态一致、指向了 summary。
- 提示词模板见第 5 节【模板 B】。

### 任务 C —【🤖便宜 + ⭐高级复盘】写 Era C 总结
- 目标：新建 `outputs/validation/cninfo_capability_final_summary.md`，一页纸包含：
  1. CNINFO 能**稳定**拿到什么（类年报文档流：标题/时间/PDF URL/报告期；公告 PDF 元数据）；
  2. **部分**能拿到什么（最新公告 34/40、F10 Playwright 22/30）；
  3. **还没验证**的（P1/P2 栏目列表，引用盘点表）；
  4. 边界：都是小样本 `testing/partial`，不等于全量可用，未接数据库。
- 便宜模型先起草，⭐**高级模型只做一次复盘**（检查数字对不对、有没有把 partial 写成 verified）。
- 提示词模板见第 5 节【模板 C】。

### 任务 D —【🧑 + 🤖便宜】（可选扩展）多一个类年报类型
- 只有余力才做。把"业绩预告"或"业绩快报"加进 `REPORT_TYPES`（`validate_cninfo_report_announcements.py` 顶部 dict），照现有格式加 `title_patterns` / `keywords_recent`。
- 🧑 你本地关 VPN 跑一遍脚本，看新类型 success 数。
- 🤖便宜模型帮你改 dict + 更新 summary 文字。
- 不做也不影响 Era C 收尾。

### 任务 E —【🧑】收尾提交
- `git add` 改动 → commit（信息参考现有风格：`validation: ...` / `docs: ...`）。
- 不 push 到 main 强制、不改 git config。

---

## 3. 1.5 天时间表（保守版）

| 时段 | 做什么 | 谁做 |
|---|---|---|
| 第 1 天上午 | 任务 B（回填盘点表） | 🤖便宜 |
| 第 1 天下午 | 任务 C 起草总结 | 🤖便宜 |
| 第 1 天傍晚 | 任务 C 复盘（1 次高级模型看一眼数字/措辞） | ⭐高级 |
| 第 2 天上午 | 任务 E 提交；若有余力做任务 D | 🧑 /🤖便宜 |
| 缓冲 | 出问题时再用高级模型救火 | ⭐高级 |

> 只要做完 B + C + E，Era C 就完整了。D 是加分项。

---

## 4. 卡住时的自救顺序（省高级额度）

1. 先看 `outputs/validation/` 里对应的 `_summary.md` 和 CSV，答案常常已经在里面。
2. 让便宜模型读 PROJECT_MAP + 本文件 + 目标脚本，先尝试。
3. 便宜模型连续 2 次没进展，再上高级模型，并**一次把上下文给全**（贴：报错、相关脚本片段、你想要的结果）。
4. 高级模型每次开场都先让它读 `PROJECT_MAP.md` + `plans/eraC_execution_plan.md`（这两份就是它的"记忆"）。

---

## 5. 便宜模型提示词模板（直接复制改）

**【模板 B｜回填盘点表】**
```
先读 PROJECT_MAP.md、CURRENT_STATUS.md、plans/eraC_execution_plan.md。
只做任务 B：编辑 plans/cninfo_data_source_value_inventory.md，
把"半年报""季报"两行当前状态改为 testing / partial，
并在第 8 节补一条类年报验证结果，引用 outputs/validation/cninfo_report_announcement_validation_summary.md
里的数字（success 368/780；annual 98 / semi 55 / Q1 113 / Q3 102）。
不要碰 Era A/B 代码，不改数据库相关内容，recommended_status 不写 verified。
```

**【模板 C｜写 Era C 总结】**
```
先读 PROJECT_MAP.md、CURRENT_STATUS.md、plans/cninfo_data_source_value_inventory.md，
以及 outputs/validation/ 下的 cninfo_p0_validation_final_summary.md 和
cninfo_report_announcement_validation_summary.md。
新建 outputs/validation/cninfo_capability_final_summary.md，一页纸总结：
CNINFO 能稳定拿到什么 / 部分能拿到什么 / 还没验证什么 / 边界。
数字必须来自上面两个 summary，不许编。partial 不能写成 verified。
```

**【通用开场（给任何模型）】**
```
这是 A 股 CNINFO 数据源研究项目。先读 PROJECT_MAP.md 和 CURRENT_STATUS.md 了解现状，
当前只在 Era C 范围内改动。红线见 plans/eraC_execution_plan.md 第 1 节。
我要做的是：<在这里写具体任务>
```

---

## 6. 额度作战（怎么挺到月底）

> 背景：账号1（$20，剩 5%，约 7-16 刷新）；账号2（$70，剩 ~88%，7-27 刷新）；需求到 7-31。

- **7/2–7/16**：主用**账号2**，但要省着花（它得撑到 7-27）。账号1 剩的 5% 只留给"一句话就能救命"的小事。
- **7/16 账号1 刷新（$20）**：7/16–7/27 优先用**账号1**，把账号2 省下来。
- **7/27 账号2 刷新（$70）**：7/27–7/31 用新的账号2，额度充裕。
- **核心省钱法**：让便宜模型干 80% 的活（改代码、写文档、跑常规），高级模型只干"规划 / 复盘 / 卡死救火"这 20%。每次高级模型开场先让它读 PROJECT_MAP + 本计划，避免它重新摸一遍仓库（那最烧钱）。
