# Controller Resource Allocation Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_mission_replanning_loop_v2.md](controller_mission_replanning_loop_v2.md) · [controller_track_execution_queue_policy_v2.md](controller_track_execution_queue_policy_v2.md) · [controller_track_stop_reason_policy_v2.md](controller_track_stop_reason_policy_v2.md)_


## 1. Purpose


Allocate Daily Loop iterations, agent slots, and commit budget across A/B/C/D by **expected mission gain** with **track fairness** — not by equal share, and not by letting one easy track consume the whole day.


### Failure mode this fixes（run4）


A-class ran many successor iterations while D-class was never invoked solely because live shareholder_change awaited approval — even though D still had autonomous offline work.



---

# 2. Allocation factors / priority calculation


Prioritize tracks and candidates using:


```text
Priority ≈
  mission impact
+ bottleneck reduction
+ track staleness
+ queue availability
```


| Factor | Prefer |
|--------|--------|
| **mission impact** | capability closest to ultimate full-market mission / current milestone |
| **bottleneck reduction** | work that clears binding constraints for multiple future tasks |
| **track staleness** | tracks with Autonomous Queue work that have not executed recently |
| **queue availability** | tracks with non-empty Controller-approved Autonomous Queues ready to continue |


Do **not** allocate 25% each by default.  
Do **not** allocate 100% to the easiest track when other tracks have autonomous candidates.  
Do **not** force equal execution counts — critical progress still wins.  
**Queue availability** raises a track’s score when successors are already validated and queued（reduces idle gaps after completion）.  


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
2. Assign surviving autonomous candidates into per-track execution queues
3. List offline_safe READY candidates from Autonomous Queues only for dispatch
4. Score: mission impact · bottleneck reduction · staleness · queue availability · safety
5. Select highest-value target under fairness constraints（§3）
6. On task complete: allow same-track queue pull only after Controller re-score（execution queue v2）
7. If another track wins the slot: set idle track stop_reason = RESOURCE_ALLOCATED_ELSEWHERE or LOW_PRIORITY_DEFERRED
8. Parallelize only when isolation allows and fairness is not violated
9. Keep Approval Queue visible · never confuse it with “no work”
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
- forcing equal drain of all track queues  
- idling a track with non-empty Autonomous Queue without recording `RESOURCE_ALLOCATED_ELSEWHERE` or `LOW_PRIORITY_DEFERRED`  
- treating `HUMAN_GATE_BLOCKED` as global `NO_VALUABLE_SAFE_TASK`



---


# 8. Relationship to Mission Execution Engine v4


[controller_mission_execution_engine_v4.md](controller_mission_execution_engine_v4.md) 要求 fairness **不得**解释成"等四轨齐步"。正确行为：


- 一轨长任务 EXECUTING 时，其他轨若有更高/同等价值 READY → **立即**分配 agent  
- 禁止：因 A 正在 CNINFO live 而让 B/C/D 空闲等待下一 Global Wave  
- 仍禁止：为"让空闲轨看起来忙碌"而发明低价值任务（§7 anti-patterns 不变）


Fairness 继续防止单轨垄断预算；v4 只禁止把 fairness 误做成同步屏障。  
