# ============================================================
# BetDestroy Sports Analysis Engine
# A 7-analyst sports betting research tool based on strict
# rules derived from professional betting methodology.
#
# HOW TO RUN:
#   1. Install dependencies:
#      pip install streamlit
#
#   2. Launch the application:
#      streamlit run app.py
#
#   3. Open your browser at: http://localhost:8501
# ============================================================
import streamlit as st
st.set_page_config(
    page_title="BetDestroy | Analysis Engine",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ============================================================
# GLOBAL STYLES
# ============================================================
st.markdown(
    """
<style>
    /* ---- Background & base ---- */
    .stApp { background-color: #0d1117; }
    section[data-testid="stSidebar"] { background-color: #161b22; }
    section[data-testid="stSidebar"] * { color: #c9d1d9 !important; }
    /* ---- Typography ---- */
    h1, h2, h3, h4 { color: #e6edf3 !important; }
    p, li, label { color: #c9d1d9; }
    /* ---- Main title ---- */
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 900;
        background: linear-gradient(135deg, #58a6ff 0%, #a371f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        padding: 0;
    }
    .main-subtitle {
        text-align: center;
        color: #8b949e;
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 24px;
    }
    /* ---- Analyst section header ---- */
    .analyst-header {
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(90deg, #1f2937 0%, #111827 100%);
        border-left: 4px solid #58a6ff;
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 16px;
    }
    .analyst-badge {
        display: inline-block;
        background: linear-gradient(135deg, #58a6ff, #a371f7);
        color: #0d1117;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    /* ---- Verdict boxes ---- */
    .verdict-card {
        border-radius: 14px;
        padding: 28px 24px;
        text-align: center;
        margin: 10px 0 20px 0;
    }
    .verdict-under-15 {
        background: linear-gradient(135deg, #052e16 0%, #065f46 100%);
        border: 2px solid #34d399;
    }
    .verdict-under-25 {
        background: linear-gradient(135deg, #0c2a1e 0%, #14532d 100%);
        border: 2px solid #4ade80;
    }
    .verdict-abort {
        background: linear-gradient(135deg, #27150a 0%, #431407 100%);
        border: 2px solid #fb923c;
    }
    .verdict-over {
        background: linear-gradient(135deg, #1e0a0a 0%, #450a0a 100%);
        border: 2px solid #f87171;
    }
    .verdict-no-signal {
        background: linear-gradient(135deg, #1c1f26 0%, #2d3139 100%);
        border: 2px solid #6b7280;
    }
    .verdict-title {
        font-size: 1.9rem;
        font-weight: 900;
        letter-spacing: 0.04em;
        margin: 0 0 8px 0;
    }
    .verdict-sub {
        font-size: 1rem;
        color: #d1d5db;
        margin: 0;
    }
    /* ---- Alert boxes ---- */
    .alert {
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0;
        line-height: 1.6;
    }
    .alert-danger {
        background: #1a0a0a;
        border: 1px solid #dc2626;
        color: #fca5a5;
    }
    .alert-warning {
        background: #1c1208;
        border: 1px solid #d97706;
        color: #fcd34d;
    }
    .alert-success {
        background: #051a0e;
        border: 1px solid #16a34a;
        color: #86efac;
    }
    .alert-info {
        background: #0a1628;
        border: 1px solid #2563eb;
        color: #93c5fd;
    }
    /* ---- Analyst report card ---- */
    .report-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px 18px;
        margin: 8px 0;
    }
    .report-card h4 { margin: 0 0 10px 0; font-size: 0.95rem; color: #58a6ff !important; }
    .report-card p  { margin: 3px 0; font-size: 0.88rem; color: #c9d1d9; }
    /* ---- Checklist items ---- */
    .check-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        background: #161b22;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 6px 0;
        border: 1px solid #30363d;
    }
    .check-icon { font-size: 1.3rem; flex-shrink: 0; margin-top: 1px; }
    .check-text { font-size: 0.9rem; line-height: 1.5; }
    .check-rule  { font-size: 0.8rem; color: #8b949e; margin-top: 4px; }
    /* ---- Divider ---- */
    .section-divider {
        border: none;
        border-top: 1px solid #30363d;
        margin: 18px 0;
    }
    /* ---- Confidence bar label ---- */
    .conf-label { font-size: 0.82rem; color: #8b949e; margin-bottom: 2px; }
    /* ---- Form row metric ---- */
    .form-pill {
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        text-align: center;
        line-height: 30px;
        font-weight: 700;
        font-size: 0.82rem;
        margin: 2px;
    }
    .form-w { background: #16a34a; color: #fff; }
    .form-d { background: #d97706; color: #fff; }
    .form-l { background: #dc2626; color: #fff; }
</style>
""",
    unsafe_allow_html=True,
)
# ============================================================
# SESSION STATE INITIALISATION
# ============================================================
_DEFAULTS: dict = {
    # --- Match setup ---
    "team_a": "Team A",
    "team_b": "Team B",
    "league_name": "",
    "league_variance": "low",
    # --- Pre-analysis checklist ---
    "chk_defensive": False,
    "chk_volatility": False,
    "chk_motivation": False,
    "chk_lineup": False,
    "chk_social": False,
    # --- Statistics ---
    "stat_a_clean_sheets": 0,
    "stat_b_clean_sheets": 0,
    "stat_a_goals_scored": 1.2,
    "stat_b_goals_scored": 1.2,
    "stat_a_goals_conceded": 1.2,
    "stat_b_goals_conceded": 1.2,
    # --- Tactics & Formations ---
    "tac_a_formation": "4-4-2",
    "tac_b_formation": "4-4-2",
    "tac_a_offensive": False,
    "tac_b_offensive": False,
    "tac_a_notes": "",
    "tac_b_notes": "",
    # --- Forms ---
    "form_a": ["W", "W", "D", "L", "W"],
    "form_b": ["W", "D", "L", "W", "D"],
    "form_a_pos": 10,
    "form_b_pos": 10,
    "form_league_total": 20,
    # --- Manager Decisions ---
    "mgr_friends": False,
    "mgr_a_needs_points": False,
    "mgr_b_needs_points": False,
    "mgr_notes": "",
    # --- Coaches & Referees ---
    "ref_name": "",
    "ref_fair": True,
    "ref_notes": "",
    "coach_a_pressure": False,
    "coach_b_pressure": False,
    # --- Players' Social Life ---
    "soc_a_nightclub": False,
    "soc_a_training": False,
    "soc_a_feud": False,
    "soc_b_nightclub": False,
    "soc_b_training": False,
    "soc_b_feud": False,
    # --- Bookmaker Intelligence ---
    "bm_odds_dropped": False,
    "bm_odds_from": 2.00,
    "bm_odds_to": 1.30,
    # --- New Transfer ---
    "xfer_team_a": False,
    "xfer_team_b": False,
    "xfer_starts": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v
# ============================================================
# HELPER UTILITIES
# ============================================================
def _team_a() -> str:
    return st.session_state.get("team_a") or "Team A"
def _team_b() -> str:
    return st.session_state.get("team_b") or "Team B"
def _alert(kind: str, title: str, body: str) -> str:
    css = f"alert-{kind}"
    icon = {"danger": "🚨", "warning": "⚠️", "success": "✅", "info": "ℹ️"}.get(kind, "•")
    return (
        f'<div class="alert {css}">'
        f'<strong>{icon} {title}</strong><br/>{body}'
        f'</div>'
    )
def _form_pills(form_list: list) -> str:
    html = ""
    for r in form_list:
        css = {"W": "form-w", "D": "form-d", "L": "form-l"}.get(r, "form-d")
        html += f'<span class="form-pill {css}">{r}</span>'
    return html
# ============================================================
# ANALYSIS ENGINE
# ============================================================
def run_analysis() -> dict:
    """
    Apply all betting rules and return a structured verdict dict.
    Rules applied (in priority order):
    1. Bookmaker odds drop warning (80% opposite outcome)
    2. Manager friendship / relaxed-game flag
    3. Pre-analysis checklist completeness
    4. Defensive Integrity abort  (< 2 clean sheets each)
    5. League Volatility abort    (high-variance league)
    6. Motivation Matrix abort    (top-3 or bottom-4 team)
    7. Confirmed Lineup abort     (offensive formation)
    8. New Transfer Under-1.5 rule (≥90% success if all 3 conditions met)
    9. Default verdict based on remaining signals
    """
    ta = _team_a()
    tb = _team_b()
    warnings = []
    analyst_reports = []
    # ── 1. Bookmaker Odds Drop ──────────────────────────────────────
    bm_drop = st.session_state.bm_odds_dropped
    if bm_drop:
        frm = st.session_state.bm_odds_from
        to_ = st.session_state.bm_odds_to
        warnings.append({
            "kind": "danger",
            "title": "BOOKMAKER PSYCHOLOGICAL TRAP DETECTED",
            "body": (
                f"Odds sharply reduced from {frm:.2f} → {to_:.2f}. "
                "In 80% of cases this signals X (Draw) or the OTHER team wins. "
                "Bookmakers manufacture false certainty to harvest mass bets. "
                "<strong>DO NOT bet on the apparently favoured side.</strong>"
            ),
        })
    # ── 2. Manager Relationship ─────────────────────────────────────
    mgr_friends = st.session_state.mgr_friends
    a_needs = st.session_state.mgr_a_needs_points
    b_needs = st.session_state.mgr_b_needs_points
    mgr_flag = mgr_friends and (a_needs != b_needs)
    if mgr_flag:
        needy  = ta if a_needs else tb
        relaxed = tb if a_needs else ta
        warnings.append({
            "kind": "warning",
            "title": "MANAGER FRIENDSHIP — RELAXED GAME RISK",
            "body": (
                f"Managers are on good terms. {needy} needs points; {relaxed} does not. "
                f"High probability {relaxed} plays relaxed and concedes the win. "
                f"Expected outcome: {needy} wins or low-energy draw."
            ),
        })
    # ── 3. Pre-analysis checklist completeness ──────────────────────
    checklist_done = all([
        st.session_state.chk_defensive,
        st.session_state.chk_volatility,
        st.session_state.chk_motivation,
        st.session_state.chk_lineup,
        st.session_state.chk_social,
    ])
    # ── 4. Defensive Integrity ──────────────────────────────────────
    cs_a = st.session_state.stat_a_clean_sheets
    cs_b = st.session_state.stat_b_clean_sheets
    both_clean = cs_a >= 2 and cs_b >= 2
    # ── 5. League Variance ──────────────────────────────────────────
    variance = st.session_state.league_variance
    is_low_var  = variance == "low"
    is_high_var = variance == "high"
    # ── 6. Motivation Matrix ────────────────────────────────────────
    pos_a   = st.session_state.form_a_pos
    pos_b   = st.session_state.form_b_pos
    n_teams = st.session_state.form_league_total
    # top-3 or bottom-4 means high-stakes position
    high_stakes_a = (pos_a <= 3) or (pos_a >= n_teams - 3)
    high_stakes_b = (pos_b <= 3) or (pos_b >= n_teams - 3)
    high_stakes   = high_stakes_a or high_stakes_b
    # ── 7. Confirmed Lineup / Offensive Formation ───────────────────
    off_a = st.session_state.tac_a_offensive
    off_b = st.session_state.tac_b_offensive
    offensive_formation = off_a or off_b
    # ── 8. Social Life Disruptions ──────────────────────────────────
    a_disrupted = any([
        st.session_state.soc_a_nightclub,
        st.session_state.soc_a_training,
        st.session_state.soc_a_feud,
    ])
    b_disrupted = any([
        st.session_state.soc_b_nightclub,
        st.session_state.soc_b_training,
        st.session_state.soc_b_feud,
    ])
    # ── 9. New Transfer ─────────────────────────────────────────────
    new_striker = st.session_state.xfer_team_a or st.session_state.xfer_team_b
    striker_starts = st.session_state.xfer_starts
    new_transfer_rule_fires = new_striker and striker_starts and both_clean and is_low_var
    # ── Abort conditions ────────────────────────────────────────────
    abort_reasons = []
    if not both_clean:
        abort_reasons.append(
            f"Defensive integrity FAILS — {ta}: {cs_a}/5 clean sheets, "
            f"{tb}: {cs_b}/5 clean sheets (both need ≥ 2)"
        )
    if is_high_var:
        abort_reasons.append(
            "High-variance league (≥ 2.6 goals/match) — Under rules are INVALID"
        )
    if high_stakes:
        if high_stakes_a:
            abort_reasons.append(
                f"{ta} is in a high-stakes table position (#{pos_a} of {n_teams}) — "
                "relegation/title pressure drives more goals"
            )
        if high_stakes_b:
            abort_reasons.append(
                f"{tb} is in a high-stakes table position (#{pos_b} of {n_teams}) — "
                "relegation/title pressure drives more goals"
            )
    if offensive_formation:
        if off_a:
            abort_reasons.append(f"{ta} confirmed offensive formation (2+ strikers)")
        if off_b:
            abort_reasons.append(f"{tb} confirmed offensive formation (2+ strikers)")
    must_abort = len(abort_reasons) > 0
    # ── Final Verdict ───────────────────────────────────────────────
    if new_transfer_rule_fires and not must_abort:
        verdict   = "UNDER 1.5 Goals"
        verdict_css = "verdict-under-15"
        confidence  = 90
        rationale   = (
            "New striker starting + both teams ≥ 2 clean sheets in last 5 + "
            "low-variance league. The 3-condition rule fires at ~90% historical accuracy."
        )
    elif must_abort:
        verdict     = "ABORT ALL UNDER BETS"
        verdict_css = "verdict-abort"
        confidence  = 0
        rationale   = "One or more critical abort conditions are active. See warnings below."
    elif is_low_var and both_clean and not high_stakes and not offensive_formation:
        verdict     = "UNDER 2.5 Goals"
        verdict_css = "verdict-under-25"
        confidence  = 65
        rationale   = (
            "Low-variance league, both teams defensively solid, no high-stakes pressure, "
            "no offensive overload detected."
        )
    elif is_high_var or high_stakes or offensive_formation:
        verdict     = "LEAN OVER 2.5 Goals"
        verdict_css = "verdict-over"
        confidence  = 60
        rationale   = (
            "League context, table pressure, or confirmed attacking setups suggest "
            "a higher-scoring game."
        )
    else:
        verdict     = "NO CLEAR SIGNAL"
        verdict_css = "verdict-no-signal"
        confidence  = 35
        rationale   = (
            "Conflicting or insufficient data. Insufficient edge to recommend a bet. "
            "Avoid this match."
        )
    if must_abort:
        warnings.append({
            "kind": "danger",
            "title": "ABORT — UNDER BET INVALIDATED",
            "body": "<br/>".join(f"• {r}" for r in abort_reasons),
        })
    if a_disrupted or b_disrupted:
        teams_hit = ", ".join(
            ([ta] if a_disrupted else []) + ([tb] if b_disrupted else [])
        )
        warnings.append({
            "kind": "warning",
            "title": "VERIFIED SOCIAL DISRUPTION",
            "body": (
                f"{teams_hit} — confirmed off-field issues (nightclub / missed training / "
                "public feud). Performance risk elevated; factor into all predictions."
            ),
        })
    if not checklist_done:
        warnings.insert(0, {
            "kind": "warning",
            "title": "PRE-ANALYSIS CHECKLIST INCOMPLETE",
            "body": (
                "Not all 5 mandatory checklist items have been confirmed. "
                "Complete the Checklist tab before trusting this verdict."
            ),
        })
    # ── Build analyst reports ───────────────────────────────────────
    form_a_str = " ".join(st.session_state.form_a)
    form_b_str = " ".join(st.session_state.form_b)
    analyst_reports = [
        {
            "analyst": "📊 Statistics Analyst",
            "lines": [
                f"{ta}: {cs_a}/5 clean sheets | Avg scored: {st.session_state.stat_a_goals_scored:.1f} | Avg conceded: {st.session_state.stat_a_goals_conceded:.1f}",
                f"{tb}: {cs_b}/5 clean sheets | Avg scored: {st.session_state.stat_b_goals_scored:.1f} | Avg conceded: {st.session_state.stat_b_goals_conceded:.1f}",
                f"Defensive integrity: {'✅ Both teams solid (≥ 2 clean sheets)' if both_clean else '❌ Fails — not enough clean sheets'}",
            ],
        },
        {
            "analyst": "⚔️ Tactics & Formations Analyst",
            "lines": [
                f"{ta}: {st.session_state.tac_a_formation} | Offensive setup: {'🔴 Yes (2+ strikers)' if off_a else '🟢 No'}",
                f"{tb}: {st.session_state.tac_b_formation} | Offensive setup: {'🔴 Yes (2+ strikers)' if off_b else '🟢 No'}",
                f"Formation abort trigger: {'❌ Active' if offensive_formation else '✅ Clear'}",
            ],
        },
        {
            "analyst": "📈 Forms & Motivation Analyst",
            "lines": [
                f"{ta}: {form_a_str} | League position #{pos_a} of {n_teams}",
                f"{tb}: {form_b_str} | League position #{pos_b} of {n_teams}",
                f"High-stakes pressure: {'🔴 Yes — Over risk elevated' if high_stakes else '🟢 None detected'}",
            ],
        },
        {
            "analyst": "🤝 Manager Decisions Analyst",
            "lines": [
                f"Managers on good terms: {'Yes' if mgr_friends else 'No'}",
                f"{ta} needs points: {'Yes' if a_needs else 'No'} | {tb} needs points: {'Yes' if b_needs else 'No'}",
                f"Relaxed-game flag: {'🔴 Active — see warning above' if mgr_flag else '🟢 Not triggered'}",
            ],
        },
        {
            "analyst": "🏟️ Coaches & Referees Analyst",
            "lines": [
                f"Referee: {st.session_state.ref_name or 'Not specified'} | Known fair: {'✅ Yes' if st.session_state.ref_fair else '⚠️ No / Unknown'}",
                f"{ta} coach under pressure: {'Yes' if st.session_state.coach_a_pressure else 'No'}",
                f"{tb} coach under pressure: {'Yes' if st.session_state.coach_b_pressure else 'No'}",
            ],
        },
        {
            "analyst": "📱 Players' Social Life Analyst",
            "lines": [
                (
                    f"{ta}: "
                    + (", ".join(filter(None, [
                        "Nightclub <48h" if st.session_state.soc_a_nightclub else "",
                        "Missed training" if st.session_state.soc_a_training else "",
                        "Coach feud" if st.session_state.soc_a_feud else "",
                    ])) or "No verified disruptions")
                ),
                (
                    f"{tb}: "
                    + (", ".join(filter(None, [
                        "Nightclub <48h" if st.session_state.soc_b_nightclub else "",
                        "Missed training" if st.session_state.soc_b_training else "",
                        "Coach feud" if st.session_state.soc_b_feud else "",
                    ])) or "No verified disruptions")
                ),
                f"Disruption flag: {'🔴 Active' if (a_disrupted or b_disrupted) else '🟢 Clear'}",
            ],
        },
        {
            "analyst": "🔄 New Transfer Analyst",
            "lines": [
                f"New striker in {ta}: {'Yes' if st.session_state.xfer_team_a else 'No'}",
                f"New striker in {tb}: {'Yes' if st.session_state.xfer_team_b else 'No'}",
                f"Striker confirmed starting: {'Yes' if striker_starts else 'No'}",
                f"Under 1.5 rule (3-condition): {'✅ Fires (~90%)' if new_transfer_rule_fires else '❌ Not active'}",
            ],
        },
    ]
    return {
        "verdict": verdict,
        "verdict_css": verdict_css,
        "confidence": confidence,
        "rationale": rationale,
        "warnings": warnings,
        "analyst_reports": analyst_reports,
        "checklist_done": checklist_done,
        "bm_drop": bm_drop,
        "new_transfer_rule_fires": new_transfer_rule_fires,
        "must_abort": must_abort,
    }
# ============================================================
# SIDEBAR — MATCH SETUP
# ============================================================
with st.sidebar:
    st.markdown(
        '<div style="font-size:1.5rem;font-weight:900;color:#58a6ff;margin-bottom:4px;">⚽ BetDestroy</div>'
        '<div style="font-size:0.78rem;color:#8b949e;margin-bottom:20px;">Analysis Engine v2.0</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Match Setup")
    st.text_input("Team A", key="team_a", placeholder="e.g. Fiorentina")
    st.text_input("Team B", key="team_b", placeholder="e.g. Napoli")
    st.text_input("League / Competition", key="league_name", placeholder="e.g. Serie A")
    st.markdown("---")
    st.markdown("**League Variance**")
    st.caption(
        "High-variance: avg ≥ 2.6 goals/match (e.g. Brasileirão, Eredivisie).  \n"
        "Low-variance: avg < 2.4 goals/match (e.g. Serie A, Ligue 1)."
    )
    st.radio(
        "Select league type",
        options=["low", "high"],
        format_func=lambda x: "Low-variance  (< 2.4 goals/match)" if x == "low" else "High-variance (≥ 2.6 goals/match)",
        key="league_variance",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**Quick Status**")
    ta, tb = _team_a(), _team_b()
    checks_done = sum([
        st.session_state.chk_defensive,
        st.session_state.chk_volatility,
        st.session_state.chk_motivation,
        st.session_state.chk_lineup,
        st.session_state.chk_social,
    ])
    st.markdown(f"Checklist: **{checks_done}/5** items confirmed")
    st.markdown(
        f"League: **{'High-variance ⚡' if st.session_state.league_variance == 'high' else 'Low-variance 🛡️'}**"
    )
    cs_a_ = st.session_state.stat_a_clean_sheets
    cs_b_ = st.session_state.stat_b_clean_sheets
    st.markdown(
        f"Clean sheets: **{ta[:10]}: {cs_a_}** | **{tb[:10]}: {cs_b_}**"
    )
# ============================================================
# MAIN HEADER
# ============================================================
st.markdown(
    '<h1 class="main-title">BetDestroy Analysis Engine</h1>'
    '<p class="main-subtitle">7-Analyst Sports Betting Research System — Rule-Based Predictions</p>',
    unsafe_allow_html=True,
)
# ============================================================
# TABS
# ============================================================
(
    t_checklist,
    t_stats,
    t_tactics,
    t_forms,
    t_mgr,
    t_officials,
    t_social,
    t_bm,
    t_verdict,
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
# TAB 1 — PRE-ANALYSIS CHECKLIST (MANDATORY)
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
        "This checklist was introduced after the RB Bragantino vs Santos (Sept 28, 2025) loss — "
        "where ignoring motivation, defense quality, and league context led to a failed Under prediction."
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    checklist_items = [
        (
            "chk_defensive",
            "Defensive Integrity",
            "Have **both** teams kept ≥ 2 clean sheets in their last 5 matches?",
            "→ If NO, **ABORT all Under bets**. One leaky defense invalidates every Under prediction.",
        ),
        (
            "chk_volatility",
            "League Volatility",
            "Is the league average goals **< 2.4 per match** (low-variance)?",
            "→ If NO, assume **Under rules are invalid**. High-variance leagues ignore typical defensive patterns.",
        ),
        (
            "chk_motivation",
            "Motivation Matrix",
            "Are both teams mid-table with no promotion/relegation stakes?",
            "→ If either team is in the top 3 or bottom 4: **HIGH Over risk**. Pressure produces goals.",
        ),
        (
            "chk_lineup",
            "Confirmed Lineup (1 hour before kickoff)",
            "Is new striker actually starting? Are key defenders present? Is formation not offensive?",
            "→ If new striker starts, key defenders missing, or 2+ striker formation: **cancel Under assumption**.",
        ),
        (
            "chk_social",
            "Players' Social Life — Verified Disruption Only",
            "Are there confirmed disruptions: nightclub < 48 h, missed training (club statement), or public feud with coach (video proof)?",
            "→ Ignore silence. Act **only on verified evidence**. Unconfirmed rumours = zero weight.",
        ),
    ]
    confirmed_count = 0
    for key, title, question, rule in checklist_items:
        val = st.session_state.get(key, False)
        icon = "✅" if val else "⬜"
        if val:
            confirmed_count += 1
        st.markdown(
            f'<div class="check-row">'
            f'<span class="check-icon">{icon}</span>'
            f'<div class="check-text"><strong>{title}</strong><br/>{question}'
            f'<div class="check-rule">{rule}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.checkbox(f"Confirm: {title}", key=key, label_visibility="collapsed")
        st.caption(f"Confirm: **{title}**")
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    prog = confirmed_count / 5
    color = "#34d399" if confirmed_count == 5 else ("#fb923c" if confirmed_count >= 3 else "#f87171")
    st.markdown(f'<div class="conf-label">Checklist progress: {confirmed_count}/5</div>', unsafe_allow_html=True)
    st.progress(prog)
    if confirmed_count == 5:
        st.success("All 5 checklist items confirmed. You may proceed to analysis.")
    else:
        st.warning(f"{5 - confirmed_count} item(s) still need confirmation. Analysis will be flagged as incomplete.")
# ──────────────────────────────────────────────────────────────
# TAB 2 — STATISTICS ANALYST
# ──────────────────────────────────────────────────────────────
with t_stats:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #1</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Statistics Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"#### {ta}")
        st.number_input(
            f"Clean sheets in last 5 matches — {ta}",
            min_value=0, max_value=5, step=1,
            key="stat_a_clean_sheets",
            help="How many of the last 5 games did this team keep a clean sheet?",
        )
        st.number_input(
            f"Average goals SCORED per match — {ta}",
            min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
            key="stat_a_goals_scored",
        )
        st.number_input(
            f"Average goals CONCEDED per match — {ta}",
            min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
            key="stat_a_goals_conceded",
        )
    with col_b:
        st.markdown(f"#### {tb}")
        st.number_input(
            f"Clean sheets in last 5 matches — {tb}",
            min_value=0, max_value=5, step=1,
            key="stat_b_clean_sheets",
            help="How many of the last 5 games did this team keep a clean sheet?",
        )
        st.number_input(
            f"Average goals SCORED per match — {tb}",
            min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
            key="stat_b_goals_scored",
        )
        st.number_input(
            f"Average goals CONCEDED per match — {tb}",
            min_value=0.0, max_value=10.0, step=0.1, format="%.1f",
            key="stat_b_goals_conceded",
        )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    cs_a = st.session_state.stat_a_clean_sheets
    cs_b = st.session_state.stat_b_clean_sheets
    if cs_a >= 2 and cs_b >= 2:
        st.markdown(
            _alert("success", "Defensive Integrity VERIFIED",
                   f"Both teams have ≥ 2 clean sheets in last 5. Under bets are defensively supported."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("danger", "Defensive Integrity FAILED",
                   f"{ta}: {cs_a}/5 clean sheets | {tb}: {cs_b}/5 clean sheets. "
                   "Both must have ≥ 2. ABORT all Under bets."),
            unsafe_allow_html=True,
        )
    avg_scored = (
        st.session_state.stat_a_goals_scored + st.session_state.stat_b_goals_scored
    ) / 2
    st.info(
        f"Combined avg goals per team per match: **{avg_scored:.2f}** "
        f"({'High-scoring fixture likely' if avg_scored > 1.5 else 'Low-scoring fixture profile'})"
    )
# ──────────────────────────────────────────────────────────────
# TAB 3 — TACTICS & FORMATIONS
# ──────────────────────────────────────────────────────────────
with t_tactics:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #2 & #3</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Tactics & Formations Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    col_a, col_b = st.columns(2)
    FORMATIONS = [
        "4-4-2", "4-3-3", "4-2-3-1", "3-5-2", "5-3-2",
        "4-5-1", "3-4-3", "4-1-4-1", "4-4-1-1", "Other",
    ]
    with col_a:
        st.markdown(f"#### {ta}")
        st.selectbox(f"Formation — {ta}", options=FORMATIONS, key="tac_a_formation")
        st.checkbox(
            f"Offensive setup (2+ strikers) — {ta}",
            key="tac_a_offensive",
            help="Tick if confirmed lineup shows 2 or more strikers / very attacking setup.",
        )
        st.text_area(
            f"Tactical notes — {ta}",
            key="tac_a_notes",
            height=100,
            placeholder="e.g. Playing high press, long-ball, possession-based...",
        )
    with col_b:
        st.markdown(f"#### {tb}")
        st.selectbox(f"Formation — {tb}", options=FORMATIONS, key="tac_b_formation")
        st.checkbox(
            f"Offensive setup (2+ strikers) — {tb}",
            key="tac_b_offensive",
            help="Tick if confirmed lineup shows 2 or more strikers / very attacking setup.",
        )
        st.text_area(
            f"Tactical notes — {tb}",
            key="tac_b_notes",
            height=100,
            placeholder="e.g. Counter-attacking, deep block, overlapping fullbacks...",
        )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    off_a = st.session_state.tac_a_offensive
    off_b = st.session_state.tac_b_offensive
    if off_a or off_b:
        teams_offensive = ", ".join(
            ([ta] if off_a else []) + ([tb] if off_b else [])
        )
        st.markdown(
            _alert("danger", "OFFENSIVE FORMATION DETECTED",
                   f"{teams_offensive} confirmed with 2+ strikers. "
                   "Cancel all Under assumptions for this match. Expect more attacking intent and goals."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "Formations Compatible with Under",
                   "Neither team has an offensive overload formation. Under assumption remains viable."),
            unsafe_allow_html=True,
        )
    # Formation reference guide
    with st.expander("Formation Reference Guide"):
        st.markdown("""
| Formation | Strikers | Profile |
|-----------|----------|---------|
| 4-4-2     | 2        | Balanced / Offensive |
| 4-3-3     | 3 (wingers) | High attacking width |
| 4-2-3-1   | 1        | Controlled / Defensive |
| 3-5-2     | 2        | Offensive with wing-backs |
| 5-3-2     | 2        | Defensive with counter threat |
| 4-5-1     | 1        | Defensive / Holding result |
| 3-4-3     | 3        | Very offensive |
| 4-1-4-1   | 1        | Deep defensive block |
> **Rule**: Any formation with 2+ outright strikers confirmed in the starting lineup triggers the **offensive formation abort**.
        """)
# ──────────────────────────────────────────────────────────────
# TAB 4 — FORMS & MOTIVATION
# ──────────────────────────────────────────────────────────────
with t_forms:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #4</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Forms & Motivation Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"#### {ta} — Recent Form (last 5 matches)")
        form_a_vals = []
        for i in range(5):
            default_idx = ["W", "D", "L"].index(st.session_state.form_a[i]) if i < len(st.session_state.form_a) else 0
            v = st.selectbox(
                f"Match {i+1} (most recent first)",
                options=["W", "D", "L"],
                index=default_idx,
                key=f"form_a_{i}",
            )
            form_a_vals.append(v)
        st.session_state.form_a = form_a_vals
    with col_b:
        st.markdown(f"#### {tb} — Recent Form (last 5 matches)")
        form_b_vals = []
        for i in range(5):
            default_idx = ["W", "D", "L"].index(st.session_state.form_b[i]) if i < len(st.session_state.form_b) else 0
            v = st.selectbox(
                f"Match {i+1} (most recent first)",
                options=["W", "D", "L"],
                index=default_idx,
                key=f"form_b_{i}",
            )
            form_b_vals.append(v)
        st.session_state.form_b = form_b_vals
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### Form Summary")
    col_fa, col_fb = st.columns(2)
    with col_fa:
        st.markdown(
            f"**{ta}**: " + _form_pills(st.session_state.form_a),
            unsafe_allow_html=True,
        )
        wins_a = st.session_state.form_a.count("W")
        draws_a = st.session_state.form_a.count("D")
        losses_a = st.session_state.form_a.count("L")
        st.caption(f"W{wins_a} D{draws_a} L{losses_a}")
    with col_fb:
        st.markdown(
            f"**{tb}**: " + _form_pills(st.session_state.form_b),
            unsafe_allow_html=True,
        )
        wins_b = st.session_state.form_b.count("W")
        draws_b = st.session_state.form_b.count("D")
        losses_b = st.session_state.form_b.count("L")
        st.caption(f"W{wins_b} D{draws_b} L{losses_b}")
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### League Table Positions")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.number_input(f"League position — {ta}", min_value=1, max_value=40, step=1, key="form_a_pos")
    with col_p2:
        st.number_input(f"League position — {tb}", min_value=1, max_value=40, step=1, key="form_b_pos")
    with col_p3:
        st.number_input("Total teams in league", min_value=8, max_value=40, step=1, key="form_league_total")
    n = st.session_state.form_league_total
    pa = st.session_state.form_a_pos
    pb = st.session_state.form_b_pos
    hs_a = pa <= 3 or pa >= n - 3
    hs_b = pb <= 3 or pb >= n - 3
    if hs_a or hs_b:
        affected = ", ".join(([ta] if hs_a else []) + ([tb] if hs_b else []))
        st.markdown(
            _alert("danger", "HIGH-STAKES TABLE POSITION",
                   f"{affected} {'are' if ' ' in affected else 'is'} in a top-3 or bottom-4 position. "
                   "Relegation or title pressure = emotional, high-intensity play = more goals. "
                   "ABORT all Under bets for this match."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "Motivation Matrix — Low Pressure",
                   "Both teams are mid-table with no immediate promotion/relegation stakes. "
                   "Safe for Under consideration from a motivation standpoint."),
            unsafe_allow_html=True,
        )
# ──────────────────────────────────────────────────────────────
# TAB 5 — MANAGER DECISIONS
# ──────────────────────────────────────────────────────────────
with t_mgr:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #5</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Manager Decisions Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    st.markdown("#### Manager Relationship")
    st.markdown(
        "> If managers are personal friends and **one team needs points while the other does not**, "
        "there is a high probability the 'comfortable' team plays relaxed and allows the needy team to win."
    )
    st.checkbox(
        "Are the club managers on good terms or personal friends?",
        key="mgr_friends",
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### Points Situation")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.checkbox(f"Does {ta} urgently need points right now?", key="mgr_a_needs_points")
    with col_m2:
        st.checkbox(f"Does {tb} urgently need points right now?", key="mgr_b_needs_points")
    st.text_area(
        "Additional manager / tactical notes",
        key="mgr_notes",
        height=100,
        placeholder="e.g. Manager A is known to rotate heavily in this fixture...",
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    friends = st.session_state.mgr_friends
    a_needs = st.session_state.mgr_a_needs_points
    b_needs = st.session_state.mgr_b_needs_points
    if friends and (a_needs != b_needs):
        needy  = ta if a_needs else tb
        relaxed = tb if a_needs else ta
        st.markdown(
            _alert("warning", "RELAXED GAME — HIGH PROBABILITY",
                   f"Managers are friends. {needy} needs points; {relaxed} does not. "
                   f"Historical pattern: {relaxed} plays below their ceiling, effectively gifting the win or a comfortable draw to {needy}. "
                   "Avoid betting against the needy team in this scenario."),
            unsafe_allow_html=True,
        )
    elif friends and a_needs == b_needs:
        st.markdown(
            _alert("info", "Manager Friendship — No Asymmetry",
                   "Both teams are in similar standing (both need points or neither does). "
                   "Friendship alone does not trigger the relaxed-game rule."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "Manager Relationship — No Flag",
                   "No friendship-based relaxed-game risk detected."),
            unsafe_allow_html=True,
        )
    with st.expander("Background: Why manager friendships matter"):
        st.markdown("""
If Manager A (4th place, needs 3rd place points) is close friends with Manager B
(8th place, nothing at stake), there is a **high probability** that Manager B's
team will play below maximum intensity — effectively giving the win to Manager A's
team.
This is one of the non-statistical signals that separates professional tipsters
from casual bettors. It cannot be found in any odds model.
**Key indicators to research:**
- Post-match interviews mentioning each other warmly
- Joint press appearances or public events
- Same nationality / former teammates / mentor relationship
- Past matches between their teams showing unusual passivity
        """)
# ──────────────────────────────────────────────────────────────
# TAB 6 — COACHES & REFEREES
# ──────────────────────────────────────────────────────────────
with t_officials:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #6</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Coaches & Referees Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    st.markdown("#### Referee Profile")
    col_r1, col_r2 = st.columns([2, 1])
    with col_r1:
        st.text_input("Referee name", key="ref_name", placeholder="e.g. Livio Marinelli")
    with col_r2:
        st.checkbox(
            "Known to be fair & accurate (rarely favours either team)",
            key="ref_fair",
        )
    st.text_area(
        "Referee notes",
        key="ref_notes",
        height=80,
        placeholder="e.g. Gives many cards, historically strict on handballs...",
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("#### Coaching Staff Pressure")
    st.markdown(
        "_Coaches under heavy pressure from the board or supporters tend to impose restrictive, "
        "defensive tactics — reducing open play and creativity._"
    )
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.checkbox(
            f"{ta} head coach is under significant board/fan pressure",
            key="coach_a_pressure",
        )
    with col_c2:
        st.checkbox(
            f"{tb} head coach is under significant board/fan pressure",
            key="coach_b_pressure",
        )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    cp_a = st.session_state.coach_a_pressure
    cp_b = st.session_state.coach_b_pressure
    ref_fair = st.session_state.ref_fair
    if not ref_fair:
        st.markdown(
            _alert("warning", "Referee Risk",
                   "Referee is not confirmed as fair/accurate. Unexpected officiating decisions "
                   "(penalties, red cards, disallowed goals) may distort the game beyond analytical models."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "Referee Verified — Fair",
                   "Game expected to proceed by the rules without biased intervention."),
            unsafe_allow_html=True,
        )
    if cp_a or cp_b:
        under_pressure = ", ".join(([ta] if cp_a else []) + ([tb] if cp_b else []))
        st.markdown(
            _alert("info", "Coaching Pressure Detected",
                   f"{under_pressure} coach(es) under pressure. Expect conservative, defensive setup — "
                   "potentially supporting an Under prediction if other conditions are met."),
            unsafe_allow_html=True,
        )
    with st.expander("Background: The referee effect (Fiorentina vs Napoli case study)"):
        st.markdown("""
In the **Fiorentina vs Napoli** match (Aug 28, 2022), referee **Livio Marinelli** was
on duty — known for being accurate and unemotional.
He correctly ruled offside on a Napoli goal in the 42nd minute, demonstrating the
reliability that our analysts had predicted. A biased or poor referee could have
allowed that goal, changing the entire match dynamic.
**What to research about referees:**
- Avg cards per game (high = disruptive to flow)
- Historical penalty frequency
- Known team bias in high-pressure games
- Avg goals per game in their matches (useful for Over/Under calibration)
        """)
# ──────────────────────────────────────────────────────────────
# TAB 7 — PLAYERS' SOCIAL LIFE
# ──────────────────────────────────────────────────────────────
with t_social:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Analyst #7</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Players\' Social Life Analyst</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    st.markdown(
        "> **Rule**: Ignore silence or absence of posts. Act **only** on verified disruptions with "
        "concrete evidence. Unconfirmed rumours carry zero analytical weight."
    )
    st.markdown(
        _alert("info", "Valid Disruption Signals Only",
               "✅ Nightclub appearance < 48 h before match (photo / video proof)<br/>"
               "✅ Missed training session (official club statement)<br/>"
               "✅ Public feud with coach (video proof / official statement)"),
        unsafe_allow_html=True,
    )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"#### {ta} — Verified Disruptions")
        st.checkbox(
            f"Nightclub / late-night event < 48 h before match — {ta}",
            key="soc_a_nightclub",
        )
        st.checkbox(
            f"Missed training session (official club statement) — {ta}",
            key="soc_a_training",
        )
        st.checkbox(
            f"Public feud with coach (video / official proof) — {ta}",
            key="soc_a_feud",
        )
    with col_s2:
        st.markdown(f"#### {tb} — Verified Disruptions")
        st.checkbox(
            f"Nightclub / late-night event < 48 h before match — {tb}",
            key="soc_b_nightclub",
        )
        st.checkbox(
            f"Missed training session (official club statement) — {tb}",
            key="soc_b_training",
        )
        st.checkbox(
            f"Public feud with coach (video / official proof) — {tb}",
            key="soc_b_feud",
        )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    a_dis = any([
        st.session_state.soc_a_nightclub,
        st.session_state.soc_a_training,
        st.session_state.soc_a_feud,
    ])
    b_dis = any([
        st.session_state.soc_b_nightclub,
        st.session_state.soc_b_training,
        st.session_state.soc_b_feud,
    ])
    if a_dis or b_dis:
        teams_dis = ", ".join(([ta] if a_dis else []) + ([tb] if b_dis else []))
        st.markdown(
            _alert("warning", "VERIFIED SOCIAL DISRUPTION",
                   f"{teams_dis} — confirmed off-field issues detected. "
                   "Player performance may be impaired. Reassess any prediction that relies on peak performance."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "No Verified Disruptions",
                   "No confirmed off-field issues for either team. Proceed with analysis."),
            unsafe_allow_html=True,
        )
    with st.expander("Background: The Fiorentina Instagram signal (Aug 28, 2022)"):
        st.markdown("""
In the days before **Fiorentina vs Napoli**, our social life analyst noticed that
Fiorentina's key attacking players — who normally posted Instagram stories daily —
went completely silent after a training session where visible disagreements occurred
between players fighting for the ball instead of collaborating.
**Interpretation**: Players who are sad, dissatisfied, or stressed do not post on
social media. The emotional state suggested a tense dressing room operating under
pressure from coach Vincenzo Italiano.
**This led to the prediction**: Fiorentina would play defensively, with pressure-filled
performances rather than free-flowing football — reducing their attacking output.
**Result**: Under 2.5 Goals confirmed at odds 2.20.
**Critical reminder**: This is not about counting posts. It is about detecting
**sudden silence after a visible conflict event**. Never flag silence alone.
        """)
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
    ta, tb = _team_a(), _team_b()
    st.markdown("### Bookmaker Odds Movement")
    st.markdown(
        "> Bookmakers employ thousands of analysts. A sharp odds drop from ~2.00 → ~1.30 is a "
        "**deliberate psychological trap**. In 80% of cases it signals that **X (Draw)** or the "
        "**other team** will win — not the now-favoured team."
    )
    st.checkbox(
        "Did the odds SHARPLY drop (e.g. 2.00 → 1.30) for one team in this match?",
        key="bm_odds_dropped",
    )
    if st.session_state.bm_odds_dropped:
        col_o1, col_o2 = st.columns(2)
        with col_o1:
            st.number_input("Odds BEFORE the drop", min_value=1.01, max_value=20.0,
                            step=0.05, format="%.2f", key="bm_odds_from")
        with col_o2:
            st.number_input("Odds AFTER the drop", min_value=1.01, max_value=20.0,
                            step=0.05, format="%.2f", key="bm_odds_to")
        st.markdown(
            _alert("danger", "BOOKMAKER TRAP — DO NOT BET ON FAVOURED SIDE",
                   f"Odds moved {st.session_state.bm_odds_from:.2f} → {st.session_state.bm_odds_to:.2f}. "
                   "This creates an illusion of certainty designed to attract mass money onto one side. "
                   "The bookmaker's own tipsters assessed the opposite. "
                   "<strong>In 80% of cases: Draw (X) or the unfavoured team wins.</strong>"),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("success", "No Sharp Odds Movement Detected",
                   "Proceed with analysis. No bookmaker psychological trap identified."),
            unsafe_allow_html=True,
        )
    st.markdown('<hr class="section-divider"/>', unsafe_allow_html=True)
    st.markdown("### New Transfer — Under 1.5 Rule")
    st.markdown(
        "> When a new **striker** joins a team, tactics change in ~75% of cases. "
        "The game is played more carefully; the manager avoids risk in the first 1–2 games. "
        "> **Predicting Under 1.5 Goals reaches ~90% accuracy ONLY IF all 3 conditions are met**:"
    )
    st.markdown(
        """
- The new striker **actually starts** (confirmed lineup)
- **Both teams** have kept ≥ 2 clean sheets in last 5 matches
- The **league is low-variance** (avg goals < 2.4/match)
> In high-variance leagues (e.g. Brasileirão), this rule **often fails**.
        """
    )
    col_x1, col_x2 = st.columns(2)
    with col_x1:
        st.checkbox(f"New striker recently joined {ta}", key="xfer_team_a")
    with col_x2:
        st.checkbox(f"New striker recently joined {tb}", key="xfer_team_b")
    if st.session_state.xfer_team_a or st.session_state.xfer_team_b:
        st.checkbox(
            "New striker is confirmed in the starting lineup (1 hour before kickoff verified)",
            key="xfer_starts",
        )
        cs_a = st.session_state.stat_a_clean_sheets
        cs_b = st.session_state.stat_b_clean_sheets
        both_cs = cs_a >= 2 and cs_b >= 2
        low_var = st.session_state.league_variance == "low"
        starts  = st.session_state.xfer_starts
        cond_1 = "✅" if starts  else "❌"
        cond_2 = "✅" if both_cs else "❌"
        cond_3 = "✅" if low_var  else "❌"
        st.markdown("**3-Condition Check:**")
        st.markdown(
            f"- {cond_1} Striker confirmed starting  \n"
            f"- {cond_2} Both teams ≥ 2 clean sheets (last 5)  \n"
            f"- {cond_3} Low-variance league (< 2.4 goals/match)"
        )
        if starts and both_cs and low_var:
            st.markdown(
                _alert("success", "UNDER 1.5 GOALS RULE FIRES — ~90% Success Rate",
                       "All 3 conditions confirmed. This is the highest-confidence Under prediction "
                       "in the entire methodology. New striker + defensive solidity + controlled league = "
                       "extremely low-scoring game expected."),
                unsafe_allow_html=True,
            )
        else:
            missing = sum([not starts, not both_cs, not low_var])
            st.markdown(
                _alert("warning", f"Under 1.5 Rule Incomplete ({missing} condition(s) unmet)",
                       "Not all 3 conditions are active. Do not apply the Under 1.5 rule. "
                       "A new striker alone is insufficient — the other conditions must also hold."),
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            _alert("info", "No New Transfer Detected",
                   "New transfer rule is not applicable for this match."),
            unsafe_allow_html=True,
        )
# ──────────────────────────────────────────────────────────────
# TAB 9 — FINAL ANALYSIS & VERDICT
# ──────────────────────────────────────────────────────────────
with t_verdict:
    st.markdown(
        '<div class="analyst-header">'
        '<span class="analyst-badge">Final Output</span>'
        '<span style="font-weight:700;font-size:1.05rem;color:#e6edf3;">Analysis Engine — Full Verdict</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    ta, tb = _team_a(), _team_b()
    league = st.session_state.league_name or "Unknown League"
    st.markdown(
        f"**Match**: {ta} vs {tb}  |  **League**: {league}  |  "
        f"**Variance**: {'High ⚡' if st.session_state.league_variance == 'high' else 'Low 🛡️'}"
    )
    st.markdown("---")
    if st.button("⚙️ Run Full Analysis", type="primary", use_container_width=True):
        result = run_analysis()
        # ── Verdict Card ───────────────────────────────────────
        verdict     = result["verdict"]
        verdict_css = result["verdict_css"]
        confidence  = result["confidence"]
        rationale   = result["rationale"]
        verdict_colors = {
            "verdict-under-15":  "#34d399",
            "verdict-under-25":  "#4ade80",
            "verdict-abort":     "#fb923c",
            "verdict-over":      "#f87171",
            "verdict-no-signal": "#6b7280",
        }
        v_color = verdict_colors.get(verdict_css, "#e6edf3")
        st.markdown(
            f'<div class="verdict-card {verdict_css}">'
            f'<div class="verdict-title" style="color:{v_color};">{verdict}</div>'
            f'<p class="verdict-sub">{rationale}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        # ── Confidence ─────────────────────────────────────────
        if confidence > 0:
            st.markdown(
                f'<div class="conf-label">Confidence Score: {confidence}%</div>',
                unsafe_allow_html=True,
            )
            st.progress(confidence / 100)
        else:
            st.markdown(
                _alert("danger", "Confidence: 0% — Bet Aborted",
                       "Critical abort conditions prevent any reliable Under prediction."),
                unsafe_allow_html=True,
            )
        st.markdown("---")
        # ── Warnings ──────────────────────────────────────────
        if result["warnings"]:
            st.markdown("### ⚠️ Active Warnings")
            for w in result["warnings"]:
                st.markdown(
                    _alert(w["kind"], w["title"], w["body"]),
                    unsafe_allow_html=True,
                )
            st.markdown("---")
        # ── Analyst Reports ────────────────────────────────────
        st.markdown("### 🗂️ Analyst Team Reports")
        col_1, col_2 = st.columns(2)
        reports = result["analyst_reports"]
        for idx, report in enumerate(reports):
            target = col_1 if idx % 2 == 0 else col_2
            with target:
                lines_html = "".join(f"<p>{line}</p>" for line in report["lines"])
                st.markdown(
                    f'<div class="report-card">'
                    f'<h4>{report["analyst"]}</h4>'
                    f'{lines_html}'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        st.markdown("---")
        # ── Rule Audit Trail ───────────────────────────────────
        st.markdown("### 📜 Rule Audit Trail")
        with st.expander("View complete rule evaluation"):
            cs_a = st.session_state.stat_a_clean_sheets
            cs_b = st.session_state.stat_b_clean_sheets
            both_cs = cs_a >= 2 and cs_b >= 2
            low_var  = st.session_state.league_variance == "low"
            high_var = st.session_state.league_variance == "high"
            n        = st.session_state.form_league_total
            pa, pb   = st.session_state.form_a_pos, st.session_state.form_b_pos
            hs_a = pa <= 3 or pa >= n - 3
            hs_b = pb <= 3 or pb >= n - 3
            def tick(b): return "✅" if b else "❌"
            st.markdown(f"""
| Rule | Condition | Status |
|------|-----------|--------|
| Defensive Integrity | Both teams ≥ 2 clean sheets (last 5) | {tick(both_cs)} |
| League Variance | Low-variance (< 2.4 goals/match) | {tick(low_var)} |
| Motivation — {ta} | Not in top 3 or bottom 4 | {tick(not hs_a)} |
| Motivation — {tb} | Not in top 3 or bottom 4 | {tick(not hs_b)} |
| Formation — {ta} | No offensive overload (< 2 strikers) | {tick(not st.session_state.tac_a_offensive)} |
| Formation — {tb} | No offensive overload (< 2 strikers) | {tick(not st.session_state.tac_b_offensive)} |
| Manager Friendship | Friends + asymmetric points need | {tick(result.get('bm_drop') is False)} |
| Bookmaker Trap | No sharp odds drop detected | {tick(not st.session_state.bm_odds_dropped)} |
| New Transfer Rule | All 3 conditions confirmed | {tick(result['new_transfer_rule_fires'])} |
| Checklist Complete | All 5 items confirmed | {tick(result['checklist_done'])} |
            """)
        # ── Disclaimer ────────────────────────────────────────
        st.markdown(
            _alert("info", "Disclaimer",
                   "This tool applies rule-based analysis methodology only. "
                   "It does not guarantee outcomes. Betting carries financial risk. "
                   "Always gamble responsibly and within your means."),
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            _alert("info", "Ready for Analysis",
                   "Fill in all tabs, then click <strong>Run Full Analysis</strong> above "
                   "to generate the verdict from all 7 analysts."),
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown("#### How the Analysis Engine Works")
        st.markdown(
            """
The engine evaluates **9 strict rules** in priority order:
1. **Bookmaker Odds Drop** — Did odds sharply fall? → 80% false certainty trap
2. **Manager Relationship** — Friends + asymmetric motivation → relaxed game flag
3. **Defensive Integrity** — Both teams need ≥ 2 clean sheets → else abort Under
4. **League Variance** — High-variance league → Under rules invalid
5. **Motivation Matrix** — Top-3 or bottom-4 teams → Over risk elevated
6. **Confirmed Lineup** — Offensive formation (2+ strikers) → cancel Under assumption
7. **New Transfer Rule** — New striker starts + clean sheets + low variance → Under 1.5 (~90%)
8. **Players' Social Life** — Verified disruptions only (nightclub / missed training / feud)
9. **Default Signal** — Based on remaining context: Under 2.5 / Over lean / No signal
The **7-analyst team** (Statistics, Tactics, Formations, Forms, Manager Decisions,
Coaches & Referees, Players' Social Life) each contribute their findings,
which feed into the final verdict.
            """
        )
