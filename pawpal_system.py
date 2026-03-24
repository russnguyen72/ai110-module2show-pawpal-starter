from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class Task:
    id: str
    description: str
    priority: int
    status: TaskStatus = TaskStatus.PENDING

    def update_priority(self, priority: int) -> None:
        self.priority = priority

    def update_description(self, description: str) -> None:
        self.description = description

    def update_status(self, status: TaskStatus) -> None:
        self.status = status


@dataclass
class Pet:
    id: str
    name: str
    animal_type: str
    last_vet_visit: date
    tasks: list[Task] = field(default_factory=list)

    def update_last_vet_visit(self, new_date: date) -> None:
        self.last_vet_visit = new_date

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def update_task(self, task_id: str, **updates) -> None:
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    setattr(task, key, value)
                break


@dataclass
class Owner:
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def remove_pet(self, pet_id: str) -> None:
        self.pets = [p for p in self.pets if p.id != pet_id]


@dataclass
class ScheduledTask:
    task_template: Task
    frequency_days: int
    next_run_date: date


@dataclass
class Scheduler:
    pet: Pet
    queue: list[ScheduledTask] = field(default_factory=list)

    def add_scheduled_task(self, template: Task, frequency_days: int) -> None:
        self.queue.append(ScheduledTask(
            task_template=template,
            frequency_days=frequency_days,
            next_run_date=date.today()
        ))

    def remove_scheduled_task(self, task_id: str) -> None:
        self.queue = [s for s in self.queue if s.task_template.id != task_id]

    def modify_frequency(self, task_id: str, frequency_days: int) -> None:
        for scheduled in self.queue:
            if scheduled.task_template.id == task_id:
                scheduled.frequency_days = frequency_days
                break

    def run(self) -> None:
        pass  # TODO: iterate queue, create tasks for pet when next_run_date is reached
