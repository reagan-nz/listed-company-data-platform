# A-FM-06 — basic_profile 覆盖扩展（offline）

_track A · CNINFO = 0 · 不 mutate C harvest / S1–S6 live_

## Metrics

| 项 | 值 |
|----|-----|
| canon profiles | **863** |
| latent-only added | **863** |
| union (overlay) | **1726** |
| overlay symlinks | **1726** |
| union with listing_date | **1720** |
| CNINFO calls | **0** |
| overlay_dir | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06` |
| matrix_csv | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv` |

## Prefix (union top 12)

```text
300	308
600	280
002	260
688	241
603	176
000	159
301	155
601	66
605	35
001	32
003	13
302	1
```

## Prefix (latent-only top 12)

```text
300	165
600	165
002	131
688	116
000	94
603	68
301	67
601	25
605	18
001	7
003	6
302	1
```

## Notes

- overlay 仅为 A 轨 symlink 视图；C-class harvest 根未改写。
- 扩大分母后，listing-aware 下一片应配合 prefix_concentration 门禁，
  避免再现 S6 首轮 mono-301 批处理 network_timeout 窗。
- S6 首轮 18×timeout 经独立 retry 可恢复，**不**作为永久点名黑名单。
