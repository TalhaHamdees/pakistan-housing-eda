"""Price model for Pakistani residential listings (the Zameen.com snapshot used in the EDA).

Library module: data preparation, validation splits, models, metrics and a hedonic (econometric) model.
`run_analysis.py` uses it to produce the results report and charts.

Design notes
- Target: log of the asking price. Errors are reported back in rupees and percent.
- Leakage control: columns derived from the price are dropped; neighbourhood encodings are fitted only on
  training rows (and cross-fitted inside them); validation holds out whole neighbourhoods.
- Uncertainty: quantile gradient boosting, calibrated by split conformal prediction, gives an 80% price range
  for each listing; its coverage is checked on held-out listings.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score
from sklearn.model_selection import (
    GroupKFold,
    GroupShuffleSplit,
    KFold,
    RandomizedSearchCV,
    ShuffleSplit,
    StratifiedGroupKFold,
    StratifiedKFold,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cleaned_housing_data.csv"

# Columns computed from the price itself. Using any of them as a feature would hand the model the answer.
LEAKY = ["price_lakh", "price_per_sqft", "price_band"]
CATEGORICAL = ["city", "area_key", "location_key"]
NUMERIC = ["bedrooms", "baths", "log_size"]
FEATURES = CATEGORICAL + NUMERIC

STRATEGIES = {
    "random": "Random folds: a test listing's neighbourhood usually also appears in training",
    "location": "Grouped by neighbourhood: every test listing is in a neighbourhood the model never saw",
    "area": "Grouped by wider area: whole areas (for example all of DHA Defence in a city) held out",
}
HEADLINE = "location"
INTERVAL = (0.10, 0.90)  # an 80% prediction interval


# ---------------------------------------------------------------- data

def _wider_area(location: str, city: str) -> str:
    """A location reads "Sub-area, Area". Return the Area part, unless that part is just the city name
    ("Warsak Road, Peshawar"), in which case the sub-area is the most specific area we have."""
    parts = [p.strip() for p in location.rsplit(",", 1)]
    if len(parts) == 2 and parts[1].lower() != city.lower():
        return parts[1]
    return parts[0]


def load(path: Path = DATA) -> pd.DataFrame:
    """Read the cleaned listings and build the model's features and target."""
    df = pd.read_csv(path).drop(columns=LEAKY + ["bedroom_group"])

    # Names repeat across cities ("DHA Phase 6, DHA Defence" is in Lahore and Karachi), so prefix the city.
    area = [_wider_area(loc, city) for loc, city in zip(df["location"], df["city"])]
    df["area_key"] = df["city"] + " / " + pd.Series(area, index=df.index)
    df["location_key"] = df["city"] + " / " + df["location"]

    # 0 bedrooms or bathrooms means "not stated" in these listings (928 and 1,037 rows), not a real zero.
    for col in ["bedrooms", "baths"]:
        df[col] = df[col].where(df[col] > 0)

    df["log_size"] = np.log(df["size"])
    df["log_price"] = np.log(df["price"])
    return df.reset_index(drop=True)


# ---------------------------------------------------------------- validation

def make_cv_splits(
    df: pd.DataFrame, strategy: str = HEADLINE, n_splits: int = 5, seed: int = 42
) -> list[tuple[np.ndarray, np.ndarray]]:
    """Return (train_idx, test_idx) pairs of row positions for cross-validation.

    "random"   : stratified by city only. Optimistic: other listings from the same neighbourhood are in
                 training, and the neighbourhood encoding has effectively seen local prices.
    "location" : whole neighbourhoods are held out (StratifiedGroupKFold), so the score answers "how well do
                 we price a listing in a neighbourhood we have no data for?" This is the headline number.
    "area"     : stricter still; whole wider areas (e.g. every DHA Defence phase in a city) are held out.

    All strategies stratify by city, so every fold keeps roughly the national city mix, including the small
    cities (Quetta 12 listings, Attock 6).
    """
    if strategy == "random":
        splitter = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        folds = splitter.split(df, df["city"])
    elif strategy in ("location", "area"):
        splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
        folds = splitter.split(df, df["city"], groups=df[f"{strategy}_key"])
    else:
        raise ValueError(f"unknown strategy {strategy!r}; use one of {list(STRATEGIES)}")
    return [(np.asarray(train), np.asarray(test)) for train, test in folds]


# ---------------------------------------------------------------- models

def city_rate_baseline(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """What an agent would do by hand: the city's median price per sq ft times the size. Returns log price."""
    rate = (train["price"] / train["size"]).groupby(train["city"]).median()
    overall = (train["price"] / train["size"]).median()
    return np.log(test["city"].map(rate).fillna(overall).to_numpy() * test["size"].to_numpy())


def _preprocess(dense: bool) -> ColumnTransformer:
    # TargetEncoder cross-fits inside fit_transform, so a listing's own price never feeds its own encoding.
    # Missing bedrooms/baths are imputed with the median and flagged, so "not stated" can carry information.
    return ColumnTransformer([
        ("city", OneHotEncoder(handle_unknown="ignore", sparse_output=not dense), ["city"]),
        ("hood", TargetEncoder(target_type="continuous", random_state=0), ["area_key", "location_key"]),
        ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), NUMERIC),
    ])


