import pandas as pd
import pytest

from means import make_trend_df, prepare_ex3_heatmap_df


def test_make_trend_df_filters_years_and_sorts():
    df = pd.DataFrame({
        "year": [2015, 2018, 2015, 2024],
        "month": [2, 1, 1, 12],
        "city": ["Katowice", "Warszawa", "Katowice", "Warszawa"],
        "PM2.5": [10.0, 20.0, 30.0, 40.0],
    })

    trend = make_trend_df(df, years=(2015, 2024))

    # test - filtrowanie lat
    assert set(trend["year"].unique()) == {2015, 2024}

    # test  - sortowanie 
    sorted_copy = trend.sort_values(["city", "year", "month"]).reset_index(drop=True)
    assert trend.reset_index(drop=True).equals(sorted_copy)


def test_make_trend_df_missing_columns_raises():
    df = pd.DataFrame({"year": [2015], "month": [1]})
# testujemy czy błędny DataFrame da ValueError:
    with pytest.raises(ValueError):
        make_trend_df(df)

def test_prepare_ex3_heatmap_df_groups_correctly():
    monthly = pd.DataFrame({
        "city": ["A", "A", "A", "B"],
        "year": [2015, 2015, 2015, 2015],
        "month": [1, 1, 2, 1],
        "PM2.5": [10.0, 20.0, 30.0, 40.0],
        "station": ["s1", "s2", "s1", "s1"], 
    })

    df_ex3 = prepare_ex3_heatmap_df(monthly)

    # Wynik dla A-2015-1 powinien być średnią z (10,20) = 15
    val = df_ex3[(df_ex3["city"] == "A") & (df_ex3["year"] == 2015) & (df_ex3["month"] == 1)]["PM2.5"].iloc[0]
    assert val == 15.0

def test_prepare_ex3_heatmap_df_missing_columns_raises():
    # Testujemy czy zły input da ValueError 
    bad = pd.DataFrame({
        "city": ["A"],
        "year": [2015],
        "month": [1],
    })

    with pytest.raises(ValueError):
        prepare_ex3_heatmap_df(bad)
