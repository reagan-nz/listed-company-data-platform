"""
CNINFO F10 / 公司资料小样本验证（Issue #84）。

Inputs:
- outputs/validation/cninfo_p0_sample_companies.csv  (40 样本公司，Issue #81)

Outputs:
- outputs/validation/cninfo_f10_company_profile_validation.csv
- outputs/validation/cninfo_f10_company_profile_validation_summary.md

Scope & Boundaries:
- 小样本验证，不是全量爬虫；不做数据库接入；不上传 MinIO。
- 优先 HTTP 公开接口；不使用 BrowserUser；若需要 Playwright 仅作为备注，不在本脚本执行。
- 不绕过登录/验证码/付费/权限；请求间 sleep 避免高频。
"""

from __future__ import annotations

import csv
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_CSV = os.path.join(BASE_DIR, "outputs", "validation", "cninfo_p0_sample_companies.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs", "validation")
OUT_CSV = os.path.join(OUT_DIR, "cninfo_f10_company_profile_validation.csv")
OUT_SUMMARY = os.path.join(OUT_DIR, "cninfo_f10_company_profile_validation_summary.md")

SLEEP_SECONDS = 0.5

CSV_FIELDS = [
    "company_code",
    "company_name",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "profile_url_rule",
    "cninfo_query_code",
    "stock_short_name",
    "exchange",
    "board",
    "industry",
    "listing_status",
    "is_st",
    "company_profile",
    "main_business_summary",
    "registered_address",
    "office_address",
    "website",
    "contact_phone",
    "contact_email",
    "board_secretary",
    "source_url",
    "crawl_time",
    "validation_status",
    "failure_reason",
    "access_method",
    "http_status_code",
    "notes",
]

FAILURE_REASONS = {
    "success",
    "partial_missing_profile_fields",
    "missing_company_code",
    "missing_company_name",
    "company_mapping_failed",
    "f10_page_not_found",
    "company_profile_missing",
    "industry_missing",
    "board_missing",
    "listing_status_missing",
    "contact_info_missing",
    "board_secretary_missing",
    "field_semantics_unclear",
    "page_structure_changed",
    "js_render_required",
    "rate_limited",
    "captcha_or_login_required",
    "network_timeout",
    "http_error",
    "unknown_error",
}

BSE_OLD_PREFIX = "430"
BSE_NEW_PREFIX = "920"

# 北交所 430→920 + orgId 人工映射（小样本，非通用规则）
BSE_MANUAL_MAPPING: Dict[str, Tuple[str, str, str]] = {
    "430017": ("920017", "9900003482", "星昊医药"),
    "430047": ("920047", "9900006121", "诺思兰德"),
    "430090": ("920090", "9900020567", "同辉信息"),
    "430139": ("920139", "9900024205", "华岭股份"),
    "430198": ("920198", "9900024889", "微创光电"),
    "430300": ("920300", "9900023934", "辰光医疗"),
}

# 科创板 688 orgId 人工映射（小样本，非通用规则；gshk0000+后三位已被推翻）
STAR_MANUAL_MAPPING: Dict[str, Tuple[str, str, str]] = {
    "688001": ("688001", "9900038969", "华兴源创"),
    "688002": ("688002", "9900038939", "睿创微纳"),
    "688003": ("688003", "gfbj0833231", "天准科技"),
    "688004": ("688004", "gfbj0871038", "博汇科技"),
    "688005": ("688005", "9900038937", "容百科技"),
    "688006": ("688006", "9900037551", "杭可科技"),
    "688007": ("688007", "9900038970", "光峰科技"),
}

CNINFO_SEARCH_URL = "https://www.cninfo.com.cn/new/information/topSearch/detailOfQuery"
CNINFO_PROFILE_BASE = "https://www.cninfo.com.cn/new/disclosure/stock"
ENTRY_MAPPING_CSV = os.path.join(OUT_DIR, "cninfo_f10_entry_mapping.csv")

ENTRY_MAPPING_FIELDS = [
    "company_code",
    "company_name",
    "exchange",
    "board",
    "cninfo_stock_code",
    "cninfo_org_id",
    "cninfo_profile_url",
    "profile_url_rule",
    "mapping_status",
    "notes",
]


