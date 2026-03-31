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
