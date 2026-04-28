import os
import streamlit as st
from datetime import date
from dotenv import load_dotenv
from pawpal_system import Owner, Pet, Task, Scheduler
from rag_advisor import PetCareRAG, ALL_PRESET_MODELS

load_dotenv()

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")

# ---------------------------------------------------------------------------
# Sidebar — AI settings (OpenRouter key + model selector)
# ---------------------------------------------------------------------------

openrouter_key = os.getenv("OPENROUTER_API_KEY", "")

with st.sidebar:
    st.header("AI Settings")

    if openrouter_key:
        st.success("API key loaded from .env")
    else:
        st.warning("No API key found. Add OPENROUTER_API_KEY to your .env file.")

    model_id = st.selectbox(
        "Model",
        options=ALL_PRESET_MODELS,
        index=0,
        help="All models are free-tier via OpenRouter — no credits required.",
    )

    ai_enabled = bool(openrouter_key and model_id)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------

if "pets" not in st.session_state:
    st.session_state.pets = []

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedule" not in st.session_state:
    st.session_state.schedule = None

if "reasoning" not in st.session_state:
    st.session_state.reasoning = ""

if "ai_used" not in st.session_state:
    st.session_state.ai_used = False

# ---------------------------------------------------------------------------
# Section 1 — Owner info
# ---------------------------------------------------------------------------

st.header("1. Owner")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Your name", value="Alex")
with col2:
    time_available = st.number_input(
        "Time available today (minutes)", min_value=5, max_value=480, value=90, step=5
    )

preferences_raw = st.text_input(
    "Preferences (comma-separated, optional)", placeholder="e.g. morning walks, short sessions"
)
preferences = [p.strip() for p in preferences_raw.split(",") if p.strip()]

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Pet management
# ---------------------------------------------------------------------------

st.header("2. Pets")

with st.expander("Add a pet", expanded=len(st.session_state.pets) == 0):
    pc1, pc2 = st.columns(2)
    with pc1:
        pet_name    = st.text_input("Pet name",   value="Biscuit")
        pet_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    with pc2:
        pet_breed   = st.text_input("Breed",      value="Beagle")
        pet_age     = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

    special_needs_raw = st.text_input(
        "Special needs (comma-separated, optional)", placeholder="e.g. daily eye drops"
    )
    special_needs = [s.strip() for s in special_needs_raw.split(",") if s.strip()]

    if st.button("Add pet"):
        st.session_state.pets.append({
            "name": pet_name,
            "species": pet_species,
            "breed": pet_breed,
            "age": int(pet_age),
            "special_needs": special_needs,
        })
        st.success(f"Added {pet_name}!")

if st.session_state.pets:
    st.write("**Registered pets:**")
    for i, p in enumerate(st.session_state.pets):
        needs_str = ", ".join(p["special_needs"]) if p["special_needs"] else "none"
        col_info, col_del = st.columns([5, 1])
        with col_info:
            st.markdown(
                f"**{p['name']}** — {p['breed']} {p['species']}, age {p['age']} | needs: {needs_str}"
            )
        with col_del:
            if st.button("Remove", key=f"remove_pet_{i}"):
                st.session_state.pets.pop(i)
                st.rerun()
else:
    st.info("No pets added yet. Use the form above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Task management
# ---------------------------------------------------------------------------

st.header("3. Tasks")

PRIORITY_MAP = {"Low (1)": 1, "Medium (3)": 3, "High (5)": 5}
CATEGORIES   = ["walk", "feeding", "meds", "grooming", "enrichment", "other"]

with st.expander("Add a task", expanded=len(st.session_state.tasks) == 0):
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        task_name     = st.text_input("Task name",      value="Morning Walk")
        task_category = st.selectbox("Category",        CATEGORIES)
    with tc2:
        task_duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30)
        task_priority = st.selectbox("Priority",        list(PRIORITY_MAP.keys()), index=2)
    with tc3:
        task_frequency = st.selectbox("Frequency", ["daily", "weekly"])
        task_time      = st.text_input("Preferred time (HH:MM, optional)", placeholder="e.g. 08:00")
        task_notes     = st.text_input("Notes (optional)", placeholder="e.g. bring treats")

    if st.button("Add task"):
        st.session_state.tasks.append({
            "name":      task_name,
            "category":  task_category,
            "duration":  int(task_duration),
            "priority":  PRIORITY_MAP[task_priority],
            "frequency": task_frequency,
            "time":      task_time.strip(),
            "notes":     task_notes,
        })
        st.success(f"Added task: {task_name}")

