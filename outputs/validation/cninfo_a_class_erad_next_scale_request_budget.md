# CNINFO A 类 Era D Next-Scale — Request Budget

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Scope

| 项 | 值 |
|----|-----|
| next slice | **300 new**（AD2E201–AD2E500） |
| mode | **fresh_metadata only**（不重跑 scale-200 accepted / unresolved） |
| reference baseline | scale-200 live：**423 CNINFO / 200 cases** ≈ **2.12 req/case** |
| matching_logic | **v2** |

---

## 2. Estimated CNINFO Requests（Slice 1 · 300 cases）

| 组件 | 估算 | 说明 |
|------|------|------|
| orgId / search primary | **300** | 每 case ≥1× 检索入口 |
| v2 rematch / expanded window | **~330** | 部分 case 额外 1× query（参考 scale-200 new_erad 比例） |
| **合计（点估计）** | **~630** | 保守执行预算 |
| **合计（上限 cap）** | **≤720** | dry-run 硬上限（300 × 2.4） |

**对比 scale-200：** 200 cases cap ≤480 · 实际 423 → slice1 300 按同比例中位 ≈ **634**；规划取 **630** 点估计 · **≤720** cap。

---

## 3. Daily / Session Caps（Future Live · Planning）

| 层级 | 建议值 | 说明 |
|------|--------|------|
| 单次 session cases | **≤150** | 半批执行 · 便于中断恢复 |
| 单日 cases 合计 | **≤200** | 跨 session 累计 |
| 单日 CNINFO 请求 | **≤400** | 约为 slice1 上限 ~55% |
| inter-request sleep | **≥1.0s** | 与 scale-200 一致 |
| inter-session gap | **≥4h** 或次日 | 降低 network_or_empty_response 聚集 |

**推荐执行节奏（slice1 300）：**

| Session | Cases | Est. CNINFO | 日 |
|---------|-------|-------------|-----|
| S1 | AD2E201–350（150） | ~315 | D1 |
| S2 | AD2E351–500（150） | ~315 | D1 或 D2 |
| Buffer | — | — | 失败 case isolated retry 另计 · **不 rerun 8 scale-200 unresolved** |

---

## 4. Throttle Notes

- 遇 `network_or_empty_response`：**不 burst 重试** · 记入 ledger · session 内最多 1 次同 case 重试
- `matching_logic_miss`：记 caveat · optional offline review · 不阻塞 batch
- HTTP 429 / 5xx：session 级 **≥60s** 退避 · 超 3 次则暂停当日

---

## 5. Parallelism vs B / C / D Live

| 并行场景 | 风险 | 规划建议 |
|----------|------|----------|
| A slice1 + B slice1 live | CNINFO 竞争 · network 上升 | **可 co-run** · 错开高峰 · 合计日 cap **≤500** CNINFO |
| A slice1 + C harvest resume | 不同 endpoint 域 | 风险较低 · 仍建议日合计 cap |
| A slice1 + D first-slice live | 同上 | 文档化 risk · 优先半批完成再启另一轨 |

**本规划不执行任何 live** · **NOT APPROVED live**

---

## 6. Gate Reference

```text
a_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
```

**NOT verified** · **NOT production_ready** · **CNINFO = 0**（本任务）
