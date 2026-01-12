# Ustawiamy backend "Agg", żeby matplotlib nie próbował otwierać okienka
import matplotlib
matplotlib.use("Agg")

import pandas as pd
import pytest
from visualizations import plot_city_trends, plot_city_heatmaps


# Sztuczne  dane do testów:
@pytest.fixture
def trend_df_small() -> pd.DataFrame:
    rows = []
    for city in ["Warszawa", "Katowice"]:
        for year in [2015, 2024]:
            for month in range(1, 13):
                rows.append(
                    {"city": city, "year": year, "month": month, "PM2.5": float(month)}
                )
    return pd.DataFrame(rows)

@pytest.fixture
def df_ex3_small() -> pd.DataFrame:
    rows = []
    for city_i, city in enumerate(["A", "B", "C", "D", "E"]):
        for year in [2015, 2018, 2021, 2024]:
            for month in range(1, 13):               
                pm = float(10 + city_i + month / 10)
                rows.append({"city": city, "year": year, "month": month, "PM2.5": pm})
    return pd.DataFrame(rows)


# Testy do  plot_city_trends:

def test_plot_city_trends_returns_figure(trend_df_small):
    # test  czy funkcja zwraca obiekt Figure.
    fig = plot_city_trends(trend_df_small)
    assert hasattr(fig, "axes")
    assert len(fig.axes) == 1  


def test_plot_city_trends_has_4_lines(trend_df_small):
   # Test:  Dla 2 miast x 2 lata powinny być 4 linie na wykresie.
    fig = plot_city_trends(trend_df_small, cities=("Warszawa", "Katowice"), years=(2015, 2024))
    ax = fig.axes[0]
    # linie na osi:
    assert len(ax.lines) == 4


def test_plot_city_trends_xticks_1_to_12(trend_df_small):
    # test  czy ticki osi X obejmują 1..12.
    fig = plot_city_trends(trend_df_small)
    ax = fig.axes[0]
    ticks = list(ax.get_xticks())
    
    for m in range(1, 13):
        assert m in ticks


# Test do plot_city_heatmap

def test_plot_city_heatmaps_returns_figure(df_ex3_small):
    # test czy heatmapy zwracają Figure.
    cities = ["A", "B", "C", "D"]
    fig = plot_city_heatmaps(df_ex3_small, cities=cities, ncols=4)
    assert hasattr(fig, "axes")
    assert len(fig.axes) > 0


def test_plot_city_heatmaps_creates_at_least_one_panel(df_ex3_small):
    # test: Dla 4 miast powinny powstać co najmniej 4 osie 'panelowe' (plus ewentualne colorbary).
    cities = ["A", "B", "C", "D"]
    fig = plot_city_heatmaps(df_ex3_small, cities=cities, ncols=4)
    panel_axes = [ax for ax in fig.axes if ax.get_title() in cities]
    assert len(panel_axes) == 4


def test_plot_city_heatmaps_month_ticks_are_1_to_12(df_ex3_small):
   # test czy na panelach są ticki 1..12 
    cities = ["A", "B", "C", "D"]
    fig = plot_city_heatmaps(df_ex3_small, cities=cities, ncols=4)

    panel_axes = [ax for ax in fig.axes if ax.get_title() in cities]
    assert len(panel_axes) == 4

    for ax in panel_axes:
        ticks = [t.get_text() for t in ax.get_xticklabels()]
        present = set(ticks)
        assert "1" in present
        assert "12" in present


def test_plot_city_heatmaps_ignores_unknown_city(df_ex3_small):
    # Test z miatem, którego nie ma w danych:
    cities = ["A", "B", "NIE_ISTNIEJE"]
    fig = plot_city_heatmaps(df_ex3_small, cities=cities, ncols=4)
    assert hasattr(fig, "axes")
