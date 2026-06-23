# Full-Market 2024 Annual Report Extraction Plan

_状态：待执行（2026-06-23 规划）_

## 背景

项目已完成：
- **eval1000_v2** 同 cohort 重跑：1020 家 / 947 ok / 73 no_announcement / 0 error；非金融 proxy **10.33/11**
- **independent eval1000** 泛化验证：1000 家 / 918 ok / 82 no_announcement / 0 error（18 ChunkedEncodingError 经 VPN-off 重试恢复）；非金融 proxy **10.30/11**
- 金融子 schema 实现；金融 YAML 标签审计（16 家 tagged）

下一步：对 **全 A 股 universe** 跑 2024 年报基础字段抽取，形成可入库的全市场数据集。

## 目标

1. 抽取全部 A 股上市公司 2024 年报 11 项（工业）/ 金融子 schema 基础字段
2. 输出至独立目录 `outputs/generalization/full_market_2024/`，不覆盖 eval1000 / eval1000_v2 / independent
3. SQLite 导入 `run_name=full_market_2024`
4. 与 eval1000_v2、independent 对比 proxy 率，验证全市场泛化

---

## 架构概览

```
CNINFO API
    ↓  lab/make_full_market_yaml.py（新建）
lab/eval_companies_full_market_2024.yaml  (~5300 家)
    ↓  按 board 拆成 5 个 batch YAML
eval_generalize.py × 5（顺序执行，每 board 独立 subdir）
    ↓
outputs/generalization/full_market_2024/
    sse_main/  star/  szse_main/  chinext/  bse/
    eval_results.json（合并后）
    eval_summary.md
    full_market_2024_summary.md
    ↓  lab/db_import.py --run-name full_market_2024
outputs/db/listed_companies_v1.db
```

---

## 1. Universe 生成

### `sample_universe.py` 不支持全市场

当前脚本始终按 `TARGETS` 分层抽样，无 `--full-market` 参数。需要新建 **`lab/make_full_market_yaml.py`**（约 30 行），复用 `board_of` / `is_financial`：

```python
"""Write a YAML of ALL A-share companies (no sampling) for full-market eval."""
import sys, os, yaml
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lab.probe_cninfo import _session
from lab.sample_universe import board_of, is_financial

STOCK_LIST_URL = "http://www.cninfo.com.cn/new/data/szse_stock.json"

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "lab/eval_companies_full_market_2024.yaml"
    sess = _session(25)
    data = sess.get(STOCK_LIST_URL, timeout=25).json()
    universe = [x for x in data["stockList"] if x.get("category") == "A股"]
    companies = []
    for x in universe:
        code = str(x.get("code", ""))
        exch, board = board_of(code)
        if not board:
            continue
        companies.append({
            "short_name": x.get("zwjc", ""),
            "stock_code": code, "exchange": exch,
            "orgid": x.get("orgId", ""), "board": board,
            "financial": is_financial(x.get("zwjc", "")),
        })
    with open(out, "w", encoding="utf-8") as fh:
        yaml.safe_dump({"companies": companies}, fh, allow_unicode=True, sort_keys=False)
    from collections import Counter
    print(f"[full_market] wrote {len(companies)} companies -> {out}")
    print("[full_market] boards:", dict(Counter(c["board"] for c in companies)))
    print("[full_market] financial:", sum(1 for c in companies if c["financial"]))

if __name__ == "__main__":
    main()
```

**输出文件：** `lab/eval_companies_full_market_2024.yaml`（纳入 Git，可复现 universe 快照）

**预期：** ~5300 家，`financial: true` ~150–200 家

---

## 2. 输出目录与 batch 策略

### 为何按 board 分 subdir？

`eval_generalize.py` 仅在全部跑完后写入 `eval_results.json`。5300 家中途崩溃会丢失内存结果。每 board 独立 subdir 可保存 5 份独立 checkpoint。

| Board | 预估家数 | 预估耗时 |
|---|---:|---:|
| `sse_main` | ~1700 | ~6–8 h |
| `star` | ~560 | ~2–3 h |
| `szse_main` | ~1400 | ~5–7 h |
| `chinext` | ~1300 | ~5–6 h |
| `bse` | ~300 | ~1–2 h |
| **合计** | **~5300** | **~20–26 h** |

