"""PawPal+ — Streamlit UI for pet care scheduling."""

import streamlit as st
from datetime import date

from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    CATEGORY_EMOJI, PRIORITY_INDICATOR,
)

DATA_FILE = "data.json"

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


# ---------------------------------------------------------------------------
# Session state initialisation (with persistence)
# ---------------------------------------------------------------------------

def _load_state() -> None:
    """Load owner from JSON on first run, or create a fresh owner."""
    loaded = Owner.load_from_json(DATA_FILE)
    if loaded:
        st.session_state.owner = loaded
        st.session_state.pets = {pet.name: pet for pet in loaded.pets}
    else:
        st.session_state.owner = Owner(name="Jordan", available_minutes=90)
        st.session_state.pets = {}


if "owner" not in st.session_state:
    _load_state()

owner: Owner = st.session_state.owner


def _save() -> None:
    """Persist current state to JSON."""
    owner.save_to_json(DATA_FILE)


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.title("🐾 PawPal+")
st.caption("Smart daily pet care planner with priority scheduling and conflict detection.")

# ---------------------------------------------------------------------------
# Sidebar — Owner & Pet setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Owner Setup")
    new_name = st.text_input("Owner name", value=owner.name)
    new_minutes = st.slider("Available minutes today", 15, 240, owner.available_minutes, step=5)
    owner.name = new_name
    owner.available_minutes = new_minutes

    st.divider()
    st.header("Add a Pet")
    pet_name = st.text_input("Pet name", value="", key="new_pet_name")
    pet_species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    pet_age = st.number_input("Age", min_value=0, max_value=30, value=1)

    if st.button("Add Pet", use_container_width=True):
        if pet_name and pet_name not in st.session_state.pets:
            new_pet = Pet(name=pet_name, species=pet_species, age=pet_age)
            st.session_state.pets[pet_name] = new_pet
            owner.add_pet(new_pet)
            _save()
            st.success(f"Added {pet_name} the {pet_species}!")
        elif pet_name in st.session_state.pets:
            st.warning(f"A pet named '{pet_name}' already exists.")
        else:
            st.warning("Please enter a pet name.")

    if st.session_state.pets:
        st.divider()
        st.header("Your Pets")
        for pname, pet in st.session_state.pets.items():
            task_count = len(pet.tasks)
            pending = len(pet.pending_tasks())
            species_emoji = {"dog": "🐕", "cat": "🐈", "bird": "🐦", "rabbit": "🐇"}.get(pet.species, "🐾")
            st.markdown(f"{species_emoji} **{pname}** (age {pet.age}) — {pending}/{task_count} tasks pending")

    st.divider()
    st.caption("Data auto-saved to `data.json`")


# ---------------------------------------------------------------------------
# Main area — Task management
# ---------------------------------------------------------------------------

if not st.session_state.pets:
    st.info("Add at least one pet in the sidebar to get started.")
    st.stop()

st.subheader("Add a Task")

col1, col2 = st.columns(2)
with col1:
    selected_pet = st.selectbox("For pet", list(st.session_state.pets.keys()))
    task_title = st.text_input("Task title", value="Morning walk")
    task_category = st.selectbox(
        "Category",
        ["walk", "feeding", "meds", "grooming", "enrichment", "general"],
        format_func=lambda c: f"{CATEGORY_EMOJI.get(c, '')} {c}",
    )

with col2:
    task_time = st.time_input("Scheduled time", value=None)
    task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
    task_priority = st.selectbox(
        "Priority",
        ["high", "medium", "low"],
        format_func=lambda p: f"{PRIORITY_INDICATOR.get(p, '')} {p}",
    )

col_freq, col_slot, col_add = st.columns([1, 1, 1])
with col_freq:
    task_frequency = st.selectbox("Frequency", ["daily", "weekly", "as_needed"])
with col_slot:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Suggest time", use_container_width=True):
        slot = Scheduler.find_next_slot(owner, int(task_duration))
        if slot:
            st.info(f"Next available slot: **{slot}**")
        else:
            st.warning("No open slots found (07:00–21:00).")
with col_add:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Add Task", use_container_width=True):
        time_str = task_time.strftime("%H:%M") if task_time else ""
        new_task = Task(
            title=task_title,
            duration_minutes=int(task_duration),
            priority=task_priority,
            category=task_category,
            frequency=task_frequency,
            scheduled_time=time_str,
            due_date=date.today(),
        )
        st.session_state.pets[selected_pet].add_task(new_task)
        _save()
        st.success(f"Added '{task_title}' to {selected_pet}.")

st.divider()

# ---------------------------------------------------------------------------
# Task list with filtering
# ---------------------------------------------------------------------------

