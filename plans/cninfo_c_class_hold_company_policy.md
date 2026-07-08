# CNINFO C-Class Hold 公司策略

_生成时间：2026-07-08_

> **性质：** hold 公司侧轨政策规划（Era C Phase 4）。**仅规划** · **不执行 hold 变更** · **不写 verified**。

**C-class 状态：** `SNAPSHOT_GENERATED_QA_REVIEW`

**依据：** [26 all6 hold](../lab/eval_companies_c_class_889_rerun_all6_hold.yaml) · [889 post-retry decision](cninfo_c_class_889_post_retry_decision.md) · [source status decision](cninfo_c_class_source_status_decision.md)

---

## 1. 当前 Hold 状态

### 1.1 26 all6 hold 子集

| 项 | 值 |
|----|-----|
| 文件 | `lab/eval_companies_c_class_889_rerun_all6_hold.yaml` |
| 数量 | **26** |
| 来源 | 889 rerun 中 6/6 主源全失败集群 |
| 与 863 关系 | **已排除**（863 = 889 − 26） |

### 1.2 统一字段（hold YAML）

| 字段 | 值（全部 26 家） |
|------|------------------|
| `failed_source_count` | 6 |
| `hold_reason` | `sample_quality_or_status_review` |
| `retry_decision` | `hold_no_retry` |
| `notes` | `889 rerun all6; HTTP 500/9240002 or blocked; *ST/delisted-like` |

### 1.3 26 家公司代码

`000043, 000416, 000562, 000569, 000638, 000765, 000787, 000827, 000982, 002113, 002325, 002503, 002776, 300116, 300262, 600112, 600247, 600253, 600260, 600286, 600357, 600393, 600700, 600842, 601258, 603056`

### 1.4 诊断结论

- **非** harvest runner bug；**非** 样本清洗可自动修复
- 主因：HTTP 500 / `9240002` + 名称 *ST/退市特征
- 与 stable-200 twelve-fail 集 **无重叠**（独立集群）
- 889 partial-fail retry 后 residual 9 fail 为 **empty_but_valid** — 不同集群

### 1.5 其他 hold 池（非 26 all6）

| 池 | 数量 | 文件 | 关系 |
|----|------|------|------|
| BSE 83/87 legacy | 8 | `smoke_195_bse_legacy_hold.yaml` | 代码层不兼容 |
| abnormal_review | 3 | `smoke_195_abnormal_review.yaml` | ST/异常上市 |

---

## 2. 未来策略选项

### Option A — 永远排除（Permanent Exclusion）

| 优点 | 缺点 |
|------|------|
| 主 gate 最干净 | 全市场 registry 不完整 |
| 无额外 harvest 成本 | 退市/ST 公司信息永久缺失 |
| 与当前 863 政策一致 | 无法响应「公司恢复上市」 |

**适用：** 明确退市且无 F10 价值的代码。

### Option B — 独立侧轨 Universe（Recommended）

| 优点 | 缺点 |
|------|------|
| 主 universe 与 hold 分离，gate 清晰 | 需维护 hold registry |
| 可定期 recheck（年度/季报后） | 额外 QA 流程 |
| 支持「恢复上市」后回迁 | 仍可能 6/6 fail |

**适用：** *ST/异常状态但仍有监管/披露价值的公司。

### Option C — 仅 Document Archive

| 优点 | 缺点 |
|------|------|
| 不消耗 F10 harvest 配额 | 无 company profile snapshot |
| 可走 Era B 公告 corpus | 与 C-class snapshot 目标不一致 |
| 适合已退市公司 | 无法填充 18 模块 snapshot |

**适用：** 纯历史档案需求；与 C-class company object 目标弱相关。

---

## 3. 推荐默认政策

**推荐：Option B（独立侧轨 universe）+ 对明确退市公司倾向 Option C**

| 规则 | 政策 |
|------|------|
| 26 all6 hold | 维持 `hold_no_retry` 直至人工复审 |
| 新发现 6/6 fail | 自动进入 hold 候选 · **不**自动剔除出 registry |
| 恢复上市 / 代码变更 | 年度 recheck → 可回迁 `supported` |
| 明确退市（名称含退且无 endpoint） | `document_archive_only` 标签 |
| 主 harvest gate | hold 公司 **不计入** pass rate 分母 |

---

## 4. Hold 分类字段定义

### 4.1 hold_status

| 值 | 含义 |
|----|------|
| `none` | 非 hold |
| `hold_active` | 当前 hold 中 |
| `hold_recheck_pending` | 待定期复审 |
| `hold_resolved` | 已解除 hold（可回迁） |
| `permanent_excluded` | 永久排除（Option A） |
| `document_archive_only` | 仅文档归档（Option C） |

### 4.2 excluded_reason

| 值 | 含义 |
|----|------|
| `sample_quality_or_status_review` | 6/6 主源失败 · 样本质量/状态审查 |
| `legacy_code_incompatible` | BSE 83/87 代码不兼容 |
| `delisted_confirmed` | 确认退市 |
| `abnormal_listing_status` | 异常上市状态 |
| `duplicate_code` | 重复代码（如 839729） |
| `manual_hold` | 人工标注 |

### 4.3 future_support

| 值 | 含义 |
|----|------|
| `f10_harvest` | 未来可能支持 F10 harvest |
| `document_only` | 仅 Era B 文档层 |
| `none` | 无扩展计划 |
| `pending_probe` | 待 targeted probe 后决定 |

---

## 5. 与全市场扩展关系

| 扩展阶段 | hold 处理 |
|----------|-------------|
| registry 派生 | 26 + BSE legacy + abnormal 预填 hold 字段 |
| phased harvest | hold 公司 **跳过**（`hold_flag=true`） |
| snapshot | hold 公司 **不生成** JSON（或生成 empty stub — 不推荐） |
| QA | hold 单独统计，不拖累主 gate |

---

## 6. 红线确认

- 本轮 **不修改** 26 hold YAML · **不 retry** · **不 harvest**
- 不请求 CNINFO · 不写 verified

**下一步（规划）：** hold recheck 年度计划模板 · 与 company_registry 字段对齐
