import logging
import requests
import zipfile
import io
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

def download_gios_archive(year, gios_archive_url, gios_id, filename):
    # Pobranie archiwum ZIP do pamięci
    url = f"{gios_archive_url}{gios_id}"
    logger.info(f"Pobieranie danych GIOŚ dla roku {year}")

    response = requests.get(url)
    response.raise_for_status()
    
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        if not filename:
            logger.error(f"Plik {filename} nie znaleziony w archiwum {year}")
            return None
        else:
            with z.open(filename) as f:
                try:
                    df = pd.read_excel(f, header=None)
                except Exception as e:
                    logger.error(f"Błąd przy wczytywaniu danych {year}: {e}")
                    return None

    logger.info(f"Dane dla {year} wczytane poprawnie")
    return df


def clean_gios_df(df, year):
    """
    Prepares raw GIOŚ measurement data by:
    - removing metadata rows,
    - using the first data row as column names,
    - removing that header row from the data,
    - standardizing the timestamp column name to 'Datetime'.
    """
    if year > 2015:
        df = df.drop(index=[0, 2, 3, 4, 5])
    else:
        df = df.drop(index=[1, 2])

    header = df.iloc[0]
    df = df.iloc[1:]
    df.columns = header
    df.columns.values[0] = "Datetime"

    df = df.reset_index(drop=True)

    # ---- NaN percentage logging ----
    nan_percent = df.isna().mean() * 100

    logging.info(f"NaN percentage per column for year {year}:")
    for col, pct in nan_percent.items():
        logging.info(f"  {col}: {pct:.2f}%")

    return df




def normalize_station_codes(df, metadata):
    """Normalize station names to keep them consistent and up to date."""
    mapping = {}

    for _, row in metadata.iterrows():
        old_code = row["Stary Kod stacji \n(o ile inny od aktualnego)"]
        new_code = row["Kod stacji"]

        if pd.notna(old_code):
            mapping[old_code] = new_code

    return df.rename(columns=mapping)


def to_long(df):
    """
    Converts wide GIOŚ PM2.5 data to long format and
    ensures PM2.5 values are numeric.
    """
    long_df = pd.melt(
        df,
        id_vars=["Datetime"],
        var_name="station",
        value_name="PM2.5"
    )

    # replace commas with dots and coerce to numeric
    long_df["PM2.5"] = (
        long_df["PM2.5"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    long_df["PM2.5"] = pd.to_numeric(long_df["PM2.5"], errors="coerce")

    return long_df



def add_city(df, metadata):
    station_city = dict(
        zip(metadata["Kod stacji"], metadata["Miejscowość"])
    )
    df["city"] = df["station"].map(station_city)
    return df


import pandas as pd
import plotly.graph_objects as go

def plot_exceeded_days_top_bottom(
    df_ex4,
    year=2024,
    top_n=3,
):
    """
    Creates a grouped bar plot for stations with the highest and lowest
    number of exceeded PM2.5 days in a given year.

    Parameters:
    - df_ex4 (pd.DataFrame): DataFrame with columns ['year', 'station', 'exceeded']
    - year (int): Reference year for selecting top/bottom stations
    - top_n (int): Number of top and bottom stations to include
    """
    df_year = df_ex4[df_ex4["year"] == year]

    top = df_year.nlargest(top_n, "exceeded")
    bottom = df_year.nsmallest(top_n, "exceeded")
    stations = pd.concat([top, bottom])["station"].unique()

    plot_df = df_ex4[df_ex4["station"].isin(stations)].copy()

    station_groups = plot_df["station"].unique()

    colors = [
        "#7FB3D5",
        "#1F618D",
        "#F4D03F",
        "#C0392B",
        "#008080",
        "#40B0A6"
    ]

    bars = []
    for i, station in enumerate(station_groups):
        df_station = plot_df[plot_df["station"] == station]
        bar = go.Bar(
            x=df_station["year"],
            y=df_station["exceeded"],
            name=station,
            marker=dict(color=colors[i % len(colors)])
        )
        bars.append(bar)

    fig = go.Figure(data=bars)
    fig.update_layout(
        height=800,
        font=dict(
            family="Liberation Serif",
            size=20,
            color="#2C3E50"
        ),
        barmode="group",
        title=dict(
            text="Dni z przekroczeniem normy (WHO)",
            x=0.5,
            xanchor="center",
            font=dict(
                family="Liberation Serif",
                size=35,
                color="#2C3E50"
            )
        ),
        xaxis_title="Rok",
        yaxis_title="Liczba przekroczonych dni",
    )

    return fig

