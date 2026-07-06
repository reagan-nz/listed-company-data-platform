# CNINFO C 类 Executive Profile Mapper Summary

_生成时间：2026-07-06_

## 1. 目的

将 `getCompanyExecutives` 单行 `data.records[]` 映射为 `c_executive_profile` fixture。
**无网络请求**；**不写 verified**。

## 2. 输入

- 脚本：`lab/seed_cninfo_c_class_executive_profile_fixtures.py`
- Mapper：`lab/cninfo_c_class_mappers.py` → `map_company_executive_profile()`
- 样本：内置 **6** 条 executive row（600000×2 · 300001×2 · 688001×2）

## 3. 字段映射

| raw | schema |
|-----|--------|
| F002V | person_name |
| F009V | position |
| F010V | gender_candidate |
| F012V | birth_year_candidate |
| F017V | education_candidate |
| F005N / F012N / SEQID / F001V | raw_record_json only |

## 4. 结果

| 指标 | 数值 |
|------|------|
| samples | **6** |
| mapped | **6** |
| fixtures written | **6** |

## 5. 逐条映射

- `600000` 张为忠: **mapped** (raw_fields=9, mapped=3)
- `600000` 谢伟: **mapped** (raw_fields=9, mapped=3)
- `300001` 于德翔: **mapped** (raw_fields=9, mapped=3)
- `300001` 康晓兵: **mapped** (raw_fields=9, mapped=3)
- `688001` 陈文源: **mapped** (raw_fields=9, mapped=2)
- `688001` 钱晓斌: **mapped** (raw_fields=9, mapped=2)

## 6. 质量边界

- Mapper draft；F005N/F012N 单位 candidate-level。
- `source_status=testing`；**无 verified**。
- 不入库；不保存完整 live response body。

## 附录

详见 [cninfo_c_class_executive_profile_mapper_report.csv](cninfo_c_class_executive_profile_mapper_report.csv)。
