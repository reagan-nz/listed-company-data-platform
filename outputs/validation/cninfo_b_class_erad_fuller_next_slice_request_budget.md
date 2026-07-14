# CNINFO B 类 Era D Fuller Next-Slice — Request Budget

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

---

## 1. Scope

| 项 | 值 |
|----|-----|
| next slice | **+300 new**（BD2E501–BD2E800） |
| mode | **fresh_metadata only**（不重跑 BD2E001–500） |
| reference baseline | slice1 live：**600 CNINFO / 300 cases** ≈ **2.0 req/case** |
| scale-200 baseline | **397 CNINFO / 200 cases** ≈ **1.99 req/case** |

**NOT APPROVED live** · **CNINFO = 0**（本任务）

---

## 2. Estimated CNINFO Requests（Slice2 · 300 cases）

| Endpoint | 估算 | 说明 |
|----------|------|------|
| EP001 | **300** | 每 case 1× 公告检索主入口 |
| EP004 | **~75** | periodic_report 轨（~50% × 150 cases） |
| EP005 | **~75** | general_announcement 轨（~50% × 150 cases） |
| EP002 | **~10** | 金融子集 orgId 辅助（draft 待 runner 计数） |
| **合计（点估计）** | **~460** | 保守执行预算 |
| **合计（中位估计）** | **~600** | 与 slice1 实际一致 |
| **合计（上限 cap）** | **≤720** | dry-run 硬上限（300 × 2.4） |

---

## 3. Daily / Session Caps（Future Live · Planning）

| 层级 | 建议值 | 说明 |
|------|--------|------|
| 单次 session cases | **≤150** | 半批执行 · 便于中断恢复 |
| 单日 cases 合计 | **≤200** | 跨 session 累计 |
| 单日 CNINFO 请求 | **≤400** | 约为 slice2 上限 ~55% |
| inter-request sleep | **≥1.0s** | 与 slice1 一致 |
| inter-session gap | **≥4h** 或次日 | 降低 network_error 聚集 |

**推荐执行节奏（slice2 300）：**

| Session | Cases | Est. CNINFO | 日 |
|---------|-------|-------------|-----|
| S1 | BD2E501–650（150） | ~300 | D1 |
| S2 | BD2E651–800（150） | ~300 | D1 或 D2 |
| Buffer | — | — | 失败 case isolated retry 另计 |

**+200 备选（BD2E501–700）：** est. **~400** CNINFO · cap **≤480**

---

## 4. Throttle Notes

- 遇 `network_error` / timeout：**不 burst 重试** · 记入 ledger · session 内最多 1 次同 case 重试
- 金融 EP002 失败：降级 EP001-only · 记 caveat · 不阻塞 batch
- HTTP 429 / 5xx：session 级 **≥60s** 退避 · 超 3 次则暂停当日

---

## 5. Parallelism vs A/C/D Live

| 并行场景 | 风险 | 规划建议 |
|----------|------|----------|
| B fuller slice2 + A next-scale live | CNINFO 竞争 | **错开高峰** · 日合计 cap **≤500** CNINFO |
| B fuller slice2 + C fuller harvest | 不同域但同源 API | 日合计 cap **≤600** CNINFO |
| B fuller slice2 + D first-slice live | 同上 | 文档化 risk · 优先半批完成 |

**本规划不执行任何 live。**

---

## 6. Gate Reference

```text
b_class_erad_fuller_next_slice_planning_gate = READY_FOR_APPROVAL
```

**NOT verified** · **NOT production_ready** · **CNINFO = 0**（本任务）
