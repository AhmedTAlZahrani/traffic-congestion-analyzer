from src.indicators import compute_hours_lost
import pandas as pd

def test_hours_lost_positive():
    df = pd.DataFrame({
        "city": ["Test"],
        "country": ["X"],
        "year": [2024],
        "congestion_pct": [50.0],
        "avg_commute_min": [30.0],
    })
    out = compute_hours_lost(df)
    assert out.loc[0, "hours_lost"] > 0