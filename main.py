from datetime import time
from pawpal_system import Owner, Pet, Task

# --- Setup ---

owner = Owner(id="owner-1")

buddy    = Pet(id="pet-1", name="Buddy",    animal_type="Dog")
whiskers = Pet(id="pet-2", name="Whiskers", animal_type="Cat")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Tasks for Buddy ---

buddy.add_task(Task(
    id="task-1",
    name="Morning Walk",
    description="30 minute walk around the block",
    scheduled_time=time(7, 30),
    frequency_days=1,
))

buddy.add_task(Task(
    id="task-2",
    name="Evening Walk",
    description="15 minute walk before sundown",
    scheduled_time=time(17, 0),
    frequency_days=1,
))

buddy.add_task(Task(
    id="task-3",
    name="Flea Treatment",
    description="Apply monthly flea and tick treatment",
    scheduled_time=time(9, 0),
    frequency_days=30,
))

# --- Tasks for Whiskers ---

whiskers.add_task(Task(
    id="task-4",
    name="Breakfast",
    description="Half a can of wet food",
    scheduled_time=time(8, 0),
    frequency_days=1,
))

whiskers.add_task(Task(
    id="task-5",
    name="Lunchtime Play",
    description="15 minutes with the feather wand",
    scheduled_time=time(12, 0),
    frequency_days=1,
))

whiskers.add_task(Task(
    id="task-6",
    name="Dinner",
    description="Half a can of wet food",
    scheduled_time=time(18, 30),
    frequency_days=1,
))

# --- Print Today's Schedule ---

print("=" * 45)
print("           TODAY'S SCHEDULE")
print("=" * 45)

for pet, task in owner.scheduler.get_tasks_sorted_by_time():
    time_str = task.scheduled_time.strftime("%I:%M %p")
    status   = f"[{task.status.value.upper()}]"
    print(f"  {time_str}  |  {pet.name} ({pet.animal_type:<4})  |  {task.name:<20} {status}")

print("=" * 45)
