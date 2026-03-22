# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

**Core user actions identified:**
1. **Add/manage pets** — Enter pet info (name, species, age) linked to an owner profile
2. **Add/edit care tasks** — Create tasks with duration, priority, and category (walk, feeding, meds, grooming, enrichment)
3. **Generate a daily schedule** — Produce an optimized daily plan that respects time constraints and task priorities, with reasoning explanations

**Classes and responsibilities:**
- **Owner** — Holds owner name and available minutes per day; owns a list of Pets
- **Pet** — Stores pet name, species, and age; holds a list of Tasks specific to that pet
- **Task** — Represents a single care activity with title, duration, priority, and category
- **Scheduler** — Takes an Owner (with Pets/Tasks) and available time, then produces a Schedule sorted by priority and fitted within time constraints
- **Schedule** — Holds the ordered list of scheduled tasks and provides explanation/reasoning for the plan

**b. Design changes**

- After reviewing the skeleton with AI, the initial design held up well — no structural changes were needed at this stage.
- One consideration was whether `Schedule` should track which pet each task belongs to (for richer explanations). I deferred this per YAGNI — the current design keeps things simple, and we can add pet-task association later if the UI requires it.
- The `Scheduler` was kept stateless (static methods only) to make it easy to test without instantiation overhead.

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
