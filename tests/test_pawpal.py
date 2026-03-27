import pytest
from datetime import date, time, timedelta
from pawpal_system import Owner, Pet, Task, TaskStatus, Scheduler


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_task():
    return Task(
        id="task-1",
        name="Morning Walk",
        description="Walk around the block",
        scheduled_time=time(8, 0),
        frequency_days=1,
    )

@pytest.fixture
def sample_pet(sample_task):
    pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
    pet.add_task(sample_task)
    return pet

@pytest.fixture
def sample_owner(sample_pet):
    owner = Owner(id="owner-1")
    owner.add_pet(sample_pet)
    return owner


# ─── Task ─────────────────────────────────────────────────────────────────────

class TestTask:

    def test_default_status_is_pending(self, sample_task):
        assert sample_task.status == TaskStatus.PENDING

    def test_default_next_due_date_is_today(self, sample_task):
        assert sample_task.next_due_date == date.today()

    def test_update_name(self, sample_task):
        sample_task.update_name("Evening Walk")
        assert sample_task.name == "Evening Walk"

    def test_update_description(self, sample_task):
        sample_task.update_description("Longer walk through the park")
        assert sample_task.description == "Longer walk through the park"

    def test_update_scheduled_time(self, sample_task):
        new_time = time(18, 0)
        sample_task.update_scheduled_time(new_time)
        assert sample_task.scheduled_time == new_time

    def test_update_frequency(self, sample_task):
        sample_task.update_frequency(7)
        assert sample_task.frequency_days == 7

    def test_update_status(self, sample_task):
        sample_task.update_status(TaskStatus.COMPLETED)
        assert sample_task.status == TaskStatus.COMPLETED


# ─── Pet ──────────────────────────────────────────────────────────────────────

class TestPet:

    def test_add_task(self):
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        task = Task(id="t1", name="Walk", description="Walk", scheduled_time=time(8, 0), frequency_days=1)
        pet.add_task(task)
        assert task in pet.tasks

    def test_remove_task(self):
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        task = Task(id="t1", name="Walk", description="Walk", scheduled_time=time(8, 0), frequency_days=1)
        pet.add_task(task)
        pet.remove_task("t1")
        assert all(t.id != "t1" for t in pet.tasks)

    def test_remove_task_nonexistent_id_is_safe(self, sample_pet):
        count_before = len(sample_pet.tasks)
        sample_pet.remove_task("does-not-exist")
        assert len(sample_pet.tasks) == count_before

    def test_update_last_vet_visit(self, sample_pet):
        new_date = date(2025, 1, 15)
        sample_pet.update_last_vet_visit(new_date)
        assert sample_pet.last_vet_visit == new_date

    def test_update_last_vet_visit_overwrites_existing_date(self, sample_pet):
        sample_pet.update_last_vet_visit(date(2024, 6, 1))
        sample_pet.update_last_vet_visit(date(2025, 3, 15))
        assert sample_pet.last_vet_visit == date(2025, 3, 15)

    def test_update_task_name(self, sample_pet, sample_task):
        sample_pet.update_task("task-1", name="New Name")
        assert sample_task.name == "New Name"

    def test_update_task_description(self, sample_pet, sample_task):
        sample_pet.update_task("task-1", description="New description")
        assert sample_task.description == "New description"

    def test_update_task_scheduled_time(self, sample_pet, sample_task):
        new_time = time(15, 0)
        sample_pet.update_task("task-1", scheduled_time=new_time)
        assert sample_task.scheduled_time == new_time

    def test_update_task_frequency(self, sample_pet, sample_task):
        sample_pet.update_task("task-1", frequency_days=7)
        assert sample_task.frequency_days == 7

    def test_update_task_status(self, sample_pet, sample_task):
        sample_pet.update_task("task-1", status=TaskStatus.COMPLETED)
        assert sample_task.status == TaskStatus.COMPLETED

    def test_update_task_nonexistent_id_is_safe(self, sample_pet):
        sample_pet.update_task("does-not-exist", name="Ghost")  # should not raise


# ─── Scheduler ────────────────────────────────────────────────────────────────

