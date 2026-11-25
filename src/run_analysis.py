"""Run the full price-model analysis and write reports/price_model_results.md plus three charts.

    python src/run_analysis.py            # full run with nested tuning (about 6 minutes)
    python src/run_analysis.py --quick    # no tuning, for a fast check
"""
from __future__ import annotations

import argparse
import time
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import price_model as pm  # noqa: E402

REPORT = pm.ROOT / "reports" / "price_model_results.md"
IMAGES = pm.ROOT / "images"

MODEL_LABELS = {
    "baseline": "City price-per-sq-ft rule",
    "ridge": "Ridge regression",
    "boosting": "Gradient boosting",
}
STRATEGY_LABELS = {
    "random": "Random folds",
    "location": "Unseen neighbourhood",
    "area": "Unseen wider area",
}

# Chart styling: validated categorical slots 1-3 (light mode), recessive axes and grid.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE_RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def _style():
    plt.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
        "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
        "font.size": 10.5, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
    })


def chart_model_by_validation(overall: pd.DataFrame, path) -> None:
    """Grouped bars: median error of each model under each validation design."""
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    strategies = list(STRATEGY_LABELS)
    x = np.arange(len(strategies))
    width = 0.26
    for i, model in enumerate(MODEL_LABELS):
        values = [overall.loc[(s, MODEL_LABELS[model]), "Median error (%)"] for s in strategies]
        bars = ax.bar(x + (i - 1) * (width + 0.02), values, width, color=SERIES[i], label=MODEL_LABELS[model],
                      edgecolor=SURFACE, linewidth=2)
        ax.bar_label(bars, labels=[f"{v:.1f}%" for v in values], padding=3, fontsize=9, color=INK_2)
    ax.set_xticks(x, [STRATEGY_LABELS[s] for s in strategies])
    ax.set_ylabel("Median error on held-out listings (%)")
    ax.set_ylim(0, max(overall["Median error (%)"]) * 1.25)
    ax.grid(axis="x", visible=False)
    ax.set_title("Price error by model and validation design (lower is better)")
    ax.legend(frameon=False, loc="upper left", ncols=3, fontsize=9.5)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_predicted_vs_actual(df: pd.DataFrame, preds: pd.DataFrame, coverage: float, path) -> None:
    """Density of predicted vs actual price (log-log), headline validation."""
    fig, ax = plt.subplots(figsize=(6.4, 6.0))
    actual = df["price"] / 1e5
    predicted = np.exp(preds["boosting"]) / 1e5
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("blue", BLUE_RAMP)
    hb = ax.hexbin(actual, predicted, gridsize=45, xscale="log", yscale="log", cmap=cmap, mincnt=1,
                   linewidths=0.2, edgecolors=SURFACE)
    lims = [min(actual.min(), predicted.min()), max(actual.max(), predicted.max())]
    ax.plot(lims, lims, color=INK_2, linewidth=1.2, linestyle="--")
    ax.text(lims[1] * 0.55, lims[1] * 0.75, "perfect prediction", color=INK_2, fontsize=9, ha="right")
    ax.set_xlabel("Asking price (lakh PKR, log scale)")
    ax.set_ylabel("Predicted price (lakh PKR, log scale)")
    ax.set_title("Predicted vs actual, unseen neighbourhoods")
    ax.text(0.02, 0.97, f"{coverage:.0f}% of prices fall inside their 80% range", transform=ax.transAxes,
            va="top", fontsize=9.5, color=INK_2)
    cbar = fig.colorbar(hb, ax=ax, shrink=0.8)
    cbar.set_label("Listings per cell", color=INK_2)
    cbar.outline.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_error_by_area_data(table: pd.DataFrame, path) -> None:
    """Single series: error falls as more listings from the same wider area are in training."""
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    bars = ax.bar(table.index.astype(str), table["Median error (%)"], width=0.55, color=SERIES[0],
                  edgecolor=SURFACE, linewidth=2)
    ax.bar_label(bars, labels=[f"{v:.1f}%\n(n={n:,})" for v, n in zip(table["Median error (%)"],
                                                                     table["Listings"])],
                 padding=3, fontsize=9, color=INK_2)
    ax.set_xlabel("Training listings in the same wider area")
    ax.set_ylabel("Median error (%)")
    ax.set_ylim(0, table["Median error (%)"].max() * 1.35)
    ax.grid(axis="x", visible=False)
    ax.set_title("Gradient boosting error by how much local data it had")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def ape(df, log_pred):
    return np.abs(np.exp(log_pred) - df["price"]) / df["price"]