def ridge_model():
    return make_pipeline(_preprocess(dense=False), RidgeCV(alphas=np.logspace(-3, 3, 13)))


BOOSTING_DEFAULTS = dict(
    learning_rate=0.05, max_iter=800, max_leaf_nodes=31, min_samples_leaf=20, l2_regularization=1.0,
    early_stopping=True, validation_fraction=0.1, n_iter_no_change=40, random_state=0,
)
SEARCH_SPACE = {
    "learning_rate": [0.03, 0.05, 0.1],
    "max_leaf_nodes": [15, 31, 63],
    "min_samples_leaf": [10, 20, 50],
    "l2_regularization": [0.0, 0.1, 1.0, 5.0],
}


def boosting_model(loss: str = "squared_error", quantile: float | None = None, **params):
    settings = {**BOOSTING_DEFAULTS, **params}
    if loss == "quantile":
        settings.update(loss="quantile", quantile=quantile)
    return make_pipeline(_preprocess(dense=True), HistGradientBoostingRegressor(**settings))


GROUP_COLUMN = {"random": None, "location": "location_key", "area": "area_key"}


def tune_boosting(train: pd.DataFrame, strategy: str = HEADLINE, n_iter: int = 10, seed: int = 0) -> dict:
    """Nested tuning: a small random search scored only on the training part of the outer fold. The inner
    folds are grouped the same way as the outer ones, so tuning faces the same task as the final test."""
    group_col = GROUP_COLUMN[strategy]
    search = RandomizedSearchCV(
        boosting_model(),
        {f"histgradientboostingregressor__{k}": v for k, v in SEARCH_SPACE.items()},
        n_iter=n_iter,
        cv=GroupKFold(n_splits=3) if group_col else KFold(n_splits=3, shuffle=True, random_state=seed),
        scoring="neg_median_absolute_error",
        random_state=seed,
        n_jobs=-1,
    )
    groups = train[group_col] if group_col else None
    search.fit(train[FEATURES], train["log_price"], groups=groups)
    return {k.split("__", 1)[1]: v for k, v in search.best_params_.items()}


