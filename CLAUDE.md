# Pakistan Housing Price EDA — Claude Code Project Guide

## Project Purpose
This is a **learning-first** EDA portfolio project. The user is building data science skills from scratch using the Zameen.com Pakistan Housing Dataset. Every session must **teach concepts thoroughly** while producing production-quality code.

## Dual Goals
1. **LEARNING**: Explain every concept, function, and decision in depth. The user is learning pandas, visualization, and data thinking. Treat this like a 1-on-1 mentorship session.
2. **PORTFOLIO**: The final Jupyter Notebook must be polished, narrative-driven, and GitHub-ready. Write code that demonstrates professional skill.

## How Sessions Work
- The project is divided into **12 sessions** defined in `SESSIONS.md`
- User starts a session by running `/session <number>` (e.g., `/session 1`)
- Each session has: learning objectives, concepts to teach, code to write, and a checkpoint
- **ALWAYS read `SESSIONS.md` for the current session's full instructions before starting**
- **ALWAYS check `PROGRESS.md` to see what's already been completed**
- After completing a session, update `PROGRESS.md` with status and key notes

## Teaching Style
- Explain the **WHY** before the **HOW** — why are we doing this step? What problem does it solve?
- Use analogies and real-world examples when explaining pandas concepts
- After writing each code block, explain what every line does
- Anticipate common beginner mistakes and address them proactively
- When the user asks a question, answer it fully — don't rush to the next step
- Use print statements and intermediate outputs so the user can SEE what's happening

## Tech Stack
- Python 3.10+
- pandas, numpy, matplotlib, seaborn, plotly (optional)
- Jupyter Notebook (`.ipynb`)
- All work happens in `notebooks/01_eda_analysis.ipynb`

## Project Structure
```
pakistan-housing-eda/
├── CLAUDE.md              # This file — Claude reads this every session
├── SESSIONS.md            # Detailed session-by-session guide
├── PROGRESS.md            # Session completion tracker
├── .claude/commands/      # Custom slash commands
│   └── session.md         # /session command definition
├── data/
│   └── raw/               # Original CSV from Kaggle
├── notebooks/
│   └── 01_eda_analysis.ipynb
├── images/                # Exported chart PNGs
├── .gitignore
├── README.md
└── requirements.txt
```

## Code Standards
- Every code cell in the notebook MUST have a markdown cell above it explaining purpose
- Use descriptive variable names: `df_clean` not `df2`
- Add inline comments for non-obvious operations
- Charts: always include title, axis labels, proper figsize (10,6 minimum)
- Use `sns.set_style('whitegrid')` and a consistent palette throughout

## Learning vs. Portfolio Separation
- **Learning happens ONLY in the conversation** — detailed explanations, analogies, beginner breakdowns, and Q&A stay in the chat. NEVER put these in the notebook or repo.
- **The notebook is portfolio-only** — markdown cells should read like a professional data analyst's write-up, not a tutorial. Use concise, confident language (e.g., "Outliers above 500M PKR were removed" NOT "Let's learn what outliers are and why we remove them").
- **No teaching comments in code** — inline comments should explain non-obvious logic, not teach syntax (e.g., `# exclude top 1% to reduce skew` is good, `# groupby groups the data by column` is not).
- **README.md should be portfolio-grade** — project overview, key findings, tech stack, and visuals. No mention of "learning project" or "beginner."

## Git Workflow
- **Initialize git** at the start of Session 1 with `git init` and an initial commit
- **Commit after every session** with a clear, descriptive message (e.g., `feat: add data loading and initial exploration`, `feat: add price distribution visualizations`)
- **Commit message format**: use conventional style — `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- **Push to GitHub** after each session: `git push origin main`
- **Never commit** `.env` files, API keys, large datasets, or notebook checkpoints — these should be in `.gitignore`
- After completing a session, Claude should prompt the user to commit and push

## Key Commands
- `pip install -r requirements.txt` — install dependencies
- `jupyter notebook` — launch notebook server

## Pakistan-Specific Domain Knowledge
- Price units: 1 Lakh = 100,000 PKR; 1 Crore = 10,000,000 PKR
- Area units: 1 Marla ≈ 272.25 sq ft; 1 Kanal = 20 Marla ≈ 5,445 sq ft
- Major cities in dataset: Islamabad, Lahore, Karachi, Rawalpindi, Faisalabad
- Premium areas: DHA, Bahria Town, Gulberg — explain these when they appear

## When Compacting
When compacting, always preserve: current session number, what code has been written so far in the notebook, any user questions that were asked, and the state of PROGRESS.md.
