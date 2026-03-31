import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("Your daily pet care planner.")

# ---------------------------------------------------------------------------
# Session state initialisation
# Streamlit reruns the whole script on every interaction, so we store
# all mutable data in st.session_state to persist it across reruns.
# ---------------------------------------------------------------------------

if "pets" not in st.session_state:
    st.session_state.pets = []         # list of dicts: {name, species, breed, age, special_needs}

if "tasks" not in st.session_state:
    st.session_state.tasks = []        # list of dicts: {name, category, duration, priority, notes}

if "schedule" not in st.session_state:
    st.session_state.schedule = None   # Schedule object from last run

if "reasoning" not in st.session_state:
    st.session_state.reasoning = ""    # explain_reasoning() output from last run

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

# Display registered pets
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
            # Each button needs a unique key to avoid Streamlit duplicate-widget errors
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
        task_notes     = st.text_input("Notes (optional)", placeholder="e.g. bring treats")

    if st.button("Add task"):
        st.session_state.tasks.append({
            "name":      task_name,
            "category":  task_category,
            "duration":  int(task_duration),
            "priority":  PRIORITY_MAP[task_priority],
            "frequency": task_frequency,
            "notes":     task_notes,
        })
        st.success(f"Added task: {task_name}")

# Display registered tasks
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

# Choose which pet to schedule for (if more than one exists)
pet_names = [p["name"] for p in st.session_state.pets]
selected_pet_name = st.selectbox(
    "Schedule for which pet?",
    options=pet_names if pet_names else ["— add a pet first —"],
    disabled=len(pet_names) == 0,
)

today = date.today().strftime("%Y-%m-%d")

if st.button("Generate schedule", type="primary", disabled=len(pet_names) == 0):
    # Guard: need at least one task to schedule
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # Build the domain objects from session state
        owner = Owner(
            name=owner_name,
            time_available=int(time_available),
            preferences=preferences,
        )

        # Find the selected pet dict and construct a Pet object
        pet_dict = next(p for p in st.session_state.pets if p["name"] == selected_pet_name)
        pet = Pet(
            name=pet_dict["name"],
            species=pet_dict["species"],
            breed=pet_dict["breed"],
            age=pet_dict["age"],
            special_needs=pet_dict["special_needs"],
        )

        # Build the Scheduler and load every registered task into it
        scheduler = Scheduler(owner=owner, pet=pet)
        for t in st.session_state.tasks:
            scheduler.add_task(Task(
                name=t["name"],
                category=t["category"],
                duration=t["duration"],
                priority=t["priority"],
                frequency=t["frequency"],
                notes=t["notes"],
            ))

        # Run the scheduling algorithm and store results in session state
        st.session_state.schedule  = scheduler.generate_schedule(date=today)
        st.session_state.reasoning = scheduler.explain_reasoning()

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
        # Render each scheduled task as a checkbox; checking it calls mark_complete()
        for st_task in sorted(scheduled, key=lambda x: x.time_slot):
            label = f"**{st_task.time_slot}** — {st_task.task.name} ({st_task.task.duration} min)"
            checked = st.checkbox(label, value=st_task.is_completed, key=f"done_{st_task.time_slot}")
            if checked and not st_task.is_completed:
                st_task.mark_complete()

        st.caption(schedule.generate_summary())

    with st.expander("Scheduling reasoning"):
        st.markdown(st.session_state.reasoning)
