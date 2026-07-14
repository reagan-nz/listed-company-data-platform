# Controller Resource Allocation Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md)_


## 1. Purpose


Allocate Daily Loop iterations, agent slots, and commit budget across A/B/C/D by **expected mission gain** with **track fairness** — not by equal share, and not by letting one easy track consume the whole day.


### Failure mode this fixes（run4）


A-class ran many successor iterations while D-class was never invoked solely because live shareholder_change awaited approval — even though D still had autonomous offline work.



---

# 2. Allocation factors


Prioritize tracks using:


| Factor | Prefer |
|--------|--------|
| **mission importance** | capability closest to ultimate full-market mission / current milestone |
| **bottleneck status** | work that clears binding constraints for multiple future tasks |
| **expected progress gain** | larger honest capability improvement per effort |
| **track inactivity / staleness** | tracks with Autonomous Queue work that have not executed recently |


Do **not** allocate 25% each by default.  
Do **not** allocate 100% to the easiest track when other tracks have autonomous candidates.



---

# 3. Track Fairness + Staleness Penalty


### Fairness rules


1. Score candidates with mission impact · bottleneck reduction · **track inactivity**.  
2. Apply a **staleness penalty** against over-served tracks and a **staleness boost** to under-served tracks.  
3. If track T has Autonomous Queue work and has not executed for **≥2 consecutive iterations** while another track keeps chaining successors → **prefer T** on the next select（unless T’s candidates are unsafe/low-value or approval-only）.  
4. Do **not** allow one easy track to consume all execution cycles when other tracks have non-empty Autonomous Queues.  
5. Approval Queue occupancy on T does **not** count as “T is inactive by design” — still plan Autonomous Queue for T.  


### Soft balance guidance（Operational Mode）


Within one daily run, if iterations ≥4 and one track already has **>50%** of track-agent dispatches while another track has Autonomous Queue candidates and **0** dispatches → next target **must** come from an under-served track（unless stuck audit shows only low-value leftovers）.



---

# 4. Procedure


```text
1. Split each track into Autonomous Queue vs Approval Queue（generator §3.1）
2. List offline_safe READY candidates from Autonomous Queues only for dispatch
3. Score: mission importance · bottleneck · expected gain · safety · staleness
4. Select highest-value target under fairness constraints（§3）
5. Parallelize only when isolation allows and fairness is not violated
6. Keep Approval Queue visible · never confuse it with “no work”
```



---

# 5. Budget interaction


- Iteration budget is scarce — spend on capability/evidence bands first.  
- Commit budget follows commit batching（few packages · not microcommits）.  
- Runtime budget: prefer finishing a high-gain package over starting many low-gain ones — **but** apply fairness before chaining a 4th successor on the same track.  
- Controller maintenance gets residual budget only.  



---

# 6. Examples


| Situation | Allocation |
|-----------|------------|
| D WAITING_APPROVAL · D has schema/sample offline · A has 3rd successor | **prefer D autonomous**（staleness + fairness） |
| D WAITING_APPROVAL · D Autonomous Queue empty after audit · A has offline gap | prefer A |
| C partial evidence packable · B only live retry | prefer C |
| All tracks Approval Queue only（Autonomous empty after audit） | `NO_VALUABLE_SAFE_TASK` + full candidate audit |



---

# 7. Anti-patterns


Forbidden:


- round-robin A→B→C→D every iteration regardless of gain  
- starving the bottleneck track to “keep all tracks busy”  
- equal commit quotas that force empty packages  
- spending runtime on controller tip-align while track READY exists  
- **skipping D/B/C entirely because approval-gated live work is pending**  
- chaining A successors until budget ends while other Autonomous Queues are non-empty  
- treating Approval Queue as the only queue for a track  
