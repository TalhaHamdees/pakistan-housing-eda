# SESSION GUIDE — Pakistan Housing Price EDA

Each session is designed to take 1.5–2.5 hours. Complete them in order. Each session builds on the previous one.

---

## SESSION 1: Environment Setup & First Contact with Data
**Goal:** Get the project running and take your first look at real data.

### Concepts to Teach
- What is a virtual environment and why use one (analogy: a clean kitchen for each recipe)
- What is a Jupyter Notebook — cells, kernel, markdown vs code cells
- What `pd.read_csv()` actually does under the hood
- The difference between `.head()`, `.info()`, `.shape`, `.describe()` and when to use each
- What data types (dtypes) are and why they matter

### Steps
1. Create virtual environment and install dependencies from `requirements.txt`
2. Create the Jupyter notebook `notebooks/01_eda_analysis.ipynb`
3. Write the notebook title and introduction in a markdown cell
4. Load the CSV with `pd.read_csv()`
5. Run `.shape` — explain what rows and columns mean in context (each row = one property listing)
6. Run `.head(10)` — walk through each column and explain what it represents
7. Run `.info()` — explain dtypes, non-null counts, memory usage
8. Run `.describe()` — explain mean, std, min, 25%, 50%, 75%, max
9. Run `.describe(include='object')` — explain categorical summaries
10. Write a markdown cell: "First Impressions" — user writes what they notice

### Checkpoint
User should be able to answer: "How many listings are in this dataset? What columns exist? What looks messy?"

### Commit Message
`"Session 1: Initial data loading and exploration"`

---

## SESSION 2: Understanding Your Data Deeply
**Goal:** Build intuition about every column before touching anything.

### Concepts to Teach
- What are null/missing values and why they exist (data collection isn't perfect)
- What `.isnull().sum()` returns and how to interpret it
- What `.nunique()` tells you — cardinality concept
- What `.value_counts()` reveals — frequency distributions
- The difference between numerical and categorical data (and why it matters for analysis)
- What duplicate rows mean and why they happen

### Steps
1. Check missing values: `df.isnull().sum()` and `df.isnull().mean() * 100` (percentage)
2. Create a missing values summary table sorted by percentage
3. For each column, run `.value_counts()` — identify weird values, inconsistencies
4. Check for duplicates: `df.duplicated().sum()`
5. Examine the price column raw values — notice Lakh/Crore strings
6. Examine the area column raw values — notice mixed units (Marla, Kanal, etc.)
7. Examine location/city columns — how many unique cities? Any misspellings?
8. Write a markdown cell: "Data Quality Assessment" — summarize all findings

### Concepts Deep Dive
- Explain the difference between MCAR, MAR, MNAR (missing data mechanisms) in simple terms
- Explain cardinality: low (city — few values) vs high (price — many values)
- Explain why we investigate BEFORE we clean — you need to understand the mess before you fix it

### Checkpoint
User should have a complete picture of data quality issues and a mental plan for cleaning.

### Commit Message
`"Session 2: Deep data investigation and quality assessment"`

---

## SESSION 3: Data Cleaning — Fixing Column Names & Data Types
**Goal:** Start the cleaning process with the simpler tasks first.

### Concepts to Teach
- Why clean column names matter (no spaces, lowercase = easier to type, fewer bugs)
- String methods in pandas: `.str.lower()`, `.str.replace()`, `.str.strip()`
- What `astype()` does — type casting
- The `category` dtype — what it is, when to use it, memory benefits
- Method chaining in pandas — why `df.column.str.lower().str.replace()` works

### Steps
1. Clean column names: lowercase, underscores, remove special characters
2. Show before/after column names
3. Identify columns that need type conversion
4. Convert obvious numeric columns stored as strings
5. Convert categorical columns to `category` dtype — show memory savings with `.memory_usage()`
6. Handle date columns if present — `pd.to_datetime()`
7. Explain `errors='coerce'` — what happens to unconvertible values

### Checkpoint
All column names are clean, data types are correct for non-price/non-area columns.

### Commit Message
`"Session 3: Column name cleanup and data type corrections"`

---

## SESSION 4: Data Cleaning — Price Column (The Hard One)
**Goal:** Parse the messy price column into a single numeric format.

### Concepts to Teach
- Writing custom functions in Python and using them with pandas
- `df.apply()` — what it does, when to use it, and why it's slower than vectorized ops
- Regular expressions basics — `re.search()`, `re.findall()` (just enough to parse prices)
- The PKR unit system: Lakh (100K), Crore (10M), Arab (1B)
- Vectorized string operations vs `.apply()` — performance difference
- What `pd.to_numeric(errors='coerce')` does

### Steps
1. Examine raw price values: `df['price'].sample(20)` — see the variety
2. Identify all price formats present (e.g., "1.2 Crore", "45 Lakh", "5,000,000")
3. Write a `parse_price()` function step by step:
   - Strip whitespace and commas
   - Detect unit (Crore, Lakh, or plain number)
   - Multiply accordingly
   - Return as float
4. Test the function on 5-6 edge cases BEFORE applying to the full column
5. Apply to the full price column
6. Verify: check min, max, mean — do they make sense for Pakistani real estate?
7. Handle any remaining NaN values from failed conversions
8. Add a markdown cell explaining the PKR system for notebook readers

### Concepts Deep Dive
- Walk through the `parse_price` function line by line
- Explain defensive programming: why we handle edge cases
- Explain `try/except` in the context of data parsing
- Show what happens if you DON'T handle edge cases (the errors you'd get)

