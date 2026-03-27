from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum
from itertools import groupby


def _validated_str(value: object, field_name: str, max_length: int = 500) -> str:
    """Raises ValueError if value is not a string or exceeds max_length."""
    if not isinstance(value, str):
        raise ValueError(f"'{field_name}' must be a string, got {type(value).__name__}")
    if len(value) > max_length:
        raise ValueError(f"'{field_name}' exceeds the {max_length}-character limit")
    return value


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

    def get_pending_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Returns all PENDING tasks for a specific pet, or an empty list if the pet is not found."""
        return [t for t in self.get_tasks_for_pet(pet_id) if t.status == TaskStatus.PENDING]

    def get_completed_tasks_for_pet(self, pet_id: str) -> list[Task]:
        """Returns all COMPLETED tasks for a specific pet, or an empty list if the pet is not found."""
        return [t for t in self.get_tasks_for_pet(pet_id) if t.status == TaskStatus.COMPLETED]

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all PENDING tasks across all pets as (pet, task) pairs."""
        return [
            (pet, task) for pet, task in self.get_all_tasks()
            if task.status == TaskStatus.PENDING
        ]

    def get_completed_tasks(self) -> list[tuple[Pet, Task]]:
        """Returns all COMPLETED tasks across all pets as (pet, task) pairs."""
        return [
            (pet, task) for pet, task in self.get_all_tasks()
            if task.status == TaskStatus.COMPLETED
        ]

    def get_tasks_due_today_or_earlier(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks whose next_due_date is today or in the past, across all pets."""
        today = date.today()
        return [(pet, task) for pet, task in self.get_all_tasks() if today >= task.next_due_date]

    def get_tasks_due_today_or_earlier_for_pet(self, pet_id: str) -> list[Task]:
        """Returns all tasks whose next_due_date is today or in the past for a specific pet."""
        today = date.today()
        return [t for t in self.get_tasks_for_pet(pet_id) if today >= t.next_due_date]

    # --- Task organization ---

    def get_tasks_sorted_by_time(self) -> list[tuple[Pet, Task]]:
        """Returns all tasks across all pets sorted ascending by scheduled_time."""
        return sorted(self.get_all_tasks(), key=lambda pair: pair[1].scheduled_time)

    def get_scheduling_conflicts(self) -> list[str]:
        """Returns a warning message for each time slot that has more than one task scheduled across any pets."""
        warnings = []
        sorted_tasks = sorted(self.get_all_tasks(), key=lambda pair: pair[1].scheduled_time)
        for scheduled_time, group in groupby(sorted_tasks, key=lambda pair: pair[1].scheduled_time):
            pairs = list(group)
            if len(pairs) > 1:
                labels = ", ".join(f"'{t.name}' ({p.name})" for p, t in pairs)
                warnings.append(f"Conflict at {scheduled_time.strftime('%H:%M')}: {labels}")
        return warnings

    # --- Task management ---

    def mark_task_complete(self, pet_id: str, task_id: str) -> None:
        """Marks a task COMPLETED and, if recurring, adds a new PENDING task for the next occurrence."""
        for pet in self.pets:
            if pet.id == pet_id:
                task = next((t for t in pet.tasks if t.id == task_id), None)
                if task is None:
                    return
                task.update_status(TaskStatus.COMPLETED)
                if task.frequency_days > 0:
                    pet.add_task(Task(
                        id=str(uuid.uuid4()),
                        name=task.name,
                        description=task.description,
                        scheduled_time=task.scheduled_time,
                        frequency_days=task.frequency_days,
                        next_due_date=task.next_due_date + timedelta(days=task.frequency_days),
                    ))
                return


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

    # --- Persistence ---

    def to_dict(self) -> dict:
        """Serializes the owner and all pets and tasks to a plain dictionary."""
        return {
            "id": self.id,
            "pets": [
                {
                    "id": p.id,
                    "name": p.name,
                    "animal_type": p.animal_type,
                    "last_vet_visit": str(p.last_vet_visit) if p.last_vet_visit else None,
                    "tasks": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "description": t.description,
                            "scheduled_time": t.scheduled_time.strftime("%H:%M"),
                            "frequency_days": t.frequency_days,
                            "status": t.status.value,
                            "next_due_date": str(t.next_due_date),
                        }
                        for t in p.tasks
                    ],
                }
                for p in self.pets
            ],
        }

    def to_json(self) -> str:
        """Serializes the owner to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def save_to_json(self, filepath: str) -> None:
        """Writes the owner's data to a JSON file at the given path."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_dict(cls, data: object) -> Owner:
        """Deserializes an Owner from a plain dictionary, validating every field."""
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")

        owner_id = _validated_str(data.get("id"), "owner.id")

        pets_raw = data.get("pets", [])
        if not isinstance(pets_raw, list):
            raise ValueError("'pets' must be a list")

        owner = cls(id=owner_id)

        for i, pet_raw in enumerate(pets_raw):
            if not isinstance(pet_raw, dict):
                raise ValueError(f"pets[{i}] must be an object")

            pet_id      = _validated_str(pet_raw.get("id"),          f"pets[{i}].id")
            pet_name    = _validated_str(pet_raw.get("name"),        f"pets[{i}].name")
            animal_type = _validated_str(pet_raw.get("animal_type"), f"pets[{i}].animal_type")

            last_vet_raw = pet_raw.get("last_vet_visit")
            if last_vet_raw is not None:
                try:
                    last_vet_visit = date.fromisoformat(_validated_str(last_vet_raw, f"pets[{i}].last_vet_visit"))
                except ValueError:
                    raise ValueError(f"pets[{i}].last_vet_visit is not a valid YYYY-MM-DD date")
            else:
                last_vet_visit = None

            pet = Pet(id=pet_id, name=pet_name, animal_type=animal_type, last_vet_visit=last_vet_visit)

            tasks_raw = pet_raw.get("tasks", [])
            if not isinstance(tasks_raw, list):
                raise ValueError(f"pets[{i}].tasks must be a list")

            for j, task_raw in enumerate(tasks_raw):
                loc = f"pets[{i}].tasks[{j}]"
                if not isinstance(task_raw, dict):
                    raise ValueError(f"{loc} must be an object")

                task_id   = _validated_str(task_raw.get("id"),          f"{loc}.id")
                task_name = _validated_str(task_raw.get("name"),        f"{loc}.name")
                task_desc = _validated_str(task_raw.get("description"), f"{loc}.description")

                time_str = _validated_str(task_raw.get("scheduled_time"), f"{loc}.scheduled_time")
                try:
                    scheduled_time = time.fromisoformat(time_str)
                except ValueError:
                    raise ValueError(f"{loc}.scheduled_time '{time_str}' is not a valid HH:MM time")

                freq = task_raw.get("frequency_days", 0)
                if isinstance(freq, bool) or not isinstance(freq, int) or freq < 0:
                    raise ValueError(f"{loc}.frequency_days must be a non-negative integer")

                status_str = _validated_str(task_raw.get("status", "pending"), f"{loc}.status")
                try:
                    status = TaskStatus(status_str)
                except ValueError:
                    raise ValueError(f"{loc}.status '{status_str}' is not a valid TaskStatus value")

                due_str = _validated_str(task_raw.get("next_due_date"), f"{loc}.next_due_date")
                try:
                    next_due_date = date.fromisoformat(due_str)
                except ValueError:
                    raise ValueError(f"{loc}.next_due_date '{due_str}' is not a valid YYYY-MM-DD date")

                pet.add_task(Task(
                    id=task_id,
                    name=task_name,
                    description=task_desc,
                    scheduled_time=scheduled_time,
                    frequency_days=freq,
                    status=status,
                    next_due_date=next_due_date,
                ))

            owner.add_pet(pet)

        return owner

    @classmethod
    def load_from_json(cls, filepath: str) -> Owner:
        """Reads a JSON file and deserializes it into an Owner, validating every field."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