def ensure_dirs() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_samples() -> List[Dict]:
    rows: List[Dict] = []
    with open(SAMPLE_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def map_bse_code_if_needed(code: str) -> str | None:
    if code.startswith(BSE_OLD_PREFIX) and len(code) >= 6:
        return BSE_NEW_PREFIX + code[len(BSE_OLD_PREFIX) :]
    return None


def build_cninfo_profile_url(company_code: str, company_name: str | None = None) -> Tuple[str, str, str, str]:
    cc = company_code.strip()

    if cc in BSE_MANUAL_MAPPING:
        stock_code, org_id, _ = BSE_MANUAL_MAPPING[cc]
        rule = "manual_bse_430_to_920_orgid_mapping"
        url = f"{CNINFO_PROFILE_BASE}?stockCode={stock_code}&orgId={org_id}#companyProfile"
        return stock_code, org_id, url, rule

    if cc in STAR_MANUAL_MAPPING:
        stock_code, org_id, _ = STAR_MANUAL_MAPPING[cc]
        rule = "manual_star_orgid_mapping"
        url = f"{CNINFO_PROFILE_BASE}?stockCode={stock_code}&orgId={org_id}#companyProfile"
        return stock_code, org_id, url, rule

    # 600 / 300
    if cc.startswith("600") or cc.startswith("300"):
        stock_code = cc
        org_id = "gssh0" + cc
        rule = "manual_rule_600_300_gssh0"
        url = f"{CNINFO_PROFILE_BASE}?stockCode={stock_code}&orgId={org_id}#companyProfile"
        return stock_code, org_id, url, rule

    # 688 科创板：不在人工映射表中则标记缺 orgId（不再使用 gshk0000+后三位）
    if cc.startswith("688"):
        stock_code = cc
        org_id = "unknown"
        rule = "star_orgid_required"
        url = ""
        return stock_code, org_id, url, rule

    # 其他 430 暂不泛化
    if cc.startswith("430"):
        stock_code = cc
        org_id = "unknown"
        rule = "bse_orgid_required"
        url = ""
        return stock_code, org_id, url, rule

    # Default fallback
    return cc, "unknown", "", "needs_orgid_mapping"


def build_entry_mapping_row(sample: Dict) -> Dict:
    company_code = sample.get("company_code", "").strip()
    company_name = sample.get("company_name", "").strip()
    exchange = sample.get("exchange", "").strip()
    board = sample.get("board", "").strip()

    cninfo_stock_code, cninfo_org_id, cninfo_profile_url, profile_url_rule = build_cninfo_profile_url(
        company_code, company_name
    )

    if cninfo_profile_url:
        mapping_status = "mapped"
        notes = ""
        if profile_url_rule == "manual_bse_430_to_920_orgid_mapping":
            notes = "manual BSE mapping from company name search"
        elif profile_url_rule == "manual_star_orgid_mapping":
            notes = "manual STAR mapping from company search"
    elif profile_url_rule in ("bse_orgid_required", "star_orgid_required", "needs_orgid_mapping"):
        mapping_status = "needs_mapping"
        notes = "orgId or mapping needed"
    else:
        mapping_status = "needs_mapping"
        notes = "orgId or mapping needed"

    return {
        "company_code": company_code,
        "company_name": company_name,
        "exchange": exchange,
        "board": board,
        "cninfo_stock_code": cninfo_stock_code,
        "cninfo_org_id": cninfo_org_id,
        "cninfo_profile_url": cninfo_profile_url,
        "profile_url_rule": profile_url_rule,
        "mapping_status": mapping_status,
        "notes": notes,
    }


def write_entry_mapping_csv(samples: List[Dict]) -> None:
    with open(ENTRY_MAPPING_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ENTRY_MAPPING_FIELDS)
        writer.writeheader()
        for sample in samples:
            writer.writerow(build_entry_mapping_row(sample))


def regenerate_entry_mapping() -> None:
    ensure_dirs()
    samples = load_samples()
    write_entry_mapping_csv(samples)
    print(f"Wrote {len(samples)} rows -> {ENTRY_MAPPING_CSV}")


def fetch_profile(query_code: str) -> Tuple[Dict, int | None, str | None]:
    try:
        resp = requests.post(CNINFO_SEARCH_URL, data={"keyWord": query_code}, timeout=10)
        status = resp.status_code
        if status != 200:
            return {}, status, "http_error"
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return {}, status, "unknown_error"
        if not data:
            return {}, status, "f10_page_not_found"
        # data is expected as list; take first
        rec = data[0] if isinstance(data, list) else data
        return rec if isinstance(rec, dict) else {}, status, None
    except requests.exceptions.Timeout:
        return {}, None, "network_timeout"
    except Exception:
        return {}, None, "unknown_error"


def pick_field(rec: Dict, keys: List[str]) -> str:
    for k in keys:
        if rec.get(k):
            return str(rec[k]).strip()
    return ""


def process_company(sample: Dict) -> Dict:
    company_code = sample.get("company_code", "").strip()
    company_name = sample.get("company_name", "").strip()
    exchange = sample.get("exchange", "").strip()
    board = sample.get("board", "").strip()
    is_st = sample.get("is_st", "").strip()
    cninfo_query_code = company_code
    access_method = "HTTP"

    if not company_code:
        return base_row(
            company_code,
            company_name,
            *build_cninfo_profile_url(company_code, company_name),
            cninfo_query_code,
            exchange,
            board,
            is_st,
            "missing_company_code",
            "failed",
            "",
            access_method,
            notes="company_code missing",
        )
    if not company_name:
        return base_row(
            company_code,
            company_name,
            *build_cninfo_profile_url(company_code, company_name),
            cninfo_query_code,
            exchange,
            board,
            is_st,
            "missing_company_name",
            "failed",
            "",
            access_method,
            notes="company_name missing",
        )

    # Entry mapping (no network)
    cninfo_stock_code, cninfo_org_id, cninfo_profile_url, profile_url_rule = build_cninfo_profile_url(company_code, company_name)

    rec, status, failure = fetch_profile(cninfo_query_code)
    retry_used = False
    if (failure in ("f10_page_not_found",) or not rec) and company_code.startswith(BSE_OLD_PREFIX):
        mapped = map_bse_code_if_needed(company_code)
        if mapped:
            cninfo_query_code = mapped
            rec, status, failure = fetch_profile(mapped)
            retry_used = True

    if failure:
        return base_row(
            company_code,
            company_name,
            cninfo_stock_code,
            cninfo_org_id,
            cninfo_profile_url,
            profile_url_rule,
            cninfo_query_code,
            exchange,
            board,
            is_st,
            failure,
            "failed",
            status,
            access_method,
            notes="retry with mapped code" if retry_used else "",
        )

    stock_short_name = pick_field(rec, ["zwjc", "shortname", "stock_short_name", "comShortName", "companyShortName"]) or company_name
    industry = pick_field(rec, ["sshy", "industry", "industryName"])
    listing_status = pick_field(rec, ["ssecode", "plate", "list_status"])
    company_profile = pick_field(rec, ["gsjj", "brief", "compIntro"])
    main_business_summary = pick_field(rec, ["jyfw", "mainBusiness", "main_business"])
    registered_address = pick_field(rec, ["zcdz", "reg_address", "registerAddress"])
    office_address = pick_field(rec, ["bgdz", "office_address"])
    website = pick_field(rec, ["gswz", "website"])
    contact_phone = pick_field(rec, ["lxrdh", "telephone"])
    contact_email = pick_field(rec, ["email"])
    board_secretary = pick_field(rec, ["dszz", "boardSecretary"])
    source_url = f"{CNINFO_SEARCH_URL}?keyWord={cninfo_query_code}"

    missing_core = []
    if not stock_short_name:
        missing_core.append("stock_short_name")
    if not exchange:
        missing_core.append("exchange")
    if not board:
        missing_core.append("board")

    missing_profile = []
    for f, val in [
        ("industry", industry),
        ("listing_status", listing_status),
        ("company_profile", company_profile),
        ("main_business_summary", main_business_summary),
        ("registered_address", registered_address),
        ("office_address", office_address),
        ("website", website),
        ("contact_phone", contact_phone),
        ("contact_email", contact_email),
        ("board_secretary", board_secretary),
    ]:
        if not val:
            missing_profile.append(f)

    if missing_core:
        failure_reason = "partial_missing_profile_fields"
        status_label = "partial"
    elif missing_profile:
        failure_reason = "partial_missing_profile_fields"
        status_label = "partial"
    else:
        failure_reason = "success"
        status_label = "success"

    return {
        "company_code": company_code,
        "company_name": company_name,
        "cninfo_stock_code": cninfo_stock_code,
        "cninfo_org_id": cninfo_org_id,
        "cninfo_profile_url": cninfo_profile_url,
        "profile_url_rule": profile_url_rule,
        "cninfo_query_code": cninfo_query_code,
        "stock_short_name": stock_short_name or "",
        "exchange": exchange or "",
        "board": board or "",
        "industry": industry or "unknown",
        "listing_status": listing_status or "unknown",
        "is_st": is_st or "",
        "company_profile": company_profile or "",
        "main_business_summary": main_business_summary or "",
        "registered_address": registered_address or "",
        "office_address": office_address or "",
        "website": website or "",
        "contact_phone": contact_phone or "",
        "contact_email": contact_email or "",
        "board_secretary": board_secretary or "",
        "source_url": source_url,
        "crawl_time": now_iso(),
        "validation_status": status_label,
        "failure_reason": failure_reason,
        "access_method": access_method,
        "http_status_code": status or "",
        "notes": "retried with mapped BSE code" if retry_used else "",
    }


def base_row(
    company_code: str,
    company_name: str,
    cninfo_stock_code: str,
    cninfo_org_id: str,
    cninfo_profile_url: str,
    profile_url_rule: str,
    cninfo_query_code: str,
    exchange: str,
    board: str,
    is_st: str,
    failure_reason: str,
    status_label: str,
    http_status: int | None,
    access_method: str,
    notes: str = "",
) -> Dict:
    return {
        "company_code": company_code,
        "company_name": company_name,
        "cninfo_stock_code": cninfo_stock_code,
        "cninfo_org_id": cninfo_org_id,
        "cninfo_profile_url": cninfo_profile_url,
        "profile_url_rule": profile_url_rule,
        "cninfo_query_code": cninfo_query_code,
        "stock_short_name": "",
        "exchange": exchange,
        "board": board,
        "industry": "unknown",
        "listing_status": "unknown",
        "is_st": is_st,
        "company_profile": "",
        "main_business_summary": "",
        "registered_address": "",
        "office_address": "",
        "website": "",
        "contact_phone": "",
        "contact_email": "",
        "board_secretary": "",
        "source_url": f"{CNINFO_SEARCH_URL}?keyWord={cninfo_query_code}",
        "crawl_time": now_iso(),
        "validation_status": status_label,
        "failure_reason": failure_reason if failure_reason in FAILURE_REASONS else "unknown_error",
        "access_method": access_method,
        "http_status_code": http_status or "",
        "notes": notes,
    }


def write_csv(rows: List[Dict]) -> None:
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def write_summary(rows: List[Dict], failure_counter: Counter, mapped_success: int) -> None:
    total = len(rows)
    success = sum(1 for r in rows if r["validation_status"] == "success")
    partial = sum(1 for r in rows if r["validation_status"] == "partial")
    failed = sum(1 for r in rows if r["validation_status"] == "failed")

    def count_field(name: str) -> int:
        return sum(1 for r in rows if r.get(name) not in ("", None, "unknown"))

    with open(OUT_SUMMARY, "w", encoding="utf-8") as fh:
        fh.write("# CNINFO 个股 F10 / 公司资料小样本验证（Issue #84）\n\n")
        fh.write("## 数据来源\n")
        fh.write(f"- 输入样本：{os.path.relpath(SAMPLE_CSV, BASE_DIR)}\n")
        fh.write("- CNINFO 公开接口：/new/information/topSearch/detailOfQuery（HTTP POST）\n\n")

        fh.write("## 样本概况\n")
        fh.write(f"- 样本公司数：{total}\n")
        fh.write(f"- success：{success}\n")
        fh.write(f"- partial：{partial}\n")
        fh.write(f"- failed：{failed}\n\n")

        fh.write("## 字段可得性（按行计数）\n")
        fh.write(f"- stock_short_name：{count_field('stock_short_name')}/{total}\n")
        fh.write(f"- exchange：{count_field('exchange')}/{total}（注意：来自样本输入/构造，不代表接口返回）\n")
        fh.write(f"- board：{count_field('board')}/{total}（注意：来自样本输入/构造，不代表接口返回）\n")
        fh.write(f"- industry：{count_field('industry')}/{total}\n")
        fh.write(f"- listing_status：{count_field('listing_status')}/{total}\n")
        fh.write(f"- is_st：{count_field('is_st')}/{total}（注意：来自样本输入/构造，不代表接口返回）\n")
        fh.write(f"- company_profile：{count_field('company_profile')}/{total}\n")
        fh.write(f"- main_business_summary：{count_field('main_business_summary')}/{total}\n")
        fh.write(f"- registered_address：{count_field('registered_address')}/{total}\n")
        fh.write(f"- office_address：{count_field('office_address')}/{total}\n")
        fh.write(f"- website：{count_field('website')}/{total}\n")
        fh.write(f"- contact_phone：{count_field('contact_phone')}/{total}\n")
        fh.write(f"- contact_email：{count_field('contact_email')}/{total}\n")
        fh.write(f"- board_secretary：{count_field('board_secretary')}/{total}\n")
        fh.write(f"- source_url：{count_field('source_url')}/{total}\n\n")

        fh.write("## 字段分层总结\n")
        fh.write("- company：company_code / company_name / stock_short_name / exchange / board / listing_status\n")
        fh.write("- company_profile 候选：industry / company_profile / main_business_summary\n")
        fh.write("- 联系方式：registered_address / office_address / website / contact_phone / contact_email（需后续语义与时效性复核）\n")
        fh.write("- 治理辅助：board_secretary（可选，需语义与时效性确认）\n")
        fh.write("- 证据：source_url / crawl_time\n\n")

        fh.write("## 失败原因汇总\n")
        for reason, cnt in failure_counter.most_common():
            fh.write(f"- {reason}: {cnt}\n")
        if not failure_counter:
            fh.write("- 无失败记录\n")
        fh.write("\n")

        fh.write("## 北交所 / 代码映射观察\n")
        bse_mapped = sum(
            1 for r in rows if r.get("profile_url_rule") == "manual_bse_430_to_920_orgid_mapping"
        )
        fh.write(f"- 已人工补充 BSE 430→920/orgId 映射：{bse_mapped} 家（见 BSE_MANUAL_MAPPING，小样本专用）\n")
        fh.write(f"- 使用 430xxx -> 920xxx 映射成功的公司数：{mapped_success}\n")
        fh.write("- 430→920 stockCode 在 6 个北交所样本上成立；orgId 无简单公式，当前来自人工搜索。\n")
        fh.write("- 映射仅为小样本保守策略，不代表长期通用；如仍失败需人工复核。\n")
        fh.write("- 下一步：重新运行 profile page reachability；若页面可达，再纳入 Playwright 字段验证。\n\n")

        fh.write("## 科创板 / orgId 映射观察\n")
        star_mapped = sum(
            1 for r in rows if r.get("profile_url_rule") == "manual_star_orgid_mapping"
        )
        fh.write(f"- 已人工补充 STAR 688 orgId 映射：{star_mapped} 家（见 STAR_MANUAL_MAPPING，小样本专用）\n")
        fh.write("- 原规则 gshk0000+后三位已被 Playwright 小样本推翻，不再作为可靠构造方式。\n")
        fh.write("- 688 orgId 可能是 99000... 或 gfbj...，无统一公式；须人工搜索或后续接口解析。\n")
        fh.write("- 下一步：重新运行 reachability / static HTML / Playwright 验证。\n\n")

        fh.write("## recommended_status（小样本）\n")
        if success > 0:
            fh.write("- 建议：testing / partial（小样本可继续验证），不代表长期稳定可用。\n")
        else:
            fh.write("- 建议：candidate（需改进可达性/映射后再测）。\n")
        fh.write("\n")

        fh.write("## 合规与边界确认\n")
        fh.write("- 未绕过登录/验证码/付费/权限。\n")
        fh.write("- 未使用 BrowserUser；如需 Playwright 仅作为后续备用。\n")
        fh.write("- 未解析 PDF 正文，未做 OCR，未做字段抽取。\n")
        fh.write("- 未上传 MinIO，未做 PostgreSQL / MongoDB 接入。\n")
        fh.write("- 请求间加入 sleep，避免高频访问。\n")
        fh.write("- 结果可能受网络/VPN/映射影响，需人工环境确认后视情况重跑。\n")


def main() -> None:
    ensure_dirs()
    samples = load_samples()
    rows: List[Dict] = []
    failure_counter: Counter = Counter()
    mapped_success = 0

    for sample in samples:
        row = process_company(sample)
        if row["failure_reason"]:
            failure_counter[row["failure_reason"]] += 1
        if row["validation_status"] == "success" and row.get("cninfo_query_code") and row["cninfo_query_code"] != row["company_code"]:
            mapped_success += 1
        rows.append(row)
        time.sleep(SLEEP_SECONDS)

    write_csv(rows)
    write_summary(rows, failure_counter, mapped_success)
    print(f"Wrote {len(rows)} rows -> {OUT_CSV}")
    print(f"Summary -> {OUT_SUMMARY}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--entry-mapping-only":
        regenerate_entry_mapping()
    else:
        main()
