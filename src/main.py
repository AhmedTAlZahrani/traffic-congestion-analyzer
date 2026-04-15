from pathlib import Path

import matplotlib.pyplot as plt

from src.load_data import load_dataset, DATA_PATH
from src.indicators import compute_hours_lost, top_n_cities, WORKDAYS

PLOTS_DIR = Path(__file__).resolve().parents[1] / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

AVG_HOURLY_WAGE_USD = 25  # rough global average for cost estimates


def compute_kpis(df):
    """Add hours_lost, cost_impact_usd, and congestion_index columns."""
    out = compute_hours_lost(df)
    out["cost_impact_usd"] = out["hours_lost"] * AVG_HOURLY_WAGE_USD
    out["congestion_index"] = out["congestion_pct"] * out["avg_commute_min"] / 100.0
    return out


def print_summary(df):
    """Print key stats to console."""
    print(f"Cities analyzed: {len(df)}")
    print(f"Average congestion: {df['congestion_pct'].mean():.1f}%")
    print(f"Average commute (one-way): {df['avg_commute_min'].mean():.0f} min")
    print()

    worst = df.sort_values("hours_lost", ascending=False).iloc[0]
    print(
        f"Worst city: {worst['city']} ({worst['hours_lost']:.0f} hours lost/year, "
        f"${worst['cost_impact_usd']:.0f} cost)"
    )
    print()

    print("All cities ranked by hours lost per year:")
    ranked = df.sort_values("hours_lost", ascending=False)
    for _, row in ranked.iterrows():
        print(
            f"  {row['city']:15s} {row['country']:20s}  "
            f"{row['hours_lost']:6.1f} hrs  ${row['cost_impact_usd']:7.0f}"
        )


def plot_top_cities(df, n=10):
    """Bar chart of top N cities by hours lost with value labels."""
    top = top_n_cities(df, n=n)

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(top["city"], top["hours_lost"], color="#e67e22")
    ax.set_title(f"Top {n} Cities - Annual Hours Lost per Commuter")
    ax.set_ylabel("Hours per year")
    ax.set_xlabel("")
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2, height + 1,
            f"{height:.0f}", ha="center", va="bottom", fontsize=9,
        )

    plt.tight_layout()
    outpath = PLOTS_DIR / "top10_hours_lost.png"
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath


def plot_cost_impact(df):
    """Horizontal bar chart of cost impact by city."""
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


def write_summary_md(df, path):
    ranked = df.sort_values("hours_lost", ascending=False)
    lines = [
        "# Traffic Congestion Analyzer — Results",
        "",
        f"Assumptions: {WORKDAYS} workdays/year, ${AVG_HOURLY_WAGE_USD}/hour average wage.",
        "",
        "| City | Country | Congestion % | One-way commute (min) | Hours lost/year | Cost/year (USD) |",
        "|------|---------|--------------|-----------------------|-----------------|-----------------|",
    ]
    for _, r in ranked.iterrows():
        lines.append(
            f"| {r['city']} | {r['country']} | {r['congestion_pct']:.0f} | "
            f"{r['avg_commute_min']:.0f} | {r['hours_lost']:.1f} | "
            f"{r['cost_impact_usd']:.0f} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run():
    print("=== Traffic Congestion Analyzer ===\n")

    df = load_dataset()
    print(f"Loaded {len(df)} rows from {DATA_PATH.name}\n")

    df = compute_kpis(df)

    print_summary(df)
    print()

    csv_out = RESULTS_DIR / "summary.csv"
    md_out = RESULTS_DIR / "summary.md"
    df.sort_values("hours_lost", ascending=False).to_csv(csv_out, index=False)
    write_summary_md(df, md_out)
    print(f"Saved: {csv_out}")
    print(f"Saved: {md_out}")
    print()

    print("Generating charts...")
    p1 = plot_top_cities(df)
    print(f"  Saved: {p1}")
    p2 = plot_cost_impact(df)
    print(f"  Saved: {p2}")
    print(f"\nWorkdays assumed: {WORKDAYS}, hourly wage: ${AVG_HOURLY_WAGE_USD}")
    print("Done!")


if __name__ == "__main__":
    run()
