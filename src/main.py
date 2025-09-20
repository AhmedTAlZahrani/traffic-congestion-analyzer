import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "traffic_index_sample.csv"
PLOTS_DIR = Path(__file__).resolve().parents[1] / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

WORKDAYS = 250
AVG_HOURLY_WAGE_USD = 25  # rough global average for cost estimates


def load_data(path=DATA_PATH):
    """Load traffic CSV and do basic cleanup."""
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    df["congestion_pct"] = df["congestion_pct"].astype(float)
    df["avg_commute_min"] = df["avg_commute_min"].astype(float)
    return df


def compute_kpis(df):
    """Add calculated columns for hours lost, cost impact, congestion index."""
    out = df.copy()

    # annual hours lost per commuter
    # formula: round-trip commute * congestion fraction * workdays, converted to hours
    out["hours_lost"] = ((out["avg_commute_min"] * 2) * (out["congestion_pct"] / 100.0) * WORKDAYS) / 60.0

    # estimated cost impact per commuter (hours lost * wage)
    out["cost_impact_usd"] = out["hours_lost"] * AVG_HOURLY_WAGE_USD

    # simple congestion index: congestion_pct * commute time (higher = worse)
    out["congestion_index"] = out["congestion_pct"] * out["avg_commute_min"] / 100.0

    return out


def print_summary(df):
    """Print key stats to console."""
    print(f"Cities analyzed: {len(df)}")
    print(f"Average congestion: {df['congestion_pct'].mean():.1f}%")
    print(f"Average commute (one-way): {df['avg_commute_min'].mean():.0f} min")
    print()

    # top city
    worst = df.sort_values("hours_lost", ascending=False).iloc[0]
    print(f"Worst city: {worst['city']} ({worst['hours_lost']:.0f} hours lost/year, ${worst['cost_impact_usd']:.0f} cost)")
    print()

    # show all cities sorted
    print("All cities ranked by hours lost per year:")
    ranked = df.sort_values("hours_lost", ascending=False)
    for _, row in ranked.iterrows():
        print(f"  {row['city']:15s} {row['country']:20s}  {row['hours_lost']:6.1f} hrs  ${row['cost_impact_usd']:7.0f}")


def plot_top_cities(df, n=10):
    """Bar chart of top N cities by hours lost."""
    import matplotlib.pyplot as plt

    top = df.sort_values("hours_lost", ascending=False).head(n)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(top["city"], top["hours_lost"], color="#e67e22")
    ax.set_title(f"Top {n} Cities - Annual Hours Lost per Commuter")
    ax.set_ylabel("Hours per year")
    ax.set_xlabel("")
    plt.xticks(rotation=45, ha="right")

    # add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 1,
                f"{height:.0f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    outpath = PLOTS_DIR / "top10_hours_lost.png"
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath


def plot_cost_impact(df):
    """Horizontal bar chart of cost impact by city."""
    import matplotlib.pyplot as plt

    ranked = df.sort_values("cost_impact_usd", ascending=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(ranked["city"], ranked["cost_impact_usd"], color="#3498db")
    ax.set_title("Estimated Annual Cost of Congestion per Commuter")
    ax.set_xlabel("USD per year")
    plt.tight_layout()
    outpath = PLOTS_DIR / "cost_impact.png"
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath


def run():
    print("=== Traffic Congestion Analyzer ===\n")

    df = load_data()
    print(f"Loaded {len(df)} rows from {DATA_PATH.name}\n")

    # compute all KPIs
    df = compute_kpis(df)

    # print summary stats
    print_summary(df)
    print()

    # generate charts
    print("Generating charts...")
    p1 = plot_top_cities(df)
    print(f"  Saved: {p1}")
    p2 = plot_cost_impact(df)
    print(f"  Saved: {p2}")
    print("\nDone!")


if __name__ == "__main__":
    run()
