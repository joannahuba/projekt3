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

    required = {"city", "year", "month", "PM2.5"}
    missing = required - set(trend_df.columns)
    if missing:
        raise ValueError(f"trend_df nie ma kolumn: {sorted(missing)}")

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


#Heatmapa do zad. 3 

def plot_city_heatmaps(
    df_ex3: pd.DataFrame,
    cities: Sequence[str],
    years: Sequence[int] = (2015, 2018, 2021, 2024),
    ncols: int = 3,
    figsize_per_panel: Tuple[float, float] = (4.2, 3.4),
    annot: bool = False,
    fmt: str = ".1f",
) -> plt.Figure:

    required = {"city", "year", "month", "PM2.5"}
    missing = required - set(df_ex3.columns)
    if missing:
        raise ValueError(f"df_ex3 nie ma kolumn: {sorted(missing)}")

    sns.set_theme(style="white")

    df_plot = df_ex3[df_ex3["city"].isin(list(cities))].copy()

    vmin = float(df_plot["PM2.5"].min())
    vmax = float(df_plot["PM2.5"].max())

    n_panels = len(cities)
    nrows = math.ceil(n_panels / ncols)

    fig_w = figsize_per_panel[0] * ncols
    fig_h = figsize_per_panel[1] * nrows
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(fig_w, fig_h), sharex=True, sharey=True)

    # gdy nrows*ncols == 1, axes nie jest tablicą
    if not isinstance(axes, (list, tuple)) and not hasattr(axes, "__len__"):
        axes = [axes]
    else:
        axes = axes.flatten()
        
    mappable = None

    for ax, city in zip(axes, cities):
        data = df_plot[df_plot["city"] == city]

        heatmap_data = (
            data.pivot(index="year", columns="month", values="PM2.5")
            .reindex(index=list(years))
            .reindex(columns=list(range(1, 13)))
        )

        hm = sns.heatmap(
            heatmap_data.astype(float),
            ax=ax,
            annot=annot,
            fmt=fmt,
            cmap="coolwarm",
            vmin=vmin,
            vmax=vmax,
            cbar=False  
        )

        mappable = hm.collections[0]

        ax.set_title(city)
        ax.set_xlabel("Miesiąc")
        ax.set_ylabel("Rok")

    for ax in axes[len(cities):]:
        ax.axis("off")

    if mappable is not None:
        cbar = fig.colorbar(mappable, ax=axes[:len(cities)], shrink=0.9)
        cbar.set_label("Średnie miesięczne PM2.5")

    fig.tight_layout()
    return fig

