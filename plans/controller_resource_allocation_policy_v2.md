# Controller Resource Allocation Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_priority_policy_v2.md](controller_task_priority_policy_v2.md) · [controller_mission_objective_v2.md](controller_mission_objective_v2.md) · [controller_progress_tracking_v2.md](controller_progress_tracking_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md)_


## 1. Purpose


Allocate Daily Loop iterations, agent slots, and commit budget across A/B/C/D by **expected mission gain** — not by equal share.



---

# 2. Allocation factors


Prioritize tracks using:


| Factor | Prefer |
|--------|--------|
| **mission importance** | capability closest to ultimate full-market mission / current milestone |
| **bottleneck status** | work that clears binding constraints for multiple future tasks |
| **expected progress gain** | larger honest capability improvement per effort |


Do **not** allocate 25% each by default.



---

# 3. Procedure


```text
1. List safe READY + generated offline_safe candidates per track
2. Score qualitatively: mission importance · bottleneck · expected gain · safety
3. Assign iteration wave to highest expected-gain track(s)
4. Parallelize only when isolation allows and it raises total mission gain
5. Leave approval-gated tracks on queue · spend budget on autonomous tracks
```



---

# 4. Budget interaction


- Iteration budget is scarce — spend on capability/evidence bands first.  
- Commit budget follows commit batching（few packages · not microcommits）.  
- Runtime budget: prefer finishing a high-gain package over starting many low-gain ones.  
- Controller maintenance gets residual budget only.  



---

# 5. Examples


| Situation | Allocation |
|-----------|------------|
| D waiting approval · A has offline gap package | prefer A（autonomous gain） |
| C partial evidence packable · B only live retry | prefer C |
| All tracks only approval-gated | stop autonomous track spend · report approval queue · optional controller report only |



---

# 6. Anti-patterns


Forbidden:


- round-robin A→B→C→D every iteration regardless of gain  
- starving the bottleneck track to “keep all tracks busy”  
- equal commit quotas that force empty packages  
- spending runtime on controller tip-align while track READY exists  
