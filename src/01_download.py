
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
gios_ids = {2015: "236", 2018: "603", 2021: "486", 2024: "582"}
gios_files = {
    2015: "2015_PM25_1g.xlsx",
    2018: "2018_PM25_1g.xlsx",
    2021: "2021_PM25_1g.xlsx",
    2024: "2024_PM25_1g.xlsx"
    }
years = [2015, 2018, 2021, 2024]

for year in years:
    raw = download_gios_archive(
        year,
        gios_archive_url,
        gios_ids[year],
        gios_files[year]
    )
    logger.info(
        f"Columns:{raw.columns}"

    )

    raw.to_csv(DATA_DIR/f"raw{year}.csv")
