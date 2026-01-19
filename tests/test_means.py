import pandas as pd
import pytest

from means import make_trend_df, prepare_ex3_heatmap_df, prepare_voivodeship_stats


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

@pytest.fixture
def df_ex4_small() -> pd.DataFrame:
    # Mini zestaw danych do testów
    return pd.DataFrame({
        "year": [2024, 2024, 2024, 2024],
        "station": ["S1", "S2", "S3", "S4"],
        "city": ["Warszawa", "Warszawa", "Kraków", "Kraków"],
        "exceeded": [10, 20, 5, 15]
    })

@pytest.fixture
def meta_df_small() -> pd.DataFrame:
    # Mini metadane z województwami
    return pd.DataFrame({
        "Kod stacji": ["S1", "S2", "S3", "S4"],
        "Województwo": ["Mazowieckie", "Mazowieckie", "Małopolskie", "Małopolskie"]
    })

def test_prepare_voivodeship_stats_detects_shuffle(df_ex4_small, meta_df_small):
    """
    Test sprawdza, czy prepare_voivodeship_stats zwraca poprawne średnie.
    Jeśli w funkcji jest 'sample(frac=1)', test powinien wywalić błąd.
    """
    stats = prepare_voivodeship_stats(df_ex4_small, meta_df_small)
    
    # Obliczamy oczekiwane średnie ręcznie
    expected = df_ex4_small.merge(
        meta_df_small, left_on="station", right_on="Kod stacji"
    ).groupby(["Województwo", "year"])["exceeded"].mean().reset_index()
    expected = expected.rename(columns={"exceeded": "avg_exceeded_days"})
    
    for idx, row in expected.iterrows():
        stat_row = stats[
            (stats["Województwo"] == row["Województwo"]) &
            (stats["year"] == row["year"])
        ]
        # Jeśli wartości nie zgadzają się dokładnie -> fail
        assert abs(stat_row["avg_exceeded_days"].values[0] - row["avg_exceeded_days"]) < 1e-6, \
            f"Detected unexpected shuffling in {row['Województwo']} year {row['year']}"
