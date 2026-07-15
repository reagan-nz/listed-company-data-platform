# CNINFO D 类 restricted_shares_unlock — D-FM-47 Next-Slice Runner Extension + S4 Dry-run Offline

_生成时间：2026-07-15 · D-FM-47 · wall≈短（纯离线 · 含 read-only / dry-run tests）_

> **性质：** restricted_shares_unlock next-slice runner extension + S4 dry-run offline · **CNINFO = 0** · **无 live** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **prefer taken：** restricted_shares_unlock next-slice runner extension + S4 dry-run（D-FM-46 approval package `STANDING_SCOPE_AUTHORIZED` / fixture VR `PASS_OFFLINE` 已 commit）— live 仍禁

---

## Task Card

| 项 | 值 |
|----|-----|
| task_id | **D-FM-47** |
| track / executor | D / d-class-executor |
| controller_execution_allowed | **false** |
| standing_scope | shareholder / capital / FIA / AT / SD |
| prefer | restricted_shares_unlock next-slice runner extension + S4 dry-run offline |

---

## Prefer Decision

| 选项 | 结果 |
|------|------|
| **restricted_shares_unlock next-slice runner extension + S4 dry-run offline** | **primary — 执行** |
| shareholder_change next-slice offline planning | deferred |
| restricted_shares_unlock next-slice bounded live | **禁止本回合**（NOT_APPROVED） |
| ESS H3/H4 | **paused** |
| DLC006R reopen | **禁止** |
| FIA / AT / SD / EP / RSU-first frozen roots mutate | **禁止** |

---

## Gates

```text
d_class_restricted_shares_unlock_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_restricted_shares_unlock_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_runner_extension_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_next_slice_s4_dryrun_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_live_path_gate = READY_FOR_APPROVAL
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_execution_gate = NOT_APPLICABLE
controller_execution_allowed = false
```

**强制语义：** READY_FOR_APPROVAL（runner/S4）≠ live_approved ≠ verified ≠ production_ready。

---

## Deliverables

| 项 | 路径 / 说明 |
|----|-------------|
| runner flags | `--restricted-shares-unlock-next-slice` · `--approve-d-class-restricted-shares-unlock-next-slice` |
| universe lock（只读） | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv`（DRU101–105） |
| S4 dry-run report | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice/reports/d_class_restricted_shares_unlock_next_slice_dryrun_report.csv` |
| S4 dry-run summary | `.../d_class_restricted_shares_unlock_next_slice_dryrun_summary.md` |
| planned snapshots | `.../planned_snapshots/DRU101–105_restricted_shares_unlock.json`（5） |
| command draft | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_command_draft_20260715.md` |
| next step | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_runner_next_step_recommendation_20260715.md` |
| matrix | `outputs/validation/cninfo_d_class_restricted_shares_unlock_dfm47_next_slice_runner_matrix_20260715.csv` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_restricted_shares_unlock_dfm47_next_slice_runner_s4_20260715.md` |
| smoke test | `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_runner.py` |

---

## S4 Dry-run Result

| 指标 | 值 |
|------|-----|
| cases | **5**（DRU101–DRU105） |
| planned_ok | **5/5** |
| planned_shared_cninfo_requests | **1** |
| CNINFO calls | **0** |
| live executed | **false** |

共享探针计划：`tdate_daily_2026-07-03` · endpoint `liftBan/detail` · 离线按 SECCODE 过滤 DRU101–105 · **禁** `2026-06-08` sole found 锚。

---

## Tests

| 测试 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_runner.py` | **23/23 PASS** |
| `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_fixtures.py` | **19/19 PASS**（回归） |
| `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_planning_offline.py` | **12/12 PASS**（回归 · 独立进程） |
| `lab/test_cninfo_d_class_restricted_shares_unlock_first_slice_runner.py` | **20/20 PASS**（回归） |
| `lab/test_cninfo_d_class_equity_pledge_next_slice_runner.py`（TestEquityPledgeNextSliceRunner） | **23/23 PASS**（回归） |

断言：live 无 approve → exit 2；mixed mode / wrong output root / wrong anchor·component 阻断；mock live CNINFO=0；freeze sha256 保持；allow-list **不含** console logs。

---

## Freeze Attestation（未触碰）

```text
rsu_next_slice_universe_lock_sha256 = 13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f
rsu_first_slice_universe_draft_sha256 = 81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9
rsu_first_slice_dryrun_report_sha256 = dc08d04c6262a46f5813e513463bc004edd222a980507484f23f8851e97bf41d
ep_next_slice_universe_lock_sha256 = 1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384
ep_next_slice_dryrun_report_sha256 = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
fia_first_slice_universe_lock_sha256 = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
fia_next_slice_universe_lock_sha256 = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
fia_further_scale_universe_lock_sha256 = 398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1
fia_further_scale_dryrun_report_sha256 = fc7cfc51493c426d0db1608aad09b0dc4a7755c0019f8d822a46e40fa85fefd4
at_next_slice_universe_lock_sha256 = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
sd_next_slice_universe_lock_sha256 = c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f
at_next_slice_dryrun_report_sha256 = 51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497
sd_next_slice_dryrun_report_sha256 = 2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362
```

---

## Allow-list / Wall

```text
allow_list = rsu_next_slice_runner_flags_dryrun_artifacts_docs_tests
exclude = console_logs;live_reports;A/B/C_roots;fia_first_next_further_locks;at_sd_dryrun_roots;ep_first_next_freeze;rsu_first_slice_freeze
wall = no_cninfo;no_live;no_commit;no_push;no_ess_h3_h4;no_dlc006r;controller_execution_allowed=false
```

---

## Footer

```text
task_id = D-FM-47
phase = restricted_shares_unlock_next_slice_runner_extension_s4_dryrun_offline
prefer_taken = rsu_next_slice_runner_extension_s4_dryrun
cninfo_calls = 0
live_executed = false
controller_execution_allowed = false
allow_list = rsu_next_slice_runner_flags_dryrun_artifacts_docs_tests
runner_extension_gate = READY_FOR_APPROVAL
s4_dryrun_gate = PASS_OFFLINE
live_gate = NOT_APPROVED
locked_cases = DRU101-DRU105
planned_ok = 5/5
ready_for_commit = true
```
