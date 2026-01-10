
from pathlib import Path
import logging
from utils import download_gios_archive

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

#---------------READ DATA FROM GIOS---------------

# configuration
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(exist_ok=True)

gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
gios_ids = {2014: "302", 2019: "322", 2024: "582"}
gios_files = {
    2014: "2014_PM2.5_1g.xlsx",
    2019: "2019_PM25_1g.xlsx",
    2024: "2024_PM25_1g.xlsx",
}
years = [2014, 2019, 2024]

for year in years:
    raw = download_gios_archive(
        year,
        gios_archive_url,
        gios_ids[year],
        gios_files[year]
    )
    logger.info(
        #f"Year: {year}: {raw.shape[0]} records, "
        #f"{raw['station'].nunique()} stations, "
        #f"{raw['city'].nunique()} cities,"
        f"Columns:{raw.columns}"

    )

    raw.to_csv(DATA_DIR/f"raw{year}.csv")
