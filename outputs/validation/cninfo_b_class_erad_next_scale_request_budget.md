# CNINFO B 类 Era D Next-Scale — Request Budget

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Scope

| 项 | 值 |
|----|-----|
| next slice | **300 new**（BD2E201–BD2E500） |
| mode | **fresh_metadata only**（不重跑 scale-200 retained） |
| reference baseline | scale-200 live：**397 CNINFO / 200 cases** ≈ **1.99 req/case** |

---

## 2. Estimated CNINFO Requests（Slice 1 · 300 cases）

| Endpoint | 估算 | 说明 |
|----------|------|------|
| EP001 | **300** | 每 case 1× 公告检索主入口 |
| EP004 | **~75** | periodic_report 轨（~50% × 150 cases） |
| EP005 | **~75** | general_announcement 轨（~50% × 150 cases） |
| EP002 | **~10** | 金融子集 orgId 辅助（draft **5** 家 × ~2） |
| **合计（点估计）** | **~460** | 保守执行预算 |
| **合计（上限 cap）** | **≤720** | dry-run 硬上限（300 × 2.4） |

**对比 scale-200：** 200 cases cap ≤480 · 实际 397 → slice1 300 按同比例 ≈ **595** 中位估计；规划取 **460–600** 保守带。

---

## 3. Daily / Session Caps（Future Live · Planning）

| 层级 | 建议值 | 说明 |
|------|--------|------|
| 单次 session cases | **≤150** | 半批执行 · 便于中断恢复 |
| 单日 cases 合计 | **≤200** | 跨 session 累计 |
| 单日 CNINFO 请求 | **≤400** | 约为 slice1 上限 60% |
| inter-request sleep | **≥1.0s** | 与 scale-200 一致 |
| inter-session gap | **≥4h** 或次日 | 降低 network_error 聚集风险 |

**推荐执行节奏（slice1 300）：**

| Session | Cases | Est. CNINFO | 日 |
|---------|-------|-------------|-----|
| S1 | BD2E201–350（150） | ~230 | D1 |
| S2 | BD2E351–500（150） | ~230 | D1 或 D2 |
| Buffer | — | — | 失败 case isolated retry 另计 |

---

## 4. Throttle Notes

- 遇 `network_error` / timeout：**不 burst 重试** · 记入 ledger · session 内最多 1 次同 case 重试
- 金融 EP002 失败：降级为 EP001-only path · 记 caveat · 不阻塞 batch
- HTTP 429 / 5xx：session 级 **≥60s** 退避 · 超 3 次则暂停当日

---

## 5. Parallelism vs A/D Live

| 并行场景 | 风险 | 规划建议 |
|----------|------|----------|
| B next-scale + A isolated retry live | CNINFO 竞争 · network_error 上升 | **可 co-run** 但 **错开高峰** · 合计日 cap **≤500** CNINFO |
| B next-scale + D first-slice live | 同上 | 文档化 risk · 优先 **B 半批完成后再 D** 或反之 |
| B next-scale + C harvest resume | 不同 endpoint 域 | 风险较低 · 仍建议日合计 cap |

**本规划不执行任何 live** · 并行策略仅供未来批准时参照。

---

## 6. Gate Reference

```text
b_class_erad_next_scale_planning_gate = READY_FOR_APPROVAL
```

**NOT verified** · **NOT production_ready** · **CNINFO = 0**（本任务）
