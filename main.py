"""PawPal+ CLI demo — verifies the backend logic in the terminal."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main() -> None:
    # --- Owner setup ---
    owner = Owner(name="Jordan", available_minutes=90)

    # --- Pets ---
    mochi = Pet(name="Mochi", species="dog", age=3)
    whiskers = Pet(name="Whiskers", species="cat", age=5)

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Tasks for Mochi (dog) ---
    mochi.add_task(Task("Morning walk", 30, priority="high", category="walk"))
    mochi.add_task(Task("Breakfast", 10, priority="high", category="feeding"))
    mochi.add_task(Task("Flea medication", 5, priority="medium", category="meds"))
    mochi.add_task(Task("Fetch in the park", 25, priority="low", category="enrichment"))

    # --- Tasks for Whiskers (cat) ---
    whiskers.add_task(Task("Wet food breakfast", 10, priority="high", category="feeding"))
    whiskers.add_task(Task("Brush coat", 15, priority="medium", category="grooming"))
    whiskers.add_task(Task("Laser pointer play", 20, priority="low", category="enrichment"))

    # --- Generate and display schedule ---
    schedule = Scheduler.generate_schedule(owner)

    print("=" * 50)
    print(f"  PawPal+ Daily Schedule for {owner.name}")
    print("=" * 50)
    print()
    print(schedule.explain())
    print()

    # --- Show what didn't make the cut ---
    scheduled_titles = {t.title for t in schedule.tasks}
    skipped = [t for t in owner.get_all_tasks() if t.title not in scheduled_titles]
    if skipped:
        print("  Skipped (not enough time):")
        for t in skipped:
            print(f"    - {t.title} ({t.duration_minutes} min, {t.priority})")
    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
