# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

# Smart Scheduling

## Sorting & Filtering

Two sort strategies live on Scheduler:

sort_tasks() sorts by priority descending, duration ascending — highest urgency first, shortest tasks as a tiebreaker to pack more into the time budget
sort_by_time() sorts by the task's preferred time field using a lambda key on "HH:MM" strings, which sort correctly lexicographically because the format is zero-padded. Tasks with no time set fall to the bottom via a "99:99" sentinel.
Filtering is split between two classes:

Scheduler.filter_by_priority(min_priority) narrows the task pool before scheduling — uses >= so the threshold is inclusive
Schedule.filter_tasks(completed, pet_name) narrows the already-scheduled tasks by completion status and/or pet name with AND logic. The is not None guard ensures completed=False isn't skipped as a falsy value.

## Automating Recurring Tasks

Task gained a due_date field and a next_occurrence() method. When called, it reads due_date as a baseline (falling back to today if unset) and adds a timedelta — +1 day for daily, +7 days for weekly. It returns a new Task instance rather than mutating the original, preserving the completed record.

ScheduledTask.mark_complete() ties it together: it flips is_completed, calls next_occurrence() if the task is recurring, and returns the new Task (or None for one-offs). The caller pattern is simply:

next_task = scheduled_task.mark_complete()
if next_task:
scheduler.add_task(next_task)

## Conflict Detection

Scheduler.detect_conflicts(\*schedules) accepts one or more Schedule objects, flattens all their tasks into a single list, then compares every unique pair using the standard interval-overlap test:

start_A < end_B AND start_B < end_A

Times are converted from "HH:MM" strings to minutes since midnight via \_slot_to_minutes() so the arithmetic is straightforward. Strict < (not <=) means tasks that share only an endpoint are not flagged — a clean handoff is not a conflict. Warnings are returned as strings rather than raised as exceptions so the app keeps running and the owner sees all conflicts at once.

## Testing PawPal+

Using {python3 -m pytest}
Pytest runs the following tests that cover multiple fields.

test_mark_complete_changes_status : ScheduledTask.mark_complete() flips is_completed from False to True - 5/5 stars reliability testing.

test_adding_task_increases_scheduler_task_count : Scheduler.add_task() grows the task pool from 0 to 1 - 5/5 stars reliability testing.

test_sort_by_time_returns_chronological_order : Scheduler.sort_by_time() orders tasks by HH:MMascending; tasks with no time sort last - 5/5 stars reliability testing.

test_mark_complete_daily_task_creates_next_day_task : Marking a daily task complete returns a new Task with due_date advanced by exactly 1 day - 5/5 stars reliability testing.

test_detect_conflicts_flags_overlapping_time_slots : Scheduler.detect_conflicts() flags tasks whose time intervals overlap, and returns no warnings for clean back-to-back tasks - 5/5 stars reliability testing.

## Features

- Priority-Based Scheduling
  Generates a daily care plan by sorting tasks highest-priority first, using duration as a tiebreaker so shorter tasks of equal urgency slot in earlier. Tasks that would push the plan past the owner's available time are skipped automatically and logged with a reason.

- Sorting by Preferred Time
  Tasks can carry an optional preferred start time (HH:MM). sort_by_time() orders them chronologically using a lambda key on zero-padded time strings — no parsing required. Tasks with no preferred time sort to the end.

- Priority Filtering
  filter_by_priority(min_priority) narrows the task pool to tasks at or above a given urgency level before scheduling, letting the owner run "urgent tasks only" plans without deleting lower-priority tasks.

- Completion Filtering
  filter_tasks(completed, pet_name) lets the owner query a finished schedule by status (done / pending) and optionally by pet name. Both filters apply together so cross-pet schedules can be queried precisely.

- Daily & Weekly Recurrence
  Marking a task complete automatically generates the next occurrence. Daily tasks advance by one day; weekly tasks advance by seven. The completed record is preserved — a fresh Task instance is returned with the updated due_date so history is never overwritten.

- Conflict Warnings
  detect_conflicts() scans one or more schedules for overlapping time intervals using the standard interval-overlap test (start_A < end_B AND start_B < end_A). It catches both same-pet overlaps and cross-pet conflicts where the owner would need to be in two places at once. Warnings are returned as messages rather than exceptions so the app keeps running.

- Scheduling Reasoning
  Every decision made during schedule generation — which tasks were included and why, which were skipped and why — is logged and surfaced via explain_reasoning() in plain English.

- Multi-Pet Support
  Each pet gets its own Scheduler instance and independent daily plan. The owner's time budget is shared context across all schedulers, and detect_conflicts() can compare schedules across pets in a single call.

## Demo

![PawPal+ App Screenshot](<Screenshot 2026-03-31 at 7.05.22 PM.png>)