def conformal_interval(train: pd.DataFrame, test: pd.DataFrame, params: dict, strategy: str = HEADLINE,
                       seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """80% price range for each test listing by conformalized quantile regression (Romano et al., 2019).

    Quantile models alone tend to give ranges that are too narrow for unseen neighbourhoods. So a quarter of
    the training data (grouped like the outer split) is held back as a calibration set; the quantile models
    are fitted on the rest; on the calibration set we measure by how much the true prices fall outside the
    predicted range, and widen every test range by the matching quantile of that miss.

    Returns (raw_low, raw_high, calibrated_low, calibrated_high) in log price.
    """
    group_col = GROUP_COLUMN[strategy]
    holdout = (GroupShuffleSplit if group_col else ShuffleSplit)(n_splits=1, test_size=0.25, random_state=seed)
    fit_idx, cal_idx = next(holdout.split(train, groups=train[group_col] if group_col else None))
    fit, cal = train.iloc[fit_idx], train.iloc[cal_idx]

    models = [boosting_model("quantile", q, **params).fit(fit[FEATURES], fit["log_price"]) for q in INTERVAL]

    def predict(frame):
        a, b = (m.predict(frame[FEATURES]) for m in models)
        return np.minimum(a, b), np.maximum(a, b)  # separately fitted quantiles can cross

    cal_low, cal_high = predict(cal)
    misses = np.maximum(cal_low - cal["log_price"].to_numpy(), cal["log_price"].to_numpy() - cal_high)
    n, alpha = len(misses), 1 - (INTERVAL[1] - INTERVAL[0])
    widen = np.quantile(misses, min(1.0, np.ceil((n + 1) * (1 - alpha)) / n), method="higher")

    low, high = predict(test)
    return low, high, low - widen, high + widen


# ---------------------------------------------------------------- cross-validation

def cross_validate(df: pd.DataFrame, splits, strategy: str = HEADLINE, tune: bool = True,
                   importance: bool = False) -> dict:
    """Out-of-fold predictions for every model, each made by models that never saw that row.

    Returns a dict with
      preds       DataFrame of log-price predictions: baseline, ridge, boosting, the raw quantile range
                  (raw_low, raw_high), the calibrated range (low, high), and the fold number
      density     for each row, how many training listings shared its neighbourhood and its wider area
      params      tuned boosting settings per fold
      importance  mean permutation importance per input column (boosting), if requested
    """
    columns = ["baseline", "ridge", "boosting", "raw_low", "raw_high", "low", "high", "fold"]
    preds = pd.DataFrame(index=df.index, columns=columns, dtype=float)
    density = pd.DataFrame(index=df.index, columns=["same_location", "same_area"], dtype=float)
    params, importances = [], []

    for fold, (train_idx, test_idx) in enumerate(splits):
        train, test = df.iloc[train_idx], df.iloc[test_idx]
        best = tune_boosting(train, strategy) if tune else {}
        params.append(best)

        point = boosting_model(**best).fit(train[FEATURES], train["log_price"])
        ridge = ridge_model().fit(train[FEATURES], train["log_price"])
        interval = conformal_interval(train, test, best, strategy, seed=fold)

        preds.iloc[test_idx] = np.column_stack([
            city_rate_baseline(train, test),
            ridge.predict(test[FEATURES]),
            point.predict(test[FEATURES]),
            *interval,
            np.full(len(test), fold),
        ])
        density.iloc[test_idx] = np.column_stack([
            test["location_key"].map(train["location_key"].value_counts()).fillna(0).to_numpy(),
            test["area_key"].map(train["area_key"].value_counts()).fillna(0).to_numpy(),
        ])
        if importance:
            result = permutation_importance(point, test[FEATURES], test["log_price"], n_repeats=5,
                                            scoring="neg_median_absolute_error", random_state=fold, n_jobs=-1)
            importances.append(pd.Series(result.importances_mean, index=FEATURES))

    return {
        "preds": preds,
        "density": density,
        "params": params,
        "importance": pd.concat(importances, axis=1).mean(axis=1).sort_values(ascending=False)
        if importances else None,
    }


# ---------------------------------------------------------------- metrics

def score(actual_price, log_pred) -> dict[str, float]:
    actual_price, pred = np.asarray(actual_price, float), np.exp(np.asarray(log_pred, float))
    ape = np.abs(pred - actual_price) / actual_price
    return {
        "Median error (%)": 100 * np.median(ape),
        "Within 10% (%)": 100 * np.mean(ape <= 0.10),
        "Within 20% (%)": 100 * np.mean(ape <= 0.20),
        "Mean abs. error (lakh PKR)": np.mean(np.abs(pred - actual_price)) / 1e5,
        "R2 (log price)": r2_score(np.log(actual_price), np.log(pred)),
    }


def interval_quality(actual_price, log_low, log_high, log_point) -> dict[str, float]:
    """Share of listings whose price falls inside the predicted range, and how wide the range is."""
    actual_price = np.asarray(actual_price, float)
    low, high, point = (np.exp(np.asarray(a, float)) for a in (log_low, log_high, log_point))
    return {
        "Coverage (%)": 100 * np.mean((actual_price >= low) & (actual_price <= high)),
        "Target coverage (%)": 100 * (INTERVAL[1] - INTERVAL[0]),
        "Median width (% of prediction)": 100 * np.median((high - low) / point),
    }


# ---------------------------------------------------------------- hedonic model (economics view)

HEDONIC_TERMS = ["log_size", "bedrooms", "baths"]


def _within_ols(frame: pd.DataFrame, clusters: np.ndarray) -> np.ndarray:
    """OLS with fixed effects: subtract each cluster's mean, then regress (the "within" estimator)."""
    cols = HEDONIC_TERMS + ["log_price"]
    demeaned = frame[cols].to_numpy() - frame[cols].groupby(clusters).transform("mean").to_numpy()
    beta, *_ = np.linalg.lstsq(demeaned[:, :-1], demeaned[:, -1], rcond=None)
    return beta


def hedonic_fixed_effects(df: pd.DataFrame, n_boot: int = 300, seed: int = 0) -> pd.DataFrame:
    """Hedonic price regression: log price on log size, bedrooms and bathrooms, comparing listings only
    within the same wider area (area fixed effects). 95% intervals come from a cluster bootstrap that
    resamples whole areas, because listings in one area are not independent.

    Uses listings that state both bedrooms and bathrooms.
    """
    d = df.dropna(subset=["bedrooms", "baths"]).reset_index(drop=True)
    estimate = _within_ols(d, d["area_key"].to_numpy())

    rng = np.random.default_rng(seed)
    members = d.groupby("area_key").indices
    names = np.array(list(members))
    draws = []
    for _ in range(n_boot):
        pick = rng.choice(names, size=len(names), replace=True)
        rows = np.concatenate([members[a] for a in pick])
        cluster_ids = np.repeat(np.arange(len(pick)), [len(members[a]) for a in pick])
        draws.append(_within_ols(d.iloc[rows], cluster_ids))
    low, high = np.percentile(np.array(draws), [2.5, 97.5], axis=0)

    out = pd.DataFrame({"term": HEDONIC_TERMS, "coef": estimate, "ci_low": low, "ci_high": high})
    out.attrs["n_listings"] = len(d)
    out.attrs["n_areas"] = d["area_key"].nunique()
    return out
