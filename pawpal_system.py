"""PawPal+ system logic — classes for pet care scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
import json


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, grooming, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", "high"
    category: str = "general"  # walk, feeding, meds, grooming, enrichment, general
    frequency: str = "daily"  # daily, weekly, as_needed
    completed: bool = False
    scheduled_time: str = ""  # "HH:MM" format, e.g. "08:30"
    due_date: date | None = None  # when this task is due

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False

    def next_occurrence(self) -> Task | None:
        """Create the next occurrence for a recurring task.

        Returns a new Task with an updated due_date, or None if the task
        is not recurring (frequency == 'as_needed').
        """
        if self.frequency == "as_needed":
            return None

        delta = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        base = self.due_date if self.due_date else date.today()

        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            frequency=self.frequency,
            scheduled_time=self.scheduled_time,
            due_date=base + delta,
        )

    def to_dict(self) -> dict:
        """Serialise this task to a JSON-safe dictionary."""
        return {
            "title": self.title,
            "duration_minutes": self.duration_minutes,
            "priority": self.priority,
            "category": self.category,
            "frequency": self.frequency,
            "completed": self.completed,
            "scheduled_time": self.scheduled_time,
            "due_date": self.due_date.isoformat() if self.due_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialise a Task from a dictionary."""
        due = data.get("due_date")
        return cls(
            title=data["title"],
            duration_minutes=data["duration_minutes"],
            priority=data.get("priority", "medium"),
            category=data.get("category", "general"),
            frequency=data.get("frequency", "daily"),
            completed=data.get("completed", False),
            scheduled_time=data.get("scheduled_time", ""),
            due_date=date.fromisoformat(due) if due else None,
        )


@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str
    species: str = "dog"
    age: int = 1
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet and tag it with the pet's name."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def pending_tasks(self) -> list[Task]:
        """Return only tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def mark_task_complete(self, title: str) -> Task | None:
        """Mark a task complete and auto-create its next occurrence if recurring.

        Returns the newly created recurring task, or None.
        """
        for task in self.tasks:
            if task.title == title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    self.tasks.append(next_task)
                return next_task
        return None

    def to_dict(self) -> dict:
        """Serialise this pet to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Pet:
        """Deserialise a Pet from a dictionary."""
        pet = cls(name=data["name"], species=data.get("species", "dog"), age=data.get("age", 1))
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


@dataclass
class Owner:
    """The pet owner / app user."""

    name: str
    available_minutes: int = 120  # daily time budget
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Gather every task across all pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_pending_tasks(self) -> list[Task]:
        """Gather only incomplete tasks across all pets."""
        return [task for pet in self.pets for task in pet.pending_tasks()]

    def to_dict(self) -> dict:
        """Serialise this owner to a JSON-safe dictionary."""
        return {
            "name": self.name,
            "available_minutes": self.available_minutes,
            "pets": [p.to_dict() for p in self.pets],
        }

    @classmethod
    def from_dict(cls, data: dict) -> Owner:
        """Deserialise an Owner from a dictionary."""
        owner = cls(name=data["name"], available_minutes=data.get("available_minutes", 120))
        owner.pets = [Pet.from_dict(p) for p in data.get("pets", [])]
        return owner

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Persist owner, pets, and tasks to a JSON file."""
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> Owner | None:
        """Load an Owner from a JSON file. Returns None if file doesn't exist."""
        p = Path(path)
        if not p.exists():
            return None
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls.from_dict(data)


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}

# Category emoji mapping for display
CATEGORY_EMOJI = {
    "walk": "🚶",
    "feeding": "🍽️",
    "meds": "💊",
    "grooming": "✂️",
    "enrichment": "🎾",
    "general": "📋",
}

PRIORITY_INDICATOR = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}


@dataclass
class Schedule:
    """The result of running the scheduler — an ordered daily plan."""

    tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0
    available_minutes: int = 0

    def explain(self) -> str:
        """Return a human-readable explanation of the schedule."""
        if not self.tasks:
            return "No tasks scheduled — nothing to do today!"

        lines = [
            f"Daily plan ({self.total_minutes} min used "
            f"of {self.available_minutes} min available):\n"
        ]
        for i, task in enumerate(self.tasks, 1):
            lines.append(
                f"  {i}. {task.title} — {task.duration_minutes} min "
                f"[{task.priority} priority, {task.category}]"
            )

        remaining = self.available_minutes - self.total_minutes
        if remaining > 0:
            lines.append(f"\n  Free time remaining: {remaining} min")
        return "\n".join(lines)


