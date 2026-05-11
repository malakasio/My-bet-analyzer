# ============================================================
# BetDestroy Sports Analysis Engine v2.0
# 7-Analyst system with live data auto-fetch
#
# HOW TO RUN:
#   pip install -r requirements.txt
#   streamlit run app.py
#   → http://localhost:8501
#
# FREE API KEYS (both have free tiers):
#   API-Football : https://rapidapi.com/api-sports/api/api-football
#                  Free: 100 requests / day
#   The Odds API : https://the-odds-api.com
#                  Free: 500 requests / month
# ============================================================

import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(
    page_title="BetDestroy | Analysis Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLES
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #0d1117; }
    section[data-testid="stSidebar"] { background-color: #161b22; }
    section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
    h1,h2,h3,h4 { color: #e6edf3 !important; }
    p,li,label  { color: #c9d1d9; }

    .main-title {
        text-align: center; font-size: 2.4rem; font-weight: 900;
        background: linear-gradient(135deg,#58a6ff 0%,#a371f7 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; margin: 0; padding: 0;
    }
    .main-subtitle {
        text-align: center; color: #8b949e; font-size: 0.9rem;
        margin-top: 4px; margin-bottom: 20px;
    }
    .analyst-header {
        display: flex; align-items: center; gap: 10px;
        background: linear-gradient(90deg,#1f2937 0%,#111827 100%);
        border-left: 4px solid #58a6ff; border-radius: 6px;
        padding: 10px 16px; margin-bottom: 14px;
    }
    .analyst-badge {
        display: inline-block;
        background: linear-gradient(135deg,#58a6ff,#a371f7);
        color: #0d1117; font-size: 0.72rem; font-weight: 700;
        padding: 3px 10px; border-radius: 20px;
        text-transform: uppercase; letter-spacing: 0.05em;
    }
    .fetched-badge {
        display: inline-block; background: #0d4429;
        border: 1px solid #238636; color: #56d364;
        font-size: 0.72rem; font-weight: 600;
        padding: 2px 8px; border-radius: 12px;
        margin-left: 8px;
    }
    .manual-badge {
        display: inline-block; background: #271c0d;
        border: 1px solid #9e6a03; color: #e3b341;
        font-size: 0.72rem; font-weight: 600;
        padding: 2px 8px; border-radius: 12px;
        margin-left: 8px;
    }
    .verdict-card { border-radius: 14px; padding: 28px 24px; text-align: center; margin: 10px 0 20px 0; }
    .verdict-under-15 { background: linear-gradient(135deg,#052e16 0%,#065f46 100%); border: 2px solid #34d399; }
    .verdict-under-25 { background: linear-gradient(135deg,#0c2a1e 0%,#14532d 100%); border: 2px solid #4ade80; }
    .verdict-abort    { background: linear-gradient(135deg,#27150a 0%,#431407 100%); border: 2px solid #fb923c; }
    .verdict-over     { background: linear-gradient(135deg,#1e0a0a 0%,#450a0a 100%); border: 2px solid #f87171; }
    .verdict-no-signal{ background: linear-gradient(135deg,#1c1f26 0%,#2d3139 100%); border: 2px solid #6b7280; }
    .verdict-title { font-size: 1.9rem; font-weight: 900; letter-spacing: 0.04em; margin: 0 0 8px 0; }
    .verdict-sub   { font-size: 1rem; color: #d1d5db; margin: 0; }

    .alert { border-radius: 10px; padding: 14px 18px; margin: 8px 0; line-height: 1.6; }
    .alert-danger  { background: #1a0a0a; border: 1px solid #dc2626; color: #fca5a5; }
    .alert-warning { background: #1c1208; border: 1px solid #d97706; color: #fcd34d; }
    .alert-success { background: #051a0e; border: 1px solid #16a34a; color: #86efac; }
    .alert-info    { background: #0a1628; border: 1px solid #2563eb; color: #93c5fd; }

    .report-card { background:#161b22; border:1px solid #30363d; border-radius:10px; padding:16px 18px; margin:8px 0; }
    .report-card h4 { margin:0 0 10px 0; font-size:0.95rem; color:#58a6ff !important; }
    .report-card p  { margin:3px 0; font-size:0.88rem; color:#c9d1d9; }

    .odds-card { background:#161b22; border:1px solid #30363d; border-radius:10px; padding:16px; text-align:center; }
    .odds-big  { font-size:2rem; font-weight:900; color:#e6edf3; margin:4px 0; }
    .odds-label{ font-size:0.78rem; color:#8b949e; }

    .fetch-log { background:#0d1117; border:1px solid #30363d; border-radius:8px; padding:12px; max-height:200px; overflow-y:auto; }
    .fetch-log p { margin:2px 0; font-size:0.82rem; font-family:monospace; }

    .form-pill { display:inline-block; width:28px; height:28px; border-radius:50%; text-align:center; line-height:28px; font-weight:700; font-size:0.82rem; margin:2px; }
    .form-w { background:#16a34a; color:#fff; }
    .form-d { background:#d97706; color:#fff; }
    .form-l { background:#dc2626; color:#fff; }
    .conf-label { font-size:0.82rem; color:#8b949e; margin-bottom:2px; }
    .section-divider { border:none; border-top:1px solid #30363d; margin:16px 0; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================
_DEFAULTS: dict = {
    # Match setup
    "team_a": "Fiorentina", "team_b": "Napoli", "league_name": "",
    "league_variance": "low",
    # API keys
    "api_key_football": "", "api_key_odds": "",
    # Fetch state
    "fetch_log": [], "fetch_errors": [], "last_fetched": None,
    "fetch_summary": [],
    "fetched_odds": {}, "fetched_odds_match": "",
    "odds_soccer_keys": {},
    # Team search / selection
    "team_a_id": None, "team_b_id": None,
    "team_a_search_results": [], "team_b_search_results": [],
    # Checklist
    "chk_defensive": False, "chk_volatility": False,
    "chk_motivation": False, "chk_lineup": False, "chk_social": False,
    # Statistics (widget keys mirror these names)
    "stat_a_clean_sheets": 0, "stat_b_clean_sheets": 0,
    "stat_a_goals_scored": 1.2, "stat_b_goals_scored": 1.2,
    "stat_a_goals_conceded": 1.2, "stat_b_goals_conceded": 1.2,
    # Tactics
    "tac_a_formation": "4-4-2", "tac_b_formation": "4-4-2",
    "tac_a_offensive": False, "tac_b_offensive": False,
    "tac_a_notes": "", "tac_b_notes": "",
    # Forms (individual widget keys: form_a_0 … form_a_4, same for b)
    "form_a_0": "W", "form_a_1": "W", "form_a_2": "D", "form_a_3": "L", "form_a_4": "W",
    "form_b_0": "W", "form_b_1": "D", "form_b_2": "L", "form_b_3": "W", "form_b_4": "D",
    "form_a_pos": 10, "form_b_pos": 10, "form_league_total": 20,
    # Manager
    "mgr_friends": False, "mgr_a_needs_points": False,
    "mgr_b_needs_points": False, "mgr_notes": "",
    # Officials
    "ref_name": "", "ref_fair": True, "ref_notes": "",
    "coach_a_pressure": False, "coach_b_pressure": False,
    # Social life
    "soc_a_nightclub": False, "soc_a_training": False, "soc_a_feud": False,
    "soc_b_nightclub": False, "soc_b_training": False, "soc_b_feud": False,
    # Bookmaker / Odds
    "bm_odds_dropped": False, "bm_odds_from": 2.00, "bm_odds_to": 1.30,
    # New transfer
    "xfer_team_a": False, "xfer_team_b": False, "xfer_starts": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ============================================================
# API-FOOTBALL FUNCTIONS
# ============================================================

@st.cache_data(ttl=1800, show_spinner=False)
def _af(endpoint: str, params: dict, api_key: str) -> dict:
    """
    Cached GET request to the official API-Football v3 endpoint.

    Base URL : https://v3.football.api-sports.io/
    Auth     : x-apisports-key header
    Free tier: 100 requests / day
    Register : https://dashboard.api-football.com/register

    TTL = 30 min for successful responses.
    Raises ValueError on auth / rate-limit errors so st.cache_data does NOT
    cache failures — a bad key or typo will not block the next attempt.
    """
    url     = f"https://v3.football.api-sports.io/{endpoint}"
    headers = {"x-apisports-key": api_key}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)

        if r.status_code in (401, 403):
            raise ValueError(
                f"Invalid API key (HTTP {r.status_code}). "
                "Go to dashboard.api-football.com and copy your key from the dashboard."
            )
        if r.status_code == 429:
            raise ValueError(
                "Daily limit reached (100 requests/day on free tier). "
                "Resets at midnight UTC."
            )
        r.raise_for_status()

        data = r.json()
        # API returns errors inside 'errors' dict even on HTTP 200
        errs = data.get("errors")
        if errs:
            msg = str(list(errs.values())[0]) if isinstance(errs, dict) else str(errs)
            raise ValueError(f"API error: {msg}")
        return data

    except requests.exceptions.Timeout:
        raise ValueError("Request timed out (12 s). Check your internet connection.")
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Network error: {exc}")


# Common alternate spellings for teams whose API-Football name differs
# from what users typically type. Both directions are listed.
_TEAM_ALT_NAMES: dict[str, list[str]] = {
    # Greek teams
    "olympiacos":               ["Olympiakos", "Olympiakos FC"],
    "olympiakos":               ["Olympiacos", "Olympiacos FC"],
    "panathinaikos":            ["Panathinaikos FC"],
    "aek":                      ["AEK Athens", "AEK Athens FC"],
    "aek athens":               ["AEK", "AEK Athens FC"],
    "paok":                     ["PAOK FC", "PAOK Salonika"],
    "aris":                     ["Aris Thessaloniki", "Aris FC"],
    # Spanish
    "atletico madrid":          ["Atletico de Madrid", "Club Atletico de Madrid"],
    "atletico de madrid":       ["Atletico Madrid"],
    "real madrid":              ["Real Madrid CF"],
    "barcelona":                ["FC Barcelona"],
    "valencia":                 ["Valencia CF"],
    "sevilla":                  ["Sevilla FC"],
    "villarreal":               ["Villarreal CF"],
    "real betis":               ["Real Betis Balompie", "Real Betis"],
    "real sociedad":            ["Real Sociedad CF"],
    # Italian
    "inter":                    ["Inter Milan", "FC Internazionale"],
    "inter milan":              ["Inter", "FC Internazionale"],
    "internazionale":           ["Inter", "Inter Milan"],
    "ac milan":                 ["Milan", "AC Milan"],
    "milan":                    ["AC Milan"],
    "as roma":                  ["Roma"],
    "roma":                     ["AS Roma"],
    "ss lazio":                 ["Lazio"],
    "lazio":                    ["SS Lazio"],
    "napoli":                   ["SSC Napoli", "Napoli"],
    "juventus":                 ["Juventus FC"],
    "fiorentina":               ["ACF Fiorentina"],
    "atalanta":                 ["Atalanta BC"],
    # French
    "psg":                      ["Paris Saint Germain", "Paris Saint-Germain"],
    "paris sg":                 ["Paris Saint Germain", "Paris Saint-Germain"],
    "paris saint germain":      ["Paris Saint-Germain", "PSG"],
    "paris saint-germain":      ["Paris Saint Germain", "PSG"],
    "marseille":                ["Olympique Marseille", "Olympique de Marseille"],
    "lyon":                     ["Olympique Lyonnais"],
    "monaco":                   ["AS Monaco"],
    # German
    "dortmund":                 ["Borussia Dortmund"],
    "bvb":                      ["Borussia Dortmund"],
    "gladbach":                 ["Borussia Monchengladbach", "Borussia M.Gladbach"],
    "leverkusen":               ["Bayer 04 Leverkusen", "Bayer Leverkusen"],
    "bayer leverkusen":         ["Bayer 04 Leverkusen"],
    "schalke":                  ["FC Schalke 04"],
    "wolfsburg":                ["VfL Wolfsburg"],
    "freiburg":                 ["SC Freiburg"],
    "frankfurt":                ["Eintracht Frankfurt"],
    "eintracht frankfurt":      ["Frankfurt"],
    # English
    "man city":                 ["Manchester City"],
    "man united":               ["Manchester United"],
    "man utd":                  ["Manchester United"],
    "spurs":                    ["Tottenham Hotspur"],
    "tottenham":                ["Tottenham Hotspur"],
    "wolves":                   ["Wolverhampton Wanderers"],
    "newcastle":                ["Newcastle United"],
    "west ham":                 ["West Ham United"],
    "brighton":                 ["Brighton & Hove Albion", "Brighton and Hove Albion"],
    "leicester":                ["Leicester City"],
    "sheffield united":         ["Sheffield Utd"],
    "nottingham forest":        ["Nottingham Forest"],
    "forest":                   ["Nottingham Forest"],
    # Portuguese
    "sporting":                 ["Sporting CP", "Sporting Lisboa"],
    "sporting cp":              ["Sporting", "Sporting Lisboa"],
    "porto":                    ["FC Porto"],
    "benfica":                  ["SL Benfica"],
    # Dutch
    "ajax":                     ["AFC Ajax"],
    "psv":                      ["PSV Eindhoven"],
    # Scottish
    "celtic":                   ["Celtic FC"],
    "rangers":                  ["Rangers FC"],
    # Turkish
    "galatasaray":              ["Galatasaray SK"],
    "fenerbahce":               ["Fenerbahce SK"],
    "besiktas":                 ["Besiktas JK"],
    # Brazilian
    "flamengo":                 ["CR Flamengo"],
    "fluminense":               ["Fluminense FC"],
    "palmeiras":                ["SE Palmeiras"],
    "santos":                   ["Santos FC"],
}


def af_search_team(name: str, api_key: str) -> dict | None:
    """
    Return first team result, trying:
      1. Exact name match   (/teams?name=X)
      2. Fuzzy/substring    (/teams?search=X)
      3. Known alt spellings (both exact + fuzzy for each)
    Returns None if genuinely not found.
    Returns {"error": msg, "team": None} on API / network error.
    """
    last_api_error: str | None = None

    def _try_name(search_name: str) -> dict | None:
        nonlocal last_api_error
        try:
            d = _af("teams", {"name": search_name}, api_key)
            if d.get("response"):
                return d["response"][0]
            d = _af("teams", {"search": search_name}, api_key)
            if d.get("response"):
                return d["response"][0]
            return None
        except ValueError as exc:
            last_api_error = str(exc)
            return None

    # 1. Try the name as typed
    result = _try_name(name)
    if result is not None:
        return result

    # 2. Try known alternate spellings
    lower = name.lower().strip()
    for alt in _TEAM_ALT_NAMES.get(lower, []):
        result = _try_name(alt)
        if result is not None:
            return result

    # 3. Return appropriate sentinel
    if last_api_error:
        return {"error": last_api_error, "team": None}
    return None  # Not found (not an API error)


@st.cache_data(ttl=300, show_spinner=False)
def af_search_all(name: str, api_key: str) -> list:
    """
    Return all teams matching `name` (fuzzy search).
    Used by the team-picker so the user can select the exact team they want.
    TTL = 5 min. Each result dict contains: team.id, team.name, team.country.
    """
    try:
        d = _af("teams", {"search": name}, api_key)
        return d.get("response", [])
    except ValueError:
        return []


def af_last_fixtures(team_id: int, n: int, api_key: str) -> list:
    """
    Return last N finished fixtures for team_id.

    IMPORTANT API-Football constraint:
    The `last` and `status` parameters CANNOT be combined — the API returns
    an empty list when both are present. The correct approach is to use a
    date range with `status`, or use `last` alone and filter client-side.

    Three-attempt strategy:
    1. Date range (today−120d → today) + status=FT  [primary]
    2. Date range without status, filter client-side  [fallback A]
    3. `last=N*3` alone, filter client-side           [fallback B]
    """
    finished_statuses = {"FT", "AET", "PEN"}
    today   = datetime.now()
    from_dt = (today - timedelta(days=120)).strftime("%Y-%m-%d")
    to_dt   = today.strftime("%Y-%m-%d")

    try:
        # ── Attempt 1: date range + status ─────────────────
        d = _af("fixtures", {
            "team": team_id, "from": from_dt, "to": to_dt, "status": "FT",
        }, api_key)
        fx = d.get("response", [])
        if fx:
            fx.sort(key=lambda x: x["fixture"].get("date", ""), reverse=True)
            return fx[:n]

        # ── Attempt 2: date range, client-side filter ───────
        d = _af("fixtures", {"team": team_id, "from": from_dt, "to": to_dt}, api_key)
        fx = [f for f in d.get("response", [])
              if f.get("fixture", {}).get("status", {}).get("short", "") in finished_statuses]
        if fx:
            fx.sort(key=lambda x: x["fixture"].get("date", ""), reverse=True)
            return fx[:n]

        # ── Attempt 3: `last` only, client-side filter ──────
        d = _af("fixtures", {"team": team_id, "last": n * 3}, api_key)
        fx = [f for f in d.get("response", [])
              if f.get("fixture", {}).get("status", {}).get("short", "") in finished_statuses]
        fx.sort(key=lambda x: x["fixture"].get("date", ""), reverse=True)
        return fx[:n]

    except ValueError:
        return []


def af_parse_fixtures(fixtures: list, team_id: int) -> dict:
    """Derive form, clean sheets, goals averages from fixture list."""
    form, clean_sheets, scored_total, conceded_total = [], 0, 0, 0
    # API returns newest-first; reverse so we can build form newest-first below
    for f in fixtures:
        h_id = f["teams"]["home"]["id"]
        hg   = f["goals"]["home"] or 0
        ag   = f["goals"]["away"] or 0
        is_home = h_id == team_id
        s = hg if is_home else ag
        c = ag if is_home else hg
        scored_total += s
        conceded_total += c
        if c == 0:
            clean_sheets += 1
        form.append("W" if s > c else ("D" if s == c else "L"))
    n = len(fixtures)
    return {
        "form": form,               # newest first (matches API order)
        "clean_sheets": clean_sheets,
        "avg_scored":   round(scored_total   / n, 2) if n else 0.0,
        "avg_conceded": round(conceded_total / n, 2) if n else 0.0,
    }


def af_team_league(team_id: int, api_key: str) -> tuple:
    """
    Return (league_id, season, league_name) for team's primary current league.
    Season is the most recent year in the league's seasons list; the standings
    function tries season and season±1 to handle different API conventions.
    """
    try:
        d = _af("leagues", {"team": team_id, "current": "true"}, api_key)
        for item in d.get("response", []):
            if item["league"]["type"] == "League":
                seasons = item.get("seasons", [])
                # Use the most recent season year available
                if seasons:
                    season = max(s["year"] for s in seasons)
                else:
                    season = datetime.now().year
                return item["league"]["id"], season, item["league"]["name"]
    except ValueError:
        pass
    return None, None, ""


def af_standings(league_id: int, season: int, api_key: str) -> list:
    """
    Return flat list of standing entries.
    Tries the given season year first, then the previous year, because
    some leagues store a season like '2025-26' under year=2025 and others
    under year=2026. Both are attempted to avoid empty results.
    """
    for try_season in [season, season - 1, season + 1]:
        try:
            d = _af("standings", {"league": league_id, "season": try_season}, api_key)
            groups = d["response"][0]["league"]["standings"]
            flat = []
            for g in groups:
                flat.extend(g)
            if flat:
                return flat
        except (IndexError, KeyError, TypeError, ValueError):
            continue
    return []


def af_team_rank(standings: list, team_id: int) -> int | None:
    for entry in standings:
        if entry["team"]["id"] == team_id:
            return entry["rank"]
    return None


def af_league_avg_goals(standings: list) -> float | None:
    """Average goals per match calculated from standings totals."""
    try:
        total_goals  = sum(t["goals"]["for"] for t in standings)
        total_played = sum(t["all"]["played"] for t in standings)
        # Each match appears twice in total_played
        matches = total_played / 2
        return round(total_goals / matches, 2) if matches else None
    except (KeyError, TypeError, ZeroDivisionError):
        return None


# ============================================================
# THE ODDS API FUNCTIONS
# ============================================================

# Verified sport key map from official Odds API /sports endpoint docs.
# Full list: https://the-odds-api.com/liveapi/guides/v4/
_SPORT_KEY_MAP = {
    # Top 5 European leagues
    "premier league":         "soccer_epl",
    "epl":                    "soccer_epl",
    "la liga":                "soccer_spain_la_liga",
    "primera division":       "soccer_spain_la_liga",
    "serie a":                "soccer_italy_serie_a",
    "bundesliga":             "soccer_germany_bundesliga",
    "ligue 1":                "soccer_france_ligue_one",
    # Other European
    "eredivisie":             "soccer_netherlands_eredivisie",
    "championship":           "soccer_efl_champ",
    "league one":             "soccer_efl_league_one",
    "league two":             "soccer_efl_league_two",
    "scottish premiership":   "soccer_scotland_premiership",
    "la liga 2":              "soccer_spain_segunda_division",
    "segunda division":       "soccer_spain_segunda_division",
    "serie b":                "soccer_italy_serie_b",
    "2. bundesliga":          "soccer_germany_bundesliga2",
    "ligue 2":                "soccer_france_ligue_two",
    "superliga":              "soccer_denmark_superliga",
    "danish":                 "soccer_denmark_superliga",
    "eliteserien":            "soccer_norway_eliteserien",
    "allsvenskan":            "soccer_sweden_allsvenskan",
    "superettan":             "soccer_sweden_superettan",
    "veikkausliiga":          "soccer_finland_veikkausliiga",
    "super lig":              "soccer_turkey_super_league",
    "turkish":                "soccer_turkey_super_league",
    "primeira liga":          "soccer_portugal_primeira_liga",
    "portuguese":             "soccer_portugal_primeira_liga",
    "jupiler":                "soccer_belgium_first_div",
    "belgian":                "soccer_belgium_first_div",
    "süper lig":              "soccer_turkey_super_league",
    "greek super league":     "soccer_greece_super_league",
    # South America / Americas
    "brasileirao":            "soccer_brazil_campeonato",
    "serie a brazil":         "soccer_brazil_campeonato",
    "campeonato":             "soccer_brazil_campeonato",
    "mls":                    "soccer_usa_mls",
    "liga mx":                "soccer_mexico_ligamx",
    "mexicana":               "soccer_mexico_ligamx",
    "argentine":              "soccer_argentina_primera_division",
    "primera division argentina": "soccer_argentina_primera_division",
    # Asia / Oceania
    "j league":               "soccer_japan_j_league",
    "a-league":               "soccer_australia_aleague",
    # European cups
    "champions league":       "soccer_uefa_champs_league",
    "europa league":          "soccer_uefa_europa_league",
    "conference league":      "soccer_uefa_europa_conference_league",
}


def _sport_key(league_name: str) -> str:
    """Map a league name to an Odds API sport key. Returns 'soccer_epl' if no match."""
    lower = league_name.lower().strip()
    for fragment, key in _SPORT_KEY_MAP.items():
        if fragment in lower:
            return key
    return "soccer_epl"


@st.cache_data(ttl=900, show_spinner=False)
def odds_fetch(sport_key: str, odds_key: str) -> list:
    """
    Fetch current h2h odds for a sport from The Odds API.
    TTL = 15 min. Raises ValueError on errors so st.cache_data
    does NOT cache failures — a bad key or wrong sport key won't block retries.

    Cost: 1 credit per call (1 region × 1 market).
    Docs: https://the-odds-api.com/liveapi/guides/v4/
    """
    try:
        r = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/",
            params={
                "apiKey": odds_key,
                "regions": "eu",        # 1 region = 1 credit (not 'eu,uk' which = 2)
                "markets": "h2h",
                "oddsFormat": "decimal",
            },
            timeout=12,
        )
        if r.status_code == 401:
            raise ValueError("Invalid Odds API key. Get one at the-odds-api.com")
        if r.status_code == 422:
            raise ValueError(
                f"Sport key '{sport_key}' is not valid for this league. "
                "Check the sport key list in the Odds Intel tab or run Test Connections."
            )
        r.raise_for_status()
        return r.json()
    except ValueError:
        raise  # Let cache skip this response
    except requests.exceptions.Timeout:
        raise ValueError("Odds API request timed out (12 s).")
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"Odds API network error: {exc}")


# ── Connection test functions (not cached — always make a fresh request) ──

def af_test_connection(api_key: str) -> dict:
    """
    Test API-Football connection via /timezone endpoint.
    Uses 1 of the 100 daily free requests.
    Returns dict: {ok, message, remaining, used}
    """
    try:
        r = requests.get(
            "https://v3.football.api-sports.io/timezone",
            headers={"x-apisports-key": api_key},
            timeout=10,
        )
        if r.status_code in (401, 403):
            return {"ok": False, "message": f"Invalid API key (HTTP {r.status_code}). "
                                             "Check dashboard.api-football.com."}
        if r.status_code == 429:
            return {"ok": False, "message": "Daily limit reached (100 req/day). Resets at midnight UTC."}
        r.raise_for_status()
        data = r.json()
        if data.get("errors"):
            msg = str(list(data["errors"].values())[0]) if isinstance(data["errors"], dict) else str(data["errors"])
            return {"ok": False, "message": f"API error: {msg}"}
        remaining = r.headers.get("x-ratelimit-requests-remaining", "?")
        used      = r.headers.get("x-ratelimit-requests-used", "?")
        return {
            "ok": True,
            "message": "Connected successfully",
            "remaining": remaining,
            "used": used,
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "message": "Request timed out. Check your internet connection."}
    except Exception as exc:
        return {"ok": False, "message": str(exc)}


def odds_test_connection(odds_key: str) -> dict:
    """
    Test The Odds API connection via /sports endpoint.
    This endpoint does NOT count against the 500/month quota.
    Returns dict: {ok, message, remaining, used, soccer_keys}
    """
    try:
        r = requests.get(
            "https://api.the-odds-api.com/v4/sports/",
            params={"apiKey": odds_key},
            timeout=10,
        )
        if r.status_code == 401:
            return {"ok": False, "message": "Invalid API key. Get one at the-odds-api.com"}
        r.raise_for_status()
        sports = r.json()
        soccer = [s for s in sports if s.get("key", "").startswith("soccer_")]
        remaining = r.headers.get("x-requests-remaining", "?")
        used      = r.headers.get("x-requests-used", "?")
        return {
            "ok": True,
            "message": f"Connected — {len(soccer)} soccer leagues available",
            "remaining": remaining,
            "used": used,
            "soccer_keys": {s["key"]: s.get("title", s["key"]) for s in soccer},
        }
    except requests.exceptions.Timeout:
        return {"ok": False, "message": "Request timed out. Check your internet connection."}
    except Exception as exc:
        return {"ok": False, "message": str(exc)}


def odds_find_match(games: list, ta: str, tb: str) -> dict | None:
    """Find a specific match in the odds list using partial name matching."""
    ta_l, tb_l = ta.lower(), tb.lower()
    for g in games:
        ht = g.get("home_team", "").lower()
        at = g.get("away_team", "").lower()
        match_a = ta_l in ht or ht in ta_l or any(w in ht for w in ta_l.split())
        match_b = tb_l in at or at in tb_l or any(w in at for w in tb_l.split())
        if match_a and match_b:
            return g
        # Try reversed home/away order
        match_ar = ta_l in at or at in ta_l or any(w in at for w in ta_l.split())
        match_br = tb_l in ht or ht in tb_l or any(w in ht for w in tb_l.split())
        if match_ar and match_br:
            return g
    return None


def extract_h2h_odds(game: dict) -> dict:
    """Pull best h2h odds from first available bookmaker."""
    for bm in game.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] == "h2h":
                return {o["name"]: o["price"] for o in mkt.get("outcomes", [])}
    return {}


# ============================================================
# MAIN AUTO-FETCH ORCHESTRATOR
# ============================================================

def do_auto_fetch(football_key: str, odds_key: str) -> None:
    """
    Fetch live data from API-Football (v3.football.api-sports.io)
    and The Odds API, then populate session_state.
    No UI elements created here — results persist after st.rerun().
    """
    ta = st.session_state.team_a.strip()
    tb = st.session_state.team_b.strip()
    now = datetime.now().strftime("%H:%M:%S")

    log: list[str]     = []
    errors: list[str]  = []
    summary: list[str] = []

    # Always set last_fetched so the results block is shown even on failure
    def _finish():
        st.session_state.fetch_log     = log
        st.session_state.fetch_errors  = errors
        st.session_state.fetch_summary = summary
        st.session_state.last_fetched  = now

    if not ta or not tb:
        errors.append("Enter both team names in the sidebar before fetching.")
        _finish()
        return

    # ── Step 1: Resolve team IDs ───────────────────────────
    # If user picked teams via the Team Picker, use those IDs directly.
    pre_a = st.session_state.get("team_a_id")
    pre_b = st.session_state.get("team_b_id")

    if pre_a and pre_b:
        ta_id = pre_a
        tb_id = pre_b
        log.append(f"✅ Using team-picker selection: {ta} (ID {ta_id}), {tb} (ID {tb_id})")
    else:
        log.append("🔍 Searching for teams on v3.football.api-sports.io…")
        ta_data = af_search_team(ta, football_key)
        tb_data = af_search_team(tb, football_key)

        for label, data in [(ta, ta_data), (tb, tb_data)]:
            if isinstance(data, dict) and data.get("error") and data.get("team") is None:
                errors.append(f"API error: {data['error']}")

        if not errors:
            if ta_data is None:
                alts = _TEAM_ALT_NAMES.get(ta.lower().strip(), [])
                hint = f" Tried alternates: {', '.join(alts)}." if alts else ""
                errors.append(
                    f"Team not found: '{ta}'.{hint} "
                    "Use the Team Picker (🔍 button above) to search and select the exact team."
                )
            else:
                log.append(f"✅ {ta} → ID {ta_data['team']['id']} ({ta_data['team']['country']})")

            if tb_data is None:
                alts = _TEAM_ALT_NAMES.get(tb.lower().strip(), [])
                hint = f" Tried alternates: {', '.join(alts)}." if alts else ""
                errors.append(
                    f"Team not found: '{tb}'.{hint} "
                    "Use the Team Picker (🔍 button above) to search and select the exact team."
                )
            else:
                log.append(f"✅ {tb} → ID {tb_data['team']['id']} ({tb_data['team']['country']})")

        if errors:
            log.append("⛔ Stopped — fix errors above or use the Team Picker to select teams.")
            _finish()
            return

        ta_id = ta_data["team"]["id"]
        tb_id = tb_data["team"]["id"]

    # ── Step 2: Last 5 fixtures ────────────────────────────
    log.append("📅 Fetching last 5 finished matches…")
    fix_a = af_last_fixtures(ta_id, 5, football_key)
    fix_b = af_last_fixtures(tb_id, 5, football_key)

    if not fix_a and not fix_b:
        errors.append(
            "No recent finished fixtures found for either team. "
            "Possible reasons: (1) the league is at off-season — try again when the season resumes; "
            "(2) this league's fixture data requires a paid API-Football plan; "
            "(3) the date range (last 120 days) had no finished matches. "
            "You can fill the Statistics and Forms tabs manually."
        )
        _finish()
        return

    if fix_a:
        stats_a = af_parse_fixtures(fix_a, ta_id)
        fa = stats_a["form"][:]
        while len(fa) < 5:
            fa.append("D")
        for i in range(5):
            st.session_state[f"form_a_{i}"] = fa[i]
        st.session_state.stat_a_clean_sheets   = stats_a["clean_sheets"]
        st.session_state.stat_a_goals_scored   = stats_a["avg_scored"]
        st.session_state.stat_a_goals_conceded = stats_a["avg_conceded"]
        form_str = " | ".join(fa[:5])
        log.append(
            f"✅ {ta}: form [{form_str}] — "
            f"{stats_a['clean_sheets']}/5 clean sheets — "
            f"avg scored {stats_a['avg_scored']} / conceded {stats_a['avg_conceded']}"
        )
        summary.append(
            f"**{ta}**: form {' '.join(fa[:5])}  |  "
            f"clean sheets {stats_a['clean_sheets']}/5  |  "
            f"GF {stats_a['avg_scored']} GA {stats_a['avg_conceded']}"
        )
    else:
        errors.append(
            f"No recent finished fixtures found for {ta} (ID {ta_id}). "
            "The league may have limited coverage on the free API tier, or the season is between rounds."
        )

    if fix_b:
        stats_b = af_parse_fixtures(fix_b, tb_id)
        fb = stats_b["form"][:]
        while len(fb) < 5:
            fb.append("D")
        for i in range(5):
            st.session_state[f"form_b_{i}"] = fb[i]
        st.session_state.stat_b_clean_sheets   = stats_b["clean_sheets"]
        st.session_state.stat_b_goals_scored   = stats_b["avg_scored"]
        st.session_state.stat_b_goals_conceded = stats_b["avg_conceded"]
        form_str = " | ".join(fb[:5])
        log.append(
            f"✅ {tb}: form [{form_str}] — "
            f"{stats_b['clean_sheets']}/5 clean sheets — "
            f"avg scored {stats_b['avg_scored']} / conceded {stats_b['avg_conceded']}"
        )
        summary.append(
            f"**{tb}**: form {' '.join(fb[:5])}  |  "
            f"clean sheets {stats_b['clean_sheets']}/5  |  "
            f"GF {stats_b['avg_scored']} GA {stats_b['avg_conceded']}"
        )
    else:
        errors.append(
            f"No recent finished fixtures found for {tb} (ID {tb_id}). "
            "The league may have limited coverage on the free API tier, or the season is between rounds."
        )

    # ── Step 3: League + standings ─────────────────────────
    log.append("🏆 Fetching league and standings…")
    league_id, season, league_name_api = af_team_league(ta_id, football_key)

    if league_id:
        if league_name_api and not st.session_state.league_name.strip():
            st.session_state.league_name = league_name_api

        standings = af_standings(league_id, season, football_key)
        if standings:
            pos_a = af_team_rank(standings, ta_id)
            pos_b = af_team_rank(standings, tb_id)
            total = len(standings)
            if pos_a:
                st.session_state.form_a_pos = pos_a
            if pos_b:
                st.session_state.form_b_pos = pos_b
            st.session_state.form_league_total = total

            log.append(
                f"✅ {league_name_api} {season} standings: "
                f"{ta} #{pos_a or '?'} | {tb} #{pos_b or '?'} of {total} teams"
            )
            summary.append(
                f"**League**: {league_name_api}  |  "
                f"{ta} #{pos_a or '?'}  |  {tb} #{pos_b or '?'}  |  {total} teams"
            )

            avg_g = af_league_avg_goals(standings)
            if avg_g:
                if avg_g >= 2.6:
                    st.session_state.league_variance = "high"
                    var_label = f"HIGH-variance ⚡ ({avg_g} g/m)"
                elif avg_g < 2.4:
                    st.session_state.league_variance = "low"
                    var_label = f"LOW-variance 🛡️ ({avg_g} g/m)"
                else:
                    var_label = f"MEDIUM ({avg_g} g/m) — confirm manually"
                log.append(f"✅ League avg: {avg_g} goals/match → {var_label}")
                summary.append(f"**Variance**: {var_label}")
        else:
            log.append(f"⚠️  Standings not available for {league_name_api}")
    else:
        log.append(f"⚠️  Could not identify current league for {ta} (may need league ID)")

    # ── Step 4: Odds (optional) ────────────────────────────
    if odds_key.strip():
        log.append("🎰 Fetching current odds…")
        league_for_key = st.session_state.league_name or league_name_api or ""
        sport_key = _sport_key(league_for_key)
        log.append(f"   Using sport key: {sport_key}")
        try:
            games = odds_fetch(sport_key, odds_key.strip())
            if isinstance(games, list) and games:
                match_game = odds_find_match(games, ta, tb)
                if match_game:
                    h2h = extract_h2h_odds(match_game)
                    st.session_state.fetched_odds = h2h
                    st.session_state.fetched_odds_match = (
                        f"{match_game.get('home_team')} vs {match_game.get('away_team')} "
                        f"({match_game.get('sport_title', '')})"
                    )
                    log.append(f"✅ Odds: {h2h}")
                    summary.append(f"**Live odds**: {h2h}")
                else:
                    log.append(
                        f"⚠️  Match not found in odds for key '{sport_key}'. "
                        "Games usually appear 2–3 days before kickoff."
                    )
            else:
                log.append("⚠️  Odds API returned no games for this sport.")
        except ValueError as exc:
            log.append(f"⚠️  Odds API: {exc}")
    else:
        log.append("ℹ️  No Odds API key provided — odds fetch skipped.")

    # ── Done ───────────────────────────────────────────────
    log.append(f"✅ Fetch finished at {now}")
    _finish()


# ============================================================
# HELPERS
# ============================================================

def _ta() -> str:
    return st.session_state.team_a or "Team A"

def _tb() -> str:
    return st.session_state.team_b or "Team B"

def _alert(kind: str, title: str, body: str) -> str:
    icons = {"danger": "🚨", "warning": "⚠️", "success": "✅", "info": "ℹ️"}
    return (
        f'<div class="alert alert-{kind}">'
        f'<strong>{icons.get(kind, "•")} {title}</strong><br/>{body}'
        f'</div>'
    )

def _form_pills(keys_prefix: str) -> str:
    html = ""
    for i in range(5):
        r   = st.session_state.get(f"{keys_prefix}_{i}", "D")
        css = {"W": "form-w", "D": "form-d", "L": "form-l"}.get(r, "form-d")
        html += f'<span class="form-pill {css}">{r}</span>'
    return html

def _get_form(prefix: str) -> list:
    return [st.session_state.get(f"{prefix}_{i}", "D") for i in range(5)]

def _badge(auto: bool) -> str:
    if auto:
        return '<span class="fetched-badge">✦ Auto-fetched</span>'
    return '<span class="manual-badge">✎ Manual input</span>'


# ============================================================
# ANALYSIS ENGINE
# ============================================================

def run_analysis() -> dict:
    ta = _ta()
    tb = _tb()
    warnings, analyst_reports = [], []

    # ── Inputs ─────────────────────────────────────────────
    form_a = _get_form("form_a")
    form_b = _get_form("form_b")
    cs_a   = st.session_state.stat_a_clean_sheets
    cs_b   = st.session_state.stat_b_clean_sheets
    both_clean = cs_a >= 2 and cs_b >= 2

    variance   = st.session_state.league_variance
    is_low_var = variance == "low"
    is_high_var= variance == "high"

    pos_a   = st.session_state.form_a_pos
    pos_b   = st.session_state.form_b_pos
    n_teams = st.session_state.form_league_total
    hs_a = pos_a <= 3 or pos_a >= n_teams - 3
    hs_b = pos_b <= 3 or pos_b >= n_teams - 3
    high_stakes = hs_a or hs_b

    off_a = st.session_state.tac_a_offensive
    off_b = st.session_state.tac_b_offensive
    offensive_formation = off_a or off_b

    a_dis = any([st.session_state.soc_a_nightclub,
                 st.session_state.soc_a_training,
                 st.session_state.soc_a_feud])
    b_dis = any([st.session_state.soc_b_nightclub,
                 st.session_state.soc_b_training,
                 st.session_state.soc_b_feud])

    mgr_friends = st.session_state.mgr_friends
    a_needs     = st.session_state.mgr_a_needs_points
    b_needs     = st.session_state.mgr_b_needs_points
    mgr_flag    = mgr_friends and (a_needs != b_needs)

    new_striker   = st.session_state.xfer_team_a or st.session_state.xfer_team_b
    striker_starts= st.session_state.xfer_starts
    transfer_rule = new_striker and striker_starts and both_clean and is_low_var

    bm_drop = st.session_state.bm_odds_dropped

    # ── Checklist: per-item confidence penalty & notes ─────
    # Each unverified area reduces confidence and adds a targeted note.
    # Nothing is blocked — analysis always runs.
    CHK_ITEMS = [
        ("chk_defensive", "Defensive Integrity",
         "Clean sheet data not personally verified — relying on auto-fetched or manually entered stats.",
         4),
        ("chk_volatility", "League Volatility",
         "League variance not personally confirmed — assumed from computed or manually set avg goals.",
         4),
        ("chk_motivation", "Motivation Matrix",
         "Table positions / points situation not personally verified — motivational context is uncertain.",
         4),
        ("chk_lineup", "Confirmed Lineup",
         "Starting lineup not confirmed (released ~1 h before kickoff) — formation and new-transfer assumptions may be wrong.",
         6),
        ("chk_social", "Players' Social Life",
         "Social media / news not researched for this match — disruptions assumed absent but unverified.",
         3),
    ]
    checklist_verified = sum(
        1 for key, *_ in CHK_ITEMS if st.session_state.get(key, False)
    )
    checklist_done = checklist_verified == 5
    checklist_penalty = sum(
        penalty for key, _, _, penalty in CHK_ITEMS
        if not st.session_state.get(key, False)
    )
    checklist_notes = [
        (label, note, penalty)
        for key, label, note, penalty in CHK_ITEMS
        if not st.session_state.get(key, False)
    ]

    # ── Warnings ───────────────────────────────────────────

    if bm_drop:
        warnings.append({"kind": "danger", "title": "BOOKMAKER PSYCHOLOGICAL TRAP",
            "body": (f"Odds dropped {st.session_state.bm_odds_from:.2f} → {st.session_state.bm_odds_to:.2f}. "
                     "In <strong>80% of cases</strong>: Draw (X) or other team wins. "
                     "Bookmakers manufacture false certainty. DO NOT bet on the favoured side.")})

    if mgr_flag:
        needy  = ta if a_needs else tb
        relaxed= tb if a_needs else ta
        warnings.append({"kind": "warning", "title": "MANAGER FRIENDSHIP — RELAXED GAME",
            "body": (f"Managers are friends. {needy} needs points; {relaxed} does not. "
                     f"High probability {relaxed} plays below ceiling, gifting win/draw to {needy}.")})

    # ── Abort conditions ───────────────────────────────────
    abort_reasons = []
    if not both_clean:
        abort_reasons.append(
            f"Defensive integrity FAILS — {ta}: {cs_a}/5, {tb}: {cs_b}/5 clean sheets (both need ≥ 2)")
    if is_high_var:
        abort_reasons.append("High-variance league (≥ 2.6 g/match) — Under rules INVALID")
    if hs_a:
        abort_reasons.append(f"{ta} is in a high-stakes position (#{pos_a}/{n_teams}) → Over risk")
    if hs_b:
        abort_reasons.append(f"{tb} is in a high-stakes position (#{pos_b}/{n_teams}) → Over risk")
    if off_a:
        abort_reasons.append(f"{ta} confirmed offensive formation (2+ strikers)")
    if off_b:
        abort_reasons.append(f"{tb} confirmed offensive formation (2+ strikers)")
    must_abort = bool(abort_reasons)

    if must_abort:
        warnings.append({"kind": "danger", "title": "ABORT ALL UNDER BETS",
            "body": "<br/>".join(f"• {r}" for r in abort_reasons)})

    if a_dis or b_dis:
        hit = ", ".join(([ta] if a_dis else []) + ([tb] if b_dis else []))
        warnings.append({"kind": "warning", "title": "VERIFIED SOCIAL DISRUPTION",
            "body": f"{hit} — confirmed off-field issues detected. Performance risk elevated."})

    # ── Verdict (base) ─────────────────────────────────────
    if transfer_rule and not must_abort:
        verdict, css, base_confidence = "UNDER 1.5 Goals", "verdict-under-15", 90
        rationale = ("New striker starting + both teams ≥ 2 clean sheets + low-variance league. "
                     "3-condition rule fires at ~90% historical accuracy.")
    elif must_abort:
        verdict, css, base_confidence = "ABORT ALL UNDER BETS", "verdict-abort", 0
        rationale = "One or more critical abort conditions active. See warnings above."
    elif is_low_var and both_clean and not high_stakes and not offensive_formation:
        verdict, css, base_confidence = "UNDER 2.5 Goals", "verdict-under-25", 65
        rationale = ("Low-variance league, both teams defensively solid, "
                     "no high-stakes pressure, no offensive overload.")
    elif is_high_var or high_stakes or offensive_formation:
        verdict, css, base_confidence = "LEAN OVER 2.5 Goals", "verdict-over", 60
        rationale = "League context, table pressure, or confirmed attacking setup suggests higher-scoring game."
    else:
        verdict, css, base_confidence = "NO CLEAR SIGNAL", "verdict-no-signal", 35
        rationale = "Conflicting or insufficient data. Insufficient edge to recommend a bet — avoid this match."

    # Apply checklist penalty to confidence (abort stays 0)
    if base_confidence > 0:
        confidence = max(base_confidence - checklist_penalty, 5)
    else:
        confidence = 0

    # ── Analyst reports ────────────────────────────────────
    analyst_reports = [
        {"analyst": "📊 Statistics Analyst", "lines": [
            f"{ta}: {cs_a}/5 clean sheets | avg scored {st.session_state.stat_a_goals_scored:.1f} | avg conceded {st.session_state.stat_a_goals_conceded:.1f}",
            f"{tb}: {cs_b}/5 clean sheets | avg scored {st.session_state.stat_b_goals_scored:.1f} | avg conceded {st.session_state.stat_b_goals_conceded:.1f}",
            f"Defensive integrity: {'✅ Both solid (≥ 2 clean sheets)' if both_clean else '❌ FAILS'}",
        ]},
        {"analyst": "⚔️ Tactics & Formations", "lines": [
            f"{ta}: {st.session_state.tac_a_formation} | Offensive: {'🔴 Yes' if off_a else '🟢 No'}",
            f"{tb}: {st.session_state.tac_b_formation} | Offensive: {'🔴 Yes' if off_b else '🟢 No'}",
            f"Formation abort: {'❌ Active' if offensive_formation else '✅ Clear'}",
        ]},
        {"analyst": "📈 Forms & Motivation", "lines": [
            f"{ta}: {' '.join(form_a)} | Position #{pos_a} of {n_teams}",
            f"{tb}: {' '.join(form_b)} | Position #{pos_b} of {n_teams}",
            f"High-stakes pressure: {'🔴 Yes — Over risk' if high_stakes else '🟢 None'}",
        ]},
        {"analyst": "🤝 Manager Decisions", "lines": [
            f"Managers friends: {'Yes' if mgr_friends else 'No'} | {ta} needs pts: {'Yes' if a_needs else 'No'} | {tb} needs pts: {'Yes' if b_needs else 'No'}",
            f"Relaxed-game flag: {'🔴 Active' if mgr_flag else '🟢 Not triggered'}",
        ]},
        {"analyst": "🏟️ Coaches & Referees", "lines": [
            f"Referee: {st.session_state.ref_name or 'Not specified'} | Fair: {'✅' if st.session_state.ref_fair else '⚠️'}",
            f"{ta} coach pressure: {'Yes' if st.session_state.coach_a_pressure else 'No'} | {tb} coach pressure: {'Yes' if st.session_state.coach_b_pressure else 'No'}",
        ]},
        {"analyst": "📱 Players' Social Life", "lines": [
            f"{ta}: " + (", ".join(filter(None, [
                "Nightclub <48h" if st.session_state.soc_a_nightclub else "",
                "Missed training" if st.session_state.soc_a_training else "",
                "Coach feud"      if st.session_state.soc_a_feud     else "",
            ])) or "No verified disruptions"),
            f"{tb}: " + (", ".join(filter(None, [
                "Nightclub <48h" if st.session_state.soc_b_nightclub else "",
                "Missed training" if st.session_state.soc_b_training else "",
                "Coach feud"      if st.session_state.soc_b_feud     else "",
            ])) or "No verified disruptions"),
            f"Disruption flag: {'🔴 Active' if (a_dis or b_dis) else '🟢 Clear'}",
        ]},
        {"analyst": "🔄 New Transfer", "lines": [
            f"New striker in {ta}: {'Yes' if st.session_state.xfer_team_a else 'No'} | {tb}: {'Yes' if st.session_state.xfer_team_b else 'No'}",
            f"Striker confirmed starting: {'Yes' if striker_starts else 'No'}",
            f"Under-1.5 rule (3-condition): {'✅ Fires (~90%)' if transfer_rule else '❌ Not active'}",
        ]},
    ]

    return {
        "verdict": verdict, "verdict_css": css,
        "confidence": confidence,
        "base_confidence": base_confidence,
        "checklist_penalty": checklist_penalty,
        "checklist_notes": checklist_notes,
        "checklist_verified": checklist_verified,
        "rationale": rationale,
        "warnings": warnings, "analyst_reports": analyst_reports,
        "checklist_done": checklist_done, "transfer_rule": transfer_rule,
        "must_abort": must_abort,
        "is_low_var": is_low_var, "both_clean": both_clean,
    }


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.4rem;font-weight:900;color:#58a6ff;margin-bottom:2px;">⚽ BetDestroy</div>'
        '<div style="font-size:0.75rem;color:#8b949e;margin-bottom:16px;">Analysis Engine v2.0 — Live Data</div>',
        unsafe_allow_html=True,
    )

    # ── Match Setup ────────────────────────────────────────
    st.markdown("### Match Setup")
    st.text_input("Team A", key="team_a", placeholder="e.g. Fiorentina")
    st.text_input("Team B", key="team_b", placeholder="e.g. Napoli")
    st.text_input("League / Competition", key="league_name", placeholder="e.g. Serie A")

    st.markdown("**League Variance**")
    st.caption("High: ≥ 2.6 goals/match | Low: < 2.4 goals/match  \n(Auto-set when you fetch data.)")
    st.radio(
        "League variance type",
        options=["low", "high"],
        format_func=lambda x: "🛡️ Low-variance (< 2.4 g/m)" if x == "low" else "⚡ High-variance (≥ 2.6 g/m)",
        key="league_variance",
        label_visibility="collapsed",
    )

    st.markdown("---")

    # ── Team Picker ────────────────────────────────────────
    st.markdown("### 🔍 Team Picker")
    st.caption(
        "When multiple teams share a similar name (e.g. Olympiakos Greece vs Cyprus), "
        "search here and pick the exact one from the API results."
    )

    picker_key = st.session_state.api_key_football.strip()
    if not picker_key:
        st.caption("Enter your API-Football key below to enable team search.")
    else:
        if st.button("🔍 Search Both Teams", use_container_width=True):
            ta_q = st.session_state.team_a.strip()
            tb_q = st.session_state.team_b.strip()
            with st.spinner("Searching…"):
                ra = af_search_all(ta_q, picker_key) if ta_q else []
                rb = af_search_all(tb_q, picker_key) if tb_q else []
            st.session_state.team_a_search_results = ra
            st.session_state.team_b_search_results = rb
            st.session_state.team_a_id = None
            st.session_state.team_b_id = None
            st.rerun()

        # Team A selector
        if st.session_state.team_a_search_results:
            opts_a = [
                f"{r['team']['name']}  [{r['team']['country']}]"
                for r in st.session_state.team_a_search_results
            ]
            sel_a = st.selectbox(
                f"Team A — select the correct one:",
                options=opts_a,
                key="team_a_picker_widget",
            )
            idx_a = opts_a.index(sel_a)
            chosen_a = st.session_state.team_a_search_results[idx_a]
            st.session_state.team_a_id = chosen_a["team"]["id"]
            st.success(
                f"✅ {chosen_a['team']['name']} — {chosen_a['team']['country']} "
                f"(ID {chosen_a['team']['id']})"
            )
        elif st.session_state.team_a_id:
            st.success(f"✅ Team A locked: ID {st.session_state.team_a_id}")

        # Team B selector
        if st.session_state.team_b_search_results:
            opts_b = [
                f"{r['team']['name']}  [{r['team']['country']}]"
                for r in st.session_state.team_b_search_results
            ]
            sel_b = st.selectbox(
                f"Team B — select the correct one:",
                options=opts_b,
                key="team_b_picker_widget",
            )
            idx_b = opts_b.index(sel_b)
            chosen_b = st.session_state.team_b_search_results[idx_b]
            st.session_state.team_b_id = chosen_b["team"]["id"]
            st.success(
                f"✅ {chosen_b['team']['name']} — {chosen_b['team']['country']} "
                f"(ID {chosen_b['team']['id']})"
            )
        elif st.session_state.team_b_id:
            st.success(f"✅ Team B locked: ID {st.session_state.team_b_id}")

        if st.session_state.team_a_search_results or st.session_state.team_b_search_results:
            if st.button("✖ Clear Selection", use_container_width=True):
                for k in ("team_a_id", "team_b_id",
                          "team_a_search_results", "team_b_search_results"):
                    st.session_state[k] = None if "id" in k else []
                st.rerun()

    st.markdown("---")

    # ── Auto-Fetch Section ─────────────────────────────────
    st.markdown("### 🔄 Auto-Fetch Live Data")

    with st.expander("🔑 API Keys (required to fetch)", expanded=not st.session_state.last_fetched):

        st.markdown("**API-Football** — free: 100 requests / day")
        st.markdown(
            "1. Register at "
            "[dashboard.api-football.com/register]"
            "(https://dashboard.api-football.com/register)  \n"
            "2. Copy your key from the dashboard  \n"
            "3. Paste it below"
        )
        st.text_input(
            "API-Football Key (x-apisports-key)", type="password",
            key="api_key_football",
            placeholder="Paste your API key here…",
        )
        st.caption(
            "Endpoint: `https://v3.football.api-sports.io/`  \n"
            "Auth header: `x-apisports-key: YOUR_KEY`"
        )

        st.markdown("---")
        st.markdown(
            "**The Odds API** — optional, free: 500 req / month  \n"
            "👉 [the-odds-api.com](https://the-odds-api.com)  \n"
            "Only needed for live match odds display."
        )
        st.text_input("The Odds API Key (optional)", type="password",
                      key="api_key_odds", placeholder="Paste your Odds API key…")

        st.markdown("---")
        st.markdown("**What gets auto-filled:**")
        st.markdown(
            "✅ Form (W/D/L last 5)  \n"
            "✅ Clean sheets (last 5)  \n"
            "✅ Goals avg (scored & conceded)  \n"
            "✅ League table positions  \n"
            "✅ League variance (auto-detected)  \n"
            "✅ Live match odds (if Odds API key set)  \n"
            "✎ Formations / lineup — manual  \n"
            "✎ Manager friendship — manual  \n"
            "✎ Social life — manual  \n"
            "✎ Referee — manual"
        )

    can_fetch = bool(st.session_state.api_key_football.strip())

    # ── Test connection button ─────────────────────────────
    if st.button("🔬 Test API Connections", use_container_width=True,
                 disabled=not can_fetch,
                 help="Verifies both keys work and shows remaining quota. "
                      "⚠️ Uses 1 of your 100 daily API-Football requests."):
        fk = st.session_state.api_key_football.strip()
        ok = st.session_state.api_key_odds.strip()
        with st.spinner("Testing connections…"):
            af_res = af_test_connection(fk)
            if af_res["ok"]:
                st.success(
                    f"✅ API-Football OK  \n"
                    f"Requests remaining today: **{af_res['remaining']}** / 100  \n"
                    f"Used so far: {af_res['used']}"
                )
            else:
                st.error(f"❌ API-Football: {af_res['message']}")

            if ok:
                od_res = odds_test_connection(ok)
                if od_res["ok"]:
                    st.success(
                        f"✅ The Odds API OK (free /sports call — no quota used)  \n"
                        f"{od_res['message']}  \n"
                        f"Credits remaining: **{od_res['remaining']}**  |  Used: {od_res['used']}"
                    )
                    # Cache available soccer keys in session state
                    st.session_state.odds_soccer_keys = od_res.get("soccer_keys", {})
                else:
                    st.error(f"❌ The Odds API: {od_res['message']}")
            else:
                st.info("No Odds API key provided — skipping odds test.")

    st.markdown("")

    # ── Main fetch button ──────────────────────────────────
    if st.button("⚡ Fetch Live Match Data", type="primary",
                 use_container_width=True, disabled=not can_fetch):
        with st.spinner("Fetching from api-sports.io…"):
            do_auto_fetch(
                st.session_state.api_key_football.strip(),
                st.session_state.api_key_odds.strip(),
            )
        st.rerun()

    if not can_fetch:
        st.caption("Enter your API-Football key above to enable fetching.")

    # ── Persistent fetch results (shown after rerun) ───────
    if st.session_state.last_fetched:
        if st.session_state.fetch_errors:
            st.markdown("---")
            st.markdown(f"**⛔ Fetch at {st.session_state.last_fetched} — errors:**")
            for e in st.session_state.fetch_errors:
                # Use explicit if — ternary with st.XXX() triggers Streamlit
                # magic mode and prints the DeltaGenerator repr as text.
                if e.strip():
                    st.error(e.strip())
        elif st.session_state.fetch_summary:
            st.markdown("---")
            st.markdown(f"**✅ Updated at {st.session_state.last_fetched}:**")
            for s in st.session_state.fetch_summary:
                st.markdown(f"<p style='margin:2px 0;font-size:0.8rem'>{s}</p>",
                            unsafe_allow_html=True)

        if st.session_state.fetch_log:
            with st.expander("Full fetch log"):
                for line in st.session_state.fetch_log:
                    if line.startswith("✅"):
                        col = "#56d364"
                    elif line.startswith("⚠"):
                        col = "#f0883e"
                    elif line.startswith("❌"):
                        col = "#f85149"
                    else:
                        col = "#8b949e"
                    st.markdown(
                        f"<p style='margin:1px 0;font-size:0.78rem;"
                        f"font-family:monospace;color:{col}'>{line}</p>",
                        unsafe_allow_html=True,
                    )

    st.markdown("---")

    # ── Quick status ───────────────────────────────────────
    st.markdown("**Quick Status**")
    chk_done = sum([st.session_state.chk_defensive, st.session_state.chk_volatility,
                    st.session_state.chk_motivation, st.session_state.chk_lineup, st.session_state.chk_social])
    cs_a_ = st.session_state.stat_a_clean_sheets
    cs_b_ = st.session_state.stat_b_clean_sheets
    ta_, tb_ = _ta(), _tb()
    _penalty_map = {"chk_defensive": 4, "chk_volatility": 4, "chk_motivation": 4,
                    "chk_lineup": 6, "chk_social": 3}
    _remaining_penalty = sum(v for k, v in _penalty_map.items()
                             if not st.session_state.get(k, False))
    if chk_done == 5:
        st.markdown(f"Verified: **5/5** ✅ full confidence")
    else:
        st.markdown(f"Verified: **{chk_done}/5** — −{_remaining_penalty}% conf")
    st.markdown(f"League: **{'High-variance ⚡' if st.session_state.league_variance == 'high' else 'Low-variance 🛡️'}**")
    st.markdown(f"Clean sheets: **{ta_[:12]}: {cs_a_}** | **{tb_[:12]}: {cs_b_}**")
    pos_a_ = st.session_state.form_a_pos
    pos_b_ = st.session_state.form_b_pos
    st.markdown(f"Positions: **#{pos_a_}** vs **#{pos_b_}** (of {st.session_state.form_league_total})")
    tid_a = st.session_state.team_a_id
    tid_b = st.session_state.team_b_id
    if tid_a or tid_b:
        st.markdown(
            f"Team IDs: **{tid_a or '?'}** / **{tid_b or '?'}** "
            f"{'✅ confirmed' if (tid_a and tid_b) else '⚠️ partial'}"
        )


# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(
    '<h1 class="main-title">BetDestroy Analysis Engine</h1>'
    '<p class="main-subtitle">'
    '7-Analyst System · Rule-Based Predictions · Live Data via API-Football & The Odds API'
    '</p>',
    unsafe_allow_html=True,
)

fetched = bool(st.session_state.last_fetched)
if fetched:
    st.success(
        f"✅ Live data loaded at {st.session_state.last_fetched} — "
        "statistical fields below are auto-populated. Review, adjust if needed, then run analysis."
    )

# ============================================================
# TABS
# ============================================================
(
    t_checklist, t_stats, t_tactics, t_forms,
    t_mgr, t_officials, t_social, t_bm, t_verdict,
) = st.tabs([
    "📋 Checklist",
    "📊 Statistics",
    "⚔️ Tactics & Formations",
    "📈 Forms & Motivation",
    "🤝 Manager Decisions",
    "🏟️ Coaches & Referees",
    "📱 Social Life",
    "🎰 Odds Intel & Transfers",
    "🔮 Final Verdict",
])

# ──────────────────────────────────────────────────────────────
# TAB 1 — PRE-ANALYSIS CHECKLIST
# ──────────────────────────────────────────────────────────────
with t_checklist:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Research Tracker</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Pre-Analysis Verification Status</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Tick each area **once you have personally researched it**. "
        "You can run the analysis at any time — unverified areas "
        "**reduce the confidence score** instead of blocking the verdict. "
        "Each item shows exactly how many confidence points it contributes."
    )
    st.markdown(
        _alert("info", "Why this matters",
               "Introduced after the RB Bragantino vs Santos (Sept 2025) loss — ignoring motivation, "
               "defense quality, and league context led to a failed Under prediction. "
               "Unverified areas = blind spots = lower confidence, not a hard stop."),
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    CHECKLIST_UI = [
        ("chk_defensive", "Defensive Integrity", 4,
         "Both teams kept ≥ 2 clean sheets in last 5?",
         "If NO → verdict will ABORT Under bets (driven by actual stats, not this checkbox)."),
        ("chk_volatility", "League Volatility", 4,
         "League average goals verified as < 2.4/match?",
         "If NO → Under rules invalid (driven by league variance setting, not this checkbox)."),
        ("chk_motivation", "Motivation Matrix", 4,
         "Table positions verified — both teams mid-table with no title/relegation pressure?",
         "If NOT mid-table → verdict flags HIGH Over risk (driven by positions entered, not this checkbox)."),
        ("chk_lineup", "Confirmed Lineup", 6,
         "Starting lineup confirmed (~1 h before kickoff)? Formation correct? New striker actually starting?",
         "Highest-weight item — formation and transfer assumptions are only reliable after lineup confirmation."),
        ("chk_social", "Players' Social Life", 3,
         "Social media / news checked for verified disruptions (nightclub / missed training / coach feud)?",
         "Ignore silence. Only act on confirmed evidence. If not checked, disruptions assumed absent."),
    ]

    count = sum(st.session_state.get(k, False) for k, *_ in CHECKLIST_UI)
    total_penalty_possible = sum(p for _, _, p, _, _ in CHECKLIST_UI)
    penalty_remaining = sum(p for k, _, p, _, _ in CHECKLIST_UI if not st.session_state.get(k, False))

    for key, title, penalty, question, impact in CHECKLIST_UI:
        val  = st.session_state.get(key, False)
        icon = "✅" if val else "⚠️"
        border_color = "#238636" if val else "#9e6a03"
        conf_label   = f'<span style="color:#34d399;font-size:0.78rem;font-weight:700;">+{penalty}% confidence</span>' if val else \
                       f'<span style="color:#e3b341;font-size:0.78rem;font-weight:700;">-{penalty}% confidence if skipped</span>'
        st.markdown(
            f'<div style="background:#161b22;border:1px solid {border_color};border-radius:8px;'
            f'padding:12px 16px;margin:6px 0">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
            f'<strong style="font-size:0.95rem">{icon} {title}</strong>{conf_label}'
            f'</div>'
            f'<span style="font-size:0.88rem;color:#c9d1d9">{question}</span><br/>'
            f'<span style="font-size:0.79rem;color:#8b949e;margin-top:3px;display:block">{impact}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.checkbox(f"I have verified: {title}", key=key, label_visibility="collapsed")
        st.caption(f"Tick to confirm: **{title}**")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    col_prog, col_info = st.columns([2, 1])
    with col_prog:
        st.markdown(f'<div class="conf-label">Verified areas: {count}/5</div>', unsafe_allow_html=True)
        st.progress(count / 5)
    with col_info:
        if penalty_remaining == 0:
            st.success(f"Full confidence available (+{total_penalty_possible}%)")
        else:
            st.warning(f"Unverified penalty: −{penalty_remaining}% confidence")

    st.markdown("")
    if count == 5:
        st.success(
            "All 5 areas verified. Analysis will run at maximum confidence for the given verdict."
        )
    elif count == 0:
        st.info(
            "No areas verified yet. Analysis will still run — confidence will be reduced by up to "
            f"{total_penalty_possible}%. This is fine if you are doing a quick preliminary check."
        )
    else:
        unverified = [title for k, title, *_ in CHECKLIST_UI if not st.session_state.get(k, False)]
        st.info(
            f"{count}/5 areas verified. Analysis will run with −{penalty_remaining}% confidence penalty "
            f"for unverified: **{', '.join(unverified)}**."
        )

# ──────────────────────────────────────────────────────────────
# TAB 2 — STATISTICS
# ──────────────────────────────────────────────────────────────
with t_stats:
    auto_lbl = _badge(fetched)
    st.markdown(
        f'<div class="analyst-header">'
        f'<span class="analyst-badge">Analyst #1</span>'
        f'<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Statistics Analyst</span>'
        f'{auto_lbl if fetched else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )
    if fetched:
        st.info("Fields below were auto-populated from live API data. Adjust if you have more accurate data.")

    ta, tb = _ta(), _tb()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### {ta}")
        st.number_input(f"Clean sheets in last 5 — {ta}", min_value=0, max_value=5,
                        step=1, key="stat_a_clean_sheets")
        st.number_input(f"Avg goals SCORED/match — {ta}", min_value=0.0, max_value=10.0,
                        step=0.1, format="%.1f", key="stat_a_goals_scored")
        st.number_input(f"Avg goals CONCEDED/match — {ta}", min_value=0.0, max_value=10.0,
                        step=0.1, format="%.1f", key="stat_a_goals_conceded")

    with col_b:
        st.markdown(f"#### {tb}")
        st.number_input(f"Clean sheets in last 5 — {tb}", min_value=0, max_value=5,
                        step=1, key="stat_b_clean_sheets")
        st.number_input(f"Avg goals SCORED/match — {tb}", min_value=0.0, max_value=10.0,
                        step=0.1, format="%.1f", key="stat_b_goals_scored")
        st.number_input(f"Avg goals CONCEDED/match — {tb}", min_value=0.0, max_value=10.0,
                        step=0.1, format="%.1f", key="stat_b_goals_conceded")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    cs_a = st.session_state.stat_a_clean_sheets
    cs_b = st.session_state.stat_b_clean_sheets
    if cs_a >= 2 and cs_b >= 2:
        st.markdown(_alert("success", "Defensive Integrity VERIFIED",
            f"Both teams have ≥ 2 clean sheets in last 5. Under bets defensively supported."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("danger", "Defensive Integrity FAILED",
            f"{ta}: {cs_a}/5 | {tb}: {cs_b}/5 — both need ≥ 2. ABORT all Under bets."),
            unsafe_allow_html=True)

    avg_s = (st.session_state.stat_a_goals_scored + st.session_state.stat_b_goals_scored) / 2
    st.info(f"Combined avg goals per team: **{avg_s:.2f}** "
            f"({'High-scoring fixture likely' if avg_s > 1.5 else 'Low-scoring fixture profile'})")

# ──────────────────────────────────────────────────────────────
# TAB 3 — TACTICS & FORMATIONS
# ──────────────────────────────────────────────────────────────
with t_tactics:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #2 & #3</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Tactics & Formations Analyst</span>'
        f'<span class="manual-badge">✎ Manual input</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.info("Lineups are released ~1 hour before kickoff. Come back to fill this section once the lineup is confirmed.")

    ta, tb = _ta(), _tb()
    FORMATIONS = ["4-4-2","4-3-3","4-2-3-1","3-5-2","5-3-2","4-5-1","3-4-3","4-1-4-1","4-4-1-1","Other"]
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### {ta}")
        st.selectbox(f"Formation — {ta}", FORMATIONS, key="tac_a_formation")
        st.checkbox(f"Offensive setup (2+ strikers confirmed) — {ta}", key="tac_a_offensive")
        st.text_area(f"Tactical notes — {ta}", key="tac_a_notes", height=90,
                     placeholder="High press, long-ball, deep block…")

    with col_b:
        st.markdown(f"#### {tb}")
        st.selectbox(f"Formation — {tb}", FORMATIONS, key="tac_b_formation")
        st.checkbox(f"Offensive setup (2+ strikers confirmed) — {tb}", key="tac_b_offensive")
        st.text_area(f"Tactical notes — {tb}", key="tac_b_notes", height=90,
                     placeholder="Counter-attack, possession, pressing…")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    if st.session_state.tac_a_offensive or st.session_state.tac_b_offensive:
        affected = ", ".join(
            ([ta] if st.session_state.tac_a_offensive else []) +
            ([tb] if st.session_state.tac_b_offensive else [])
        )
        st.markdown(_alert("danger", "OFFENSIVE FORMATION DETECTED",
            f"{affected} has 2+ strikers confirmed. Cancel all Under assumptions."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "Formations Compatible with Under",
            "Neither team has an offensive overload. Under assumption remains viable."),
            unsafe_allow_html=True)

    with st.expander("Formation guide"):
        st.markdown("""
| Formation | Strikers | Profile |
|-----------|----------|---------|
| 4-4-2 | 2 | Balanced / Offensive |
| 4-3-3 | 3 (wingers) | High attacking width |
| 4-2-3-1 | 1 | Controlled / Defensive |
| 3-5-2 | 2 | Offensive with wing-backs |
| 5-3-2 | 2 | Defensive with counter threat |
| 4-5-1 | 1 | Defensive / Holding result |
| 3-4-3 | 3 | Very offensive |
| 4-1-4-1 | 1 | Deep defensive block |
> **Rule**: 2+ outright strikers confirmed = **offensive formation abort** for Under bets.
        """)

# ──────────────────────────────────────────────────────────────
# TAB 4 — FORMS & MOTIVATION
# ──────────────────────────────────────────────────────────────
with t_forms:
    auto_lbl = _badge(fetched)
    st.markdown(
        f'<div class="analyst-header">'
        f'<span class="analyst-badge">Analyst #4</span>'
        f'<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Forms & Motivation Analyst</span>'
        f'{auto_lbl if fetched else ""}'
        f'</div>',
        unsafe_allow_html=True,
    )
    if fetched:
        st.info("Form and positions are auto-fetched. Each dropdown shows the fetched result — adjust if needed.")

    ta, tb = _ta(), _tb()
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### {ta} — Last 5 Matches (newest first)")
        for i in range(5):
            cur = st.session_state.get(f"form_a_{i}", "D")
            idx = ["W", "D", "L"].index(cur) if cur in ["W", "D", "L"] else 1
            st.selectbox(f"Match {i+1}", ["W", "D", "L"], index=idx, key=f"form_a_{i}")

    with col_b:
        st.markdown(f"#### {tb} — Last 5 Matches (newest first)")
        for i in range(5):
            cur = st.session_state.get(f"form_b_{i}", "D")
            idx = ["W", "D", "L"].index(cur) if cur in ["W", "D", "L"] else 1
            st.selectbox(f"Match {i+1}", ["W", "D", "L"], index=idx, key=f"form_b_{i}")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    col_fa, col_fb = st.columns(2)
    with col_fa:
        fa = _get_form("form_a")
        st.markdown(f"**{ta}**: " + _form_pills("form_a"), unsafe_allow_html=True)
        st.caption(f"W{fa.count('W')} D{fa.count('D')} L{fa.count('L')}")
    with col_fb:
        fb = _get_form("form_b")
        st.markdown(f"**{tb}**: " + _form_pills("form_b"), unsafe_allow_html=True)
        st.caption(f"W{fb.count('W')} D{fb.count('D')} L{fb.count('L')}")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### League Table Positions")
    cp1, cp2, cp3 = st.columns(3)
    with cp1:
        st.number_input(f"Position — {ta}", 1, 40, step=1, key="form_a_pos")
    with cp2:
        st.number_input(f"Position — {tb}", 1, 40, step=1, key="form_b_pos")
    with cp3:
        st.number_input("Total teams", 8, 40, step=1, key="form_league_total")

    n  = st.session_state.form_league_total
    pa = st.session_state.form_a_pos
    pb = st.session_state.form_b_pos
    hs_a = pa <= 3 or pa >= n - 3
    hs_b = pb <= 3 or pb >= n - 3

    if hs_a or hs_b:
        aff = ", ".join(([ta] if hs_a else []) + ([tb] if hs_b else []))
        st.markdown(_alert("danger", "HIGH-STAKES TABLE POSITION",
            f"{aff} is in top-3 or bottom-4. Relegation/title pressure = more goals. ABORT Under bets."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "Motivation Matrix — Low Pressure",
            "Both teams mid-table. Safe for Under consideration from motivation standpoint."),
            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 5 — MANAGER DECISIONS
# ──────────────────────────────────────────────────────────────
with t_mgr:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #5</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Manager Decisions Analyst</span>'
        '<span class="manual-badge">✎ Manual input</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _ta(), _tb()

    st.checkbox("Are the club managers on good terms or personal friends?", key="mgr_friends")
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### Points Situation")
    mc1, mc2 = st.columns(2)
    with mc1:
        st.checkbox(f"Does {ta} urgently need points?", key="mgr_a_needs_points")
    with mc2:
        st.checkbox(f"Does {tb} urgently need points?", key="mgr_b_needs_points")
    st.text_area("Additional notes", key="mgr_notes", height=80,
                 placeholder="Manager rotation tendencies, squad depth, etc.")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    friends = st.session_state.mgr_friends
    an = st.session_state.mgr_a_needs_points
    bn = st.session_state.mgr_b_needs_points
    if friends and (an != bn):
        needy  = ta if an else tb
        relaxed= tb if an else ta
        st.markdown(_alert("warning", "RELAXED GAME — HIGH PROBABILITY",
            f"Managers are friends. {needy} needs points; {relaxed} does not. "
            f"High probability {relaxed} plays below ceiling. Avoid betting against {needy}."),
            unsafe_allow_html=True)
    elif friends and (an == bn):
        st.markdown(_alert("info", "Manager Friendship — No Asymmetry",
            "Both teams in similar standing. Friendship alone does not trigger relaxed-game rule."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "No Manager Friendship Flag",
            "No relaxed-game risk detected from manager relationships."),
            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 6 — COACHES & REFEREES
# ──────────────────────────────────────────────────────────────
with t_officials:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #6</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Coaches & Referees Analyst</span>'
        '<span class="manual-badge">✎ Manual input</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _ta(), _tb()
    rc1, rc2 = st.columns([2, 1])
    with rc1:
        st.text_input("Referee name", key="ref_name", placeholder="e.g. Livio Marinelli")
    with rc2:
        st.checkbox("Known fair & accurate", key="ref_fair")
    st.text_area("Referee notes", key="ref_notes", height=80,
                 placeholder="Card frequency, penalty bias, avg goals in their matches…")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### Coaching Pressure")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.checkbox(f"{ta} coach under significant pressure", key="coach_a_pressure")
    with cc2:
        st.checkbox(f"{tb} coach under significant pressure", key="coach_b_pressure")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    if not st.session_state.ref_fair:
        st.markdown(_alert("warning", "Referee Risk",
            "Referee not confirmed as fair. Unexpected decisions may distort game beyond models."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "Referee Verified — Fair",
            "Game expected to proceed without biased intervention."),
            unsafe_allow_html=True)

    if st.session_state.coach_a_pressure or st.session_state.coach_b_pressure:
        hit = ", ".join(
            ([ta] if st.session_state.coach_a_pressure else []) +
            ([tb] if st.session_state.coach_b_pressure else [])
        )
        st.markdown(_alert("info", "Coaching Pressure Detected",
            f"{hit} coach(es) under pressure → expect conservative, defensive setup."),
            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 7 — PLAYERS' SOCIAL LIFE
# ──────────────────────────────────────────────────────────────
with t_social:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #7</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Players\' Social Life Analyst</span>'
        '<span class="manual-badge">✎ Manual input</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _ta(), _tb()
    st.markdown(
        "> **Rule**: Ignore silence. Act **only** on verified disruptions with concrete evidence."
    )
    st.markdown(_alert("info", "Valid Disruption Signals Only",
        "✅ Nightclub < 48 h before match (photo/video proof)<br/>"
        "✅ Missed training (official club statement)<br/>"
        "✅ Public feud with coach (video / official statement)"),
        unsafe_allow_html=True)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown(f"#### {ta} — Verified Disruptions")
        st.checkbox(f"Nightclub / late-night event < 48 h — {ta}", key="soc_a_nightclub")
        st.checkbox(f"Missed training (club statement) — {ta}", key="soc_a_training")
        st.checkbox(f"Public feud with coach (proof) — {ta}", key="soc_a_feud")

    with sc2:
        st.markdown(f"#### {tb} — Verified Disruptions")
        st.checkbox(f"Nightclub / late-night event < 48 h — {tb}", key="soc_b_nightclub")
        st.checkbox(f"Missed training (club statement) — {tb}", key="soc_b_training")
        st.checkbox(f"Public feud with coach (proof) — {tb}", key="soc_b_feud")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    a_dis = any([st.session_state.soc_a_nightclub, st.session_state.soc_a_training, st.session_state.soc_a_feud])
    b_dis = any([st.session_state.soc_b_nightclub, st.session_state.soc_b_training, st.session_state.soc_b_feud])

    if a_dis or b_dis:
        hit = ", ".join(([ta] if a_dis else []) + ([tb] if b_dis else []))
        st.markdown(_alert("warning", "VERIFIED SOCIAL DISRUPTION",
            f"{hit} — confirmed off-field issues. Performance risk elevated."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "No Verified Disruptions",
            "No confirmed off-field issues for either team."),
            unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# TAB 8 — ODDS INTEL & NEW TRANSFER
# ──────────────────────────────────────────────────────────────
with t_bm:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Intelligence</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Bookmaker Odds Intelligence & Transfer Analysis</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _ta(), _tb()

    # ── Live Odds Display (if fetched) ─────────────────────
    if st.session_state.fetched_odds:
        st.markdown("#### 📡 Live Odds (auto-fetched from The Odds API)")
        st.caption(f"Match: {st.session_state.fetched_odds_match}")
        odds = st.session_state.fetched_odds
        col_o = st.columns(len(odds)) if odds else []
        for col, (name, price) in zip(col_o, odds.items()):
            col.markdown(
                f'<div class="odds-card">'
                f'<div class="odds-label">{name}</div>'
                f'<div class="odds-big">{price:.2f}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # ── Bookmaker Odds Drop ────────────────────────────────
    st.markdown("#### Sharp Odds Movement")
    st.markdown(
        "> A sharp drop from ~2.00 → ~1.30 is a **bookmaker psychological trap**. "
        "In 80% of cases it signals Draw (X) or **other team** wins — not the favoured one."
    )
    st.checkbox("Did odds SHARPLY drop for one team? (e.g. 2.00 → 1.30)", key="bm_odds_dropped")

    if st.session_state.bm_odds_dropped:
        bc1, bc2 = st.columns(2)
        with bc1:
            st.number_input("Odds BEFORE drop", 1.01, 20.0, step=0.05, format="%.2f", key="bm_odds_from")
        with bc2:
            st.number_input("Odds AFTER drop", 1.01, 20.0, step=0.05, format="%.2f", key="bm_odds_to")
        st.markdown(_alert("danger", "BOOKMAKER TRAP — DO NOT BET ON FAVOURED SIDE",
            f"Odds moved {st.session_state.bm_odds_from:.2f} → {st.session_state.bm_odds_to:.2f}. "
            "<strong>80% probability: Draw or the other team wins.</strong> "
            "This is manufactured confidence to attract mass money."),
            unsafe_allow_html=True)
    else:
        st.markdown(_alert("success", "No Sharp Odds Movement Detected",
            "No bookmaker trap identified."), unsafe_allow_html=True)

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    # ── New Transfer Rule ──────────────────────────────────
    st.markdown("#### New Striker Transfer — Under 1.5 Rule")
    st.markdown(
        "> **~90% success ONLY IF all 3 conditions are met**: new striker actually starts + "
        "both teams ≥ 2 clean sheets (last 5) + low-variance league."
    )

    xc1, xc2 = st.columns(2)
    with xc1:
        st.checkbox(f"New striker recently joined {ta}", key="xfer_team_a")
    with xc2:
        st.checkbox(f"New striker recently joined {tb}", key="xfer_team_b")

    has_xfer = st.session_state.xfer_team_a or st.session_state.xfer_team_b
    if has_xfer:
        st.checkbox("New striker confirmed in starting lineup (verified 1 h before kickoff)", key="xfer_starts")

        cs_a_ = st.session_state.stat_a_clean_sheets
        cs_b_ = st.session_state.stat_b_clean_sheets
        bc = cs_a_ >= 2 and cs_b_ >= 2
        lv = st.session_state.league_variance == "low"
        st_ = st.session_state.xfer_starts

        st.markdown(
            f"**3-Condition Check:**\n"
            f"- {'✅' if st_ else '❌'} Striker confirmed starting\n"
            f"- {'✅' if bc else '❌'} Both teams ≥ 2 clean sheets\n"
            f"- {'✅' if lv else '❌'} Low-variance league\n"
        )
        if st_ and bc and lv:
            st.markdown(_alert("success", "UNDER 1.5 GOALS RULE FIRES — ~90% Success Rate",
                "All 3 conditions confirmed. Highest-confidence Under prediction in the methodology."),
                unsafe_allow_html=True)
        else:
            missing = sum([not st_, not bc, not lv])
            st.markdown(_alert("warning", f"Under 1.5 Rule Incomplete ({missing} condition(s) unmet)",
                "Not all 3 conditions active. Do not apply Under 1.5 rule."),
                unsafe_allow_html=True)

    else:
        st.markdown(_alert("info", "No New Transfer", "Transfer rule not applicable."),
            unsafe_allow_html=True)

    # ── Odds API Sport Key helper ──────────────────────────
    with st.expander("The Odds API — sport keys & troubleshooting"):
        # If test was run, show live keys; otherwise show static table
        if st.session_state.odds_soccer_keys:
            st.markdown("**Available soccer leagues (from your last Test Connections run):**")
            rows = "\n".join(
                f"| {title} | `{key}` |"
                for key, title in sorted(st.session_state.odds_soccer_keys.items())
            )
            st.markdown(f"| League | Sport Key |\n|--------|----------|\n{rows}")
        else:
            st.markdown("**Common sport keys (static list):**")
            st.markdown("""
| League | Sport Key |
|--------|-----------|
| Premier League | `soccer_epl` |
| La Liga | `soccer_spain_la_liga` |
| Serie A | `soccer_italy_serie_a` |
| Bundesliga | `soccer_germany_bundesliga` |
| Ligue 1 | `soccer_france_ligue_one` |
| Eredivisie | `soccer_netherlands_eredivisie` |
| Brasileirão | `soccer_brazil_campeonato` |
| Champions League | `soccer_uefa_champs_league` |
| Europa League | `soccer_uefa_europa_league` |
| MLS | `soccer_usa_mls` |
| Denmark Superliga | `soccer_denmark_superliga` |
| Norway Eliteserien | `soccer_norway_eliteserien` |
| Sweden Allsvenskan | `soccer_sweden_allsvenskan` |
| Turkey Süper Lig | `soccer_turkey_super_league` |
| Portuguese Liga | `soccer_portugal_primeira_liga` |
| Argentine Primera | `soccer_argentina_primera_division` |

Run **🔬 Test API Connections** in the sidebar to see all leagues currently available
for your key.
""")
        st.markdown(
            "**If odds are not found for a match:**  \n"
            "- Games usually appear in the odds 2–3 days before kickoff  \n"
            "- Make sure the league name in the sidebar matches the table above  \n"
            "- Sport key is auto-selected from the league name you entered"
        )

# ──────────────────────────────────────────────────────────────
# TAB 9 — FINAL VERDICT
# ──────────────────────────────────────────────────────────────
with t_verdict:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Final Output</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Analysis Engine — Full Verdict</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _ta(), _tb()
    league  = st.session_state.league_name or "Unknown League"

    st.markdown(
        f"**{ta}** vs **{tb}**  |  {league}  |  "
        f"{'High-variance ⚡' if st.session_state.league_variance == 'high' else 'Low-variance 🛡️'}"
    )
    if fetched:
        st.caption(f"Statistical data auto-fetched at {st.session_state.last_fetched} — "
                   "manual fields (tactics, managers, social life, referee) were entered by you.")

    st.markdown("---")

    if st.button("⚙️  Run Full Analysis", type="primary", use_container_width=True):
        result = run_analysis()

        # ── Verdict Card ─────────────────────────────────
        v_colors = {
            "verdict-under-15":   "#34d399",
            "verdict-under-25":   "#4ade80",
            "verdict-abort":      "#fb923c",
            "verdict-over":       "#f87171",
            "verdict-no-signal":  "#6b7280",
        }
        vc = v_colors.get(result["verdict_css"], "#e6edf3")
        st.markdown(
            f'<div class="verdict-card {result["verdict_css"]}">'
            f'<div class="verdict-title" style="color:{vc};">{result["verdict"]}</div>'
            f'<p class="verdict-sub">{result["rationale"]}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Note: the verdict TYPE above is determined strictly by the rules from
        # the betting methodology document — it does NOT change based on the checklist.
        # Only the confidence number below is affected by unverified areas.
        st.markdown(
            _alert("info", "Verdict rules: strictly from the methodology",
                   "The verdict above (Under 1.5 / Abort / Over / etc.) is determined "
                   "<strong>only</strong> by the 9 strict rules from the document — "
                   "league variance, clean sheets, motivation, formation, manager relations, "
                   "transfer rule, social life, odds drop. "
                   "The checklist affects <em>only</em> the confidence % below."),
            unsafe_allow_html=True,
        )

        # ── Confidence breakdown ─────────────────────────
        conf      = result["confidence"]
        base_conf = result["base_confidence"]
        penalty   = result["checklist_penalty"]
        verified  = result["checklist_verified"]
        chk_notes = result["checklist_notes"]

        if conf > 0:
            if penalty > 0:
                st.markdown(
                    f'<div class="conf-label">'
                    f'Confidence: <strong>{conf}%</strong> '
                    f'<span style="color:#8b949e">'
                    f'= base {base_conf}% − {penalty}% ({5 - verified} unverified area(s))'
                    f'</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="conf-label">Confidence: <strong>{conf}%</strong> '
                    f'<span style="color:#34d399">(all areas verified — full confidence)</span></div>',
                    unsafe_allow_html=True,
                )
            st.progress(conf / 100)

            if chk_notes:
                with st.expander(f"Why is confidence below {base_conf}%? "
                                 f"({len(chk_notes)} area(s) unverified)"):
                    for lbl, note, item_penalty in chk_notes:
                        st.markdown(f"**{lbl}** −{item_penalty}%: {note}")
                    st.caption(
                        "Verify these areas in their tabs and click Run Analysis again to raise confidence."
                    )
        else:
            st.markdown(_alert("danger", "Confidence: 0% — Bet Aborted",
                "Critical abort conditions prevent any reliable Under prediction."),
                unsafe_allow_html=True)

        st.markdown("---")

        # ── Warnings ─────────────────────────────────────
        if result["warnings"]:
            st.markdown("### ⚠️  Active Warnings")
            for w in result["warnings"]:
                st.markdown(_alert(w["kind"], w["title"], w["body"]),
                            unsafe_allow_html=True)
            st.markdown("---")

        # ── Analyst Reports ───────────────────────────────
        st.markdown("### 🗂️  Analyst Team Reports")
        rc1, rc2 = st.columns(2)
        for idx, rep in enumerate(result["analyst_reports"]):
            tgt = rc1 if idx % 2 == 0 else rc2
            with tgt:
                lines_html = "".join(f"<p>{l}</p>" for l in rep["lines"])
                st.markdown(
                    f'<div class="report-card"><h4>{rep["analyst"]}</h4>{lines_html}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # ── Rule Audit ────────────────────────────────────
        st.markdown("### 📜  Rule Audit Trail")
        with st.expander("View complete rule evaluation"):
            fa = _get_form("form_a")
            fb = _get_form("form_b")
            cs_a = st.session_state.stat_a_clean_sheets
            cs_b = st.session_state.stat_b_clean_sheets
            bc   = cs_a >= 2 and cs_b >= 2
            lv   = st.session_state.league_variance == "low"
            hv   = st.session_state.league_variance == "high"
            n    = st.session_state.form_league_total
            pa   = st.session_state.form_a_pos
            pb   = st.session_state.form_b_pos
            hs_a = pa <= 3 or pa >= n - 3
            hs_b = pb <= 3 or pb >= n - 3

            def t(b): return "✅" if b else "❌"
            st.markdown(f"""
| Rule | Condition | Result |
|------|-----------|--------|
| Defensive Integrity | Both teams ≥ 2/5 clean sheets | {t(bc)} |
| League Variance | Low-variance (< 2.4 g/m) | {t(lv)} |
| Motivation — {ta} | Not top-3 or bottom-4 | {t(not hs_a)} |
| Motivation — {tb} | Not top-3 or bottom-4 | {t(not hs_b)} |
| Formation — {ta} | No offensive overload | {t(not st.session_state.tac_a_offensive)} |
| Formation — {tb} | No offensive overload | {t(not st.session_state.tac_b_offensive)} |
| Bookmaker Trap | No sharp odds drop | {t(not st.session_state.bm_odds_dropped)} |
| Manager Friendship | No relaxed-game risk | {t(not (st.session_state.mgr_friends and (st.session_state.mgr_a_needs_points != st.session_state.mgr_b_needs_points)))} |
| New Transfer Rule | All 3 conditions confirmed | {t(result['transfer_rule'])} |
| Research Verified | {result['checklist_verified']}/5 areas confirmed | {'✅' if result['checklist_done'] else f"⚠️ ({result['checklist_verified']}/5)"} |
| Data Source | Live API data fetched | {t(fetched)} |
            """)

        # ── Disclaimer ────────────────────────────────────
        st.markdown(
            _alert("info", "Disclaimer",
                   "Rule-based analytical tool only. Does not guarantee outcomes. "
                   "Betting carries financial risk. Always gamble responsibly."),
            unsafe_allow_html=True,
        )

    else:
        st.markdown(_alert("info", "Ready for Analysis",
            "Fill all tabs, then click <strong>⚙️ Run Full Analysis</strong> above. "
            "Use <strong>⚡ Fetch Live Match Data</strong> in the sidebar to auto-populate stats."),
            unsafe_allow_html=True)

        st.markdown("#### How It Works")
        st.markdown("""
**Auto-fetch flow (sidebar → ⚡ button):**
1. Searches both teams in API-Football by name
2. Fetches last 5 finished fixtures → form (W/D/L), clean sheets, goals averages
3. Detects current league → standings → table positions
4. Computes league avg goals → auto-sets High/Low variance
5. Optionally fetches current match odds from The Odds API

**After fetch**, come back to each tab to:
- Confirm/adjust the auto-populated values
- Fill in manual fields (tactics, managers, social life, referee)
- Then click **Run Full Analysis** for the verdict

**9 Rules evaluated:**
1. League variance (auto) | 2. Bookmaker trap | 3. Manager friendship
4. Defensive integrity (auto) | 5. Motivation matrix (auto) | 6. Offensive formation
7. New transfer Under-1.5 | 8. Social life disruptions | 9. Checklist gate
        """)
