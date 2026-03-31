# PawPal+ Project Reflection

## 1. System Design

1. Let a user be able to define the owner and their pet with information such as the owner's schedule and the breed + necessities of the pet.

2. Generate a daily schedule/routine that has restrictions and specifications revolving around the defined owner and pet.

3. Create tasks that have durations and priorities.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Data Classes (pure data holders using @dataclass)

Pet — Stores a pet's profile: name, species, breed, age, and any special needs. Has get_info() to return a readable summary.

Task — Represents a single care task with its category (walk, feeding, meds, etc.), how long it takes (duration), how urgent it is (priority 1–5), how often it recurs (frequency), and optional notes. Has get_summary() for a one-liner description.

ScheduledTask — Wraps a Task once it's been placed into a time slot. Tracks whether it's been completed. Has mark_complete() and get_label() for display.

Regular Classes (hold behavior and mutable state)

Owner — Stores the pet owner's name, how many minutes per day they have available, and their care preferences. Manages a list of pets via add_pet() / get_pets().

Schedule — The finished daily plan for a given date. Holds an ordered list of ScheduledTask items. Knows how to compute total time used (get_total_duration()), display the plan (display_plan()), and produce a short summary (generate_summary()).

Scheduler — The planning engine. Holds the Owner, Pet, a pool of Task objects, and a time_limit pulled from the owner's availability. Responsible for adding/removing tasks, sorting and filtering them by priority, building a Schedule that respects constraints (generate_schedule()), and explaining its choices in plain English (explain_reasoning()).

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

  One change that was made was the Schedule has a reference to a pet. At first, when the schedule was generated, there was no way to know whose play it was. Adding the pet to the schedule made it self contained.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
