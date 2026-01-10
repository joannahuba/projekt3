import pandas as pd

def make_trend_df(df_ex2: pd.DataFrame, years=(2015, 2024)) -> pd.DataFrame:
    """
    Przygotowuję dataframe do analizy trendów średnich miesięcznych
    stężenia PM2.5 dla Warszawy i Katowic.

    oczekiwane kolumny w df_ex2:
        - year (int)
        - month (int 1-12)
        - city (str)
        - PM2.5 (float)
    Funkcja zwraca DataFrame trend_df posortowany według city, year, month.
    """
    required = {"year", "month", "city", "PM2.5"}
    missing = required - set(df_ex2.columns)
    if missing:
        raise ValueError(f"df_ex2 is missing columns: {sorted(missing)}")

    trend_df = df_ex2[df_ex2["year"].isin(list(years))].copy()

    # sanity check - months should be 1..12
    trend_df["month"] = pd.to_numeric(trend_df["month"], errors="coerce")

    trend_df.sort_values(["city", "year", "month"], inplace=True)
    trend_df.reset_index(drop=True, inplace=True)

    return trend_df

# sanity checks:
def trend_sanity_summary(trend_df: pd.DataFrame) -> dict:
    years_present = sorted(trend_df["year"].dropna().unique().tolist())
    cities_present = sorted(trend_df["city"].dropna().unique().tolist())

    months_per_city_year = (
        trend_df.groupby(["city", "year"])["month"].nunique().unstack()
        if len(trend_df) else None
    )

    mean_pm25_city_year = (
        trend_df.groupby(["city", "year"])["PM2.5"].mean()
        if len(trend_df) else None
    )

    return {
        "years_present": years_present,
        "cities_present": cities_present,
        "months_per_city_year": months_per_city_year,
        "mean_pm25_city_year": mean_pm25_city_year,
    }


def save_trend_df(trend_df: pd.DataFrame, out_path) -> None:
    trend_df.to_csv(out_path, index=False)

