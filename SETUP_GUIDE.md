# 🚀 Quick Start Guide — Using Claude Code for This Project

## What You Have

```
pakistan-housing-eda/
├── CLAUDE.md                    ← Claude reads this EVERY session (project context)
├── SESSIONS.md                  ← 12 detailed learning sessions
├── PROGRESS.md                  ← Auto-updated progress tracker
├── .claude/commands/
│   ├── session.md               ← /session <number> — start a session
│   ├── explain.md               ← /explain <concept> — deep dive on any concept
│   ├── review.md                ← /review [session] — check your work
│   └── quiz.md                  ← /quiz [session] — test your understanding
├── data/raw/                    ← PUT YOUR KAGGLE CSV HERE
├── notebooks/                   ← Notebook will be created in Session 1
├── images/                      ← Charts saved here automatically
├── requirements.txt
└── .gitignore
```

## Step 0: Download the Dataset (Do This First!)

1. Go to [Kaggle](https://www.kaggle.com) and search **"Zameen.com Pakistan Housing"**
2. Download the CSV file
3. Place it in `data/raw/` folder

## Step 1: Install Claude Code (If Not Already)

```bash
npm install -g @anthropic-ai/claude-code
```

## Step 2: Open Your Project

```bash
cd pakistan-housing-eda
claude
```

Claude Code will automatically read `CLAUDE.md` and know the entire project context.

## Step 3: Start Your First Session

```
/session 1
```

That's it. Claude will:
- Brief you on what you'll learn
- Walk you through each step
- Write code and explain every line
- Create the Jupyter notebook
- Update your progress tracker
- Commit your work to git

## Available Commands

| Command | What It Does |
|---------|-------------|
| `/session 3` | Start Session 3 (replace with any number 1-12) |
| `/explain groupby` | Get a deep explanation of any concept |
| `/explain "what is a KDE plot"` | Works with questions too |
| `/review` | Check overall project progress |
| `/review 4` | Review Session 4's work specifically |
| `/quiz` | Test yourself on all completed sessions |
| `/quiz 2` | Quiz on Session 2 concepts only |

## How Each Session Works

1. **Briefing** — Claude tells you what you'll learn and build
2. **Teach & Code** — Concepts explained → Code written → Output shown → Questions answered
3. **Wrap-up** — Summary, progress updated, git commit, next session preview

## Tips for Maximum Learning

- **Don't just watch Claude code.** Read every explanation. Ask questions with `/explain`.
- **Run the notebook yourself** alongside Claude. See the outputs with your own eyes.
- **After each session**, use `/quiz` to test yourself.
- **If Claude rushes**, just say: *"Slow down, explain that again"*
- **If you're curious about something**, just ask mid-session — Claude will answer then continue.
- **Use Plan Mode** (Shift+Tab twice) if you want Claude to explain its approach before coding.

## Session Overview (12 Sessions, ~20 hours total)

| Phase | Sessions | Focus |
|-------|----------|-------|
| **Data Loading** | 1-2 | Load data, understand every column, assess quality |
| **Data Cleaning** | 3-6 | Fix types, parse prices, standardize areas, handle outliers |
| **Analysis** | 7 | GroupBy, pivot tables, summary statistics |
| **Visualization** | 8-10 | 10 publication-quality charts |
| **Storytelling** | 11 | Write the investor memo narrative |
| **Publication** | 12 | Polish, README, push to GitHub |

## Resuming After a Break

Claude Code doesn't remember past sessions, but it doesn't need to — everything is in files:
- `PROGRESS.md` tells Claude what's done
- `SESSIONS.md` tells Claude what's next
- The notebook itself shows all completed work

Just open Claude Code and run `/session <next_number>`. It picks up right where you left off.

## If Something Goes Wrong

- **Context getting long?** Type `/compact` to summarize and free up space
- **Want to redo a session?** Just run `/session <number>` again
- **Notebook errors?** Ask Claude: *"The notebook has an error in cell X, please fix it"*
- **Need a break mid-session?** Just close Claude Code. Your notebook and progress are saved.

---

*Remember: This isn't a tutorial you're copying. It's YOUR project. Ask questions. Challenge the code. Understand everything. That's how you learn.*
