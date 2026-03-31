from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date, datetime, timedelta


# ---------------------------------------------------------------------------
# Data classes — pure data holders, no scheduling logic
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a human-readable summary of the pet."""
        # Join special needs into a comma-separated string, or show "none"
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.breed} {self.species}, age {self.age}) — special needs: {needs}"


@dataclass
class Task:
    name: str
    category: str       # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    duration: int       # minutes
    priority: int       # 1 (low) – 5 (high)
    frequency: str = "daily"
    notes: str = ""
    time: str = ""          # preferred start time in "HH:MM" format, e.g. "08:00" (optional)
    due_date: str = ""      # "YYYY-MM-DD" — set to today when a task is first created

    def get_summary(self) -> str:
        """Return a one-line description of the task."""
        due = f", due {self.due_date}" if self.due_date else ""
        return f"[P{self.priority}] {self.name} ({self.category}, {self.duration} min, {self.frequency}{due})"

    def next_occurrence(self) -> "Task":
        """
        Return a new Task instance scheduled for the next occurrence.

        The due date is calculated from due_date if it is set, otherwise
        today is used as the baseline so there is always a valid starting
        point for the timedelta arithmetic.

        Daily  → baseline + 1 day
        Weekly → baseline + 7 days

        A new instance is returned rather than mutating the current one so
        the completed task's record stays intact and the caller decides what
        to do with the next occurrence (add it to the scheduler, display it, etc.)
        """
        INTERVAL = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}

        # Parse the stored due_date, or fall back to today
        if self.due_date:
            baseline = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        else:
            baseline = date.today()

        delta = INTERVAL.get(self.frequency)
        if delta is None:
            raise ValueError(
                f"Cannot compute next occurrence for frequency '{self.frequency}'. "
                "Only 'daily' and 'weekly' are supported."
            )

        next_due = (baseline + delta).strftime("%Y-%m-%d")

        # dataclasses.replace() would be cleaner, but a direct constructor call
        # is explicit and avoids importing dataclasses here
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            notes=self.notes,
            time=self.time,
            due_date=next_due,
        )


@dataclass
class ScheduledTask:
    task: Task
    time_slot: str      # "HH:MM" string, e.g. "08:00"
    is_completed: bool = False

    def mark_complete(self) -> Optional["Task"]:
        """
        Mark this task as completed and return the next occurrence.

        For 'daily' and 'weekly' tasks, delegates to Task.next_occurrence()
        to produce a ready-to-schedule Task with its due_date already set.

        Returns None for any other frequency so callers can check:
            next_task = scheduled_task.mark_complete()
            if next_task:
                scheduler.add_task(next_task)
        """
        self.is_completed = True

        # Only generate a next occurrence for recurring frequencies
        if self.task.frequency in ("daily", "weekly"):
            return self.task.next_occurrence()
        return None

    def get_label(self) -> str:
        """Return a display-friendly label showing slot, status, name, and duration."""
        status = "✓" if self.is_completed else "○"
        return f"{self.time_slot}  {status}  {self.task.name} ({self.task.duration} min)"


# ---------------------------------------------------------------------------
# Regular classes — hold behaviour / mutable state
# ---------------------------------------------------------------------------

class Owner:
    """
    Represents the pet owner.

    Holds the owner's identity, how many minutes they have available each day,
    their care preferences, and the list of pets they own. The time_available
    field is read live by Scheduler.generate_schedule() each run so that any
    updates made after the Scheduler was created are always reflected.
    """

    def __init__(self, name: str, time_available: int, preferences: Optional[List[str]] = None):
        self.name: str = name
        self.time_available: int = time_available   # total minutes available per day
        self.preferences: List[str] = preferences or []
        self._pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Append a Pet to the owner's internal list."""
        self._pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of the pet list so callers can't mutate the internal state."""
        return list(self._pets)


