"""Tests for PawPal+ core logic."""

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Task tests
# ---------------------------------------------------------------------------

class TestTask:
    """Tests for Task completion behaviour."""

    def test_mark_complete_changes_status(self):
        task = Task("Walk", 30, priority="high")
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_mark_incomplete_resets_status(self):
        task = Task("Walk", 30)
        task.mark_complete()
        task.mark_incomplete()
        assert task.completed is False


# ---------------------------------------------------------------------------
# Pet tests
# ---------------------------------------------------------------------------

class TestPet:
    """Tests for Pet task management."""

    def test_add_task_increases_count(self):
        pet = Pet("Mochi", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task("Walk", 30))
        assert len(pet.tasks) == 1
        pet.add_task(Task("Feed", 10))
        assert len(pet.tasks) == 2

    def test_remove_task_by_title(self):
        pet = Pet("Mochi")
        pet.add_task(Task("Walk", 30))
        pet.add_task(Task("Feed", 10))
        pet.remove_task("Walk")
        assert len(pet.tasks) == 1
        assert pet.tasks[0].title == "Feed"

    def test_pending_tasks_excludes_completed(self):
        pet = Pet("Mochi")
        t1 = Task("Walk", 30)
        t2 = Task("Feed", 10)
        t2.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        assert len(pet.pending_tasks()) == 1


# ---------------------------------------------------------------------------
# Scheduler tests
# ---------------------------------------------------------------------------

class TestScheduler:
    """Tests for scheduling logic."""

    def _make_owner_with_tasks(self, minutes: int = 120) -> Owner:
        owner = Owner("Test", available_minutes=minutes)
        pet = Pet("Buddy")
        pet.add_task(Task("Walk", 30, priority="high", category="walk"))
        pet.add_task(Task("Feed", 10, priority="high", category="feeding"))
        pet.add_task(Task("Play", 25, priority="low", category="enrichment"))
        pet.add_task(Task("Meds", 5, priority="medium", category="meds"))
        owner.add_pet(pet)
        return owner

    def test_high_priority_scheduled_first(self):
        owner = self._make_owner_with_tasks()
        schedule = Scheduler.generate_schedule(owner)
        priorities = [t.priority for t in schedule.tasks]
        # high tasks should appear before medium/low
        high_indices = [i for i, p in enumerate(priorities) if p == "high"]
        other_indices = [i for i, p in enumerate(priorities) if p != "high"]
        if high_indices and other_indices:
            assert max(high_indices) < min(other_indices)

    def test_respects_time_budget(self):
        owner = self._make_owner_with_tasks(minutes=40)
        schedule = Scheduler.generate_schedule(owner)
        assert schedule.total_minutes <= 40

    def test_skips_completed_tasks(self):
        owner = self._make_owner_with_tasks()
        # mark walk as done
        owner.pets[0].tasks[0].mark_complete()
        schedule = Scheduler.generate_schedule(owner)
        titles = [t.title for t in schedule.tasks]
        assert "Walk" not in titles

    def test_empty_tasks_produce_empty_schedule(self):
        owner = Owner("Empty", available_minutes=60)
        owner.add_pet(Pet("Solo"))
        schedule = Scheduler.generate_schedule(owner)
        assert len(schedule.tasks) == 0
        assert schedule.total_minutes == 0

    def test_explain_returns_string(self):
        owner = self._make_owner_with_tasks()
        schedule = Scheduler.generate_schedule(owner)
        explanation = schedule.explain()
        assert isinstance(explanation, str)
        assert "Daily plan" in explanation
