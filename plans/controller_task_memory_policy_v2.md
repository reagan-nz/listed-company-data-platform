# Controller Task Memory Policy v2


_最后更新：2026-07-14_  
_配套：[controller_task_generator_policy_v2.md](controller_task_generator_policy_v2.md) · [controller_task_continuation_policy_v2.md](controller_task_continuation_policy_v2.md) · [controller_stuck_detection_policy_v2.md](controller_stuck_detection_policy_v2.md)_


## 1. Purpose


Maintain an **autonomous memory layer** so the Daily Loop does not repeat:


- completed work  
- blocked approaches  
- rejected strategies  


Memory is evidence under `outputs/validation/`（and optional YAML companion）— not tribal chat recall.



---

# 2. Memory classes


| Class | Meaning |
|-------|---------|
| **Completed tasks** | finished with evidence · gap impact recorded |
| **Failed tasks** | attempted · failed safely · lesson recorded |
| **Deferred tasks** | intentionally postponed（e.g. BD2E624） |
| **Human rejected tasks** | human said no / rejected plan |
| **Known blockers** | recurring gates · approvals · dirty worktree · snapshot block |


Each entry should include: `task_id` · `track` · `summary` · `evidence_paths` · `date` · `do_not_repeat_reason`（if any）.



---

# 3. Preferred artifact


Suggested daily/rolling file:


`outputs/validation/controller_task_memory_YYYYMMDD.md`  
（or append-only `controller_task_memory_ledger.md`）


May also emit `controller_task_memory_YYYYMMDD.yaml` without secrets.



---

# 4. Read/write rules


**Write** after: task complete · task fail · human reject · blocker confirmed · defer decision.


**Read** before: task generation · continuation successor · stuck analysis · resource allocation.


Generator **must** drop candidates that are memory-equivalent to completed work or human-rejected strategies — unless human reopens scope.



---

# 5. Equivalence


Two tasks are memory-equivalent when they share:


- same track + same objective intent + same primary evidence target  


Cosmetic renames do not bypass memory.



---

# 6. Anti-patterns


Forbidden:


- regenerating the same offline package every loop as “progress”  
- forgetting human rejection and re-proposing the same live scope  
- using memory to block **new** gap-aligned successors that are not equivalent  
- storing secrets / tokens in memory files  
