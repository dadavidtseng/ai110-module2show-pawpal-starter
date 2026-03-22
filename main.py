"""PawPal+ CLI demo — verifies the backend logic in the terminal."""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def section(title: str) -> None:
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print("=" * 50)


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
                        scheduled_time="08:00"))  # same time as Breakfast!

    # --- Tasks for Whiskers (cat) ---
    whiskers.add_task(Task("Wet food breakfast", 10, priority="high",
                           category="feeding", scheduled_time="08:00"))
    whiskers.add_task(Task("Brush coat", 15, priority="medium",
                           category="grooming", scheduled_time="09:00"))
    whiskers.add_task(Task("Laser pointer play", 20, priority="low",
                           category="enrichment", scheduled_time="10:00"))

    # --- 1. Generate and display schedule ---
    section(f"PawPal+ Daily Schedule for {owner.name}")
    schedule = Scheduler.generate_schedule(owner)
    print()
    print(schedule.explain())

    # Show skipped tasks
    scheduled_titles = {t.title for t in schedule.tasks}
    skipped = [t for t in owner.get_all_tasks() if t.title not in scheduled_titles]
    if skipped:
        print("\n  Skipped (not enough time):")
        for t in skipped:
            print(f"    - {t.title} ({t.duration_minutes} min, {t.priority})")

    # --- 2. Sort by scheduled time ---
    section("Tasks Sorted by Time")
    all_tasks = owner.get_all_tasks()
    for t in Scheduler.sort_by_time(all_tasks):
        status = "done" if t.completed else "pending"
        print(f"  {t.scheduled_time or '--:--'}  {t.title:25s} [{status}]")

    # --- 3. Filter by pet ---
    section("Mochi's Tasks Only")
    for t in Scheduler.filter_by_pet(owner, "Mochi"):
        print(f"  - {t.title} ({t.duration_minutes} min)")

    # --- 4. Filter by category ---
    section("Feeding Tasks Across All Pets")
    for t in Scheduler.filter_by_category(all_tasks, "feeding"):
        print(f"  - {t.title}")

    # --- 5. Conflict detection ---
    section("Conflict Detection")
    conflicts = Scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts detected.")

    # --- 6. Recurring task demo ---
    section("Recurring Tasks Demo")
    print(f"  Mochi task count before completion: {len(mochi.tasks)}")
    next_task = mochi.mark_task_complete("Morning walk")
    print(f"  Mochi task count after completing 'Morning walk': {len(mochi.tasks)}")
    if next_task:
        print(f"  Auto-created: '{next_task.title}' due {next_task.due_date}")

    print()


if __name__ == "__main__":
    main()
