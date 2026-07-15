# CNINFO D 类 abnormal_trading — D-FM-04 Offline Edge Fixtures

_生成时间：2026-07-15 · D-FM-04_

> **性质：** Tier-1 synthetic edge fixtures · **CNINFO = 0** · **无 live** · **不是 verified**

## Scope

在既有 DAT001–DAT005 first-slice 根下增补 **2** 个 edge fixture，覆盖此前 VR 缺口：

| 文件 | case | VR 焦点 |
|------|------|---------|
| `DAT003_market_list_filtered_empty.json` | DAT003 | VR-009/010 有 marketList 但 secCode 无匹配 → empty_but_valid |
| `DAT004_multi_type_found.json` | DAT004 | VR-011 同日多 type 骨架；VR-021/024 totals raw_only + detail 不扁平 |

**未改：** universe lock · runner `CASE_FIXTURES` map · live path · S4 dry-run artifacts

## Gates（不变）

```text
d_class_abnormal_trading_fixture_vr_gate = PASS_OFFLINE
d_class_abnormal_trading_first_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_abnormal_trading_first_slice_live_gate = NOT_APPROVED
```

## Explicit Non-Claims

- 不 claim verified / production_ready / bare PASS
- 不 reopen DLC006R / 301259 / 688671
- 不触碰 A/B/C 产物根
- 不 commit / push（executor）

```text
task_id = D-FM-04
phase = abnormal_trading_tier1_fixture_edge_extension
ready_for_commit = true
cninfo_calls = 0
```