def main(quick: bool) -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    _style()
    start = time.time()
    df = pm.load()
    results = {}
    for strategy in pm.STRATEGIES:
        t = time.time()
        splits = pm.make_cv_splits(df, strategy)
        results[strategy] = pm.cross_validate(df, splits, strategy, tune=not quick,
                                              importance=strategy == pm.HEADLINE)
        print(f"{strategy:9s} done in {time.time() - t:.0f}s")

    # Overall scores per validation design and model
    rows, intervals = {}, {}
    for strategy, r in results.items():
        p = r["preds"]
        for key, label in MODEL_LABELS.items():
            rows[(strategy, label)] = pm.score(df["price"], p[key])
        intervals[STRATEGY_LABELS[strategy]] = {
            **{f"Raw quantile: {k}": v for k, v in
               pm.interval_quality(df["price"], p["raw_low"], p["raw_high"], p["boosting"]).items()
               if k != "Target coverage (%)"},
            **{f"Conformal: {k}": v for k, v in
               pm.interval_quality(df["price"], p["low"], p["high"], p["boosting"]).items()},
        }
    overall = pd.DataFrame(rows).T
    intervals = pd.DataFrame(intervals).T.round(1)

    head = results[pm.HEADLINE]
    hp = head["preds"]
    err = ape(df, hp["boosting"])
    inside = (df["price"] >= np.exp(hp["low"])) & (df["price"] <= np.exp(hp["high"]))

    by_city = (
        pd.DataFrame({"city": df["city"], "err": err, "inside": inside})
        .groupby("city")
        .agg(Listings=("err", "size"), **{"Median error (%)": ("err", lambda s: 100 * s.median()),
                                          "Range coverage (%)": ("inside", lambda s: 100 * s.mean())})
        .sort_values("Listings", ascending=False)
        .round(1)
    )

    buckets = pd.cut(head["density"]["same_area"], [-1, 0, 9, 49, np.inf], labels=["0", "1-9", "10-49", "50+"])
    by_density = (
        pd.DataFrame({"bucket": buckets, "err": err})
        .groupby("bucket", observed=True)
        .agg(Listings=("err", "size"), **{"Median error (%)": ("err", lambda s: 100 * s.median())})
        .round(1)
    )

    importance = head["importance"].rename("Increase in median log error when shuffled").to_frame().round(4)
    hedonic = pm.hedonic_fixed_effects(df)
    params = pd.DataFrame(head["params"]).rename_axis("fold") if not quick else None

    # Charts
    IMAGES.mkdir(exist_ok=True)
    chart_model_by_validation(overall, IMAGES / "chart11_model_by_validation.png")
    chart_predicted_vs_actual(df, hp, 100 * inside.mean(), IMAGES / "chart12_predicted_vs_actual.png")
    chart_error_by_area_data(by_density, IMAGES / "chart13_error_by_area_data.png")

    # Report
    def pct(x):
        return f"{100 * (np.exp(x) - 1):+.1f}%"

    size_row = hedonic.set_index("term").loc["log_size"]
    names = {"bedrooms": "bedroom", "baths": "bathroom"}
    hed = hedonic.assign(**{
        "Effect": [f"+10% size: {100 * (1.1 ** c - 1):+.1f}% price" if t == "log_size"
                   else f"+1 {names[t]} at the same size: {pct(c)}"
                   for t, c in zip(hedonic["term"], hedonic["coef"])],
        "95% interval": [f"{100 * (1.1 ** lo - 1):+.1f}% to {100 * (1.1 ** hi - 1):+.1f}%" if t == "log_size"
                         else f"{pct(lo)} to {pct(hi)}"
                         for t, lo, hi in zip(hedonic["term"], hedonic["ci_low"], hedonic["ci_high"])],
    })[["term", "coef", "Effect", "95% interval"]].round(4)

    table = overall.round(2)
    table.index = [f"{STRATEGY_LABELS[s]} / {m}" for s, m in table.index]
    lines = [
        "# Price model results",
        "",
        f"Generated by `src/run_analysis.py`{' --quick (no tuning)' if quick else ''}. "
        f"{len(df):,} listings, {df['city'].nunique()} cities, 5-fold cross-validation stratified by city.",
        "",
        "## Accuracy by validation design",
        "",
        "Every number is measured on listings the model did not see in training. "
        "*Unseen neighbourhood* (whole neighbourhoods held out) is the headline; *random folds* are shown to "
        "measure how optimistic the usual random split would be.",
        "",
        table.to_markdown(),
        "",
        "## Price ranges (80% prediction intervals)",
        "",
        "Raw quantile models versus the same models calibrated by split conformal prediction.",
        "",
        intervals.to_markdown(),
        "",
        "## Headline model by city (gradient boosting, unseen neighbourhoods)",
        "",
        by_city.to_markdown(),
        "",
        "## Error by local data (unseen neighbourhoods)",
        "",
        by_density.to_markdown(),
        "",
        "## What drives the predictions (permutation importance, unseen neighbourhoods)",
        "",
        importance.to_markdown(),
        "",
        "`location_key` scores zero by design here: every test neighbourhood is new, so its encoding falls back "
        "to the overall mean and shuffling it changes nothing.",
        "",
        "## Hedonic regression (area fixed effects, cluster bootstrap by area)",
        "",
        f"{hedonic.attrs['n_listings']:,} listings that state bedrooms and bathrooms, "
        f"{hedonic.attrs['n_areas']:,} areas. Coefficients compare listings within the same area.",
        "",
        hed.to_markdown(index=False),
        "",
        f"Size elasticity {size_row['coef']:.2f}: price rises less than proportionally with size, so larger "
        "homes are cheaper per square foot within the same area.",
    ]
    if params is not None:
        lines += ["", "## Tuned gradient boosting settings per fold (nested search)", "", params.to_markdown()]
    lines += ["", f"Run time: {time.time() - start:.0f} s.", ""]
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(table.to_string())
    print(intervals.to_string())
    print(by_city.to_string())
    print(by_density.to_string())
    print(importance.to_string())
    print(hed.to_string(index=False))
    print(f"Wrote {REPORT.relative_to(pm.ROOT)} and 3 charts in {time.time() - start:.0f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quick", action="store_true", help="skip the nested tuning")
    main(parser.parse_args().quick)