st.subheader("All Tasks")

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    filter_pet = st.selectbox("Filter by pet", ["All"] + list(st.session_state.pets.keys()), key="filter_pet")
with filter_col2:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"], key="filter_status")
with filter_col3:
    filter_category = st.selectbox(
        "Filter by category",
        ["All", "walk", "feeding", "meds", "grooming", "enrichment", "general"],
        key="filter_category",
    )

# Gather tasks based on filters
if filter_pet == "All":
    display_tasks = owner.get_all_tasks()
    display_pet_names = {id(t): pname for pname, pet in st.session_state.pets.items() for t in pet.tasks}
else:
    display_tasks = Scheduler.filter_by_pet(owner, filter_pet)
    display_pet_names = {id(t): filter_pet for t in display_tasks}

if filter_status == "Pending":
    display_tasks = Scheduler.filter_by_status(display_tasks, completed=False)
elif filter_status == "Completed":
    display_tasks = Scheduler.filter_by_status(display_tasks, completed=True)

if filter_category != "All":
    display_tasks = Scheduler.filter_by_category(display_tasks, filter_category)

# Sort by time
display_tasks = Scheduler.sort_by_time(display_tasks)

if display_tasks:
    for task in display_tasks:
        pet_label = display_pet_names.get(id(task), "?")
        status_icon = "✅" if task.completed else "⬜"
        time_label = task.scheduled_time if task.scheduled_time else "--:--"
        freq_label = f" | {task.frequency}" if task.frequency != "as_needed" else ""
        cat_emoji = CATEGORY_EMOJI.get(task.category, "📋")
        pri_dot = PRIORITY_INDICATOR.get(task.priority, "")
        score = Scheduler.weighted_score(task)

        col_check, col_info, col_action = st.columns([0.5, 4, 1])
        with col_check:
            st.markdown(f"### {status_icon}")
        with col_info:
            st.markdown(
                f"{cat_emoji} **{task.title}** ({pet_label})  \n"
                f"`{time_label}` · {task.duration_minutes} min · "
                f"{pri_dot} {task.priority} · {task.category}{freq_label} · "
                f"score {score:.1f}"
            )
        with col_action:
            if not task.completed:
                if st.button("Done", key=f"done_{id(task)}"):
                    pet_obj = st.session_state.pets.get(pet_label)
                    if pet_obj:
                        next_task = pet_obj.mark_task_complete(task.title)
                        _save()
                        if next_task:
                            st.toast(f"Recurring: '{next_task.title}' created for {next_task.due_date}")
                        st.rerun()
else:
    st.info("No tasks match the current filters.")

st.divider()

# ---------------------------------------------------------------------------
# Schedule generation
# ---------------------------------------------------------------------------

st.subheader("Generate Daily Schedule")

use_weighted = st.toggle("Use weighted scoring", value=False, help="Rank by composite score instead of simple priority order")

if st.button("Build Schedule", type="primary", use_container_width=True):
    # Conflict detection first
    conflicts = Scheduler.detect_conflicts(owner)
    if conflicts:
        for warning in conflicts:
            st.warning(f"⚠️ {warning}")

    if use_weighted:
        schedule = Scheduler.generate_weighted_schedule(owner)
    else:
        schedule = Scheduler.generate_schedule(owner)

    if not schedule.tasks:
        st.info("No pending tasks to schedule.")
    else:
        remaining = schedule.available_minutes - schedule.total_minutes
        st.success(
            f"Scheduled {len(schedule.tasks)} tasks · "
            f"{schedule.total_minutes} min used of {schedule.available_minutes} min available · "
            f"{remaining} min free"
        )

        # Schedule table with emojis and priority indicators
        table_data = []
        for i, task in enumerate(schedule.tasks, 1):
            cat_emoji = CATEGORY_EMOJI.get(task.category, "📋")
            pri_dot = PRIORITY_INDICATOR.get(task.priority, "")
            table_data.append({
                "#": i,
                "Task": f"{cat_emoji} {task.title}",
                "Duration": f"{task.duration_minutes} min",
                "Priority": f"{pri_dot} {task.priority}",
                "Category": task.category,
                "Time": task.scheduled_time or "--:--",
            })
        st.table(table_data)

        # Skipped tasks
        scheduled_titles = {t.title for t in schedule.tasks}
        skipped = [t for t in owner.get_pending_tasks() if t.title not in scheduled_titles]
        if skipped:
            with st.expander(f"Skipped tasks ({len(skipped)})"):
                for t in skipped:
                    pri = PRIORITY_INDICATOR.get(t.priority, "")
                    st.markdown(f"- {pri} **{t.title}** — {t.duration_minutes} min, {t.priority} priority")
                st.caption("These tasks didn't fit within the time budget.")