class Schedule:
    """
    The finished daily plan for a single pet on a single date.

    Stores an ordered list of ScheduledTask items and knows how to display,
    summarise, and filter them. Schedule is the output of Scheduler — it holds
    results, not planning logic. Both owner and pet are stored here so the
    schedule is self-contained and can be displayed or passed around without
    needing external context.
    """

    def __init__(self, date: str, owner: Owner, pet: Pet):
        self.date: str = date
        # Storing owner and pet on the schedule makes it self-contained —
        # we can display whose plan it is without passing context externally.
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.scheduled_tasks: List[ScheduledTask] = []

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """
        Append a ScheduledTask to the plan.

        Raises ValueError if the time slot is already occupied, preventing
        overlapping tasks from being silently added.
        """
        occupied_slots = {st.time_slot for st in self.scheduled_tasks}
        if scheduled_task.time_slot in occupied_slots:
            raise ValueError(
                f"Time slot {scheduled_task.time_slot} is already occupied."
            )
        self.scheduled_tasks.append(scheduled_task)

    def get_total_duration(self) -> int:
        """Sum the duration of every task currently in the schedule."""
        return sum(st.task.duration for st in self.scheduled_tasks)

    def display_plan(self) -> str:
        """
        Return a formatted, human-readable version of the daily plan.

        Tasks are sorted by time slot so the output is always chronological,
        regardless of the order they were added.
        """
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.date}."

        lines = [
            f"Daily Plan for {self.pet.name}  —  {self.date}  (Owner: {self.owner.name})",
            "-" * 55,
        ]

        # Sort by time_slot string; "HH:MM" format sorts correctly lexicographically
        for st in sorted(self.scheduled_tasks, key=lambda x: x.time_slot):
            lines.append(st.get_label())

        lines.append("-" * 55)
        total = self.get_total_duration()
        lines.append(f"Total: {total} min / {self.owner.time_available} min available")
        return "\n".join(lines)

    def generate_summary(self) -> str:
        """Return a short one-line summary of the plan."""
        count = len(self.scheduled_tasks)
        total = self.get_total_duration()
        remaining = self.owner.time_available - total
        return (
            f"{count} task(s) scheduled for {self.date}, "
            f"totaling {total} min — {remaining} min remaining."
        )

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[ScheduledTask]:
        """
        Return a filtered subset of scheduled_tasks.

        Parameters
        ----------
        completed : bool or None
            - True  → return only tasks that have been marked complete
            - False → return only tasks still pending
            - None  → completion status is not used as a filter (default)

        pet_name : str or None
            - A name string → return tasks only if this schedule belongs to
              that pet (case-insensitive match against self.pet.name)
            - None → pet name is not used as a filter (default)

        Both filters are applied together with AND logic, so passing both
        arguments narrows the results further.  Passing neither returns the
        full list — equivalent to reading self.scheduled_tasks directly.

        Examples
        --------
        # All completed tasks for any pet
        schedule.filter_tasks(completed=True)

        # Pending tasks that belong to "Biscuit"
        schedule.filter_tasks(completed=False, pet_name="Biscuit")

        # All tasks on a schedule regardless of status (no-op filter)
        schedule.filter_tasks()
        """
        results = self.scheduled_tasks

        # Filter by completion status when the caller specifies True or False.
        # Checking `is not None` lets False through — a plain `if completed:`
        # would incorrectly skip the filter when completed=False.
        if completed is not None:
            results = [st for st in results if st.is_completed == completed]

        # Filter by pet name when provided.
        # Case-insensitive so "biscuit" and "Biscuit" both match.
        if pet_name is not None:
            if self.pet.name.lower() != pet_name.lower():
                return []   # this schedule belongs to a different pet entirely
            # pet matches — no per-task filtering needed since every task in
            # this schedule already belongs to self.pet

        return results