if st.session_state.tasks:
    st.write("**Registered tasks:**")
    for i, t in enumerate(st.session_state.tasks):
        col_info, col_del = st.columns([5, 1])
        with col_info:
            st.markdown(
                f"**{t['name']}** — {t['category']}, {t['duration']} min, "
                f"priority {t['priority']}, {t['frequency']}"
                + (f" | _{t['notes']}_" if t["notes"] else "")
            )
        with col_del:
            if st.button("Remove", key=f"remove_task_{i}"):
                st.session_state.tasks.pop(i)
                st.rerun()
else:
    st.info("No tasks added yet. Use the form above.")

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Generate schedule
# ---------------------------------------------------------------------------

st.header("4. Generate Schedule")

pet_names = [p["name"] for p in st.session_state.pets]
selected_pet_name = st.selectbox(
    "Schedule for which pet?",
    options=pet_names if pet_names else ["— add a pet first —"],
    disabled=len(pet_names) == 0,
)

today = date.today().strftime("%Y-%m-%d")

if st.button("Generate schedule", type="primary", disabled=len(pet_names) == 0):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(
            name=owner_name,
            time_available=int(time_available),
            preferences=preferences,
        )

        pet_dict = next(p for p in st.session_state.pets if p["name"] == selected_pet_name)
        pet = Pet(
            name=pet_dict["name"],
            species=pet_dict["species"],
            breed=pet_dict["breed"],
            age=pet_dict["age"],
            special_needs=pet_dict["special_needs"],
        )

        scheduler = Scheduler(owner=owner, pet=pet)
        for t in st.session_state.tasks:
            scheduler.add_task(Task(
                name=t["name"],
                category=t["category"],
                duration=t["duration"],
                priority=t["priority"],
                frequency=t["frequency"],
                time=t.get("time", ""),
                notes=t["notes"],
            ))

        for key in list(st.session_state.keys()):
            if key.startswith("done_"):
                del st.session_state[key]

        schedule = scheduler.generate_schedule(date=today)
        st.session_state.schedule = schedule

        # --- RAG: retrieve guidelines then generate grounded AI advice ---
        if ai_enabled:
            try:
                rag = PetCareRAG(api_key=openrouter_key, model=model_id)
                st.session_state.reasoning = rag.generate_advice(pet, owner, schedule)
                st.session_state.ai_used = True
            except Exception as e:
                st.warning(f"AI advice unavailable ({e}). Showing mechanical reasoning.")
                st.session_state.reasoning = scheduler.explain_reasoning()
                st.session_state.ai_used = False
        else:
            st.session_state.reasoning = scheduler.explain_reasoning()
            st.session_state.ai_used = False

# ---------------------------------------------------------------------------
# Section 5 — Display results
# ---------------------------------------------------------------------------

if st.session_state.schedule is not None:
    schedule = st.session_state.schedule

    st.subheader(f"Today's Plan — {selected_pet_name}")

    scheduled = schedule.scheduled_tasks
    if not scheduled:
        st.warning("No tasks could be fit within the available time.")
    else:
        for st_task in sorted(scheduled, key=lambda x: x.time_slot):
            label = f"**{st_task.time_slot}** — {st_task.task.name} ({st_task.task.duration} min)"
            checked = st.checkbox(label, value=st_task.is_completed, key=f"done_{st_task.time_slot}")
            if checked and not st_task.is_completed:
                next_task = st_task.mark_complete()
                if next_task is not None:
                    st.session_state.tasks.append({
                        "name":      next_task.name,
                        "category":  next_task.category,
                        "duration":  next_task.duration,
                        "priority":  next_task.priority,
                        "frequency": next_task.frequency,
                        "time":      next_task.time,
                        "notes":     next_task.notes,
                    })
                    st.toast(f"'{next_task.name}' rescheduled for {next_task.due_date}.")

        st.caption(schedule.generate_summary())

    expander_label = (
        f"AI Schedule Analysis (via {model_id})"
        if st.session_state.ai_used
        else "Scheduling reasoning"
    )
    with st.expander(expander_label):
        st.markdown(st.session_state.reasoning)
