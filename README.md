# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ includes several algorithmic features beyond basic task listing:

- **Priority-based scheduling** — Tasks are sorted high > medium > low, with shorter tasks preferred within the same tier. A greedy algorithm fits as many tasks as possible into the owner's daily time budget.
- **Time-based sorting** — Tasks can have a `scheduled_time` (HH:MM) and are sorted chronologically for display.
- **Filtering** — Filter tasks by pet name, completion status, or category (walk, feeding, meds, grooming, enrichment).
- **Conflict detection** — Warns when two or more pending tasks (same pet or across pets) share the same scheduled time.
- **Recurring tasks** — Daily and weekly tasks automatically generate their next occurrence when marked complete, using `timedelta` for accurate date math.

## Testing PawPal+

Run the test suite:

```bash
python -m pytest tests/ -v
```

The suite covers **35 tests** across 7 test classes:

| Class | What it tests |
|---|---|
| `TestTask` | Completion toggling, recurring task generation (daily/weekly/as_needed) |
| `TestPet` | Add/remove tasks, pending filter, mark_task_complete with auto-recurrence |
| `TestScheduler` | Priority ordering, time budget, completed skipping, empty schedule, explain output |
| `TestSortByTime` | Chronological sorting, untimed tasks placed last |
| `TestFiltering` | Filter by pet, status, category; missing pet returns empty |
| `TestConflictDetection` | Same-pet conflict, cross-pet conflict, no false positives, completed tasks ignored |
| `TestEdgeCases` | Zero budget, all completed, oversized task, no pets, no tasks, nonexistent title |

**Confidence Level: 4/5** — Core scheduling, filtering, and conflict logic are well-tested. The main gaps are UI integration tests (Streamlit) and duration-based overlap detection, which was intentionally deferred.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
