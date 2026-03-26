# PawPal+ Project Reflection

## 1. System Design

Three core actions that this app should be able to handle are a user adding pets that they want to keep track of, adding tasks that a user wants to do with their pets (e.g. scheduled walks, vet visits, purchasing food, visiting the groomer etc.), and seeing the tasks that are assigned either to each specific pets or tasks in general.

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design that I brainstormed had 4 classes. These classes were Owner, Pet, Task, and Scheduler. The Owner class initially only had a list of pets, with a methods to add and remove pets from the list. The Pet class had identifying information as well as a list of tasks that each pet had. There were methods to update the last vet visit, add a task, remove a task, and update a given task. The Task class had an ID, description, and priority, with methods to modify description and priority. The Scheduler class has a pet that its attached to and a queue of Tasks that are waiting to be automatically added to each pet, with methods to add or remove a scheduled task, modify the frequency of the repeated task, and a method to automatically append a queued task to a pet.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design changed a lot during implementation. One change that occured was that priority within the Task class was removed. I made this change because each Task has a specific time designated for it to occur, and because of each Task having a designated time, there should be no time period where two Tasks are happening simultaneously. Therefore, due to the specificity of when Tasks are occuring, priority got removed.

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
