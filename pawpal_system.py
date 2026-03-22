"""PawPal+ system logic — classes for pet care scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single pet care activity."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", "high"
    category: str = "general"  # walk, feeding, meds, grooming, enrichment, general


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


# ---------------------------------------------------------------------------
# Scheduling
# ---------------------------------------------------------------------------

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Schedule:
    """The result of running the scheduler — an ordered daily plan."""

    tasks: list[Task] = field(default_factory=list)
    total_minutes: int = 0

    def explain(self) -> str:
        """Return a human-readable explanation of the schedule."""
        if not self.tasks:
            return "No tasks scheduled."

        lines = [f"Daily plan ({self.total_minutes} min total):\n"]
        for i, task in enumerate(self.tasks, 1):
            lines.append(
                f"  {i}. {task.title} — {task.duration_minutes} min "
                f"[{task.priority} priority, {task.category}]"
            )
        return "\n".join(lines)


class Scheduler:
    """Generates a daily Schedule from an Owner's tasks and time budget."""

    @staticmethod
    def generate_schedule(owner: Owner) -> Schedule:
        """Build an optimised daily plan.

        Strategy:
        1. Collect all tasks from all pets.
        2. Sort by priority (high → medium → low).
        3. Greedily fit tasks into the available time budget.
        """
        # TODO: implement scheduling logic
        pass

    # -- private helpers -----------------------------------------------------

    @staticmethod
    def _prioritize(tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high first)."""
        # TODO: implement
        pass

    @staticmethod
    def _fit_to_time(tasks: list[Task], available_minutes: int) -> list[Task]:
        """Select tasks that fit within the time budget."""
        # TODO: implement
        pass
