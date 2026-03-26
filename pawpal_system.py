from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    id: str
    name: str
    description: str
    scheduled_time: time
    frequency_days: int = 0
    status: TaskStatus = TaskStatus.PENDING
    next_due_date: date = field(default_factory=date.today)

    def update_name(self, name: str) -> None:
        """Replaces the task's name."""
        self.name = name

    def update_description(self, description: str) -> None:
        """Replaces the task's description."""
        self.description = description

    def update_scheduled_time(self, scheduled_time: time) -> None:
        """Replaces the time of day this task is scheduled for."""
        self.scheduled_time = scheduled_time

    def update_frequency(self, frequency_days: int) -> None:
        """Sets how often the task recurs in days. Use 0 for non-recurring tasks."""
        self.frequency_days = frequency_days

    def update_status(self, status: TaskStatus) -> None:
        """Sets the task's completion status."""
        self.status = status


@dataclass
class Pet:
    id: str
    name: str
    animal_type: str
    last_vet_visit: date = None
    tasks: list[Task] = field(default_factory=list)

    def update_last_vet_visit(self, new_date: date) -> None:
        """Records the date of the pet's most recent veterinarian visit."""
        self.last_vet_visit = new_date

    def add_task(self, task: Task) -> None:
        """Appends a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Removes the task matching task_id. Does nothing if the id is not found."""
        self.tasks[:] = [t for t in self.tasks if t.id != task_id]

    def update_task(
        self,
        task_id: str,
        name: str = None,
        description: str = None,
        scheduled_time: time = None,
        frequency_days: int = None,
        status: TaskStatus = None,
    ) -> None:
        """Updates any combination of fields on the task matching task_id. Does nothing if the id is not found."""
        for task in self.tasks:
            if task.id == task_id:
                if name is not None:           task.update_name(name)
                if description is not None:    task.update_description(description)
                if scheduled_time is not None: task.update_scheduled_time(scheduled_time)
                if frequency_days is not None: task.update_frequency(frequency_days)
                if status is not None:         task.update_status(status)
                break


@dataclass
class Scheduler:
    pets: list[Pet] = field(default_factory=list)

    # --- Pet management ---

    def add_pet(self, pet: Pet) -> None:
        """Registers a pet with the scheduler so its tasks are included in all queries."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Unregisters the pet matching pet_id from the scheduler."""
        self.pets[:] = [p for p in self.pets if p.id != pet_id]

    # --- Task retrieval ---

    def _find_task(self, pet_id: str, task_id: str) -> Task | None:
        """Returns the Task matching task_id under the given pet, or None if not found."""
        for pet in self.pets:
            if pet.id == pet_id:
                return next((t for t in pet.tasks if t.id == task_id), None)
        return None

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns every task across all managed pets as (pet, task) pairs."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Returns all tasks belonging to a specific pet, or an empty list if the pet is not found."""
        for pet in self.pets:
            if pet.id == pet_id:
                return list(pet.tasks)
        return []

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all PENDING tasks across all pets as (pet, task) pairs."""
        return [
            (pet, task) for pet, task in self.get_all_tasks()
            if task.status == TaskStatus.PENDING
        ]

    def get_tasks_due_today_or_earlier(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks whose next_due_date is today or in the past, across all pets."""
        return [
            (pet, task) for pet, task in self.get_all_tasks()
            if date.today() >= task.next_due_date
        ]

    # --- Task organization ---

    def get_tasks_sorted_by_time(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks across all pets sorted ascending by scheduled_time."""
        return sorted(self.get_all_tasks(), key=lambda pair: pair[1].scheduled_time)

    # --- Task management ---

    def mark_task_complete(self, pet_id: str, task_id: str) -> None:
        """Marks a task COMPLETED. If recurring, advances next_due_date by frequency_days."""
        task = self._find_task(pet_id, task_id)
        if task is None:
            return
        task.update_status(TaskStatus.COMPLETED)
        if task.frequency_days > 0:
            task.next_due_date += timedelta(days=task.frequency_days)


@dataclass
class Owner:
    id: str
    pets: list[Pet] = field(default_factory=list)
    scheduler: Scheduler = field(init=False)

    def __post_init__(self) -> None:
        """Initializes the scheduler with a shared reference to the owner's pet list."""
        self.scheduler = Scheduler(pets=self.pets)

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner's list, making it automatically visible to the scheduler."""
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        """Removes the pet matching pet_id from the owner's list and the scheduler simultaneously."""
        self.pets[:] = [p for p in self.pets if p.id != pet_id]