### 目录结构

```
outputs/generalization/full_market_2024/
  sse_main/              ← eval_results.json + 各公司子目录
  star/
  szse_main/
  chinext/
  bse/
  eval_results.json      ← 5 batch 合并后
  eval_summary.md
  full_market_2024_summary.md
  batch_sse_main.log
  batch_star.log
  ...
```

旧 run（eval1000 / eval1000_v2 / eval1000_independent_20260623）完全隔离，不会被覆盖。

---

## 3. 运行策略

- **顺序执行 5 个 batch**（不并行）— 避免 CNINFO 限流
- 使用 **`nohup`**，终端断开不影响进程
- **batch 内可 resume**：已有 `<code>.pdf` + `meta.json` 的公司跳过下载，仅重跑未完成部分
- **`--throttle 1.5`** 保持不变；全市场 run 不建议低于 1.0

---

## 4. 网络 / 缓存策略

| 策略 | 建议 |
|---|---|
| VPN | **关闭** — CNINFO 为国内站点；independent run 曾出现 18 次 ChunkedEncodingError |
| PDF 预拷贝 | **推荐** — 从 eval1000 / v2 / independent 预拷贝 ~2000 重叠 PDF+meta，节省 2–3 h 与 ~25 GB 下载 |
| parse cache | 可选 — 拷贝 `.cache/*.pages.json` 可再省 ~1 h parse，非必须 |
| 全新下载 | 仅 ~3300 家无重叠 PDF 需下载 |

---

## 5. `.gitignore` 新增项

运行前加入 [`.gitignore`](../.gitignore)：

```
# Full-market 2024
outputs/generalization/full_market_2024/sse_main/
outputs/generalization/full_market_2024/star/
outputs/generalization/full_market_2024/szse_main/
outputs/generalization/full_market_2024/chinext/
outputs/generalization/full_market_2024/bse/
outputs/generalization/full_market_2024/*.log
lab/batch_*_2024.yaml
```

已有规则已覆盖：`outputs/generalization/**/*.pdf`、`**/.cache/`、`**/eval_results.json`

### 运行后可 commit

- `lab/make_full_market_yaml.py`
- `lab/eval_companies_full_market_2024.yaml`
- `outputs/generalization/full_market_2024/eval_summary.md`
- `outputs/generalization/full_market_2024/full_market_2024_summary.md`
- `CURRENT_STATUS.md`、`CHANGELOG.md`

### 不可 commit

- 所有 `[0-9]*/` 公司子目录（PDF、profile、brief）
- `eval_results.json`（~40 MB）
- `batch_*.log` / `run.log`
- `outputs/db/*.db`
- `lab/batch_*_2024.yaml`（派生产物）

---

## 6. 逐步命令

### Step 0：Pre-run

```bash
cd listed_company_data_collector
git status --short     # 须 clean
df -h .                # 需要 ≥80 GiB 可用
```

### Step 1：生成全市场 YAML

```bash
.venv/bin/python lab/make_full_market_yaml.py lab/eval_companies_full_market_2024.yaml
```

验证：

```bash
.venv/bin/python - <<'PY'
import yaml
from collections import Counter
cs = yaml.safe_load(open("lab/eval_companies_full_market_2024.yaml"))["companies"]
print(f"total={len(cs)}")
print("boards:", dict(Counter(c["board"] for c in cs)))
print("financial:", sum(1 for c in cs if c["financial"]))
PY
```

### Step 2：拆成 5 个 board batch YAML

```bash
.venv/bin/python - <<'PY'
import yaml
cs = yaml.safe_load(open("lab/eval_companies_full_market_2024.yaml"))["companies"]
for board in ["sse_main", "star", "szse_main", "chinext", "bse"]:
    batch = [c for c in cs if c["board"] == board]
    out = f"lab/batch_{board}_2024.yaml"
    yaml.safe_dump({"companies": batch}, open(out, "w", encoding="utf-8"),
                   allow_unicode=True, sort_keys=False)
    print(f"  {board}: {len(batch)} -> {out}")
PY
```

