import json
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


# ─── Owner persistence helpers ────────────────────────────────────────────────

def _task_dict(**overrides):
    base = {
        "id": "t1", "name": "Morning Walk", "description": "Walk around the block",
        "scheduled_time": "08:00", "frequency_days": 1,
        "status": "pending", "next_due_date": "2025-01-01",
    }
    return {**base, **overrides}

def _pet_dict(tasks=None, **overrides):
    base = {"id": "p1", "name": "Buddy", "animal_type": "dog", "last_vet_visit": None, "tasks": tasks or []}
    return {**base, **overrides}

def _owner_dict(pets=None, **overrides):
    base = {"id": "o1", "pets": pets or []}
    return {**base, **overrides}


# ─── Owner persistence ────────────────────────────────────────────────────────

class TestOwnerPersistence:

    @pytest.fixture
    def owner_with_data(self):
        owner = Owner(id="owner-1")
        pet = Pet(id="pet-1", name="Buddy", animal_type="Dog", last_vet_visit=date(2025, 1, 15))
        pet.add_task(Task(
            id="task-1", name="Morning Walk", description="Walk",
            scheduled_time=time(8, 0), frequency_days=1,
        ))
        pet.add_task(Task(
            id="task-2", name="Flea Treatment", description="Apply treatment",
            scheduled_time=time(9, 0), frequency_days=30,
            status=TaskStatus.COMPLETED, next_due_date=date(2025, 2, 15),
        ))
        owner.add_pet(pet)
        return owner

    # --- to_dict / to_json ---

    def test_to_dict_contains_owner_id(self, owner_with_data):
        assert owner_with_data.to_dict()["id"] == "owner-1"

    def test_to_dict_contains_pet(self, owner_with_data):
        assert owner_with_data.to_dict()["pets"][0]["name"] == "Buddy"

    def test_to_dict_contains_all_tasks(self, owner_with_data):
        assert len(owner_with_data.to_dict()["pets"][0]["tasks"]) == 2

    def test_to_dict_serializes_scheduled_time_as_hhmm(self, owner_with_data):
        task = owner_with_data.to_dict()["pets"][0]["tasks"][0]
        assert task["scheduled_time"] == "08:00"

    def test_to_dict_serializes_completed_status(self, owner_with_data):
        tasks = owner_with_data.to_dict()["pets"][0]["tasks"]
        completed = next(t for t in tasks if t["id"] == "task-2")
        assert completed["status"] == "completed"

    def test_to_dict_serializes_last_vet_visit(self, owner_with_data):
        assert owner_with_data.to_dict()["pets"][0]["last_vet_visit"] == "2025-01-15"

    def test_to_dict_null_last_vet_visit_when_none(self):
        owner = Owner(id="o1")
        owner.add_pet(Pet(id="p1", name="Mochi", animal_type="cat"))
        assert owner.to_dict()["pets"][0]["last_vet_visit"] is None

    def test_to_json_produces_valid_json(self, owner_with_data):
        result = json.loads(owner_with_data.to_json())
        assert isinstance(result, dict)

    def test_to_json_round_trips_owner_id(self, owner_with_data):
        assert json.loads(owner_with_data.to_json())["id"] == "owner-1"

    # --- save / load round-trip ---

    def test_roundtrip_preserves_owner_id(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert Owner.load_from_json(path).id == "owner-1"

    def test_roundtrip_preserves_pet_name(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert Owner.load_from_json(path).pets[0].name == "Buddy"

    def test_roundtrip_preserves_task_count(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert len(Owner.load_from_json(path).pets[0].tasks) == 2

    def test_roundtrip_preserves_scheduled_time(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert Owner.load_from_json(path).pets[0].tasks[0].scheduled_time == time(8, 0)

    def test_roundtrip_preserves_completed_status(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        loaded_tasks = Owner.load_from_json(path).pets[0].tasks
        completed = next(t for t in loaded_tasks if t.id == "task-2")
        assert completed.status == TaskStatus.COMPLETED

    def test_roundtrip_preserves_last_vet_visit(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert Owner.load_from_json(path).pets[0].last_vet_visit == date(2025, 1, 15)

    def test_roundtrip_preserves_frequency_days(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        assert Owner.load_from_json(path).pets[0].tasks[1].frequency_days == 30

    def test_roundtrip_loaded_owner_scheduler_shares_pets_list(self, owner_with_data, tmp_path):
        path = str(tmp_path / "save.json")
        owner_with_data.save_to_json(path)
        loaded = Owner.load_from_json(path)
        assert loaded.pets is loaded.scheduler.pets

    # --- load_from_json file-level edge cases ---

    def test_load_from_json_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            Owner.load_from_json(str(tmp_path / "nonexistent.json"))

    def test_load_from_json_empty_file_raises(self, tmp_path):
        path = tmp_path / "empty.json"
        path.write_text("")
        with pytest.raises(Exception):  # json.JSONDecodeError
            Owner.load_from_json(str(path))

    def test_load_from_json_malformed_json_raises(self, tmp_path):
        path = tmp_path / "bad.json"
        path.write_text("{not: valid, json}")
        with pytest.raises(Exception):
            Owner.load_from_json(str(path))

    def test_load_from_json_valid_json_wrong_structure_raises(self, tmp_path):
        path = tmp_path / "list.json"
        path.write_text('["this", "is", "a", "list"]')
        with pytest.raises(ValueError):
            Owner.load_from_json(str(path))

    # --- from_dict — owner-level validation ---

    def test_from_dict_rejects_list_root(self):
        with pytest.raises(ValueError):
            Owner.from_dict([])

    def test_from_dict_rejects_string_root(self):
        with pytest.raises(ValueError):
            Owner.from_dict("not a dict")

    def test_from_dict_rejects_non_string_owner_id(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(id=123))

    def test_from_dict_rejects_owner_id_exceeding_max_length(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(id="x" * 501))

    def test_from_dict_rejects_non_list_pets(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets="not a list"))

    # --- from_dict — pet-level validation ---

    def test_from_dict_rejects_non_dict_pet(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=["not a dict"]))

    def test_from_dict_rejects_non_string_pet_name(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(name=42)]))

    def test_from_dict_rejects_non_string_animal_type(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(animal_type=True)]))

    def test_from_dict_rejects_invalid_last_vet_visit(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(last_vet_visit="not-a-date")]))

    def test_from_dict_rejects_non_list_tasks(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks="not a list")]))

    # --- from_dict — task-level validation ---

    def test_from_dict_rejects_non_dict_task(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=["not a dict"])]))

    def test_from_dict_rejects_non_string_task_name(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(name=99)])]))

    def test_from_dict_rejects_invalid_scheduled_time_value(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(scheduled_time="99:99")])]))

    def test_from_dict_rejects_non_string_scheduled_time(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(scheduled_time=800)])]))

    def test_from_dict_rejects_negative_frequency_days(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(frequency_days=-1)])]))

    def test_from_dict_rejects_bool_frequency_days(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(frequency_days=True)])]))

    def test_from_dict_rejects_float_frequency_days(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(frequency_days=1.5)])]))

    def test_from_dict_rejects_unknown_status(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(status="in_progress")])]))

    def test_from_dict_rejects_invalid_next_due_date(self):
        with pytest.raises(ValueError):
            Owner.from_dict(_owner_dict(pets=[_pet_dict(tasks=[_task_dict(next_due_date="32-13-2025")])]))