class Scheduler:
    """Generates a daily Schedule from an Owner's tasks and time budget."""

    # -- Core scheduling -------------------------------------------------------

    @staticmethod
    def generate_schedule(owner: Owner) -> Schedule:
        """Build an optimised daily plan.

        Strategy:
        1. Collect all pending (incomplete) tasks from all pets.
        2. Sort by priority (high -> medium -> low).
        3. Greedily fit tasks into the available time budget.
        """
        pending = owner.get_pending_tasks()
        prioritized = Scheduler._prioritize(pending)
        selected = Scheduler._fit_to_time(prioritized, owner.available_minutes)
        total = sum(t.duration_minutes for t in selected)

        return Schedule(
            tasks=selected,
            total_minutes=total,
            available_minutes=owner.available_minutes,
        )

    # -- Sorting ---------------------------------------------------------------

    @staticmethod
    def sort_by_time(tasks: list[Task]) -> list[Task]:
        """Sort tasks by scheduled_time in HH:MM format (earliest first).

        Tasks without a scheduled_time are placed at the end.
        """
        def _time_key(t: Task) -> tuple[int, int]:
            if not t.scheduled_time:
                return (99, 99)  # push to end
            parts = t.scheduled_time.split(":")
            return (int(parts[0]), int(parts[1]))

        return sorted(tasks, key=_time_key)

    # -- Filtering -------------------------------------------------------------

    @staticmethod
    def filter_by_pet(owner: Owner, pet_name: str) -> list[Task]:
        """Return all tasks belonging to a specific pet."""
        for pet in owner.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []

    @staticmethod
    def filter_by_status(tasks: list[Task], *, completed: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in tasks if t.completed == completed]

    @staticmethod
    def filter_by_category(tasks: list[Task], category: str) -> list[Task]:
        """Return tasks matching a specific category."""
        return [t for t in tasks if t.category == category]

    # -- Conflict detection ----------------------------------------------------

    @staticmethod
    def detect_conflicts(owner: Owner) -> list[str]:
        """Detect scheduling conflicts — tasks with overlapping times.

        A conflict exists when two pending tasks (across any pets) share the
        same scheduled_time.  Returns a list of human-readable warning strings.

        Limitation: only checks for exact time matches, not duration-based
        overlap. This is a deliberate simplicity tradeoff (see reflection.md).
        """
        time_map: dict[str, list[tuple[str, str]]] = {}  # time -> [(title, pet)]
        for pet in owner.pets:
            for task in pet.pending_tasks():
                if task.scheduled_time:
                    entry = (task.title, pet.name)
                    time_map.setdefault(task.scheduled_time, []).append(entry)

        warnings: list[str] = []
        for time_slot, entries in sorted(time_map.items()):
            if len(entries) > 1:
                names = ", ".join(
                    f"'{title}' ({pet})" for title, pet in entries
                )
                warnings.append(
                    f"Conflict at {time_slot}: {names}"
                )
        return warnings

    # -- Advanced: next available slot -----------------------------------------

    @staticmethod
    def find_next_slot(
        owner: Owner, duration_minutes: int, start_hour: int = 7, end_hour: int = 21,
    ) -> str:
        """Find the next available time slot that doesn't conflict with existing tasks.

        Scans from start_hour to end_hour in 15-minute increments and returns
        the first HH:MM slot where no pending task is scheduled. This is a
        simple "first-fit" approach — it doesn't account for task durations
        overlapping, only exact start-time collisions.

        Returns "" if no slot is available.
        """
        occupied: set[str] = set()
        for pet in owner.pets:
            for task in pet.pending_tasks():
                if task.scheduled_time:
                    occupied.add(task.scheduled_time)

        for hour in range(start_hour, end_hour):
            for minute in (0, 15, 30, 45):
                slot = f"{hour:02d}:{minute:02d}"
                if slot not in occupied:
                    return slot
        return ""

    # -- Advanced: weighted priority scoring -----------------------------------

    @staticmethod
    def weighted_score(task: Task) -> float:
        """Compute a weighted priority score for ranking tasks.

        Score = priority_weight * (duration_factor + recurrence_bonus).
        Higher score = more important to schedule.
        """
        weight = PRIORITY_WEIGHT.get(task.priority, 1)
        # Shorter tasks get a slight bonus (efficiency factor)
        duration_factor = max(1, 60 - task.duration_minutes) / 60
        # Recurring tasks get a bonus since skipping them has compounding effects
        recurrence_bonus = 0.2 if task.frequency != "as_needed" else 0
        return weight * (duration_factor + recurrence_bonus)

    @staticmethod
    def generate_weighted_schedule(owner: Owner) -> Schedule:
        """Build a schedule using weighted scoring instead of simple priority order.

        Tasks are ranked by weighted_score (descending) and greedily fitted
        into the time budget. This produces subtly different results from
        generate_schedule when recurring short tasks compete with one-off long
        tasks.
        """
        pending = owner.get_pending_tasks()
        ranked = sorted(pending, key=Scheduler.weighted_score, reverse=True)
        selected = Scheduler._fit_to_time(ranked, owner.available_minutes)
        total = sum(t.duration_minutes for t in selected)

        return Schedule(
            tasks=selected,
            total_minutes=total,
            available_minutes=owner.available_minutes,
        )

    # -- Private helpers -------------------------------------------------------

    @staticmethod
    def _prioritize(tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high first), then by duration (shorter first)."""
        return sorted(
            tasks,
            key=lambda t: (PRIORITY_ORDER.get(t.priority, 1), t.duration_minutes),
        )

    @staticmethod
    def _fit_to_time(tasks: list[Task], available_minutes: int) -> list[Task]:
        """Greedily select tasks that fit within the time budget."""
        selected: list[Task] = []
        remaining = available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected
