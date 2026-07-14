# Controller Task Continuation Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_capability_gap_analysis_v2.md](controller_capability_gap_analysis_v2.md) · [controller_execution_cycle_policy_v2.md](controller_execution_cycle_policy_v2.md) · [controller_stuck_detection_policy_v2.md](controller_stuck_detection_policy_v2.md)_


## 1. Purpose


After every completed task, Controller must decide whether the **capability gap** closed — and if not, **generate a successor**.


**Completed task ≠ completed track.**  
The Daily Loop must continue in the same run when valuable successor work exists and budget remains.



---

# 2. Post-task evaluation（normative）


For each finished task `T`:


```text
1. Record T in task memory（completed or failed）
2. Re-run capability gap analysis for T.track
3. Ask: Did T close the targeted capability gap?
   - YES → find next bottleneck（progress + gap + resource allocation）
   - NO  → generate successor task(s) via task generator
4. Promote safe successors to READY if any
5. Continue execution cycle unless stop condition hits
```



---

# 3. Gap-closed vs gap-open


| Outcome | Meaning | Next |
|---------|---------|------|
| **gap_closed** | expected_capability_improvement verified by evidence | select next bottleneck / milestone step |
| **gap_partial** | useful progress · residual gap remains | successor on residual gap |
| **gap_unchanged** | no capability movement | stuck detection + alternate generation |
| **failed** | task failed safely | memory failed · generate alternate or escalate if required |


Do not treat “docs written” as gap_closed unless the gap was documentation/evidence completeness.



---

# 4. Successor rules


1. Successor must reference `predecessor_task_id`.  
2. Successor must target the **remaining** gap（not redo completed work）.  
3. Successor must pass generator safety filters.  
4. Prefer same track until local bottleneck clears — unless resource allocation says switch.  
5. If successor would require missing approval → enqueue approval item · continue **other** tracks.  



---

# 5. Loop continuation


Continue the daily run when:


- safe READY successors exist, or  
- generator finds new offline_safe candidates, or  
- other tracks have READY work  


Stop only under execution cycle stop reasons（including post-generation `NO_SAFE_READY`）.



---

# 6. Anti-patterns


Forbidden:


- stop the day because one task package committed  
- declare track COMPLETED because one offline analysis finished  
- endless successors with zero capability movement（stuck detection must fire）  
- successor that bypasses the same approval the predecessor respected  
