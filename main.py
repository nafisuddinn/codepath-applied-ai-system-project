from pawpal_system import Owner, Pet, Task, Scheduler, Schedule, ScheduledTask
from datetime import date

today = date.today().strftime("%Y-%m-%d")

# ---------------------------------------------------------------------------
# Owner & Pets
# ---------------------------------------------------------------------------

owner = Owner(name="Alex", time_available=120, preferences=["morning walks"])

dog = Pet(name="Biscuit", species="dog", breed="Beagle", age=3)
cat = Pet(name="Luna",    species="cat", breed="Siamese", age=5,
          special_needs=["daily eye drops"])

owner.add_pet(dog)
owner.add_pet(cat)

# ---------------------------------------------------------------------------
# Section 1 — Normal schedules (no conflicts)
# ---------------------------------------------------------------------------

print("=" * 60)
print("  SECTION 1: Normal schedules (cross-pet conflicts detected)")
print("=" * 60)

dog_scheduler = Scheduler(owner=owner, pet=dog)
dog_scheduler.add_task(Task(name="Morning Walk", category="walk",      duration=30, priority=5, time="08:00"))
dog_scheduler.add_task(Task(name="Breakfast",    category="feeding",   duration=10, priority=5, time="08:30"))
dog_scheduler.add_task(Task(name="Fetch / Play", category="enrichment",duration=20, priority=3, time="12:30"))

cat_scheduler = Scheduler(owner=owner, pet=cat)
cat_scheduler.add_task(Task(name="Eye Drops", category="meds",    duration=5,  priority=5, time="09:00"))
cat_scheduler.add_task(Task(name="Cat Meal",  category="feeding", duration=10, priority=5, time="09:10"))

dog_schedule = dog_scheduler.generate_schedule(date=today)
cat_schedule = cat_scheduler.generate_schedule(date=today)

print(dog_schedule.display_plan())
print()
print(cat_schedule.display_plan())

# Check for conflicts across both normal schedules
clean_warnings = dog_scheduler.detect_conflicts(dog_schedule, cat_schedule)
print()
if clean_warnings:
    for w in clean_warnings:
        print(w)
else:
    print("No conflicts detected across both schedules.")

# ---------------------------------------------------------------------------
# Section 2 — Same-pet conflict: two tasks overlap for the dog
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("  SECTION 2: Same-pet conflict (Biscuit)")
print("=" * 60)
print("  Grooming starts at 08:15, while Morning Walk (08:00, 30 min)")
print("  is still running — expected overlap warning.")
print()

# Build the conflicting schedule manually so we can force the overlap.
# generate_schedule() assigns slots sequentially and would never do this.
conflict_dog = Schedule(date=today, owner=owner, pet=dog)
conflict_dog.scheduled_tasks = [
    ScheduledTask(task=Task(name="Morning Walk", category="walk",     duration=30, priority=5), time_slot="08:00"),
    ScheduledTask(task=Task(name="Grooming",     category="grooming", duration=20, priority=4), time_slot="08:15"),  # starts 15 min into the walk
]

same_pet_warnings = dog_scheduler.detect_conflicts(conflict_dog)
for w in same_pet_warnings:
    print(w)

# ---------------------------------------------------------------------------
# Section 3 — Cross-pet conflict: dog's walk and cat's vet visit overlap
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("  SECTION 3: Cross-pet conflict (Biscuit vs Luna)")
print("=" * 60)
print("  Dog's walk (08:00, 30 min) and cat's vet visit (08:20, 40 min)")
print("  overlap — owner cannot attend both at the same time.")
print()

conflict_cat = Schedule(date=today, owner=owner, pet=cat)
conflict_cat.scheduled_tasks = [
    ScheduledTask(task=Task(name="Morning Walk", category="walk", duration=30, priority=5), time_slot="08:00"),
    ScheduledTask(task=Task(name="Vet Visit",    category="meds", duration=40, priority=5), time_slot="08:20"),  # starts 20 min into the walk
]

cross_pet_warnings = dog_scheduler.detect_conflicts(conflict_cat)
for w in cross_pet_warnings:
    print(w)

# ---------------------------------------------------------------------------
# Section 4 — Edge case: tasks share only an endpoint (no conflict)
# ---------------------------------------------------------------------------

print()
print("=" * 60)
print("  SECTION 4: Clean handoff — tasks share only an endpoint")
print("=" * 60)
print("  Morning Walk ends at 08:30, Breakfast starts at 08:30 exactly.")
print("  This is a clean handoff, not an overlap — no warning expected.")
print()

handoff_schedule = Schedule(date=today, owner=owner, pet=dog)
handoff_schedule.scheduled_tasks = [
    ScheduledTask(task=Task(name="Morning Walk", category="walk",    duration=30, priority=5), time_slot="08:00"),
    ScheduledTask(task=Task(name="Breakfast",    category="feeding", duration=10, priority=5), time_slot="08:30"),
]

edge_warnings = dog_scheduler.detect_conflicts(handoff_schedule)
if edge_warnings:
    for w in edge_warnings:
        print(w)
else:
    print("No conflicts detected — clean handoff confirmed.")
