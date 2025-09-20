import pandas as pd

WORKDAYS = 250  # tweak if needed


def compute_hours_lost(df: pd.DataFrame) -> pd.DataFrame:
    """Compute annual hours lost per commuter using a simple congestion factor.

    hours_lost ≈ ((avg_commute_min * 2) * congestion_pct/100) * WORKDAYS / 60
    """
    out = df.copy()
    out["hours_lost"] = ((out["avg_commute_min"] * 2) * (out["congestion_pct"] / 100.0) * WORKDAYS) / 60.0
    return out


def top_n_cities(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("hours_lost", ascending=False).head(n)