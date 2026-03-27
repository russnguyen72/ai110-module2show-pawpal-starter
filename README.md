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

## Smarter Scheduling

Within the app, it can filter tasks displayed by a specific pet, whether a task is pending or completed, or a combination of both. It can also sort tasks by time, even if it is not inserted in time order.

## Testing PawPal+

```bash
python -m pytest tests/test_pawpal.py
```

The test suite provided tests a myriad of different functions with different edge cases. It tests all methods of each class. 
- Task: Tests update methods
- Pet: Tests adding and removing tasks safely, as well as updating a non-existent task ID safely without crashing. 
- Scheduler: Tests pet management, task retrival, due date filtering, sorting time in ascending order, recurring time completion, edge cases for when there is unknown pet or unknown task, and conflict detection. 
- Owner, it tests adding a pet adds to both Owner and Scheduler's pet list, remvoing a pet removes from both, and both pet list fields reference the same list object.

**Confidence Level:** ⭐⭐⭐⭐⭐