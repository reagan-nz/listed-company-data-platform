# CNINFO C 类 Era D — Fuller-Market Request Budget

_生成时间：2026-07-10 · offline planning only · CNINFO = 0_

> **NOT APPROVED live** · **approved_for_live = false**

---

## 1. Scope

| 项 | 值 |
|----|-----|
| next slice | **200 new**（CE1E001–CE1E200） |
| mode | **fresh harvest**（10 normalized sources / company） |
| reference baseline | 863 full harvest 经验 · ~10 HTTP cases/company |
| isolated root | `outputs/harvest/cninfo_c_class/fuller_market_slice1_200/`（规划） |

---

## 2. Estimated CNINFO Requests（Slice 1 · 200 companies）

| 源 | 估算 req/公司 | 200 公司合计 |
|----|---------------|--------------|
| cninfo_company_profile | 1 | 200 |
| cninfo_executive_profile | 1 | 200 |
| cninfo_share_capital_profile | 1 | 200 |
| cninfo_dividend_financing_profile | 1 | 200 |
| cninfo_top_shareholders_profile | 1 | 200 |
| cninfo_top_float_shareholders_profile | 1 | 200 |
| + 4 其他 normalized 源 | 4 | 800 |
| **小计（点估计）** | **10** | **~2000** |
| 重试/empty_but_valid 缓冲（×1.2） | — | **~2400** |
| **硬上限 cap（规划）** | — | **≤2800** |

**对比：** 863 全量粗估 ~8600 req；slice1 约为其 **23%** · 可分 2 session × 100。

---

## 3. Daily / Session Caps（Future Live · Planning）

| 层级 | 建议值 | 说明 |
|------|--------|------|
| 单次 session companies | **≤100** | 半批 · 便于 resume |
| 单日 companies 合计 | **≤150** | 跨 session 累计 |
| 单日 CNINFO 请求 | **≤1500** | ≈ cap 2800 的 54% |
| inter-request sleep | **≥1.0s** | 与历史 C harvest 一致 |
| inter-session gap | **≥4h** 或次日 | 降低 network_error 聚集 |

---

## 4. Resume / Cleanup / Protected Roots

| 项 | 政策 |
|----|------|
| `--resume` | 跳过 `company_harvest_status.csv` complete 行（slice 隔离 CSV） |
| cleanup | `cninfo_c_class_erad_cleanup_guard.py` · **禁止**删生产 863 根 |
| protected roots | [cninfo_c_class_erad_protected_output_roots.csv](cninfo_c_class_erad_protected_output_roots.csv) · slice1 写 **仅** 新子树 |
| failure isolation | 单公司失败不阻塞批 · unresolved ledger |
| rollback | 删除 slice 子树 · **不触碰** 863 primary |

---

## 5. Snapshot（Future · Separate Approval）

| 项 | 政策 |
|----|------|
| 863 full rebuild | **Option A HOLD** · `approved_for_snapshot_rebuild=false` |
| slice1 snapshot | 未来 **增量** build · 新 output root · 须另批 |
| 粗估 JSON | 200 × ~50KB ≈ **10MB**（远低于 863 ~45MB） |

---

## 6. Approval Status

```
approval_status = NOT_APPROVED
approved_for_live = false
approved_for_snapshot_rebuild = false
```

**本文件 CNINFO 实际调用：0**
