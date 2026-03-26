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

    def test_mark_task_complete_sets_status(self, sample_owner, sample_task):
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.status == TaskStatus.COMPLETED

    def test_mark_task_complete_advances_next_due_date(self, sample_owner, sample_task):
        sample_task.frequency_days = 7
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.next_due_date == date.today() + timedelta(days=7)

    def test_mark_task_complete_non_recurring_sets_status_without_advancing_date(self, sample_owner, sample_task):
        sample_task.frequency_days = 0
        original_due_date = sample_task.next_due_date
        sample_owner.scheduler.mark_task_complete("pet-1", "task-1")
        assert sample_task.status == TaskStatus.COMPLETED
        assert sample_task.next_due_date == original_due_date


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