class Scheduler:
    """
    The planning engine that turns a pool of Tasks into a Schedule.

    Scheduler is created per-pet: one Scheduler manages one pet's task pool
    and produces one Schedule per day. It is responsible for all decisions
    about which tasks are selected, in what order, and why — keeping that
    logic out of both Task (data) and Schedule (output).

    Core algorithm (generate_schedule):
        Sort by priority → filter to daily → walk the list greedily →
        assign consecutive time slots → skip anything that exceeds the budget.

    Conflict detection (detect_conflicts) is a separate, read-only concern
    that can compare any number of Schedule objects without modifying them.
    """

    def __init__(self, owner: Owner, pet: Pet):
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.tasks: List[Task] = []
        # Reasoning notes are populated during generate_schedule() and read by
        # explain_reasoning(), so both methods stay in sync automatically.
        self._last_reasoning: List[str] = []

    def add_task(self, task: Task) -> None:
        """Add a Task to the pool the scheduler can draw from."""
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        """
        Remove every task whose name matches (case-insensitive).

        Using a list comprehension keeps only tasks that do NOT match,
        which is simpler and safer than mutating the list while iterating.
        """
        self.tasks = [t for t in self.tasks if t.name.lower() != name.lower()]

    def filter_by_priority(self, min_priority: int = 1) -> List[Task]:
        """
        Return all tasks whose priority is at or above min_priority.

        Uses >= (inclusive) so that passing min_priority=3 keeps tasks
        ranked 3, 4, and 5 — not just tasks strictly above 3. The default
        of 1 means all tasks pass unless a higher threshold is specified.

        This does not modify self.tasks; it returns a new filtered list so
        the original pool stays intact for future scheduling runs.

        Example
        -------
        # Keep only high-priority tasks (P4 and P5)
        urgent = scheduler.filter_by_priority(min_priority=4)
        """
        return [t for t in self.tasks if t.priority >= min_priority]

    def sort_tasks(self) -> List[Task]:
        """
        Sort tasks by priority descending (5 = most urgent first), then by
        duration ascending as a tiebreaker (shorter tasks first so more tasks
        can fit within the time limit).
        """
        return sorted(self.tasks, key=lambda t: (-t.priority, t.duration))

    def sort_by_time(self) -> List[Task]:
        """
        Sort tasks by their preferred start time in ascending order.

        "HH:MM" strings compare correctly with plain string ordering because
        the format is zero-padded and fixed-width — "08:00" < "09:30" < "14:00"
        holds true both numerically and lexicographically.

        Tasks with no time set (empty string "") sort to the front since ""
        is less than any "HH:MM" string. They are moved to the end instead by
        using a fallback of "99:99" so unscheduled tasks don't crowd the top.
        """
        return sorted(
            self.tasks,
            key=lambda t: t.time if t.time else "99:99"
        )

    def generate_schedule(self, date: str) -> Schedule:
        """
        Build and return a Schedule for the given date.

        Algorithm:
          1. Read time_available fresh from owner (avoids stale snapshot).
          2. Separate daily tasks (eligible today) from non-daily tasks (skipped).
          3. Sort eligible tasks by priority then duration.
          4. Walk through the sorted list, assigning consecutive time slots
             starting at 08:00 and advancing by each task's duration.
          5. Skip any task that would push the total past the time limit.
          6. Record a reasoning note for every decision made.
        """
        self._last_reasoning = []
        schedule = Schedule(date=date, owner=self.owner, pet=self.pet)

        # Read directly from owner so changes to time_available are always respected
        time_limit = self.owner.time_available
        time_used = 0

        # Separate eligible (daily) from non-daily tasks up front
        eligible = [t for t in self.sort_tasks() if t.frequency == "daily"]
        non_daily = [t for t in self.tasks if t.frequency != "daily"]

        if non_daily:
            names = ", ".join(t.name for t in non_daily)
            self._last_reasoning.append(
                f"Skipped non-daily tasks (need manual scheduling): {names}."
            )

        # Time slots are computed as datetime objects so arithmetic is exact,
        # then formatted back to "HH:MM" strings for storage.
        current_time = datetime.strptime("08:00", "%H:%M")

        for task in eligible:
            if time_used + task.duration > time_limit:
                # Task doesn't fit — log why and move on to the next one
                self._last_reasoning.append(
                    f"Skipped '{task.name}' ({task.duration} min) — would exceed "
                    f"the {time_limit}-min daily limit."
                )
                continue

            time_slot = current_time.strftime("%H:%M")
            schedule.add_task(ScheduledTask(task=task, time_slot=time_slot))

            self._last_reasoning.append(
                f"Scheduled '{task.name}' at {time_slot} "
                f"(priority {task.priority}, {task.duration} min)."
            )

            # Advance the clock by this task's duration for the next slot
            time_used += task.duration
            current_time += timedelta(minutes=task.duration)

        return schedule

    def explain_reasoning(self) -> str:
        """
        Return a plain-English explanation of the last schedule generated.

        explain_reasoning() reads _last_reasoning, which is populated by
        generate_schedule(), so they're always in sync without needing arguments.
        """
        if not self._last_reasoning:
            return "No schedule has been generated yet. Call generate_schedule() first."
        return "Scheduling reasoning:\n" + "\n".join(
            f"  • {note}" for note in self._last_reasoning
        )

    @staticmethod
    def _slot_to_minutes(time_slot: str) -> int:
        """Convert a 'HH:MM' string to total minutes since midnight."""
        hours, minutes = map(int, time_slot.split(":"))
        return hours * 60 + minutes

    def detect_conflicts(self, *schedules: "Schedule") -> List[str]:
        """
        Check one or more Schedule objects for overlapping tasks and return
        a list of human-readable warning strings — one per conflict found.
        Returns an empty list when there are no conflicts.

        This is intentionally lightweight: it warns rather than raises so the
        app keeps running and the owner can decide how to resolve each clash.

        Overlap rule
        ------------
        Two tasks A and B overlap when A starts before B ends AND B starts
        before A ends:
            start_A < end_B  AND  start_B < end_A
        This is the standard interval-overlap test. Tasks that share only an
        endpoint (A ends exactly when B starts) are NOT flagged — that is a
        clean handoff, not a conflict.

        Parameters
        ----------
        *schedules : Schedule
            Pass one schedule to check it against itself, or multiple schedules
            to also catch cross-pet conflicts (e.g. dog's walk vs cat's vet
            visit when the owner can only be in one place at a time).
        """
        warnings: List[str] = []

        # Flatten all scheduled tasks into (ScheduledTask, pet_name) pairs so
        # we can compare across schedules while keeping context for the message.
        all_tasks: List[tuple] = []
        for schedule in schedules:
            for st in schedule.scheduled_tasks:
                all_tasks.append((st, schedule.pet.name))

        # Compare every unique pair — avoid (i, j) and (j, i) duplicates
        for i in range(len(all_tasks)):
            for j in range(i + 1, len(all_tasks)):
                st_a, pet_a = all_tasks[i]
                st_b, pet_b = all_tasks[j]

                # Convert slots to minutes so arithmetic is straightforward
                start_a = self._slot_to_minutes(st_a.time_slot)
                end_a   = start_a + st_a.task.duration

                start_b = self._slot_to_minutes(st_b.time_slot)
                end_b   = start_b + st_b.task.duration

                # Standard interval overlap: A starts before B ends, B starts before A ends
                if start_a < end_b and start_b < end_a:
                    same_pet = pet_a == pet_b
                    scope    = f"{pet_a}" if same_pet else f"{pet_a} and {pet_b}"
                    warnings.append(
                        f"WARNING: Conflict for {scope} — "
                        f"'{st_a.task.name}' ({st_a.time_slot}, {st_a.task.duration} min) "
                        f"overlaps with "
                        f"'{st_b.task.name}' ({st_b.time_slot}, {st_b.task.duration} min)."
                    )

        return warnings
