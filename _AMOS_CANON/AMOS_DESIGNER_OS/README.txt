AMOS Designer OS (Starter Pack)
===============================

What this is
------------

A minimal, designer-first AMOS shell that you can unzip anywhere and run
without editing Python code. It gives you:

- One control file you edit: AMOS.brain
- A simple runtime: run_amos.py
- A small worker layer: workers.py
- Logging and growth notes in logs/ and memory/

It does NOT depend on any online API or large model. It is a structural shell
meant to keep your ideas, roles, and brain model organised and auditable.


How to run it
-------------

1. Open a terminal.
2. cd into the folder where you unzipped this project.
3. Make sure you have Python 3.9+ installed.
4. Run:

   python run_amos.py

You should see:

- Loaded brain sections
- Planner output
- Analyst output
- Auditor output
- Logs written to logs/amos.log
- Growth notes in memory/growth.log


How YOU interact with it
------------------------

You ONLY edit AMOS.brain.

- Update GOALS, CONSTRAINTS, BRAIN_MODEL, WORKER_ROLES.
- Change NEXT_ACTION to steer what AMOS focuses on next.
- Everything else is treated as a black box.

When you want to extend it with real AI code-writing ability, you can:

- Add an LLM client (e.g. OpenAI, local model) inside workers.py, or
- Use ChatGPT / other tools to generate safe patches to this project.

For now, this is a clean, deterministic container for your AMOS architecture
and reasoning design.