### Checkpoint
Price column is fully numeric in PKR. User can explain the parsing logic to someone else.

### Commit Message
`"Session 4: Price column parsing — Lakh/Crore to numeric PKR"`

---

## SESSION 5: Data Cleaning — Area Column & Feature Engineering
**Goal:** Standardize area measurements and create derived features.

### Concepts to Teach
- Why standardizing units matters (you can't compare Marla to Sq Ft directly)
- Dictionary mapping in pandas — using `.map()` with a dict
- Feature engineering concept — creating new columns from existing ones
- `price_per_sqft` — the most important derived metric in real estate
- Binning/bucketing continuous variables — `pd.cut()` and `pd.qcut()`

### Steps
1. Examine area column: identify all units present
2. Create a conversion dictionary: `{'Marla': 272.25, 'Kanal': 5445, ...}`
3. Split the area column into value and unit (or however the data is structured)
4. Multiply each value by its conversion factor to get square feet
5. Create `area_sqft` column
6. Create `price_per_sqft` = price / area_sqft
7. If dates exist: extract `year`, `month`, `day_of_week`
8. Bin bedrooms: group 7+ as "7+"
9. Verify all new columns with `.describe()` — do values make sense?

### Checkpoint
All areas in sq ft, `price_per_sqft` calculated, basic feature engineering done.

### Commit Message
`"Session 5: Area standardization and feature engineering"`

---

## SESSION 6: Handling Missing Values & Outliers
**Goal:** Make final decisions about missing data and remove impossible values.

### Concepts to Teach
- Imputation strategies: drop, fill with mean/median/mode — when each is appropriate
- Why median is usually better than mean for skewed data
- What outliers are — statistical definition (IQR method) vs domain knowledge approach
- Box plots as outlier visualization tools
- The tension between removing outliers and losing real data
- `.dropna()` vs `.fillna()` — parameters and behavior

### Steps
1. Review missing value summary from Session 2
2. For each column with missing values, decide: drop rows, impute, or drop column
3. Write the reasoning for each decision in a markdown cell
4. Implement the decisions
5. Show before/after row counts
6. Visualize price distribution with a box plot — identify outliers
7. Calculate IQR bounds: Q1 - 1.5*IQR and Q3 + 1.5*IQR
8. Also apply domain knowledge: price < 100,000 PKR is probably an error
9. Remove outliers, show before/after counts
10. Create `df_clean` — the final cleaned dataframe
11. Save to CSV: `data/cleaned_housing_data.csv`
12. Write summary markdown: "Cleaning Summary — X rows removed, Y imputed, Z columns dropped"

### Concepts Deep Dive
- Draw (in markdown) the IQR method visually
- Explain survivorship bias in data cleaning — we might be removing real luxury properties
- Discuss when NOT to remove outliers

### Checkpoint
Clean dataset saved. User can justify every cleaning decision.

### Commit Message
`"Session 6: Missing value handling, outlier removal, clean dataset saved"`

---

## SESSION 7: Summary Statistics & Grouped Analysis
**Goal:** Extract meaningful numbers from the clean data using groupby.

### Concepts to Teach
- `groupby()` — the split-apply-combine pattern (explain with a visual analogy)
- `.agg()` — applying multiple functions at once
- The difference between `mean` and `median` — when each tells a better story
- Pivot tables — `pd.pivot_table()` — when to use instead of groupby
- Cross-tabulation — `pd.crosstab()`
- Sorting and formatting output tables

### Steps
1. Overall `.describe()` with interpretation markdown
2. Group by city: median price, mean price_per_sqft, count — sorted by median price
3. Group by property type: same metrics
4. Group by bedrooms: mean price, median area, count
5. Cross-tab: city × property type (counts)
6. Pivot table: city × property type → median price
7. Pivot table: city × bedrooms → median price
8. **After EVERY table**, write 2-3 sentences of narrative insight
9. Identify the "story" — what patterns emerge?

### Concepts Deep Dive
- Walk through `groupby` step by step: what does the grouped object look like?
- Show `df.groupby('city').get_group('Lahore')` — peek inside a group
- Explain aggregation functions: count, sum, mean, median, std, min, max
- Explain named aggregation syntax: `.agg(avg_price=('price', 'mean'))`

### Checkpoint
User can write groupby chains from memory and explain what split-apply-combine means.

### Commit Message
`"Session 7: Summary statistics and grouped analysis with narrative"`

---

## SESSION 8: Visualization Foundations — Charts 1-4
**Goal:** Build the first 4 visualizations with proper styling.

### Concepts to Teach
- matplotlib vs seaborn — relationship and when to use each
- Anatomy of a chart: figure, axes, title, labels, legend, ticks
- `plt.figure(figsize=())` and `plt.subplots()`
- Distribution plots: histograms, KDE, box plots — what each reveals
- Log scale — when and why to use it
- `sns.set_style()` and `sns.set_palette()` — consistent aesthetics

### Charts to Build
1. **Price Distribution** — `sns.histplot` with KDE, log scale
2. **Price by City** — `sns.boxplot`, ordered by median, top 5-7 cities
3. **Price Per Sqft by City** — `sns.barplot` with median estimator
4. **Property Type Distribution** — `sns.countplot` or pie chart

### For Each Chart
1. Markdown cell: "Question this chart answers"
2. Code cell: build the chart with full styling
3. `plt.savefig()` to images/ directory
4. Markdown cell: "What we found" — 2-3 sentences of insight

### Visualization Standards (apply to ALL charts from now on)
- `sns.set_style('whitegrid')`
- `sns.set_palette('Set2')` or custom
- `plt.figure(figsize=(10, 6))` minimum
- Descriptive title with context (not "Chart 1")
- Axis labels with units
- `plt.tight_layout()` before saving
- DPI 150 for saved images

### Checkpoint
4 polished charts with narrative. User can explain when to use histogram vs box plot vs bar chart.

### Commit Message
`"Session 8: Visualizations 1-4 — distributions and comparisons"`

---

## SESSION 9: Visualization Deep Dive — Charts 5-7
**Goal:** Build relationship and correlation visualizations.

### Concepts to Teach
- Scatter plots — visualizing relationships between two variables
- What correlation means (and doesn't mean — correlation ≠ causation)
- Pearson correlation coefficient — range [-1, 1], interpretation
- Heatmaps — reading and interpreting correlation matrices
- Color maps (cmaps) — sequential, diverging, qualitative — when to use each
- `alpha` transparency for overlapping points

### Charts to Build
5. **Price vs Area Scatter** — `sns.scatterplot` with hue=city, alpha=0.5
6. **Price by Bedrooms** — grouped bar chart, colored by city
7. **Correlation Heatmap** — `sns.heatmap` with annotations

### For Each Chart
Same structure: Question → Code → Save → Insight

### Concepts Deep Dive
- Show how to read a correlation matrix: what does 0.85 between price and area mean?
- Explain why correlation between price and bedrooms might be lower than expected
- Discuss confounding variables (bigger house = more bedrooms AND higher price — is it the bedrooms or the size?)

### Checkpoint
User understands correlation, can read a heatmap, and can choose the right chart type for a given question.

### Commit Message
`"Session 9: Visualizations 5-7 — relationships and correlations"`

---

## SESSION 10: Advanced Visualizations — Charts 8-10
**Goal:** Build the most insightful, portfolio-worthy charts.

### Concepts to Teach
- Subsetting data for focused analysis — `.query()` and boolean indexing
- Pivot tables for heatmap data — reshaping for visualization
- Horizontal bar charts — when and why they're better than vertical
- Multi-panel figures — `plt.subplots(nrows, ncols)`
- Annotations on charts — `plt.annotate()` and `ax.text()`
- plotly basics (optional) — interactive charts for notebook viewers

### Charts to Build
8. **Top Neighborhoods in Islamabad** — horizontal bar, top 15 by median price
9. **Listings Over Time** — line chart (if date column exists), otherwise price trends by property age
10. **Price/Sqft Heatmap: City × Property Type** — the "power chart"

### Bonus (if time permits)
- An interactive plotly chart for one of the above
- A pair plot of key numeric features: `sns.pairplot()`

### Checkpoint
10 complete visualizations. User has a chart for every major analytical question.

### Commit Message
`"Session 10: Visualizations 8-10 — neighborhood deep dive and power chart"`

---

## SESSION 11: The Investor Memo — Narrative Analysis
**Goal:** Write the analytical narrative that makes this notebook stand out.

### Concepts to Teach
- Data storytelling — structure: situation → complication → resolution
- How to write for a non-technical audience (an investor, not a data scientist)
- Citing your own visualizations — "As shown in Chart 3..."
- Stating limitations honestly — this builds credibility, not weakness
- Suggesting next steps — shows you can think beyond the current analysis

### Steps
1. Create a new section in the notebook: "## Key Findings: What Would a Real Estate Investor Care About?"
2. Write the **Market Overview** paragraph (200 words) — dataset scope and limitations
3. Write the **Geographic Insights** paragraph (150 words) — best value cities, premium markets
4. Write the **Property Type Insights** paragraph (150 words) — what dominates, opportunities
5. Write the **Price Drivers** paragraph (150 words) — what most influences price
6. Write the **Limitations & Next Steps** paragraph (150 words) — honesty + vision
7. Review the entire narrative for flow and clarity

### Concepts Deep Dive
- Show examples of good vs bad data narratives
- Explain the "so what?" test — every paragraph should pass it
- Discuss how this section differentiates a portfolio project from a tutorial exercise

### Checkpoint
500-800 word narrative analysis written. User can present findings verbally.

### Commit Message
`"Session 11: Investor memo — narrative analysis and key findings"`

---

## SESSION 12: Polish, README & Publish
**Goal:** Turn the notebook into a finished, publishable portfolio piece.

### Concepts to Teach
- Notebook hygiene — Restart & Run All, import ordering, removing dead code
- Writing a GitHub README that makes people want to click
- Embedding images in README using markdown
- `.gitignore` — what to exclude and why
- Git basics: init, add, commit, remote, push
- How recruiters and hiring managers evaluate GitHub portfolios

### Steps
1. **Notebook Polish:**
   - Restart kernel, Run All — fix any errors
   - Check every markdown cell for typos and clarity
   - Ensure imports are at the top, organized
   - Remove any scratch/experimental cells
   - Verify all charts render correctly
2. **Create `.gitignore`:**
   ```
   data/raw/
   __pycache__/
   .ipynb_checkpoints/
   *.pyc
   .DS_Store
   ```
3. **Create `README.md`:**
   - Project title and one-line description
   - Key Findings (3-4 bullet points — your best insights)
   - 2-3 chart images embedded
   - Tech stack
   - How to run locally
   - Dataset link
4. **Create `requirements.txt`** (if not already done)
5. **Git init, commit, push to GitHub**
6. **Final review: would you be proud to show this in an interview?**

### Checkpoint
Project is live on GitHub. README is polished. Notebook runs top to bottom without errors.

### Commit Message
`"Session 12: Final polish, README, and GitHub publication"`

---

## POST-PROJECT: Self-Assessment Questions

After completing all 12 sessions, you should be able to answer these confidently:

1. What does `groupby().agg()` do and how does split-apply-combine work?
2. When should you use median instead of mean?
3. What's the difference between dropping and imputing missing values?
4. How do you detect and handle outliers?
5. What does a correlation coefficient of 0.7 mean? What about -0.3?
6. When should you use a box plot vs a histogram vs a bar chart?
7. What is feature engineering? Give an example from this project.
8. What's the most expensive area for real estate in Pakistan based on this data?
9. What are 3 limitations of this dataset?
10. If you had to predict house prices, what features would matter most based on your EDA?