class TestScheduler:

    def test_add_pet(self):
        scheduler = Scheduler()
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        scheduler.add_pet(pet)
        assert pet in scheduler.pets

    def test_remove_pet(self):
        scheduler = Scheduler()
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        scheduler.add_pet(pet)
        scheduler.remove_pet("pet-1")
        assert all(p.id != "pet-1" for p in scheduler.pets)

    def test_get_all_tasks_contains_expected_pair(self, sample_owner, sample_pet, sample_task):
        assert (sample_pet, sample_task) in sample_owner.scheduler.get_all_tasks()

    def test_get_tasks_for_pet_returns_tasks(self, sample_owner, sample_task):
        assert sample_task in sample_owner.scheduler.get_tasks_for_pet("pet-1")

    def test_get_tasks_for_pet_unknown_id_returns_empty(self, sample_owner):
        assert sample_owner.scheduler.get_tasks_for_pet("unknown") == []

    def test_get_pending_tasks_includes_pending(self, sample_owner, sample_pet, sample_task):
        assert (sample_pet, sample_task) in sample_owner.scheduler.get_pending_tasks()

    def test_get_pending_tasks_excludes_completed(self, sample_owner, sample_pet, sample_task):
        sample_task.update_status(TaskStatus.COMPLETED)
        assert (sample_pet, sample_task) not in sample_owner.scheduler.get_pending_tasks()

    def test_get_tasks_due_today_or_earlier_includes_past_due(self, sample_owner, sample_pet, sample_task):
        sample_task.next_due_date = date.today() - timedelta(days=1)
        assert (sample_pet, sample_task) in sample_owner.scheduler.get_tasks_due_today_or_earlier()

    def test_get_tasks_due_today_or_earlier_includes_today(self, sample_owner, sample_pet, sample_task):
        sample_task.next_due_date = date.today()
        assert (sample_pet, sample_task) in sample_owner.scheduler.get_tasks_due_today_or_earlier()

    def test_get_tasks_due_today_or_earlier_excludes_future(self, sample_owner, sample_pet, sample_task):
        sample_task.next_due_date = date.today() + timedelta(days=1)
        assert (sample_pet, sample_task) not in sample_owner.scheduler.get_tasks_due_today_or_earlier()

    def test_get_tasks_sorted_by_time(self, sample_owner, sample_pet):
        task_late  = Task(id="t-late",  name="Late",  description="", scheduled_time=time(20, 0), frequency_days=1)
        task_early = Task(id="t-early", name="Early", description="", scheduled_time=time(6, 0),  frequency_days=1)
        sample_pet.add_task(task_late)
        sample_pet.add_task(task_early)
        sorted_times = [task.scheduled_time for _, task in sample_owner.scheduler.get_tasks_sorted_by_time()]
        assert sorted_times == sorted(sorted_times)

    def test_get_tasks_sorted_by_time_first_is_earliest(self, sample_owner, sample_pet):
        task_late  = Task(id="t-late",  name="Late",  description="", scheduled_time=time(20, 0), frequency_days=1)
        task_early = Task(id="t-early", name="Early", description="", scheduled_time=time(6, 0),  frequency_days=1)
        sample_pet.add_task(task_late)
        sample_pet.add_task(task_early)
        results = sample_owner.scheduler.get_tasks_sorted_by_time()
        assert results[0][1].scheduled_time == time(6, 0)
        assert results[-1][1].scheduled_time == time(20, 0)

    def test_get_tasks_sorted_by_time_is_strictly_chronological(self, sample_owner, sample_pet):
        times = [time(14, 0), time(7, 30), time(9, 0), time(23, 59)]
        for i, t in enumerate(times):
            sample_pet.add_task(Task(id=f"tx-{i}", name=f"Task{i}", description="", scheduled_time=t, frequency_days=0))
        result_times = [task.scheduled_time for _, task in sample_owner.scheduler.get_tasks_sorted_by_time()]
        assert result_times == sorted(result_times)
        assert result_times[0] < result_times[1] < result_times[2]

    def test_mark_task_complete_sets_status(self, sample_owner, sample_task):
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.status == TaskStatus.COMPLETED

    def test_mark_task_complete_original_due_date_unchanged(self, sample_owner, sample_task):
        """The original task's due date is not mutated; a new task carries the advanced date."""
        sample_task.frequency_days = 7
        original_due = sample_task.next_due_date
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.next_due_date == original_due

    def test_mark_recurring_task_complete_creates_new_task(self, sample_owner, sample_pet, sample_task):
        """Completing a recurring task should add a new PENDING task to the pet."""
        sample_task.frequency_days = 1
        count_before = len(sample_pet.tasks)
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert len(sample_pet.tasks) == count_before + 1

    def test_mark_recurring_task_complete_new_task_is_pending(self, sample_owner, sample_pet, sample_task):
        sample_task.frequency_days = 3
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        new_tasks = [t for t in sample_pet.tasks if t.id != "task-1"]
        assert len(new_tasks) == 1
        assert new_tasks[0].status == TaskStatus.PENDING

    def test_mark_recurring_task_complete_new_task_has_advanced_due_date(self, sample_owner, sample_pet, sample_task):
        sample_task.frequency_days = 7
        original_due = sample_task.next_due_date
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        new_tasks = [t for t in sample_pet.tasks if t.id != "task-1"]
        assert new_tasks[0].next_due_date == original_due + timedelta(days=7)

    def test_mark_recurring_task_complete_new_task_inherits_properties(self, sample_owner, sample_pet, sample_task):
        sample_task.frequency_days = 2
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        new_tasks = [t for t in sample_pet.tasks if t.id != "task-1"]
        new_task = new_tasks[0]
        assert new_task.name == sample_task.name
        assert new_task.description == sample_task.description
        assert new_task.scheduled_time == sample_task.scheduled_time
        assert new_task.frequency_days == sample_task.frequency_days
        assert new_task.id != sample_task.id

    def test_mark_non_recurring_task_complete_does_not_create_new_task(self, sample_owner, sample_pet, sample_task):
        sample_task.frequency_days = 0
        count_before = len(sample_pet.tasks)
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert len(sample_pet.tasks) == count_before

    def test_mark_task_complete_non_recurring_sets_status_without_advancing_date(self, sample_owner, sample_task):
        sample_task.frequency_days = 0
        original_due_date = sample_task.next_due_date
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.status == TaskStatus.COMPLETED
        assert sample_task.next_due_date == original_due_date

    def test_mark_task_complete_unknown_pet_does_nothing(self, sample_owner, sample_task):
        sample_owner.scheduler.mark_task_complete("no-such-pet", "task-1")
        assert sample_task.status == TaskStatus.PENDING

    def test_mark_task_complete_unknown_task_does_nothing(self, sample_owner, sample_pet):
        count_before = len(sample_pet.tasks)
        sample_owner.scheduler.mark_task_complete("pet-1", "no-such-task")
        assert len(sample_pet.tasks) == count_before

    def test_get_scheduling_conflicts_no_conflicts(self, sample_owner, sample_pet):
        task2 = Task(id="t2", name="Feed", description="", scheduled_time=time(12, 0), frequency_days=0)
        sample_pet.add_task(task2)
        # sample_task is at 8:00, task2 at 12:00 — no overlap
        assert sample_owner.scheduler.get_scheduling_conflicts() == []

    def test_get_scheduling_conflicts_detects_two_tasks_at_same_time(self, sample_owner, sample_pet):
        task2 = Task(id="t2", name="Feed", description="", scheduled_time=time(8, 0), frequency_days=0)
        sample_pet.add_task(task2)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert len(conflicts) == 1

    def test_get_scheduling_conflicts_warning_contains_task_names(self, sample_owner, sample_pet, sample_task):
        task2 = Task(id="t2", name="Feed", description="", scheduled_time=time(8, 0), frequency_days=0)
        sample_pet.add_task(task2)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert "Morning Walk" in conflicts[0]
        assert "Feed" in conflicts[0]

    def test_get_scheduling_conflicts_warning_contains_pet_name(self, sample_owner, sample_pet):
        task2 = Task(id="t2", name="Feed", description="", scheduled_time=time(8, 0), frequency_days=0)
        sample_pet.add_task(task2)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert "Buddy" in conflicts[0]

    def test_get_scheduling_conflicts_warning_contains_time(self, sample_owner, sample_pet):
        task2 = Task(id="t2", name="Feed", description="", scheduled_time=time(8, 0), frequency_days=0)
        sample_pet.add_task(task2)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert "08:00" in conflicts[0]

    def test_get_scheduling_conflicts_three_tasks_same_time(self, sample_owner, sample_pet):
        task2 = Task(id="t2", name="Feed",  description="", scheduled_time=time(8, 0), frequency_days=0)
        task3 = Task(id="t3", name="Brush", description="", scheduled_time=time(8, 0), frequency_days=0)
        sample_pet.add_task(task2)
        sample_pet.add_task(task3)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert len(conflicts) == 1
        assert "Feed" in conflicts[0]
        assert "Brush" in conflicts[0]

    def test_get_scheduling_conflicts_across_multiple_pets(self):
        scheduler = Scheduler()
        pet1 = Pet(id="p1", name="Buddy", animal_type="Dog")
        pet2 = Pet(id="p2", name="Whiskers", animal_type="Cat")
        pet1.add_task(Task(id="t1", name="Walk", description="", scheduled_time=time(9, 0), frequency_days=0))
        pet2.add_task(Task(id="t2", name="Feed", description="", scheduled_time=time(9, 0), frequency_days=0))
        scheduler.add_pet(pet1)
        scheduler.add_pet(pet2)
        conflicts = scheduler.get_scheduling_conflicts()
        assert len(conflicts) == 1
        assert "Buddy" in conflicts[0]
        assert "Whiskers" in conflicts[0]

    def test_get_completed_tasks_includes_completed(self, sample_owner, sample_pet, sample_task):
        sample_task.update_status(TaskStatus.COMPLETED)
        assert (sample_pet, sample_task) in sample_owner.scheduler.get_completed_tasks()

    def test_get_completed_tasks_excludes_pending(self, sample_owner, sample_pet, sample_task):
        assert (sample_pet, sample_task) not in sample_owner.scheduler.get_completed_tasks()

    def test_get_completed_tasks_empty_when_none_completed(self, sample_owner):
        assert sample_owner.scheduler.get_completed_tasks() == []

    def test_get_pending_tasks_for_pet_returns_pending(self, sample_owner, sample_task):
        assert sample_task in sample_owner.scheduler.get_pending_tasks_for_pet("pet-1")

    def test_get_pending_tasks_for_pet_excludes_completed(self, sample_owner, sample_task):
        sample_task.update_status(TaskStatus.COMPLETED)
        assert sample_task not in sample_owner.scheduler.get_pending_tasks_for_pet("pet-1")

    def test_get_pending_tasks_for_pet_unknown_id_returns_empty(self, sample_owner):
        assert sample_owner.scheduler.get_pending_tasks_for_pet("unknown") == []

    def test_get_completed_tasks_for_pet_returns_completed(self, sample_owner, sample_task):
        sample_task.update_status(TaskStatus.COMPLETED)
        assert sample_task in sample_owner.scheduler.get_completed_tasks_for_pet("pet-1")

    def test_get_completed_tasks_for_pet_excludes_pending(self, sample_owner, sample_task):
        assert sample_task not in sample_owner.scheduler.get_completed_tasks_for_pet("pet-1")

    def test_get_completed_tasks_for_pet_unknown_id_returns_empty(self, sample_owner):
        assert sample_owner.scheduler.get_completed_tasks_for_pet("unknown") == []

    def test_get_tasks_due_today_or_earlier_for_pet_includes_past_due(self, sample_owner, sample_task):
        sample_task.next_due_date = date.today() - timedelta(days=1)
        assert sample_task in sample_owner.scheduler.get_tasks_due_today_or_earlier_for_pet("pet-1")

    def test_get_tasks_due_today_or_earlier_for_pet_includes_today(self, sample_owner, sample_task):
        sample_task.next_due_date = date.today()
        assert sample_task in sample_owner.scheduler.get_tasks_due_today_or_earlier_for_pet("pet-1")

    def test_get_tasks_due_today_or_earlier_for_pet_excludes_future(self, sample_owner, sample_task):
        sample_task.next_due_date = date.today() + timedelta(days=1)
        assert sample_task not in sample_owner.scheduler.get_tasks_due_today_or_earlier_for_pet("pet-1")

    def test_get_tasks_due_today_or_earlier_for_pet_unknown_id_returns_empty(self, sample_owner):
        assert sample_owner.scheduler.get_tasks_due_today_or_earlier_for_pet("unknown") == []

    def test_get_scheduling_conflicts_multiple_distinct_conflicts(self, sample_owner, sample_pet):
        # 8:00 conflict (with existing sample_task) + a new 12:00 conflict
        task_8b  = Task(id="t-8b",  name="Meds",   description="", scheduled_time=time(8, 0),  frequency_days=0)
        task_12a = Task(id="t-12a", name="Lunch",   description="", scheduled_time=time(12, 0), frequency_days=0)
        task_12b = Task(id="t-12b", name="Nap",     description="", scheduled_time=time(12, 0), frequency_days=0)
        sample_pet.add_task(task_8b)
        sample_pet.add_task(task_12a)
        sample_pet.add_task(task_12b)
        conflicts = sample_owner.scheduler.get_scheduling_conflicts()
        assert len(conflicts) == 2


# ─── Owner ────────────────────────────────────────────────────────────────────

class TestOwner:

    def test_add_pet_appears_in_owner_pets(self):
        owner = Owner(id="owner-1")
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        owner.add_pet(pet)
        assert pet in owner.pets

    def test_add_pet_appears_in_scheduler_pets(self):
        owner = Owner(id="owner-1")
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog")
        owner.add_pet(pet)
        assert pet in owner.scheduler.pets

    def test_remove_pet_removes_from_owner_pets(self, sample_owner):
        sample_owner.remove_pet("pet-1")
        assert all(p.id != "pet-1" for p in sample_owner.pets)

    def test_remove_pet_removes_from_scheduler_pets(self, sample_owner):
        sample_owner.remove_pet("pet-1")
        assert all(p.id != "pet-1" for p in sample_owner.scheduler.pets)

    def test_owner_and_scheduler_share_same_list(self):
        owner = Owner(id="owner-1")
        assert owner.pets is owner.scheduler.pets
