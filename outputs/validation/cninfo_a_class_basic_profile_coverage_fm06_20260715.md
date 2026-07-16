# A-FM-06 — basic_profile 覆盖扩展（offline）

_track A · CNINFO = 0 · 不 mutate C harvest / S1–S6 live_

## Metrics

| 项 | 值 |
|----|-----|
| canon profiles | **863** |
| latent-only added | **1350** |
| union (overlay) | **2213** |
| overlay symlinks | **2213** |
| union with listing_date | **2207** |
| CNINFO calls | **0** |
| overlay_dir | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_basic_profile_coverage_overlay_fm06` |
| matrix_csv | `/Users/zhao/Desktop/97/实操/数据收集测试/listed_company_data_collector/outputs/validation/cninfo_a_class_basic_profile_coverage_matrix_fm06_20260715.csv` |

## Prefix (union top 12)

```text
300	395
002	351
600	345
688	296
603	228
000	200
301	197
601	88
605	51
001	44
003	17
302	1
```

## Prefix (latent-only top 12)

```text
300	252
600	230
002	222
688	171
000	135
603	120
301	109
601	47
605	34
001	19
003	10
302	1
```

## Notes

- overlay 仅为 A 轨 symlink 视图；C-class harvest 根未改写。
- 扩大分母后，listing-aware 下一片应配合 prefix_concentration 门禁，
  避免再现 S6 首轮 mono-301 批处理 network_timeout 窗。
- S6 首轮 18×timeout 经独立 retry 可恢复，**不**作为永久点名黑名单。
