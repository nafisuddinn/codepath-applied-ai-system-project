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

The schedular considered three constraints:

- Time : The owner of the pet would have to be on schedule with their time management,
  especially making sure not to push past a total limit.
- Priority : Tasks have a priority ranked from 1-5 and sorted by highest rank first.
  Regardless of the order added, a high ranking priority will come first.
- Frequency : Daily takss are eligible on any given run. WEekly or one-off tasks are  
   filterd out so they don't consume the day's budget.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- The scheduler uses a greedy algorithm so it picks tasks in priority order and takes each one if it fits, then moves on without reconsidering. This means a single large high priority task can block several smaller lowe priority tasks that would have fit together. This works because we can consider scenarios like where a dog's medication should always be scheduled even if it crowds out playtime, not optimized away in favor of fitting more lower priority tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I utilized Artificial Intelligence using a two step process in which I find the most effective. First, I defined my problem and task at hand by generating a plan with the LLM and then brainstorming the method we should take to complete the task. Asking the model to come with a plan by defining the different classes and methods allowed me to grasp the implemenatations that were needed.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One momemnt where I did not accept an AI suggestion was if it was making implementations without the proper documentation. Keeping comments with the code that the AI generated allowed for me to get a grasp easily on what I should expect for the code to do without having to determine line by line.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

Behaviors that mattered to me the most were accurately prioritizing tasks and keeping a count of the tasks we had. When creating any type of scheduler, the most important thing is being able to actually hold the tasks needed to be scheduled in the way they are supposed to. Especially for a pet scheduler, having priorities for pets are important.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that the scheduler works correctly. If I had more time, I would test edge cases across adding more people to the scheduler. Let's say a family takes care of a pet all together, there might be situations where different family members take care of the pet. So I would like to test adding more people into schedules for a pet.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am satisfied with the results the AI has given me. Using the workflow of planning first then implementing makes it easier on the AI to understand the task at hand.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the user experience, add ways to get multiple people involved. Multiple users can schedule to take care of the same pet.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One important thing I learned about designing systems is the different ways that the system can be planned. Using a UML diagram made it easy to visualize the relationships between the different entities, and by creating the UML -- creating the program was easier because of the visualization of entity relationships.