### Step 3：（推荐）预拷贝重叠 PDF

```bash
mkdir -p outputs/generalization/full_market_2024

.venv/bin/python - <<'PY'
import yaml, os, shutil
full = {c["stock_code"] for c in yaml.safe_load(open("lab/eval_companies_full_market_2024.yaml"))["companies"]}
src_dirs = [
    "outputs/generalization/eval1000",
    "outputs/generalization/eval1000_v2",
    "outputs/generalization/eval1000_independent_20260623",
]
dst_base = "outputs/generalization/full_market_2024"
copied = 0
for code in full:
    for src in src_dirs:
        src_pdf = f"{src}/{code}/{code}.pdf"
        src_meta = f"{src}/{code}/meta.json"
        dst_dir = f"{dst_base}/{code}"
        if os.path.exists(src_pdf) and os.path.getsize(src_pdf) >= 10000:
            os.makedirs(dst_dir, exist_ok=True)
            if not os.path.exists(f"{dst_dir}/{code}.pdf"):
                shutil.copy2(src_pdf, f"{dst_dir}/{code}.pdf")
            if os.path.exists(src_meta) and not os.path.exists(f"{dst_dir}/meta.json"):
                shutil.copy2(src_meta, f"{dst_dir}/meta.json")
            copied += 1
            break
print(f"Pre-copied {copied} PDFs")
PY

df -h .   # 预拷贝后再确认磁盘
```

### Step 4：顺序跑 5 个 batch（overnight）

```bash
mkdir -p outputs/generalization/full_market_2024/{sse_main,star,szse_main,chinext,bse}

for board in sse_main star szse_main chinext bse; do
  echo "=== Starting $board $(date) ===" | tee -a outputs/generalization/full_market_2024/batch_${board}.log
  .venv/bin/python lab/eval_generalize.py \
    --companies lab/batch_${board}_2024.yaml \
    --out outputs/generalization/full_market_2024/${board} \
    --throttle 1.5 \
    2>&1 | tee -a outputs/generalization/full_market_2024/batch_${board}.log
  echo "=== Done $board $(date) ===" | tee -a outputs/generalization/full_market_2024/batch_${board}.log
done
```

或使用 `nohup` 后台跑单个 batch：

```bash
nohup .venv/bin/python lab/eval_generalize.py \
  --companies lab/batch_sse_main_2024.yaml \
  --out outputs/generalization/full_market_2024/sse_main \
  --throttle 1.5 \
  > outputs/generalization/full_market_2024/batch_sse_main.log 2>&1 &
echo "PID: $!"
```

### Step 5：合并 batch 结果

```bash
.venv/bin/python - <<'PY'
import json, os
from lab.eval_generalize import write_summary

OUT = "outputs/generalization/full_market_2024"
boards = ["sse_main", "star", "szse_main", "chinext", "bse"]
all_results = []
for board in boards:
    p = f"{OUT}/{board}/eval_results.json"
    if os.path.exists(p):
        r = json.load(open(p, encoding="utf-8"))
        all_results.extend(r)
        print(f"  {board}: {len(r)}")

json.dump(all_results, open(f"{OUT}/eval_results.json", "w"), ensure_ascii=False, indent=2)
write_summary(all_results, f"{OUT}/eval_summary.md")
print(f"Merged total: {len(all_results)}")
PY
```

### Step 6：快速指标检查

```bash
.venv/bin/python - <<'PY'
import json, statistics
from collections import Counter

rs = json.load(open("outputs/generalization/full_market_2024/eval_results.json"))
status = Counter(r["status"] for r in rs)
ok = [r for r in rs if r["status"] == "ok"]
nonfin = [r for r in ok if not r.get("financial")]
fin = [r for r in ok if r.get("financial")]

print(f"total={len(rs)}")
print("status:", dict(status))
print(f"ok={len(ok)} nonfin={len(nonfin)} fin={len(fin)}")
print(f"success rate: {100*len(ok)/len(rs):.1f}%")
print(f"nonfin plausible mean: {statistics.mean(r['plausible'] for r in nonfin):.3f}/11")

for field in ("rnd_investment", "revenue_by_region", "revenue_by_segment"):
    p = sum(1 for r in nonfin if r.get("fields", {}).get(field, {}).get("plausible"))
    print(f"  {field}: {p}/{len(nonfin)} ({100*p/len(nonfin):.1f}%)")

from collections import Counter as C
print("fin subtypes:", dict(C(r.get("schema_profile", "unknown") for r in fin)))
PY
```

