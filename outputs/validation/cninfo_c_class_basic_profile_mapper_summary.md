# CNINFO C 类 Basic Profile Mapper Summary

_生成时间：2026-07-06_

## 1. 目的

将 `getCompanyIntroduction` 的 basicInformation/listingInformation 映射为 `c_company_basic_profile` fixture。**无网络请求**；**不写 verified**。

## 2. 输入

- 脚本：`lab/seed_cninfo_c_class_basic_profile_fixtures.py`
- Mapper：`lab/cninfo_c_class_mappers.py`
- 样本：内置 **300001**、**688001** 简化 raw_record（2 条非空）

## 3. 结果

| 指标 | 数值 |
|------|------|
| samples | **2** |
| mapped | **2** |
| fixtures written | **2** |

**说明：** 600000 无保存的完整 raw body，本轮 fixture 仅用 2 家非空样本。

## 4. 逐条映射

- `300001` 特锐德: **mapped** (basic_fields=22, listing_fields=5, mapped=12)
- `688001` 华兴源创: **mapped** (basic_fields=17, listing_fields=4, mapped=12)

## 5. 质量边界

- Mapper draft；字段语义 candidate-level。
- `source_status=testing`；**无 verified**。
- 不入库；不保存完整 live response body。

## 附录

详见 [cninfo_c_class_basic_profile_mapper_report.csv](cninfo_c_class_basic_profile_mapper_report.csv)。
