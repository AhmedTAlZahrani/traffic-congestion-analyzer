from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

PLOTS_DIR = Path(__file__).resolve().parents[1] / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def plot_top10(df: pd.DataFrame, filename: str = "top10_hours_lost.png") -> Path:
    fig, ax = plt.subplots()
    ax.bar(df["city"], df["hours_lost"])  # no explicit colors
    ax.set_title("Top 10 Cities – Annual Hours Lost per Commuter")
    ax.set_ylabel("Hours per year")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=45, labelrotation=45)
    outpath = PLOTS_DIR / filename
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)
    return outpath