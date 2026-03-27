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

The constraints that my schedule considers is time. This matters the most because while priority can be held by the human, the amount of tasks and the time that they need to happen is the hardest to keep track of, which is why this application was built in the first place. Therefore, there was a lot of emphasis placed on tracking exact times and warning when two tasks conflict chronologically. This warning does not prevent the user from any functionality however, as some tasks can be done simultaneously and some cannot, which is up to the user's judgement.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is checking exact time that a Task should be either done by or attempted, rather than a period of time for that task to be dealt with. I made this tradeoff because each task can have unpredictable time demands associated with them. For example, taking a pet to the vet may take more or less time depending on traffic or how busy the vet is, so checking for exact time makes it way more flexible than rigidly scheduling blocks of time off incase too little time is allotted.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for the majority of the debugging and refactoring. I asked it about holes in the app logic and architected an application through many back-and-forths with the AI. The most helpful prompts were the most detailed, which spelled out exactly what I wanted done, what I did not want done, and what the end product should look like. This gave AI the best path to follow in achieving what I envision in my head.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment I did not accept an AI suggestion as-is is when I asked it to help implement the pawpal_system.py logic into app.py so that the user could interact with the application and get the desired functionality. It wanted to overhaul the whole UI, so I asked it to change as little as possible while achieving the desired functionality. I evaluated this by looking at the thinking it produces while making changes as well as checking each edit before I give the final approval, making sure that the code is exactly how I want it.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the class methods within test_pawpal_system and the UI logic by running the application myself and running through how an end user would use the application. These tests are important because not only do they ensure that the logic within the app works, but also that the end user does not come across any weird bug when actually interacting with the app that app.py may have.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am pretty confident that my scheduler works. Some edge cases that I would test for next time is a lot more user input, as there are a lot of test cases for the logic behind the app already, but the app itself can be a large error point, especially as AI cannot interact with the app like I can.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with how the AI can do a large amount of work when it comes to creating tests and giving me feedback on what has already been implemented.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would improve the UI and make sure that the logic wihtin the UI is more airtight by spending more time debugging and trying to find weird user edge cases that the end user discover while legitmately using my application or out of boredom to see where the limits of the app truly lie.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is definitely a strong and powerful tool, but like all tools, it needs to be wielded with intent. Without specificity, AI can definitely start heading the wrong direction very quickly and create lots of damage that will take a lot of time to correct. So, the best way to work with AI is incrementally with a lot of guard rails, so that if a mistake is spotted, it is easier to roll back and inform AI about its mistake.