# CNINFO D 类 restricted_shares_unlock — D-FM-46 Next-Slice Approval Package Offline

_生成时间：2026-07-15 · D-FM-46 · wall≈短（纯离线 · 含 tests）_

> **性质：** restricted_shares_unlock（ES / 限售解禁）next-slice approval package offline（universe lock + VR + fixtures）· **CNINFO = 0** · **无 live** · **无 runner** · **NOT verified** · **NOT production_ready** · **无 commit** · **无 push**
>
> **prefer taken：** ES / RSU next-slice approval package offline（D-FM-45 planning `READY_FOR_APPROVAL` 已 commit）— live 仍禁 · shareholder_change deferred

---

## 1. Authorization Boundary

| 项 | 值 |
|----|-----|
| task_id | **D-FM-46** |
| track | D · d-class-executor |
| HEAD（任务开始） | `c9cfe41`（D-FM-45 restricted_shares_unlock next-slice offline planning committed） |
| standing_scope | shareholder / capital / FIA / AT / SD |
| controller_execution_allowed | **false** |
| Live CNINFO | **forbidden**（本回合） |
| CNINFO calls | **0** |
| DLC006R / 301259 / 688671 | **未重开** |
| RSU first-slice lock / live | **未 mutate** |
| EP first/next lock / dry-run | **未 mutate** |
| FIA first/next/further-scale lock / dry-run | **未 mutate** |
| AT/SD first/next lock / dry-run | **未 mutate** |
| ESS H3/H4 | **未探**（禁止） |
| A/B/C | **未触碰** |

Frozen sha256（任务前后一致）:

```text
rsu_first_universe = 81a792f43962849778d53af97b4d67c64d53b1cd15d8428ff6d0a74931c84ec9
rsu_first_live     = 9a0de0186eb22dceb5be7357267438d9a9ebb94ffcaf996f5a81440407ab5c57
ep_next_lock       = 1e8ceb722d87427269c48867376380d02371a1af0cbac09b62a97dc7c5135384
ep_next_dryrun     = 054cb015aebb6072f39becb7e13fd99cef57f0e614b13e34035f43c602708d4e
ep_first_universe  = 5fb4fa005236a162ef3bcc5322fe3b7134b36cbe7727fb0273724d0638dc8e10
fia_further_lock   = 398494f1cf6a6cf00637b82d6e3f5c38ae21671a4b47324fd1ee2262df92e9f1
fia_first          = 49345c88dee35e568784048aed4bcadcf3adb69fdb7c22495bcd0741f413dc8c
fia_next           = c9f2c3598b48dd823e1ad60c66f326b91d8bf2b6564565b083e13eeb8b9d0515
at_first           = d197b9618dc86c89d2a034addb75c37999baaf58e7455ab8626facd3f02adac2
at_next            = 4847d2017822f0d3758e0a1f3f034cd57cb35cbca4dd2ad14615427124ca73f6
sd_first           = 06633a0da42d5ddc669935b64942f4182611017d55907d7076528fc0993917b5
sd_next            = c07c2f27546bf11a3ea02b3efaa8adf1886b8a24549afe6dfe035c22978b994f
at_dryrun          = 51bda4864aee4853328b6e76f3ee0de073ca9e6d14b7d78d7cd8fb6ffe329497
sd_dryrun          = 2b74aac55299bc844e7df49725ad9ccf1f9c4dfbfc7db403f026412faf177362
sample_raw         = 8abe168ca57b5a7543618946c95ef806313b03a4e3b7ae89f78fa3397b15245d
sketch_csv         = c6f5dc02d46bea9e88acfcee11d7dd7efe35b771e9f9db14cd65865ffcecec07
```

---

## 2. Prefer Decision

| 选项 | 本任务取舍 |
|------|------------|
| **ES / RSU next-slice approval package offline** | **primary — 执行** |
| shareholder_change next-slice offline planning | deferred |
| ESS DevTools pause / hold | documented in next-step · **不**盲探 |
| ESS H3/H4 blind probe | **禁止** |
| next-slice runner / live | **禁止本回合** |
| EP/FIA/AT/SD live flip | **禁止**（controller_execution_allowed=false） |
| Level-2 IDLE | **禁止** |

---

## 3. Approval Package Result

| 项 | 值 |
|----|-----|
| approval gate | **`STANDING_SCOPE_AUTHORIZED`** |
| fixture VR gate | **`PASS_OFFLINE`** |
| live / runner gates | **`NOT_APPROVED`** |
| locked cases | **DRU101–DRU105** |
| shared anchor_tdate | **`2026-07-03`** |
| Tier-1 fixtures | **9** |
| shared probes（未来） | prefer **1** · tdate=`2026-07-03` |
| RSU first / EP / FIA / AT / SD | **frozen** |
| CNINFO this round | **0** |
| runner / live | **not implemented / not run** |
| live found-path DRU101–105 | **NOT_PROVEN** |

