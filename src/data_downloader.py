# This script downloads football match data from football-data.co.uk for specified seasons and leagues
# It saves the data in CSV format in the "data/raw" directory.
import requests
from pathlib import Path

RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Seasons in football-data format (you can add more later)
SEASONS = [
    "2324",
    "2223",
    "2122",
    "2021",
    "1920",
    "1819",
    "1718",
    "1617",
    "1516",
    "1415",
]

# League codes on football-data.co.uk
# You can add more later if you want even more games.
# LEAGUES = [
#     "E0",  # England Premier League
#     "E1",  # England Championship
#     "D1",  # Germany Bundesliga
#     "SP1", # Spain La Liga
#     "I1",  # Italy Serie A
#     "F1",  # France Ligue 1
# ]
LEAGUES = [
    "E0",  # Premier League
    "E1",  # England Championship
    "D1",  # Bundesliga
    "SP1", # La Liga
    "I1",  # Serie A
    "F1",  # Ligue 1
    "P1",  # Portugal
    "N1",  # Netherlands
]

BASE_URL = "https://www.football-data.co.uk/mmz4281/{season}/{league}.csv"


def download_all():
    for season in SEASONS:
        for league in LEAGUES:
            url = BASE_URL.format(season=season, league=league)
            filename = f"{league}_{season}.csv"
            dest = RAW_DATA_DIR / filename

            print(f"Downloading {url} -> {dest}")

            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200 and len(resp.content) > 0:
                    dest.write_bytes(resp.content)
                    print(f"Saved {dest}")
                else:
                    print(f"Skipped {url} (status {resp.status_code}, empty or missing)")
            except Exception as e:
                print(f"Error downloading {url}: {e}")


if __name__ == "__main__":
    download_all()
