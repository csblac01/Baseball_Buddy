import pandas as pd
import statsapi
from datetime import datetime, timezone
from pathlib import Path

WATCHLIST = Path("data/watchlist.csv")
OUTFILE = Path("data/players.csv")

# What we want to keep (we’ll expand later)
STAT_KEYS = {
    "gamesPlayed": "g",
    "atBats": "ab",
    "runs": "r",
    "hits": "h",
    "doubles": "2b",
    "triples": "3b",
    "homeRuns": "hr",
    "rbi": "rbi",
    "baseOnBalls": "bb",
    "strikeOuts": "so",
    "avg": "avg",
    "obp": "obp",
    "slg": "slg",
    "ops": "ops",
}

def get_season_candidates():
    y = datetime.now(timezone.utc).year
    return [y, y - 1]  # if current year has no stats yet, fall back

def safe_player_season_stats(mlb_id: int):
    # statsapi.player_stat_data(personId, group="[hitting...]", type="season", season=...)
    # group format is a string like "[hitting]" or "[hitting,pitching]" :contentReference[oaicite:2]{index=2}
    for season in get_season_candidates():
        try:
            data = statsapi.player_stat_data(mlb_id, group="[hitting]", type="season", season=season)
            stats = (data or {}).get("stats", [])
            splits = stats[0].get("splits", []) if stats else []
            if splits:
                return season, splits[0].get("stat", {})
        except Exception:
            pass
    return None, {}

def main():
    if not WATCHLIST.exists():
        raise FileNotFoundError("Missing data/watchlist.csv")

    wl = pd.read_csv(WATCHLIST)
    rows = []

    for _, r in wl.iterrows():
        name = str(r["name"]).strip()
        mlb_id = int(r["mlb_id"])

        season, stat = safe_player_season_stats(mlb_id)

        row = {"name": name, "mlb_id": mlb_id, "year": season}
        for k, outk in STAT_KEYS.items():
            row[outk] = stat.get(k)
        rows.append(row)

    df = pd.DataFrame(rows)
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTFILE, index=False)
    print(f"✅ Wrote {OUTFILE} with {len(df)} players")

if __name__ == "__main__":
    main()