**不使用：** bare PASS · verified · production_ready。

### Delivered Delta（相对 D-FM-45 sketch）

1. **universe lock 晋升** — sketch `draft_not_locked` → 独立 lock CSV `locked`（sketch 保留为只读历史）。
2. **VR-RSU-NS-002** — 更新为 `locked` + `approval_task_id=D-FM-46`；不覆盖 first-slice VR。
3. **Tier-1 fixtures** — 结构 cite Tier-0 sample_raw；仍 `synthetic=true` · `cninfo_called=false` · 全案锚 `2026-07-03`。
4. **mixed 期望覆盖** — DRU101–104 found+empty；DRU105 empty control。

---

## 4. ESS Pause Hold（CNINFO=0 · no probe）

| 项 | 值 |
|----|-----|
| probe gate | `FAIL_REVIEW_REQUIRED` |
| status | `unconfirmed_probe_failed` |
| H1/H2 | rejected_404 |
| H3/H4 | **forbidden blind retry** |
| next | DevTools Network capture（人工） |

---

## 5. Artifacts

| 类型 | 路径 |
|------|------|
| universe lock | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_universe_lock_20260715.csv` |
| VR | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_validation_rules_20260715.md` |
| approval package | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_approval_package_20260715.md` |
| command draft | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_command_draft_20260715.md` |
| checklist | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_offline_prep_checklist_20260715.csv` |
| fixtures | `fixtures/d_class/restricted_shares_unlock_next_slice/`（9 files） |
| fixture VR matrix | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_fixture_vr_matrix_20260715.csv` |
| fixture VR summary | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_fixture_vr_validation_20260715.md` |
| next step | `outputs/validation/cninfo_d_class_restricted_shares_unlock_next_slice_approval_next_step_recommendation_20260715.md` |
| evidence（本文件） | `outputs/validation/cninfo_d_class_restricted_shares_unlock_dfm46_next_slice_approval_package_20260715.md` |
| smoke test | `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_fixtures.py` |

---

## 6. Tests

| 套件 | 结果 |
|------|------|
| `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_fixtures.py` | **19/19 PASS**（`.venv/bin/python`） |
| `lab/test_cninfo_d_class_restricted_shares_unlock_next_slice_planning_offline.py` | **12/12 PASS**（回归 · D-FM-45 未破坏） |

断言：DRU101–105 lock + denser-day `2026-07-03` · RSU/EP/FIA/AT/SD freeze sha256 · sketch 仍 draft · 禁 H3/H4 · **无** `requests` / CNINFO · allow-list **不含** console logs。

```text
rsu_next_slice_universe_lock_sha256 = 13254f44f344c0f2976dfbde6fe75e363f91283a6eec1a5ae02d29f3831f193f
```

---

## 7. Gates

```text
d_class_restricted_shares_unlock_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
d_class_restricted_shares_unlock_next_slice_fixture_vr_gate = PASS_OFFLINE
d_class_restricted_shares_unlock_next_slice_live_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_runner_gate = NOT_APPROVED
d_class_restricted_shares_unlock_next_slice_planning_gate = READY_FOR_APPROVAL
d_class_executive_shareholding_summary_endpoint_probe_gate = FAIL_REVIEW_REQUIRED
endpoint_status = unconfirmed_probe_failed
standing_scope_auth = shareholder_capital_fia_at_sd
level2_phrase_required = false
controller_execution_allowed = false
cninfo_calls = 0
rsu_first_mutated = false
ep_fia_at_sd_roots_mutated = false
ess_h3_h4_probed = false
verified_claim = false
ready_for_commit = true
```

---

## 8. Allow-List / Wall

```text
allow_list = rsu_next_slice_lock_vr_fixtures_docs_tests
allow_list_excludes = console_logs
cninfo_calls = 0
live = not_run
wall = offline_only
ready_for_commit = true
push = forbidden
```

**说明：** allow-list **不含** console logs（不得把 `*_console*.log` / live_console 列入可提交产物备注）。

---

## 9. Machine Footer

```text
task_id = D-FM-46
phase = restricted_shares_unlock_next_slice_approval_package_offline
prefer_taken = restricted_shares_unlock_next_slice_approval_package_offline
cninfo_calls = 0
allow_list = rsu_next_slice_lock_vr_fixtures_docs_tests
allow_list_excludes = console_logs
wall = offline_only
ready_for_commit = true
push = forbidden
controller_execution_allowed = false
rsu_next_slice_approval_gate = STANDING_SCOPE_AUTHORIZED
rsu_next_slice_fixture_vr_gate = PASS_OFFLINE
sketch_cases = DRU101-DRU105
locked_cases = DRU101-DRU105
```
