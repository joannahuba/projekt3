import pandas as pd
import pytest
import logging
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.utils import (
    clean_gios_df,
    normalize_station_codes,
    to_long,
    add_city
)


# -------------------- logging config --------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------- pytest fixtures --------------------

@pytest.fixture
def metadata_basic():
    """
    Basic metadata fixture reused across multiple tests.
    """
    logger.info("Creating metadata_basic fixture")

    return pd.DataFrame({
        "Kod stacji": ["ST01", "ST02"],
        "Miejscowość": ["Warszawa", "Katowice"],
        "Stary Kod stacji \n(o ile inny od aktualnego)": ["OLD001", None]
    })

@pytest.fixture
def raw_df_2015():
    """
    Raw GIOŚ dataframe for year <= 2015
    (Kod stacji in row 0, data from row 3)
    """
    logger.info("Creating raw_df_2015 fixture")

    return pd.DataFrame([
        ["Kod stacji", "ST01", "ST02"],
        ["Wskaźnik", "PM2.5", "PM2.5"],
        ["Czas uśredniania", "1g", "1g"],
        ["2015-01-01 01:00:00", "10", "20"],
        ["2015-01-01 02:00:00", "30", "40"],
    ])


@pytest.fixture
def raw_df_after_2015():
    """
    Raw GIOŚ dataframe for years > 2015
    """
    logger.info("Creating raw_df_after_2015 fixture")

    return pd.DataFrame([
        ["Nr", 1, 2],
        ["Kod stacji", "ST01", "ST02"],
        ["Wskaźnik", "PM2.5", "PM2.5"],
        ["Czas uśredniania", "1g", "1g"],
        ["Jednostka", "ug/m3", "ug/m3"],
        ["Czas pomiaru", "ST01-PM2.5", "ST02-PM2.5"],
        ["2018-01-01 01:00:00", "10.5", "20.3"],
        ["2018-01-01 02:00:00", "15.2", "25.1"],
    ])

@pytest.fixture
def realistic_raw_df():
    """
    Realistic GIOŚ-like raw dataframe for end-to-end testing (>2015 format).
    """
    return pd.DataFrame([
        ["Nr", 1, 2],
        ["Kod stacji", "ST01", "ST02"],
        ["Wskaźnik", "PM2.5", "PM2.5"],
        ["Czas uśredniania", "1g", "1g"],
        ["Jednostka", "ug/m3", "ug/m3"],
        ["Czas pomiaru", "ST01-PM2.5", "ST02-PM2.5"],
        ["2018-01-01 01:00:00", "10,5", "20,3"],
        ["2018-01-01 02:00:00", "15,2", "25,1"],
    ])



# -------------------- tests --------------------

def test_clean_gios_df_after_2015(raw_df_after_2015):
    """
    Test cleaning of a realistic GIOŚ raw dataframe
    for years > 2015.
    """
    logger.info("Running test_clean_gios_df_after_2015")

    clean = clean_gios_df(raw_df_after_2015, 2018)

    assert list(clean.columns) == ["Datetime", "ST01", "ST02"]
    assert len(clean) == 2

def test_clean_gios_df_2015(raw_df_2015):
    logger.info("Running test_clean_gios_df_2015")

    clean = clean_gios_df(raw_df_2015, 2015)

    assert list(clean.columns) == ["Datetime", "ST01", "ST02"]
    assert len(clean) == 2
    assert clean.iloc[0]["ST01"] == "10"


@pytest.mark.parametrize(
    "year,fixture_name,expected_rows",
    [
        (2015, "raw_df_2015", 2),
        (2018, "raw_df_after_2015", 2),
    ]
)
def test_clean_gios_df_by_year(request, year, fixture_name, expected_rows):
    df = request.getfixturevalue(fixture_name)

    clean = clean_gios_df(df, year)

    assert len(clean) == expected_rows



def test_normalize_station_codes(metadata_basic):
    """
    Test replacement of old station codes
    with current ones using metadata.
    """
    logger.info("Running test_normalize_station_codes")

    df = pd.DataFrame({
        "Datetime": ["2018-01-01 01:00:00"],
        "OLD001": ["10,0"],
        "ST02": ["20,0"]
    })

    out = normalize_station_codes(df, metadata_basic)

    logger.info(f"Columns after normalization: {list(out.columns)}")

    assert "ST01" in out.columns
    assert "OLD001" not in out.columns
    assert out["ST01"].iloc[0] == "10,0"


@pytest.mark.parametrize(
    "value,expected_nan",
    [
        ("10,5", False),
        ("bad", True),
        (None, True),
    ]
)
def test_to_long_numeric_coercion(value, expected_nan):
    """
    Parametrized test verifying numeric coercion
    of PM2.5 values in long format.
    """
    logger.info(f"Running test_to_long_numeric_coercion with value={value}")

    df = pd.DataFrame({
        "Datetime": ["2018-01-01 01:00:00"],
        "ST01": [value],
    })

    long = to_long(df)

    result = long.loc[0, "PM2.5"]
    logger.info(f"Converted PM2.5 value: {result}")

    is_nan = pd.isna(result)
    assert is_nan == expected_nan


def test_add_city_mapping(metadata_basic):
    """
    Test correct mapping of station codes to cities.
    """
    logger.info("Running test_add_city_mapping")

    df = pd.DataFrame({
        "station": ["ST01", "ST02", "UNKNOWN"],
        "PM2.5": [10.0, 20.0, 30.0]
    })

    out = add_city(df, metadata_basic)

    logger.info("City mapping results:")
    logger.info(out)

    assert out.loc[out["station"] == "ST01", "city"].iloc[0] == "Warszawa"
    assert out.loc[out["station"] == "ST02", "city"].iloc[0] == "Katowice"
    assert pd.isna(out.loc[out["station"] == "UNKNOWN", "city"]).iloc[0]


def test_to_long_raises_without_datetime():
    """
    Test that to_long raises an error
    when the Datetime column is missing.
    """
    logger.info("Running test_to_long_raises_without_datetime")

    df = pd.DataFrame({
        "ST01": [10, 20]
    })

    with pytest.raises(KeyError):
        to_long(df)

    logger.info("KeyError correctly raised")


def test_utils_realistic_flow(metadata_basic, realistic_raw_df):
    """
    End-to-end sanity test using pytest fixtures
    and a realistic GIOŚ-like structure.
    """
    logger.info("Running test_utils_realistic_flow")
    print(metadata_basic)
    print(realistic_raw_df)

    clean = clean_gios_df(realistic_raw_df, 2018)
    print(metadata_basic)
    print(realistic_raw_df)
    long = to_long(clean)
    print(metadata_basic)
    print(realistic_raw_df)
    out = add_city(long, metadata_basic)

    logger.info(f"Final dataframe head:\n{out.head()}")

    assert out["PM2.5"].dtype.kind in "fi"
    assert out["city"].notna().any()
