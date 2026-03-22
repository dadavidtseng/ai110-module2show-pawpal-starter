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

- **Design brainstorming** — Used AI to validate class relationships from the UML diagram, confirm whether a separate `Schedule` dataclass was justified, and check for missing edges (e.g., pet-task back-reference).
- **Code generation** — AI generated class skeletons from the UML description, implemented the greedy scheduling algorithm, and scaffolded the Streamlit UI layout.
- **Test generation** — AI proposed test classes and edge cases (zero budget, cross-pet conflicts, recurring attribute preservation) that I reviewed and kept.
- **Refactoring** — Asked AI to simplify the `sort_by_time` lambda and consolidate filtering methods into the `Scheduler` class rather than scattering them.
- **Most helpful prompts**: "Based on my skeletons, how should the Scheduler retrieve tasks from the Owner?", "What edge cases should I test for a scheduler with recurring tasks?", and "How can I use `timedelta` for daily recurrence?"

**b. Judgment and verification**

- AI initially suggested making `Scheduler` an instance class that stores a reference to `Owner`. I rejected this because it creates unnecessary coupling — the Scheduler doesn't need mutable state, and static methods are easier to test. I kept the stateless design.
- I verified AI-generated test assertions by manually tracing expected values (e.g., confirming that `date.today() + timedelta(days=1)` is correct for daily recurrence rather than blindly trusting the assertion).
- When AI suggested a complex regex-based time parser for `sort_by_time`, I replaced it with a simpler `split(":")` approach — KISS over cleverness.

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

- The **stateless Scheduler design** (static methods only) made testing trivial — no setup/teardown, no mock objects, just pass data in and assert outputs. This was the single best architectural decision.
- The **dataclass-first approach** kept the domain models clean and readable. Adding new fields (scheduled_time, due_date) later was painless because dataclasses handle defaults and `__init__` automatically.
- The **CLI-first workflow** (main.py before Streamlit) caught logic bugs early, before UI complexity muddied the feedback loop.

**b. What you would improve**

- **Duration-based conflict detection** — Currently only checks exact time matches. Overlapping intervals (e.g., a 30-min task at 08:00 conflicts with anything at 08:15) would be more realistic.
- **Pet-task association in Schedule** — The schedule output doesn't show which pet each task belongs to. Adding a `pet_name` field to Task or a mapping in Schedule would make the UI more informative.
- **Persistent storage** — All data lives in session state and is lost on refresh. Adding SQLite or JSON file persistence would make the app practical.

**c. Key takeaway**

- **AI is a powerful accelerator, but the human is the architect.** AI can generate code faster than I can type, but it doesn't understand system-level tradeoffs — when to defer a feature (YAGNI), when simplicity beats correctness (exact-time vs. interval overlap), or when a "clever" solution hurts readability. The most valuable skill is knowing when to accept, modify, or reject AI suggestions based on the project's actual needs.
