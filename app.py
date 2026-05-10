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
from datetime import datetime

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
    "fetched_odds": {}, "fetched_odds_match": "",
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
    """Cached API-Football GET. TTL = 30 min."""
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
    }
    try:
        r = requests.get(
            f"https://api-football-v1.p.rapidapi.com/v3/{endpoint}",
            headers=headers, params=params, timeout=12,
        )
        if r.status_code == 429:
            return {"error": "Daily API limit reached (100/day on free tier)", "response": []}
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        return {"error": "Request timed out after 12 s", "response": []}
    except Exception as exc:
        return {"error": str(exc), "response": []}


def af_search_team(name: str, api_key: str) -> dict | None:
    """Return first team result for exact name, then fuzzy search."""
    d = _af("teams", {"name": name}, api_key)
    if d.get("response"):
        return d["response"][0]
    d = _af("teams", {"search": name}, api_key)
    if d.get("response"):
        return d["response"][0]
    return None


def af_last_fixtures(team_id: int, n: int, api_key: str) -> list:
    """Return last N finished fixtures for team_id."""
    d = _af("fixtures", {"team": team_id, "last": n, "status": "FT"}, api_key)
    return d.get("response", [])


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
    """Return (league_id, season, league_name) for team's primary current league."""
    d = _af("leagues", {"team": team_id, "current": "true"}, api_key)
    for item in d.get("response", []):
        if item["league"]["type"] == "League":
            seasons = item.get("seasons", [])
            season  = seasons[-1]["year"] if seasons else datetime.now().year
            return item["league"]["id"], season, item["league"]["name"]
    return None, None, ""


def af_standings(league_id: int, season: int, api_key: str) -> list:
    """Return flat list of standing entries."""
    d = _af("standings", {"league": league_id, "season": season}, api_key)
    try:
        groups = d["response"][0]["league"]["standings"]
        flat = []
        for g in groups:
            flat.extend(g)
        return flat
    except (IndexError, KeyError, TypeError):
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

# Maps common league names → Odds API sport keys
_SPORT_KEY_MAP = {
    "premier league": "soccer_epl",
    "epl": "soccer_epl",
    "la liga": "soccer_spain_la_liga",
    "serie a": "soccer_italy_serie_a",
    "bundesliga": "soccer_germany_bundesliga",
    "ligue 1": "soccer_france_ligue_one",
    "eredivisie": "soccer_netherlands_eredivisie",
    "brasileirao": "soccer_brazil_campeonato",
    "campeonato": "soccer_brazil_campeonato",
    "mls": "soccer_usa_mls",
    "champions league": "soccer_uefa_champs_league",
    "europa league": "soccer_uefa_europa_league",
    "championship": "soccer_efl_champ",
    "primera division": "soccer_spain_la_liga",
}


def _sport_key(league_name: str) -> str:
    lower = league_name.lower().strip()
    for fragment, key in _SPORT_KEY_MAP.items():
        if fragment in lower:
            return key
    return "soccer_epl"


@st.cache_data(ttl=900, show_spinner=False)
def odds_fetch(sport_key: str, odds_key: str) -> list:
    """Fetch all current odds for a sport. TTL = 15 min."""
    try:
        r = requests.get(
            f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/",
            params={"apiKey": odds_key, "regions": "eu,uk", "markets": "h2h",
                    "oddsFormat": "decimal"},
            timeout=12,
        )
        if r.status_code in (401, 403):
            return [{"error": "Invalid Odds API key"}]
        if r.status_code == 422:
            return [{"error": f"Sport key '{sport_key}' not found in Odds API"}]
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        return [{"error": str(exc)}]


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
        # Try reversed (team order may differ)
        match_ar = ta_l in at or at in ta_l or any(w in at for w in ta_l.split())
        match_br = tb_l in ht or ht in tb_l or any(w in ht for w in tb_l.split())
        if match_ar and match_br:
            return g
    return None


def extract_h2h_odds(game: dict) -> dict:
    """Pull best h2h odds from first bookmaker."""
    result = {}
    for bm in game.get("bookmakers", []):
        for mkt in bm.get("markets", []):
            if mkt["key"] == "h2h":
                for o in mkt.get("outcomes", []):
                    result[o["name"]] = o["price"]
                return result
    return result


# ============================================================
# MAIN AUTO-FETCH ORCHESTRATOR
# ============================================================