### Step 7：重试 error 公司（VPN off）

与 independent run 相同模式：读取 error 列表，对每家公司调用 `evaluate_company`，合并回 `eval_results.json`。

```bash
.venv/bin/python - <<'PY'
import json, time, yaml
from lab.eval_generalize import evaluate_company, write_summary
from lab.probe_cninfo import _session

OUT = "outputs/generalization/full_market_2024"
results = json.load(open(f"{OUT}/eval_results.json", encoding="utf-8"))
error_codes = {r["stock_code"] for r in results if r["status"] == "error"}
if not error_codes:
    print("No errors to retry"); raise SystemExit(0)

companies = yaml.safe_load(open("lab/eval_companies_full_market_2024.yaml"))["companies"]
retry = [c for c in companies if c["stock_code"] in error_codes]
print(f"[retry] {len(retry)} companies — VPN should be OFF")

sess = _session(90)
by_code = {r["stock_code"]: r for r in results}
for i, c in enumerate(retry, 1):
    code = c["stock_code"]
    # PDF 可能在 board subdir 或 flat dir；evaluate_company 用 --out 根目录
    print(f"[{i}/{len(retry)}] {c['short_name']} {code} ...", flush=True)
    r = evaluate_company(c, sess, OUT)
    print(f"    -> status={r['status']} err={str(r.get('error',''))[:50]}", flush=True)
    by_code[code] = r
    time.sleep(1.5)

merged = [by_code[r["stock_code"]] for r in results]
json.dump(merged, open(f"{OUT}/eval_results.json", "w"), ensure_ascii=False, indent=2)
write_summary(merged, f"{OUT}/eval_summary.md")
print("[done]")
PY
```

> **注意：** error retry 时 `evaluate_company` 的 `out_dir` 需与 batch 写入路径一致。若 PDF 在 `full_market_2024/sse_main/600000/`，需确认路径或统一将预拷贝 PDF 放在 `full_market_2024/<code>/` flat 结构。

### Step 8：SQLite 导入

```bash
.venv/bin/python lab/db_init.py

.venv/bin/python lab/db_import.py \
  --eval-dir outputs/generalization/full_market_2024 \
  --run-name full_market_2024 \
  --limit 0

sqlite3 outputs/db/listed_companies_v1.db \
  "SELECT run_name, COUNT(*) FROM evaluation_result GROUP BY run_name;"
```

### Step 9：撰写报告

创建 `outputs/generalization/full_market_2024/full_market_2024_summary.md`，对比：
- status 计数 vs eval1000_v2 / independent
- 非金融 proxy mean
- rnd / revenue 字段率
- 金融 subtype 分布
- no_announcement 率（全市场预期更高）
- SQLite 行数
- error 类型分布

---

## 7. 指标检查清单

| 指标 | eval1000_v2 参考 | independent 参考 | 全市场目标 |
|---|---:|---:|---|
| Total | 1020 | 1000 | ~5300 |
| ok | 947 (92.8%) | 918 (91.8%) | ~85–90% |
| no_announcement | 73 (7.2%) | 82 (8.2%) | ~10–15% |
| errors | 0 | 0（retry 后） | ≤50（可重试） |
| Non-fin proxy mean | 10.33/11 | 10.30/11 | ~10.2–10.4/11 |
| rnd plausible rate | 66.1% | 66.7% | ~64–68% |
| revenue_by_region | 90.7% | 90.0% | ~88–92% |
| revenue_by_segment | 95.7% | 94.9% | ~93–96% |
| Financial ok | 11 | 11 | ~150–200 |
| SQLite extracted_field | 10428 | 10112 | ~55000–58000 |
| strict-usable | **未重跑** | **未重跑** | **未重跑** |

