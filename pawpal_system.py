"""PawPal+ system logic — classes for pet care scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task to incomplete."""
        self.completed = False


@dataclass
class Pet:
    """A pet belonging to an owner."""

    name: str
    species: str = "dog"
    age: int = 1
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove a task by title."""
        self.tasks = [t for t in self.tasks if t.title != title]

    def pending_tasks(self) -> list[Task]:
        """Return only tasks that are not yet completed."""
        return [t for t in self.tasks if not t.completed]


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


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


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