def do_auto_fetch(football_key: str, odds_key: str) -> None:
    """
    Fetch live data from APIs and populate session_state.
    Shows inline progress within the sidebar fetch section.
    """
    ta = st.session_state.team_a.strip()
    tb = st.session_state.team_b.strip()

    if not ta or not tb:
        st.sidebar.error("Enter both team names first.")
        return

    log: list[str] = []
    errors: list[str] = []

    ph_status   = st.sidebar.empty()
    ph_progress = st.sidebar.progress(0)

    # ── Step 1: Find team IDs ──────────────────────────────
    ph_status.info("🔍 Searching teams…")
    ph_progress.progress(8)

    ta_data = af_search_team(ta, football_key)
    tb_data = af_search_team(tb, football_key)

    if ta_data is None:
        errors.append(f"Team not found: '{ta}'. Try the exact official name (e.g. 'Manchester City').")
    else:
        log.append(f"✅ {ta} → ID {ta_data['team']['id']} ({ta_data['team']['country']})")

    if tb_data is None:
        errors.append(f"Team not found: '{tb}'.")
    else:
        log.append(f"✅ {tb} → ID {tb_data['team']['id']} ({tb_data['team']['country']})")

    if errors:
        ph_progress.progress(100)
        ph_status.error("Fetch failed — see errors below.")
        st.session_state.fetch_log    = log
        st.session_state.fetch_errors = errors
        return

    ta_id = ta_data["team"]["id"]
    tb_id = tb_data["team"]["id"]

    # ── Step 2: Last 5 fixtures ────────────────────────────
    ph_status.info("📅 Fetching last 5 results…")
    ph_progress.progress(22)

    fix_a = af_last_fixtures(ta_id, 5, football_key)
    fix_b = af_last_fixtures(tb_id, 5, football_key)

    if not fix_a:
        errors.append(f"No recent finished fixtures found for {ta}.")
    if not fix_b:
        errors.append(f"No recent finished fixtures found for {tb}.")

    if not errors:
        stats_a = af_parse_fixtures(fix_a, ta_id)
        stats_b = af_parse_fixtures(fix_b, tb_id)

        # Pad form lists to exactly 5 entries (oldest fill = "D")
        fa = stats_a["form"][:]
        while len(fa) < 5:
            fa.append("D")
        fb = stats_b["form"][:]
        while len(fb) < 5:
            fb.append("D")

        # Write directly to widget session-state keys
        for i in range(5):
            st.session_state[f"form_a_{i}"] = fa[i]
            st.session_state[f"form_b_{i}"] = fb[i]

        st.session_state.stat_a_clean_sheets  = stats_a["clean_sheets"]
        st.session_state.stat_b_clean_sheets  = stats_b["clean_sheets"]
        st.session_state.stat_a_goals_scored   = stats_a["avg_scored"]
        st.session_state.stat_a_goals_conceded = stats_a["avg_conceded"]
        st.session_state.stat_b_goals_scored   = stats_b["avg_scored"]
        st.session_state.stat_b_goals_conceded = stats_b["avg_conceded"]

        form_a_str = " ".join(fa[:5])
        form_b_str = " ".join(fb[:5])
        log.append(
            f"✅ {ta}: [{form_a_str}] — {stats_a['clean_sheets']}/5 clean sheets | "
            f"avg {stats_a['avg_scored']} scored / {stats_a['avg_conceded']} conceded"
        )
        log.append(
            f"✅ {tb}: [{form_b_str}] — {stats_b['clean_sheets']}/5 clean sheets | "
            f"avg {stats_b['avg_scored']} scored / {stats_b['avg_conceded']} conceded"
        )

    # ── Step 3: League + standings ─────────────────────────
    ph_status.info("🏆 Fetching league table…")
    ph_progress.progress(50)

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
                f"✅ Standings ({league_name_api}, {season}): "
                f"{ta} #{pos_a or '?'} | {tb} #{pos_b or '?'} of {total}"
            )

            # Auto-set league variance from average goals
            avg_g = af_league_avg_goals(standings)
            if avg_g:
                if avg_g >= 2.6:
                    st.session_state.league_variance = "high"
                    var_tag = f"HIGH-variance (≥2.6, actual {avg_g})"
                elif avg_g < 2.4:
                    st.session_state.league_variance = "low"
                    var_tag = f"LOW-variance (<2.4, actual {avg_g})"
                else:
                    var_tag = f"MEDIUM ({avg_g}) — please confirm manually"
                log.append(f"✅ League avg goals/match: {avg_g} → {var_tag}")
        else:
            log.append(f"⚠️  Standings not available for {league_name_api or 'this league'}")
    else:
        log.append(f"⚠️  Could not determine current league for {ta}")

    # ── Step 4: Odds (optional) ────────────────────────────
    if odds_key.strip():
        ph_status.info("🎰 Fetching current odds…")
        ph_progress.progress(78)

        league_for_key = st.session_state.league_name or league_name_api or ""
        sport_key = _sport_key(league_for_key)
        games = odds_fetch(sport_key, odds_key.strip())

        if games and "error" in games[0]:
            log.append(f"⚠️  Odds API: {games[0]['error']}")
        else:
            match = odds_find_match(games, ta, tb)
            if match:
                h2h = extract_h2h_odds(match)
                st.session_state.fetched_odds = h2h
                st.session_state.fetched_odds_match = (
                    f"{match.get('home_team')} vs {match.get('away_team')} "
                    f"({match.get('sport_title','')})"
                )
                log.append(f"✅ Odds found: {h2h}")
            else:
                log.append(
                    f"⚠️  Match not listed in current odds for sport key '{sport_key}'. "
                    "Game may not be scheduled soon, or try a different sport key."
                )

    # ── Done ───────────────────────────────────────────────
    ph_progress.progress(100)
    now = datetime.now().strftime("%H:%M:%S")
    ph_status.success(f"✅ Fetch complete at {now}")

    st.session_state.fetch_log    = log
    st.session_state.fetch_errors = errors
    st.session_state.last_fetched = now


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

    checklist_done = all([
        st.session_state.chk_defensive, st.session_state.chk_volatility,
        st.session_state.chk_motivation, st.session_state.chk_lineup,
        st.session_state.chk_social,
    ])

    # ── Warnings ───────────────────────────────────────────
    if not checklist_done:
        warnings.append({"kind": "warning", "title": "PRE-ANALYSIS CHECKLIST INCOMPLETE",
            "body": "Not all 5 mandatory checklist items confirmed. Verdict may be unreliable."})

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

    # ── Verdict ────────────────────────────────────────────
    if transfer_rule and not must_abort:
        verdict, css, confidence = "UNDER 1.5 Goals", "verdict-under-15", 90
        rationale = ("New striker starting + both teams ≥ 2 clean sheets + low-variance league. "
                     "3-condition rule fires at ~90% historical accuracy.")
    elif must_abort:
        verdict, css, confidence = "ABORT ALL UNDER BETS", "verdict-abort", 0
        rationale = "One or more critical abort conditions active. See warnings above."
    elif is_low_var and both_clean and not high_stakes and not offensive_formation:
        verdict, css, confidence = "UNDER 2.5 Goals", "verdict-under-25", 65
        rationale = ("Low-variance league, both teams defensively solid, "
                     "no high-stakes pressure, no offensive overload.")
    elif is_high_var or high_stakes or offensive_formation:
        verdict, css, confidence = "LEAN OVER 2.5 Goals", "verdict-over", 60
        rationale = "League context, table pressure, or confirmed attacking setup suggests higher-scoring game."
    else:
        verdict, css, confidence = "NO CLEAR SIGNAL", "verdict-no-signal", 35
        rationale = "Conflicting or insufficient data. Insufficient edge to recommend a bet — avoid this match."

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
        "confidence": confidence, "rationale": rationale,
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

    # ── Auto-Fetch Section ─────────────────────────────────
    st.markdown("### 🔄 Auto-Fetch Live Data")

    with st.expander("🔑 API Keys (required to fetch)", expanded=not st.session_state.last_fetched):
        st.markdown(
            "**API-Football** (free: 100 req/day)  \n"
            "👉 [rapidapi.com → api-football](https://rapidapi.com/api-sports/api/api-football)"
        )
        st.text_input("API-Football Key (RapidAPI)", type="password",
                      key="api_key_football", placeholder="Paste your RapidAPI key…")

        st.markdown(
            "**The Odds API** (free: 500 req/month) — *optional*  \n"
            "👉 [the-odds-api.com](https://the-odds-api.com)"
        )
        st.text_input("The Odds API Key (optional)", type="password",
                      key="api_key_odds", placeholder="Paste your Odds API key…")

        st.markdown("**What gets auto-filled:**")
        st.markdown(
            "✅ Form (W/D/L last 5)  \n"
            "✅ Clean sheets count  \n"
            "✅ Goals avg (scored & conceded)  \n"
            "✅ League table positions  \n"
            "✅ League variance (auto-detected)  \n"
            "✅ Current match odds (if Odds API key set)  \n"
            "✎ Manager friendship — manual  \n"
            "✎ Formations/lineup — manual  \n"
            "✎ Social life — manual  \n"
            "✎ Referee — manual"
        )

    can_fetch = bool(st.session_state.api_key_football.strip())
    if st.button("⚡ Fetch Live Match Data", type="primary",
                 use_container_width=True, disabled=not can_fetch):
        do_auto_fetch(
            st.session_state.api_key_football.strip(),
            st.session_state.api_key_odds.strip(),
        )
        st.rerun()

    if not can_fetch:
        st.caption("Enter your API-Football key above to enable fetching.")

    if st.session_state.last_fetched:
        st.caption(f"Last fetched: **{st.session_state.last_fetched}**")

        if st.session_state.fetch_errors:
            for e in st.session_state.fetch_errors:
                st.error(e)

        if st.session_state.fetch_log:
            with st.expander("Fetch log"):
                for line in st.session_state.fetch_log:
                    st.markdown(f"<p style='margin:2px 0;font-size:0.8rem;font-family:monospace'>{line}</p>",
                                unsafe_allow_html=True)

    st.markdown("---")

    # ── Quick status ───────────────────────────────────────
    st.markdown("**Quick Status**")
    chk_done = sum([st.session_state.chk_defensive, st.session_state.chk_volatility,
                    st.session_state.chk_motivation, st.session_state.chk_lineup, st.session_state.chk_social])
    cs_a_ = st.session_state.stat_a_clean_sheets
    cs_b_ = st.session_state.stat_b_clean_sheets
    ta_, tb_ = _ta(), _tb()
    st.markdown(f"Checklist: **{chk_done}/5**")
    st.markdown(f"League: **{'High-variance ⚡' if st.session_state.league_variance == 'high' else 'Low-variance 🛡️'}**")
    st.markdown(f"Clean sheets: **{ta_[:12]}: {cs_a_}** | **{tb_[:12]}: {cs_b_}**")
    pos_a_ = st.session_state.form_a_pos
    pos_b_ = st.session_state.form_b_pos
    st.markdown(f"Positions: **#{pos_a_}** vs **#{pos_b_}** (of {st.session_state.form_league_total})")


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
        '<span class="analyst-badge">Mandatory</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Pre-Analysis Checklist</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "All five items **must** be confirmed before any tip is finalised. "
        "Introduced after the RB Bragantino vs Santos (Sept 2025) loss — where ignoring motivation, "
        "defense quality, and league context led to a failed Under prediction."
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)

    CHECKLIST = [
        ("chk_defensive", "Defensive Integrity",
         "Both teams kept ≥ 2 clean sheets in last 5 matches?",
         "→ If NO, **ABORT all Under bets**."),
        ("chk_volatility", "League Volatility",
         "League average goals < 2.4/match (low-variance)?",
         "→ If NO, **Under rules are invalid**."),
        ("chk_motivation", "Motivation Matrix",
         "Both teams mid-table — no promotion/relegation stakes?",
         "→ If either is top-3 or bottom-4: **HIGH Over risk**."),
        ("chk_lineup", "Confirmed Lineup (1 h before kickoff)",
         "New striker actually starting? Key defenders present? Formation not offensive?",
         "→ If offensive or key defenders missing: **cancel Under assumption**."),
        ("chk_social", "Players' Social Life — Verified Disruption Only",
         "Any confirmed disruptions: nightclub < 48 h, missed training (club statement), coach feud (video)?",
         "→ Ignore silence. Only verified evidence has weight."),
    ]

    count = sum(st.session_state.get(k, False) for k, *_ in CHECKLIST)
    for key, title, question, rule in CHECKLIST:
        val  = st.session_state.get(key, False)
        icon = "✅" if val else "⬜"
        st.markdown(
            f'<div style="background:#161b22;border:1px solid #30363d;border-radius:8px;'
            f'padding:12px 16px;margin:6px 0">'
            f'<strong>{icon} {title}</strong><br/>'
            f'<span style="font-size:0.9rem">{question}</span><br/>'
            f'<span style="font-size:0.8rem;color:#8b949e">{rule}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.checkbox(f"Confirm: {title}", key=key, label_visibility="collapsed")
        st.caption(f"Confirm: **{title}**")

    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown(f'<div class="conf-label">Progress: {count}/5 confirmed</div>', unsafe_allow_html=True)
    st.progress(count / 5)
    if count == 5:
        st.success("All 5 items confirmed — proceed to analysis.")
    else:
        st.warning(f"{5 - count} item(s) still need confirmation.")

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
    with st.expander("The Odds API — supported leagues & sport keys"):
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

The app auto-selects the sport key from your league name. If odds aren't found,
try adjusting the league name to match one of the rows above.
        """)

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

        # ── Confidence ───────────────────────────────────
        conf = result["confidence"]
        if conf > 0:
            st.markdown(f'<div class="conf-label">Confidence Score: {conf}%</div>',
                        unsafe_allow_html=True)
            st.progress(conf / 100)
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
| Checklist | All 5 items confirmed | {t(result['checklist_done'])} |
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