---

## 8. 风险与缓解

| 风险 | 可能性 | 缓解 |
|---|---|---|
| 磁盘：~70 GB 新 PDF | **高** | 预拷贝 ~2000 PDF；运行前 `df -h` ≥80 GiB |
| 总耗时 20–26 h | 确定 | 5 batch 顺序 overnight；nohup |
| CNINFO 403 / 限流 | 中 | throttle 1.5；VPN off；error retry |
| no_announcement 10–15% | 预期 | BSE/退市正常，非失败 |
| batch 中途崩溃丢 JSON | 低 | 每 board 独立 subdir 保存 JSON |
| 金融 auto-tag 遗漏（资本类） | 低 | `_FIN_KW` 未含「资本」；约 10–20 家可能走 industrial schema |
| error retry 路径不一致 | 中 | 预拷贝 PDF 至 flat `full_market_2024/<code>/` 结构 |

---

## 9. 交付物

| 文件 | 说明 |
|---|---|
| `lab/make_full_market_yaml.py` | 全市场 YAML 生成脚本 |
| `lab/eval_companies_full_market_2024.yaml` | ~5300 家公司列表（commit） |
| `outputs/generalization/full_market_2024/eval_summary.md` | 自动汇总（commit） |
| `outputs/generalization/full_market_2024/full_market_2024_summary.md` | 对比报告（commit） |
| `CURRENT_STATUS.md` / `CHANGELOG.md` | 项目状态更新 |

---

## 10. 是否今天开跑？

**建议暂不立即开跑**，先确认：

1. **磁盘 ≥80 GiB 可用**（当前 ~88 GiB，预拷贝 + 新下载后偏紧）
2. 机器可 **overnight 无人值守** 20–26 h
3. **VPN 关闭**

满足后再按 Step 0 → 1 → 2 → 3 → 4 顺序执行。

---

## GitHub Issue Checklist

```markdown
## Full-market 2024 annual report extraction — checklist

### Pre-run
- [ ] git status clean
- [ ] df -h: ≥80 GiB free
- [ ] Add .gitignore entries (full_market_2024 subdirs, batch_*.log, batch_*_2024.yaml)
- [ ] Create lab/make_full_market_yaml.py

### YAML generation
- [ ] Run make_full_market_yaml.py → lab/eval_companies_full_market_2024.yaml
- [ ] Verify ~5300 companies; financial ~150–200
- [ ] Split into 5 board batch YAMLs

### PDF pre-copy (recommended)
- [ ] Pre-copy ~2000 PDFs+meta.json from eval1000/v2/independent
- [ ] Verify disk ≥80 GiB after pre-copy

### Batch evaluation (sequential, overnight)
- [ ] Batch 1: sse_main (~1700, ~6–8 h)
- [ ] Batch 2: star (~560, ~2–3 h)
- [ ] Batch 3: szse_main (~1400, ~5–7 h)
- [ ] Batch 4: chinext (~1300, ~5–6 h)
- [ ] Batch 5: bse (~300, ~1–2 h)
- [ ] Spot-check each batch log for mass errors

### Post-run
- [ ] Merge 5 batch eval_results.json → full_market_2024/eval_results.json
- [ ] Run status summary; compare vs eval1000_v2 (10.33/11) and independent (10.30/11)
- [ ] Retry error companies (VPN off)
- [ ] db_import.py --run-name full_market_2024 --limit 0
- [ ] Confirm SQLite ~55000–58000 extracted_field rows

### Documentation
- [ ] Write full_market_2024_summary.md
- [ ] Update CURRENT_STATUS.md and CHANGELOG.md

### Commit
- [ ] Commit: make_full_market_yaml.py, eval_companies_full_market_2024.yaml,
       eval_summary.md, full_market_2024_summary.md, CURRENT_STATUS, CHANGELOG
- [ ] Do NOT commit: PDFs, [0-9]*/ dirs, eval_results.json, *.log, .db, batch_*_2024.yaml
```
