# Controller Stuck Detection Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_memory_policy_v2.md](controller_task_memory_policy_v2.md) · [controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_human_interrupt_policy_v2.md](controller_human_interrupt_policy_v2.md)_


## 1. Purpose


Detect when the Daily Loop is **spinning without capability progress**, then produce a stuck analysis and stop endless repetition.



---

# 2. Stuck signals


Fire stuck detection when **any** persist across iterations（same daily run or consecutive days if memory shows pattern）:


1. Repeated cycles produce **no capability progress**（gap metrics unchanged · only controller churn）.  
2. The **same blocker** appears repeatedly（e.g. snapshot blocked · D WAITING_APPROVAL · dirty worktree）.  
3. **No task state changes**（READY set identical · no new evidence · no successor）.  
4. Generator keeps emitting **memory-equivalent** candidates.  



---

# 3. Required stuck analysis output


```text
Stuck analysis:
  Cause:
  Possible autonomous actions:
  Human dependency:
```


Rules:


- `Possible autonomous actions` must be empty or truly new offline_safe options.  
- If only human dependency remains → escalate per interrupt policy（approval unlocks meaningful next · or no autonomous progress remains）.  
- **Do not endlessly repeat** the same package.  



---

# 4. Response actions


| Case | Action |
|------|--------|
| New autonomous actions exist | generate → rank → execute once |
| Only human dependency | record approval queue · may stop with `NO_SAFE_READY` or track-scoped interrupt |
| Controller-only churn detected | halt maintenance band · report stuck · stop or switch tracks |


Mark stuck pattern in task memory as known blocker / deferred approach.



---

# 5. Threshold guidance（Operational Mode）


Default soft thresholds（tighten via human if needed）:


- ≥2 consecutive iterations with zero capability movement on the active track → analyze  
- ≥3 memory-equivalent generations blocked → stuck  
- Same blocker cited in ≥2 daily reports without new autonomous path → stuck  



---

# 6. Anti-patterns


Forbidden:


- ignoring unchanged gaps while committing report tip-aligns  
- re-running identical offline packaging as “activity”  
- declaring stuck to avoid doing available offline work on another track  
- using stuck analysis to bypass approvals  
