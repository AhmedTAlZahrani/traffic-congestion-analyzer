import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "traffic_index_sample.csv"


def load_dataset(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Load the traffic index CSV into a DataFrame and do basic validation."""
    df = pd.read_csv(path)
    required = {"city", "country", "year", "congestion_pct", "avg_commute_min"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    # basic clean
    df["year"] = df["year"].astype(int)
    df["congestion_pct"] = df["congestion_pct"].astype(float)
    df["avg_commute_min"] = df["avg_commute_min"].astype(float)
    return df