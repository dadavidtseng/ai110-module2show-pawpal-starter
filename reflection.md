# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions identified:**
1. **Add/manage pets** — Enter pet info (name, species, age) linked to an owner profile
2. **Add/edit care tasks** — Create tasks with duration, priority, and category (walk, feeding, meds, grooming, enrichment)
3. **Generate a daily schedule** — Produce an optimized daily plan that respects time constraints and task priorities, with reasoning explanations

**Classes and responsibilities:**
- **Owner** — Holds owner name and available minutes per day; owns a list of Pets
- **Pet** — Stores pet name, species, and age; holds a list of Tasks specific to that pet
- **Task** — Represents a single care activity with title, duration, priority, and category
- **Scheduler** — Takes an Owner (with Pets/Tasks) and available time, then produces a Schedule sorted by priority and fitted within time constraints
- **Schedule** — Holds the ordered list of scheduled tasks and provides explanation/reasoning for the plan

**b. Design changes**

- After reviewing the skeleton with AI, the initial design held up well — no structural changes were needed at this stage.
- One consideration was whether `Schedule` should track which pet each task belongs to (for richer explanations). I deferred this per YAGNI — the current design keeps things simple, and we can add pet-task association later if the UI requires it.
- The `Scheduler` was kept stateless (static methods only) to make it easy to test without instantiation overhead.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers **time budget** (owner's available minutes per day) and **task priority** (high > medium > low).
- Within the same priority tier, shorter tasks are preferred — this maximises the number of tasks that fit within the budget.
- Priority was chosen as the primary constraint because missing a high-priority task (e.g., medication) has real consequences, while skipping enrichment is merely disappointing.

**b. Tradeoffs**

- **Conflict detection uses exact-time matching only**, not duration-based overlap. Two tasks at "08:00" and "08:15" won't trigger a warning even if the first task runs 30 minutes. This was a deliberate simplicity tradeoff — implementing proper interval overlap requires tracking start+end times, which adds complexity without clear benefit for a daily planner where most tasks are approximate.
- **Greedy scheduling is not optimal.** A knapsack algorithm could theoretically pack more value into the time budget, but the greedy approach is easier to understand, debug, and explain to users. For a pet care app with ~10 tasks, the difference is negligible.
- **Recurring task regeneration is eager** — a new occurrence is created immediately when the current one is completed, rather than at the start of each day. This keeps the logic stateless (no background scheduler needed) but means the task list grows over time.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- **Task lifecycle**: mark_complete/mark_incomplete toggling, recurring task generation for daily/weekly/as_needed frequencies, attribute preservation across recurrence.
- **Pet task management**: add/remove tasks, pending_tasks filter, mark_task_complete with auto-recurrence and without (as_needed), completing nonexistent or already-done tasks.
- **Scheduler core**: priority ordering (high before medium before low), time budget enforcement, completed task exclusion, empty input handling.
- **Sorting**: chronological ordering by HH:MM, untimed tasks pushed to end.
- **Filtering**: by pet name (including missing pet), by completion status, by category.
- **Conflict detection**: same-pet conflicts, cross-pet conflicts, no false positives on different times, completed tasks correctly excluded.
- **Edge cases**: zero budget, all tasks completed, single oversized task, owner with no pets, pet with no tasks, mixed empty/full pets.

These tests matter because they verify both happy paths and boundary conditions — the scheduler must never crash on unexpected input, and its algorithmic decisions (priority ordering, greedy fit, conflict warnings) must be deterministic and correct.

**b. Confidence**

- **4 out of 5.** The 35 tests cover the core logic thoroughly — scheduling, sorting, filtering, conflict detection, and recurring tasks all behave as designed.
- If I had more time, I would test: (1) duration-based time overlap (not just exact-time conflicts), (2) Streamlit UI integration (button clicks triggering correct backend calls), (3) large-scale stress tests (100+ tasks to verify performance), and (4) property-based tests with Hypothesis to find unexpected input combinations.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
