import numpy as np
import pandas as pd
import pytest

import price_model as pm


@pytest.fixture(scope="module")
def df():
    return pm.load()


# ---------------------------------------------------------------- data

def test_no_feature_is_computed_from_the_price():
    assert not set(pm.FEATURES) & set(pm.LEAKY + ["price", "log_price"])


def test_zero_rooms_become_missing(df):
    assert not (df[["bedrooms", "baths"]] == 0).any().any()
    assert df["bedrooms"].isna().sum() == 928 and df["baths"].isna().sum() == 1037


def test_neighbourhood_keys_carry_the_city(df):
    # "DHA Phase 6, DHA Defence" exists in Lahore and Karachi; the keys must keep them apart.
    assert (df.groupby("location_key")["city"].nunique() == 1).all()
    assert (df.groupby("area_key")["city"].nunique() == 1).all()


@pytest.mark.parametrize("location, city, expected", [
    ("DHA Phase 6, DHA Defence", "Lahore", "DHA Defence"),
    ("Warsak Road, Peshawar", "Peshawar", "Warsak Road"),
    ("Gulberg", "Lahore", "Gulberg"),
])
def test_wider_area(location, city, expected):
    assert pm._wider_area(location, city) == expected


# ---------------------------------------------------------------- validation

@pytest.mark.parametrize("strategy", list(pm.STRATEGIES))
def test_every_row_is_tested_exactly_once(df, strategy):
    tested = np.concatenate([test for _, test in pm.make_cv_splits(df, strategy)])
    assert len(tested) == len(df)
    assert len(np.unique(tested)) == len(df)


@pytest.mark.parametrize("strategy", list(pm.STRATEGIES))
def test_train_and_test_never_share_a_row(df, strategy):
    for train, test in pm.make_cv_splits(df, strategy):
        assert not set(train) & set(test)


@pytest.mark.parametrize("strategy", ["location", "area"])
def test_grouped_splits_hold_out_whole_neighbourhoods(df, strategy):
    key = f"{strategy}_key"
    for train, test in pm.make_cv_splits(df, strategy):
        assert not set(df[key].iloc[train]) & set(df[key].iloc[test])


@pytest.mark.parametrize("strategy", list(pm.STRATEGIES))
def test_every_fold_keeps_the_big_cities(df, strategy):
    big = df["city"].value_counts().loc[lambda s: s >= 400].index
    for _, test in pm.make_cv_splits(df, strategy):
        assert set(big) <= set(df["city"].iloc[test])


def test_unknown_strategy_is_rejected(df):
    with pytest.raises(ValueError):
        pm.make_cv_splits(df, "by_vibes")


# ---------------------------------------------------------------- models and metrics

def test_models_predict_finite_prices_on_unseen_neighbourhoods(df):
    sample = df.sample(1500, random_state=0)
    train, test = next(iter(pm.make_cv_splits(sample.reset_index(drop=True), "location")))
    data = sample.reset_index(drop=True)
    for make in (pm.ridge_model, pm.boosting_model):
        model = make().fit(data.iloc[train][pm.FEATURES], data.iloc[train]["log_price"])
        assert np.isfinite(model.predict(data.iloc[test][pm.FEATURES])).all()


def test_conformal_interval_is_ordered_and_adjusted_uniformly(df):
    data = df.sample(1500, random_state=1).reset_index(drop=True)
    train, test = next(iter(pm.make_cv_splits(data, "location")))
    raw_low, raw_high, low, high = pm.conformal_interval(data.iloc[train], data.iloc[test], {}, "location")
    assert (raw_low <= raw_high).all() and (low <= high).all()
    assert np.allclose((low - raw_low), (low - raw_low)[0])  # one common widening for every listing


def test_score_is_zero_error_for_perfect_predictions():
    prices = np.array([1e6, 5e6, 2e7])
    result = pm.score(prices, np.log(prices))
    assert result["Median error (%)"] == pytest.approx(0)
    assert result["Within 10% (%)"] == pytest.approx(100)


def test_interval_quality_counts_coverage():
    prices = np.array([100.0, 200.0, 300.0, 400.0])
    low, high = np.log([90, 150, 310, 390]), np.log([110, 250, 320, 410])
    assert pm.interval_quality(prices, low, high, np.log(prices))["Coverage (%)"] == pytest.approx(75)


def test_hedonic_recovers_known_effects():
    rng = np.random.default_rng(0)
    n, areas = 3000, 60
    area = rng.integers(0, areas, n)
    log_size = rng.normal(7.5, 0.5, n)
    bedrooms = rng.integers(1, 7, n).astype(float)
    baths = rng.integers(1, 6, n).astype(float)
    area_effect = rng.normal(0, 0.8, areas)[area]  # areas differ a lot in price level
    log_price = 0.8 * log_size + 0.05 * bedrooms + 0.09 * baths + area_effect + rng.normal(0, 0.1, n)
    synthetic = pd.DataFrame({"area_key": area.astype(str), "log_size": log_size, "bedrooms": bedrooms,
                              "baths": baths, "log_price": log_price})
    out = pm.hedonic_fixed_effects(synthetic, n_boot=50).set_index("term")
    assert out.loc["log_size", "coef"] == pytest.approx(0.8, abs=0.02)
    assert out.loc["bedrooms", "coef"] == pytest.approx(0.05, abs=0.01)
    assert out.loc["baths", "coef"] == pytest.approx(0.09, abs=0.01)
    assert (out["ci_low"] < out["coef"]).all() and (out["coef"] < out["ci_high"]).all()
