import pandas as pd
import pytest

from src.indicators import compute_hours_lost, top_n_cities, WORKDAYS
from src.load_data import load_dataset


def _sample():
    return pd.DataFrame({
        "city": ["Alpha", "Beta", "Gamma"],
        "country": ["X", "Y", "Z"],
        "year": [2024, 2024, 2024],
        "congestion_pct": [50.0, 30.0, 10.0],
        "avg_commute_min": [30.0, 30.0, 30.0],
    })


def test_hours_lost_positive():
    out = compute_hours_lost(_sample())
    assert (out["hours_lost"] > 0).all()


def test_hours_lost_formula_matches_manual_calc():
    df = pd.DataFrame({
        "city": ["Test"],
        "country": ["X"],
        "year": [2024],
        "congestion_pct": [50.0],
        "avg_commute_min": [30.0],
    })
    out = compute_hours_lost(df)
    # (30*2 * 0.5 * 250) / 60 = 125
    assert out.loc[0, "hours_lost"] == pytest.approx(125.0)


def test_top_n_returns_n_rows_sorted():
    df = compute_hours_lost(_sample())
    top2 = top_n_cities(df, n=2)
    assert len(top2) == 2
    assert list(top2["city"]) == ["Alpha", "Beta"]


def test_workdays_is_reasonable():
    # sanity guard — 250 is close to standard US working-days-per-year
    assert 200 <= WORKDAYS <= 260


def test_load_dataset_has_required_columns():
    df = load_dataset()
    for col in ["city", "country", "year", "congestion_pct", "avg_commute_min"]:
        assert col in df.columns


def test_load_dataset_raises_on_missing_columns(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("city,country\nA,X\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing columns"):
        load_dataset(bad)
