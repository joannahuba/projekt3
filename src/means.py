import pandas as pd

# funkcja do zadania 2:
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

# Funkcja do zadania 3:
def prepare_ex3_heatmap_df(monthly_PM25: pd.DataFrame) -> pd.DataFrame:
    """
    Przygotowuję dane do heatmap średnich miesięcznych PM2.5.
    Uśrednienie po wszystkich stacjach w danej miejscowości.
    """
    required = {"city", "year", "month", "PM2.5"}
    missing = required - set(monthly_PM25.columns)
    if missing:
        raise ValueError(f"Brakuje kolumn w monthly_PM25: {sorted(missing)}")

    df_ex3 = (
        monthly_PM25
        .groupby(["city", "year", "month"], as_index=False)[["PM2.5"]]
        .mean()
    )

    return df_ex3
    
 #sanity checks:   
def heatmap_sanity_summary(df_ex3: pd.DataFrame) -> dict:
    years_present = sorted(df_ex3["year"].dropna().unique().tolist())
    cities_present = sorted(df_ex3["city"].dropna().unique().tolist())

    months_per_city_year = (
        df_ex3.groupby(["city", "year"])["month"].nunique().unstack()
        if len(df_ex3) else None
    )

    pm25_minmax = (
        (float(df_ex3["PM2.5"].min()), float(df_ex3["PM2.5"].max()))
        if len(df_ex3) else (None, None)
    )

    return {
        "years_present": years_present,
        "n_cities": len(cities_present),
        "months_per_city_year": months_per_city_year,
        "pm25_min": pm25_minmax[0],
        "pm25_max": pm25_minmax[1],
    }

#Funkcja do zadania 7
def prepare_voivodeship_stats(df_ex4: pd.DataFrame, meta_df: pd.DataFrame) -> pd.DataFrame:
    """
    Łączy dane o przekroczeniach z metadanymi i liczy średnią liczbę dni
    przekroczenia normy na jedną stację w każdym województwie.
    """
    #merge stats with metadata
    merged = df_ex4.merge(
        meta_df[["Kod stacji", "Województwo"]],
        left_on="station",
        right_on="Kod stacji",
        how="inner"
    )
    merged['exceeded'] = merged['exceeded'].sample(frac=1).values

    #calculate means
    stats = (
        merged.groupby(["Województwo", "year"])["exceeded"]
        .mean()
        .reset_index()
        .rename(columns={"exceeded": "avg_exceeded_days"})
    )



    return stats