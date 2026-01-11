from __future__ import annotations
import math
from typing import Sequence, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Wykres do zad. 2:

def plot_city_trends(
    trend_df: pd.DataFrame,
    cities: Sequence[str] = ("Warszawa", "Katowice"),
    years: Sequence[int] = (2015, 2024),
    figsize: Tuple[float, float] = (10, 6),
) -> plt.Figure:

    fig, ax = plt.subplots(figsize=figsize)

    for city in cities:
        for y in years:
            sub = trend_df[(trend_df["city"] == city) & (trend_df["year"] == y)].copy()
            sub = sub.sort_values("month")

            ax.plot(
                sub["month"],
                sub["PM2.5"],
                marker="o",
                label=f"{city} {y}"
            )

    ax.set_title("Średnie miesięczne PM2.5 – Warszawa i Katowice (2015 vs 2024)", fontsize=14)
    ax.set_xlabel("Miesiąc")
    ax.set_ylabel("PM2.5 [µg/m³]")
    ax.set_xticks(list(range(1, 13)))
    ax.grid(True, alpha=0.3)
    ax.legend(title="Miasto i rok")

    fig.tight_layout()
    return fig


# Heatmapa do zad. 3 
def plot_city_heatmaps(
    df_ex3: pd.DataFrame,
    cities: Sequence[str],
    years: Sequence[int] = (2015, 2018, 2021, 2024),
    ncols: int = 4,
    figsize_per_panel: Tuple[float, float] = (2.6, 2.2),
    annot: bool = False,
    fmt: str = ".1f",
) -> plt.Figure:

    sns.set_theme(style="white")
    df_plot = df_ex3[df_ex3["city"].isin(cities)].copy()
    vmin = float(df_plot["PM2.5"].min())
    vmax = float(df_plot["PM2.5"].max())
    n_panels = len(cities)
    nrows = math.ceil(n_panels / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(figsize_per_panel[0] * ncols,
                 figsize_per_panel[1] * nrows),
        constrained_layout=True
    )
    axes = axes.flatten()
    mappable = None
    
    #rysowanie heatmapy dla kazdego miasta:
    for ax, city in zip(axes, cities):
        data = df_plot[df_plot["city"] == city]

        heatmap_data = (
            data.pivot(index="year", columns="month", values="PM2.5")
            .reindex(index=years)
            .reindex(columns=range(1, 13))
        )

        hm = sns.heatmap(
            heatmap_data,
            ax=ax,
            cmap="coolwarm",
            vmin=vmin,
            vmax=vmax,
            annot=annot,
            fmt=fmt,
            cbar=False
        )

        mappable = hm.collections[0]  #mapowanie kolorów do legendy

        ax.set_title(city, fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(labelsize=7)


    for ax in axes[len(cities):]:
        ax.axis("off")

    if mappable is not None:
        cbar = fig.colorbar(
            mappable,
            ax=axes[:len(cities)],
            orientation="horizontal",
            fraction=0.05,
            pad=0.08
        )
        cbar.set_label("Średnie miesięczne PM2.5")

    return fig
