---
argument-hint: <session_number>
description: Start a learning session for the Pakistan Housing EDA project. Each session teaches concepts and writes code.
---

You are starting **Session $ARGUMENTS** of the Pakistan Housing EDA project.

Follow this exact workflow:

## Step 1: Read Context
1. Read `SESSIONS.md` and find the section for Session $ARGUMENTS
2. Read `PROGRESS.md` to check what's already been completed
3. If previous sessions are marked incomplete, warn the user

## Step 2: Session Briefing
Before writing ANY code, give the user a brief overview:
- **Session Title** and goal
- **What you'll learn today** (list the concepts)
- **What you'll build today** (list the outputs)
- Estimated time: 1.5-2.5 hours

## Step 3: Teach & Build
Work through each step in the session guide:
- **Before each code block**: Explain the concept in depth. Use analogies. Explain WHY we're doing this.
- **Write the code**: Add it to the Jupyter notebook with proper markdown cells above each code cell.
- **After each code block**: Explain what every important line does. Show the output. Ask if the user has questions.
- **Pause at natural breakpoints** and check understanding

## Step 4: Session Wrap-up
At the end of the session:
1. Summarize what was learned
2. Update `PROGRESS.md` with completion status
3. Git commit with the session's commit message from SESSIONS.md
4. Preview what's coming in the next session

## Rules
- NEVER rush through concepts to finish faster
- If the user asks a question, answer it FULLY before moving on
- Show intermediate outputs — the user needs to SEE what the code does
- Write narrative markdown cells in the notebook — this is a portfolio piece
- Every chart must have: title, axis labels, proper figsize, saved to images/
