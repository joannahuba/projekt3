from utils import normalize_station_codes, clean_gios_df, add_city, to_long
import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -------------------- configuration --------------------
DATA_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(exist_ok=True)

# -------------------- read metadata --------------------
meta_df = pd.read_excel(DATA_DIR/"Metadata.xlsx")
logger.info(f"Wczytano metadane: {meta_df.shape[0]} stacji")
logger.info(f"Kolumny metadanych: {list(meta_df.columns)}")

# -------------------- read raw data --------------------
df_2015 = pd.read_csv(DATA_DIR / "raw2015.csv", index_col=0)
df_2018 = pd.read_csv(DATA_DIR / "raw2019.csv", index_col=0)
df_2021 = pd.read_csv(DATA_DIR / "raw2021.csv", index_col=0)
df_2024 = pd.read_csv(DATA_DIR / "raw2024.csv", index_col=0)

# -------------------- data cleaning --------------------
dfs = {2015: df_2015,
       2018: df_2018,
       2021: df_2021,
       2024: df_2024}

for year in dfs.keys():
    raw = dfs[year]
    clean = clean_gios_df(raw, year)

    # sanity check: columns
    logger.info(f"Columns in {year}: {list(clean.columns)}")
    clean = normalize_station_codes(clean, meta_df)

    print(f"\n------------------ {year}: first 10 rows AFTER normalize_station_codes ------------------")
    print(clean.head(10))

    long = to_long(clean)
    long = add_city(long, meta_df)
    long["Datetime"] = pd.to_datetime(long["Datetime"], errors="coerce", dayfirst=True)
    long["year"] = year

    dfs[year] = long
    # sanity check: basic stats
    logger.info(
        f"year {year}: {long.shape[0]} records, "
        f"{long['station'].nunique()} stations, "
        f"{long['city'].nunique()} cities"
    )


# -------------------- common stations --------------------
common_stations = set(dfs[2015]["station"]) \
    & set(dfs[2018]["station"]) \
    & set(dfs[2021]["station"]) \
    & set(dfs[2024]["station"])

# sanity check: number of common stations
logger.info(f"Number of common stations for common years: {len(common_stations)}")
logger.info(f"Common stations: {common_stations}")

for year in dfs:
    dfs[year] = dfs[year][dfs[year]["station"].isin(common_stations)]

combined_df = pd.concat(dfs.values(), ignore_index=True)
combined_df = combined_df.dropna(subset=["Datetime", "PM2.5"])

print(f"\n------------------ {year}: first 10 rows AFTER combining dfs ------------------")
print(combined_df.head(10))


# -------------------- datetime handing --------------------
combined_df["date"] = combined_df["Datetime"].apply(
    lambda x: x.date() if x.hour != 0 else (x - pd.Timedelta(days=1)).date()
)
combined_df["month"] = pd.to_datetime(combined_df["date"]).dt.month

# sanity check: 
logger.info(f"Combined data set: {combined_df.shape[0]} rows")
logger.info(f"Years in data: {combined_df['year'].unique()}")

# save into a file 
combined_df = combined_df.drop(columns=["Datetime"])
print(combined_df.head(10))
combined_df.to_csv(OUT_DIR / "cleaned_and_combined.csv", index=False)
logger.info("Saved cleaned_and_combined.csv")


# -------------------- MONTHLY PM2.5 --------------------
monthly_PM25 = combined_df.copy()
monthly_PM25 = monthly_PM25.groupby(
    ["year", "month", "station", "city"], as_index=False
)[["PM2.5"]].mean()
logger.info(f"Number of rows in monthly_PM25: {len(monthly_PM25)}")
monthly_PM25.to_csv(OUT_DIR / "monthly_PM25.csv")

# Mean PM2.5 per city (Warszawa, Katowice)
df_ex2 = monthly_PM25[monthly_PM25["city"].isin(["Warszawa", "Katowice"])]
df_ex2 = df_ex2.groupby(
    ["year", "month", "city"], as_index=False
)[["PM2.5"]].mean()

# -------------------- Number of days PM2.5 norm exceeded --------------------
daily_avg = combined_df.groupby(
    ["year", "station", "city", "date"]
)[["PM2.5"]].mean().reset_index()

daily_avg["exceeded"] = daily_avg["PM2.5"] > 15

df_ex4 = daily_avg.groupby(
    ["year", "station", "city"]
)["exceeded"].sum().reset_index()

# save into files
df_ex2.to_csv(OUT_DIR / "df_ex2.csv", index=False)
logger.info("Zapisano df_ex2.csv")
df_ex4.to_csv(OUT_DIR / "df_ex4.csv", index=False)
logger.info("Zapisano df_ex4.csv")

# sanity checks
logger.info(f"Brakujące PM2.5: {combined_df['PM2.5'].isna().sum()}")
logger.info(f"Wartości PM2.5 < 0: {(combined_df['PM2.5'] < 0).sum()}")
logger.info(f"Liczba wierszy w df_ex4: {len(df_ex4)}")
logger.info(
    f"Maksymalna liczba dni z przekroczeniem: {df_ex4['exceeded'].max()}"
)


print("\n--- combined_df (head) ---")
print(combined_df.head())

print("\n--- combined_df.info() ---")
print(combined_df.info())

print("\n--- monthly_PM25 (Warszawa, styczeń) ---")
print(
    monthly_PM25[
        (monthly_PM25["city"] == "Warszawa") &
        (monthly_PM25["month"] == 1)
    ].head()
)

print("\n--- df_ex4: top 5 stacji z największą liczbą przekroczeń ---")
print(
    df_ex4.sort_values("exceeded", ascending=False).head()
)