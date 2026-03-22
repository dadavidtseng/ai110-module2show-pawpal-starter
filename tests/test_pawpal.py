"""Tests for PawPal+ core logic."""

from datetime import date, timedelta

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

    def test_next_occurrence_daily(self):
        today = date.today()
        task = Task("Walk", 30, frequency="daily", due_date=today)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == today + timedelta(days=1)
        assert nxt.completed is False

    def test_next_occurrence_weekly(self):
        today = date.today()
        task = Task("Meds", 5, frequency="weekly", due_date=today)
        nxt = task.next_occurrence()
        assert nxt is not None
        assert nxt.due_date == today + timedelta(weeks=1)

    def test_next_occurrence_as_needed_returns_none(self):
        task = Task("Bath", 60, frequency="as_needed")
        assert task.next_occurrence() is None


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

    def test_mark_task_complete_creates_recurring(self):
        pet = Pet("Mochi")
        pet.add_task(Task("Walk", 30, frequency="daily", due_date=date.today()))
        assert len(pet.tasks) == 1
        next_task = pet.mark_task_complete("Walk")
        assert next_task is not None
        assert len(pet.tasks) == 2  # original (completed) + new occurrence
        assert pet.tasks[0].completed is True
        assert pet.tasks[1].completed is False

    def test_mark_task_complete_no_recurring_for_as_needed(self):
        pet = Pet("Mochi")
        pet.add_task(Task("Bath", 60, frequency="as_needed"))
        next_task = pet.mark_task_complete("Bath")
        assert next_task is None
        assert len(pet.tasks) == 1  # no new task created


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


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

class TestSortByTime:
    """Tests for time-based sorting."""

    def test_sorts_by_scheduled_time(self):
        tasks = [
            Task("Late", 10, scheduled_time="10:00"),
            Task("Early", 10, scheduled_time="07:30"),
            Task("Mid", 10, scheduled_time="09:00"),
        ]
        sorted_tasks = Scheduler.sort_by_time(tasks)
        assert [t.title for t in sorted_tasks] == ["Early", "Mid", "Late"]

    def test_no_time_pushed_to_end(self):
        tasks = [
            Task("Timed", 10, scheduled_time="08:00"),
            Task("Untimed", 10, scheduled_time=""),
        ]
        sorted_tasks = Scheduler.sort_by_time(tasks)
        assert sorted_tasks[0].title == "Timed"
        assert sorted_tasks[1].title == "Untimed"


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------

class TestFiltering:
    """Tests for filtering methods."""

    def _make_owner(self) -> Owner:
        owner = Owner("Test")
        dog = Pet("Buddy")
        cat = Pet("Whiskers")
        dog.add_task(Task("Walk", 30, category="walk"))
        dog.add_task(Task("Feed Dog", 10, category="feeding"))
        cat.add_task(Task("Feed Cat", 10, category="feeding"))
        owner.add_pet(dog)
        owner.add_pet(cat)
        return owner

    def test_filter_by_pet(self):
        owner = self._make_owner()
        buddy_tasks = Scheduler.filter_by_pet(owner, "Buddy")
        assert len(buddy_tasks) == 2
        assert all(t.title != "Feed Cat" for t in buddy_tasks)

    def test_filter_by_pet_not_found(self):
        owner = self._make_owner()
        assert Scheduler.filter_by_pet(owner, "Ghost") == []

    def test_filter_by_status(self):
        tasks = [Task("A", 10), Task("B", 10)]
        tasks[0].mark_complete()
        assert len(Scheduler.filter_by_status(tasks, completed=True)) == 1
        assert len(Scheduler.filter_by_status(tasks, completed=False)) == 1

    def test_filter_by_category(self):
        owner = self._make_owner()
        feeding = Scheduler.filter_by_category(owner.get_all_tasks(), "feeding")
        assert len(feeding) == 2


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

class TestConflictDetection:
    """Tests for scheduling conflict detection."""

    def test_detects_same_time_conflict(self):
        owner = Owner("Test")
        pet = Pet("Buddy")
        pet.add_task(Task("Walk", 30, scheduled_time="08:00"))
        pet.add_task(Task("Feed", 10, scheduled_time="08:00"))
        owner.add_pet(pet)

        conflicts = Scheduler.detect_conflicts(owner)
        assert len(conflicts) == 1
        assert "08:00" in conflicts[0]

    def test_cross_pet_conflict(self):
        owner = Owner("Test")
        dog = Pet("Buddy")
        cat = Pet("Whiskers")
        dog.add_task(Task("Walk Dog", 30, scheduled_time="09:00"))
        cat.add_task(Task("Feed Cat", 10, scheduled_time="09:00"))
        owner.add_pet(dog)
        owner.add_pet(cat)

        conflicts = Scheduler.detect_conflicts(owner)
        assert len(conflicts) == 1
        assert "Buddy" in conflicts[0]
        assert "Whiskers" in conflicts[0]

    def test_no_conflict_different_times(self):
        owner = Owner("Test")
        pet = Pet("Buddy")
        pet.add_task(Task("Walk", 30, scheduled_time="07:00"))
        pet.add_task(Task("Feed", 10, scheduled_time="08:00"))
        owner.add_pet(pet)

        assert Scheduler.detect_conflicts(owner) == []

    def test_completed_tasks_ignored(self):
        owner = Owner("Test")
        pet = Pet("Buddy")
        t1 = Task("Walk", 30, scheduled_time="08:00")
        t2 = Task("Feed", 10, scheduled_time="08:00")
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        owner.add_pet(pet)

        assert Scheduler.detect_conflicts(owner) == []
