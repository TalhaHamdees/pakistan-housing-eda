---
argument-hint: [session_number]
description: Quiz yourself on concepts from completed sessions to reinforce learning.
---

Generate a quick quiz based on completed sessions.

1. Check `PROGRESS.md` to see which sessions are completed
2. If a session number ($ARGUMENTS) is provided, quiz on that session's concepts
3. If no number, quiz on all completed sessions

## Quiz Format
- Ask 5 questions, one at a time
- Mix of types: "What does X do?", "When would you use X vs Y?", "What's wrong with this code?"
- Wait for the user's answer before revealing the correct one
- After each answer, explain WHY — reinforce the concept
- Give a score at the end with encouragement

## Rules
- Questions should be practical, not trivia
- Include at least one question that references actual data from our project
- Be encouraging even for wrong answers — frame them as learning moments
