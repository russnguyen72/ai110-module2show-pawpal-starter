import uuid
from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# ── One-time initialization ────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = Owner(id=str(uuid.uuid4()))
    st.session_state.owner.add_pet(
        Pet(id=str(uuid.uuid4()), name="Mochi", animal_type="dog")
    )

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "schedule_label" not in st.session_state:
    st.session_state.schedule_label = None

owner: Owner = st.session_state.owner

# ── Owner & Pets ───────────────────────────────────────────────────────────
st.subheader("Quick Demo Inputs")

st.text_input("Owner name", key="owner_name", value="Jordan")

st.markdown("### Pets")
st.caption("Pets currently being tracked.")

if owner.pets:
    st.table([
        {"Name": p.name, "Species": p.animal_type, "Tasks": len(p.tasks)}
        for p in owner.pets
    ])
else:
    st.info("No pets yet. Add one below.")

def _add_pet():
    name = st.session_state.new_pet_name.strip()
    if name:
        owner.add_pet(Pet(
            id=str(uuid.uuid4()),
            name=name,
            animal_type=st.session_state.new_pet_species,
        ))
        st.session_state.schedule = None

col_a, col_b = st.columns(2)
with col_a:
    st.text_input("Pet name", key="new_pet_name", value="")
with col_b:
    st.selectbox("Species", ["dog", "cat", "other"], key="new_pet_species")

st.button("Add pet", on_click=_add_pet)

# ── Tasks ──────────────────────────────────────────────────────────────────
st.markdown("### Tasks")
st.caption("Add tasks and assign them to one or all pets.")

if owner.pets:
    assign_options = [p.name for p in owner.pets] + ["All pets"]

    def _add_task():
        targets = (
            owner.pets if st.session_state.task_assign_to == "All pets"
            else [p for p in owner.pets if p.name == st.session_state.task_assign_to]
        )
        for target_pet in targets:
            target_pet.add_task(Task(
                id=str(uuid.uuid4()),
                name=st.session_state.task_name,
                description=st.session_state.task_desc,
                scheduled_time=st.session_state.task_time,
                frequency_days=int(st.session_state.task_freq),
            ))
        st.session_state.schedule = None

    st.selectbox("Assign to", assign_options, key="task_assign_to")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.text_input("Task name", key="task_name", value="Morning walk")
    with col2:
        st.text_input("Description", key="task_desc", value="Walk around the block")
    with col3:
        st.time_input("Scheduled time", key="task_time", value=time(8, 0))

    st.number_input(
        "Repeat every N days (0 = one-time)",
        key="task_freq", min_value=0, max_value=365, value=1,
    )

    if st.button("Add task"):
        _add_task()

    all_tasks = [(p, t) for p in owner.pets for t in p.tasks]
    if all_tasks:
        st.write("Current tasks:")
        st.table([
            {
                "Pet": p.name,
                "Name": t.name,
                "Description": t.description,
                "Scheduled time": t.scheduled_time.strftime("%H:%M"),
                "Repeats every (days)": t.frequency_days if t.frequency_days else "one-time",
                "Status": t.status.value,
                "Next due": str(t.next_due_date),
            }
            for p, t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Add a pet above before adding tasks.")

st.divider()

# ── Build Schedule ─────────────────────────────────────────────────────────
st.subheader("Build Schedule")
st.caption("Generates a time-ordered schedule for one or all pets.")

if owner.pets:
    schedule_options = [p.name for p in owner.pets] + ["All pets"]

    def _generate_schedule():
        selected = st.session_state.schedule_for
        all_sorted = owner.scheduler.get_tasks_sorted_by_time()
        st.session_state.schedule = (
            all_sorted if selected == "All pets"
            else [(p, t) for p, t in all_sorted if p.name == selected]
        )
        st.session_state.schedule_label = selected

    st.selectbox("Schedule for", schedule_options, key="schedule_for")

    if st.button("Generate schedule"):
        _generate_schedule()

    if st.session_state.schedule is not None:
        if st.session_state.schedule:
            owner_label = st.session_state.get("owner_name", "")
            scope_label = st.session_state.get("schedule_label", "All pets")
            st.success(f"Schedule for **{owner_label}** — **{scope_label}**")
            st.table([
                {
                    "Pet": p.name,
                    "Time": t.scheduled_time.strftime("%H:%M"),
                    "Task": t.name,
                    "Description": t.description,
                    "Status": t.status.value,
                    "Next due": str(t.next_due_date),
                }
                for p, t in st.session_state.schedule
            ])
        else:
            st.warning("No tasks to schedule for this selection.")
else:
    st.info("Add a pet above before generating a schedule.")
