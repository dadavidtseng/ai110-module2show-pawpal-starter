"""PawPal+ CLI demo — verifies the backend logic in the terminal."""

from datetime import date

import sys
import io

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    CATEGORY_EMOJI, PRIORITY_INDICATOR, PRIORITY_WEIGHT,
)

# Force UTF-8 output on Windows to support emojis
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def fmt_task(task: Task, index: int | None = None) -> str:
    """Format a single task line with emojis and indicators."""
    cat = CATEGORY_EMOJI.get(task.category, "📋")
    pri = PRIORITY_INDICATOR.get(task.priority, " ")
    status = "✅" if task.completed else "⬜"
    time_str = task.scheduled_time or "--:--"
    prefix = f"  {index:2d}." if index else "     "
    return f"{prefix} {status} {pri} {cat}  {time_str}  {task.title:25s} {task.duration_minutes:3d} min"


def main() -> None:
    # --- Owner setup ---
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Pets ---
    mochi = Pet(name="Mochi", species="dog", age=3)
    whiskers = Pet(name="Whiskers", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Tasks for Mochi (dog) — added out of order to test sorting ---
    mochi.add_task(Task("Fetch in the park", 25, priority="low",
                        category="enrichment", scheduled_time="10:00"))
    mochi.add_task(Task("Morning walk", 30, priority="high",
                        category="walk", frequency="daily",
                        scheduled_time="07:00", due_date=date.today()))
    mochi.add_task(Task("Breakfast", 10, priority="high",
                        category="feeding", scheduled_time="08:00"))
    mochi.add_task(Task("Flea medication", 5, priority="medium",
                        category="meds", frequency="weekly",
                        scheduled_time="08:00"))

    # --- Tasks for Whiskers (cat) ---
    whiskers.add_task(Task("Wet food breakfast", 10, priority="high",
                           category="feeding", scheduled_time="08:00"))
    whiskers.add_task(Task("Brush coat", 15, priority="medium",
                           category="grooming", scheduled_time="09:00"))
    whiskers.add_task(Task("Laser pointer play", 20, priority="low",
                           category="enrichment", scheduled_time="10:00"))

    # --- 1. Priority-based schedule ---
    section(f"PawPal+ Daily Schedule for {owner.name} (priority-based)")
    schedule = Scheduler.generate_schedule(owner)
    print()
    for i, t in enumerate(schedule.tasks, 1):
        print(fmt_task(t, i))
    remaining = schedule.available_minutes - schedule.total_minutes
    print(f"\n  Time: {schedule.total_minutes}/{schedule.available_minutes} min used, {remaining} min free")

    # Skipped
    scheduled_titles = {t.title for t in schedule.tasks}
    skipped = [t for t in owner.get_all_tasks() if t.title not in scheduled_titles]
    if skipped:
        print("\n  Skipped (not enough time):")
        for t in skipped:
            pri = PRIORITY_INDICATOR.get(t.priority, " ")
            print(f"    {pri}  {t.title} ({t.duration_minutes} min)")

    # --- 2. Weighted schedule ---
    section(f"Weighted Schedule for {owner.name} (score-based)")
    w_schedule = Scheduler.generate_weighted_schedule(owner)
    print()
    for i, t in enumerate(w_schedule.tasks, 1):
        score = Scheduler.weighted_score(t)
        print(f"{fmt_task(t, i)}  (score {score:.1f})")

    # --- 3. Sort by scheduled time ---
    section("Tasks Sorted by Time")
    all_tasks = owner.get_all_tasks()
    for t in Scheduler.sort_by_time(all_tasks):
        print(fmt_task(t))

    # --- 4. Filter by pet ---
    section("Mochi's Tasks Only")
    for t in Scheduler.filter_by_pet(owner, "Mochi"):
        print(fmt_task(t))

    # --- 5. Filter by category ---
    section("Feeding Tasks Across All Pets")
    for t in Scheduler.filter_by_category(all_tasks, "feeding"):
        print(fmt_task(t))

    # --- 6. Conflict detection ---
    section("Conflict Detection")
    conflicts = Scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("  No conflicts detected.")

    # --- 7. Next available slot ---
    section("Next Available Slot")
    slot = Scheduler.find_next_slot(owner, 30)
    print(f"  Next free 15-min slot: {slot}")

    # --- 8. Recurring task demo ---
    section("Recurring Tasks Demo")
    print(f"  Mochi task count before: {len(mochi.tasks)}")
    next_task = mochi.mark_task_complete("Morning walk")
    print(f"  Mochi task count after:  {len(mochi.tasks)}")
    if next_task:
        print(f"  Auto-created: '{next_task.title}' due {next_task.due_date}")

    # --- 9. JSON persistence demo ---
    section("JSON Persistence")
    owner.save_to_json("data.json")
    print("  Saved to data.json")
    loaded = Owner.load_from_json("data.json")
    if loaded:
        total = sum(len(p.tasks) for p in loaded.pets)
        print(f"  Loaded: {loaded.name}, {len(loaded.pets)} pets, {total} tasks")

    print()


if __name__ == "__main__":
    main()
