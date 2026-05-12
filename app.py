import streamlit as st
import numpy as np
import pickle
import os
import plotly.graph_objects as go

# ================= CONFIG =================
st.set_page_config(
    page_title="Goal Goblin – EPL Analytics",
    page_icon="⚽",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap');

/* ── ROOT TOKENS ── */
:root {
    --pitch:    #00E87A;
    --pitch-dim:#00B85F;
    --navy:     #04091A;
    --panel:    #080F22;
    --card:     #0D1830;
    --border:   rgba(0,232,122,0.18);
    --text:     #E8EDF5;
    --muted:    #7A90B0;
    --accent:   #1B6EF3;
    --danger:   #F34545;
    --gold:     #FFD234;
}

/* ── GLOBAL ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    background: var(--navy) !important;
    color: var(--text) !important;
    font-family: 'Barlow', sans-serif !important;
}

/* ── PITCH GRID BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,232,122,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,232,122,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* keep content above pseudo */
section[data-testid="stMain"] > div { position: relative; z-index: 1; }

/* ── HEADER BANNER ── */
.gg-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #010B1F 0%, #061230 50%, #010B1F 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 36px 42px 32px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 28px;
}
.gg-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,232,122,0.12) 0%, transparent 70%);
}
.gg-header::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 400px; height: 120px;
    background: radial-gradient(ellipse, rgba(27,110,243,0.10) 0%, transparent 70%);
}
.gg-badge {
    font-size: 3.8rem;
    line-height: 1;
    filter: drop-shadow(0 0 18px rgba(0,232,122,0.55));
    animation: pulse-ball 3s ease-in-out infinite;
}
@keyframes pulse-ball {
    0%,100% { filter: drop_shadow(0 0 14px rgba(0,232,122,0.55)); }
    50%      { filter: drop_shadow(0 0 28px rgba(0,232,122,0.90)); }
}
.gg-titles { flex: 1; }
.gg-brand {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 3.0rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    background: linear-gradient(90deg, #fff 30%, var(--pitch) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0; line-height: 1.05;
}
.gg-sub {
    font-family: 'Barlow', sans-serif;
    font-weight: 400;
    font-size: 0.88rem;
    color: var(--muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}
.gg-league-badge {
    background: rgba(0,232,122,0.08);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 18px;
    text-align: center;
}
.gg-league-badge .lg-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--pitch);
}
.gg-league-badge .lg-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 1.18rem;
    color: var(--text);
    letter-spacing: 0.5px;
}

/* ── SECTION LABEL ── */
.section-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 3.5px;
    text-transform: uppercase;
    color: var(--pitch);
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 20px; height: 2px;
    background: var(--pitch);
    border-radius: 2px;
}

/* ── MATCHUP STRIP ── */
.matchup-strip {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}
.team-name-display {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 1.45rem;
    letter-spacing: 0.5px;
    color: var(--text);
}
.team-name-display.home { color: var(--pitch); }
.team-name-display.away { color: #7AB4FF; }
.vs-pill {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 50%;
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700; font-size: 0.9rem;
    color: var(--muted);
}

/* ── PANEL / CARD ── */
.stat-panel {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 16px;
}
.stat-panel-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.70rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 14px;
}

/* ── INPUT OVERRIDES ── */
[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label {
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
}
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    color: var(--pitch) !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-color: var(--pitch) !important;
    box-shadow: 0 0 0 3px rgba(0,232,122,0.12) !important;
    outline: none !important;
}

/* ── BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #00C96B 0%, #00A855 100%) !important;
    color: #03100A !important;
    border: none !important;
    border-radius: 12px !important;
    height: 54px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.05rem !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    box-shadow: 0 4px 24px rgba(0,200,100,0.30) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(0,200,100,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── RESULT CARDS ── */
.result-win {
    background: linear-gradient(135deg, rgba(0,232,122,0.14) 0%, rgba(0,184,95,0.06) 100%);
    border: 1px solid rgba(0,232,122,0.40);
    border-radius: 16px;
    padding: 24px 28px;
    text-align: center;
    margin-bottom: 16px;
    animation: fade-in 0.5s ease;
}
.result-loss {
    background: linear-gradient(135deg, rgba(243,69,69,0.14) 0%, rgba(180,30,30,0.06) 100%);
    border: 1px solid rgba(243,69,69,0.40);
    border-radius: 16px;
    padding: 24px 28px;
    text-align: center;
    margin-bottom: 16px;
    animation: fade-in 0.5s ease;
}
@keyframes fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-verdict {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 1.9rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin: 0;
}
.result-verdict.win  { color: var(--pitch); }
.result-verdict.loss { color: var(--danger); }
.result-icon { font-size: 2.4rem; margin-bottom: 6px; }

/* ── PROB BAR ── */
.prob-wrap {
    background: var(--card);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px 22px;
    margin-bottom: 16px;
}
.prob-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 0.70rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}
.prob-value {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 900;
    font-size: 2.6rem;
    color: var(--pitch);
    line-height: 1;
    margin-bottom: 10px;
}
.prob-bar-track {
    background: rgba(255,255,255,0.07);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}
.prob-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.8s cubic-bezier(.22,.68,0,1.2);
}
.prob-bar-fill.win  { background: linear-gradient(90deg, #00C96B, #00FFB0); }
.prob-bar-fill.loss { background: linear-gradient(90deg, #F34545, #FF8080); }

/* ── STAT TILES ── */
.stat-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin-bottom: 16px;
}
.stat-tile {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 12px 14px;
    text-align: center;
}
.stat-tile .st-val {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: var(--text);
}
.stat-tile .st-lbl {
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 2px;
}

/* ── IDLE STATE ── */
.idle-state {
    background: var(--card);
    border: 1px dashed rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 48px 28px;
    text-align: center;
    color: var(--muted);
}
.idle-icon { font-size: 3rem; margin-bottom: 12px; opacity: 0.55; }
.idle-text {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 600;
    font-size: 1.1rem;
    letter-spacing: 1px;
    color: var(--muted);
}

/* ── DIVIDER ── */
.pitch-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 16px 0;
}

/* ── ALERTS ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-family: 'Barlow', sans-serif !important;
    font-size: 0.9rem !important;
}

/* ── PLOTLY BACKGROUND FIX ── */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--navy); }
::-webkit-scrollbar-thumb { background: rgba(0,232,122,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ================= MODEL =================
model = None
if os.path.exists("model.pkl"):
    try:
        with open("model.pkl", "rb") as f:
            model = pickle.load(f)
    except:
        model = None

# ================= HEADER =================
st.markdown("""
<div class="gg-header">
    <div class="gg-badge">⚽</div>
    <div class="gg-titles">
        <div class="gg-brand">Goal Goblin</div>
        <div class="gg-sub">AI Football Analytics &amp; Prediction Engine</div>
    </div>
    <div class="gg-league-badge">
        <div class="lg-label">League</div>
        <div class="lg-name">Premier League</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= LAYOUT =================
left, right = st.columns([1, 1], gap="large")

# ================= INPUT =================
with left:
    st.markdown('<div class="section-label">Match Setup</div>', unsafe_allow_html=True)

    col_h, col_a = st.columns(2)
    with col_h:
        home = st.text_input("Home Team", "Liverpool")
    with col_a:
        away = st.text_input("Away Team", "Arsenal")

    # Live matchup strip
    st.markdown(f"""
    <div class="matchup-strip">
        <span class="team-name-display home">{home or "Home"}</span>
        <span class="vs-pill">VS</span>
        <span class="team-name-display away">{away or "Away"}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Attacking Stats</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        xg = st.number_input("xG (Current Match)", 0.0, 5.0, 1.5, step=0.1)
    with col2:
        xg_rolling = st.number_input("xG (Rolling Avg)", 0.0, 5.0, 1.5, step=0.1)
    with col3:
        gf_rolling = st.number_input("Goals For (Rolling Avg)", 0.0, 5.0, 1.3, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Defensive Stats</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
    col4, col5, col6 = st.columns(3)
    with col4:
        xga = st.number_input("xGA (Current Match)", 0.0, 5.0, 1.2, step=0.1)
    with col5:
        xga_rolling = st.number_input("xGA (Rolling Avg)", 0.0, 5.0, 1.2, step=0.1)
    with col6:
        ga_rolling = st.number_input("Goals Against (Rolling Avg)", 0.0, 5.0, 1.1, step=0.1)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Other Stats</div>', unsafe_allow_html=True)
    st.markdown('<div class="stat-panel">', unsafe_allow_html=True)
    col7, col8 = st.columns(2)
    with col7:
        poss_rolling = st.number_input("Possession % (Rolling Avg)", 0,  100,  55,  step=1)
    with col8:
        target_rolling = st.number_input("Win Rate (Rolling Avg)", 0.0, 1.0, 0.6, step=0.05)
    st.markdown('</div>', unsafe_allow_html=True)

    run = st.button("⚡  Run Prediction")

# ================= OUTPUT =================
with right:
    st.markdown('<div class="section-label">Prediction Output</div>', unsafe_allow_html=True)

    if run:
        if home.strip() == away.strip():
            st.error("Home and Away teams must be different.")
            st.stop()

        # Features must match the exact order and names used in model training
        features = np.array([[xg, xga, xg_rolling, xga_rolling, gf_rolling, ga_rolling, poss_rolling, target_rolling]])

        if model is None:
            st.error("Model not loaded — ensure model.pkl is present.")
            st.stop()

        try:
            pred = model.predict(features)[0]
            prob = model.predict_proba(features)[0][1]
            pct  = round(prob * 100, 1)

            is_win      = pred == 1
            verdict_cls = "win" if is_win else "loss"
            verdict_txt = f"🏆 {home} WIN PREDICTED" if is_win else f"⚠ {home} NOT FAVOURITE"
            icon        = "🏆" if is_win else "⚠️"
            card_cls    = "result-win" if is_win else "result-loss"

            # Result card
            st.markdown(f"""
            <div class="{card_cls}">
                <div class="result-icon">{icon}</div>
                <p class="result-verdict {verdict_cls}">{verdict_txt}</p>
            </div>
            """, unsafe_allow_html=True)

            # Probability bar
            bar_cls = "win" if is_win else "loss"
            st.markdown(f"""
            <div class="prob-wrap">
                <div class="prob-label">Win Probability</div>
                <div class="prob-value">{pct}%</div>
                <div class="prob-bar-track">
                    <div class="prob-bar-fill {bar_cls}" style="width:{pct}%"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Stat summary tiles (using rolling features for display)
            st.markdown(f"""
            <div class="stat-grid">
                <div class="stat-tile">
                    <div class="st-val">{xg_rolling:.1f}</div>
                    <div class="st-lbl">xG Avg</div>
                </div>
                <div class="stat-tile">
                    <div class="st-val">{poss_rolling}%</div>
                    <div class="st-lbl">Possession Avg</div>
                </div>
                <div class="stat-tile">
                    <div class="st-val">{int(target_rolling*100)}%</div>
                    <div class="st-lbl">Win Rate Avg</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Gauge chart
            gauge_color = "#00C96B" if is_win else "#F34545"
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=pct,
                number={
                    'suffix': '%',
                    'font': {'color': gauge_color, 'size': 36, 'family': 'Barlow Condensed'}
                },
                title={
                    'text': "Confidence Score",
                    'font': {'color': '#7A90B0', 'size': 13, 'family': 'Barlow'}
                },
                gauge={
                    'axis': {
                        'range': [0, 100],
                        'tickfont': {'color': '#7A90B0', 'size': 11},
                        'tickwidth': 1,
                        'tickcolor': 'rgba(255,255,255,0.15)'
                    },
                    'bar': {'color': gauge_color, 'thickness': 0.22},
                    'bgcolor': 'rgba(255,255,255,0.04)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0,  40], 'color': 'rgba(243,69,69,0.10)'},
                        {'range': [40, 60], 'color': 'rgba(255,210,52,0.08)'},
                        {'range': [60,100], 'color': 'rgba(0,232,122,0.10)'},
                    ],
                    'threshold': {
                        'line': {'color': gauge_color, 'width': 3},
                        'thickness': 0.75,
                        'value': pct
                    }
                }
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Barlow Condensed'},
                height=240,
                margin=dict(t=30, b=10, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Prediction failed: {e}")

    else:
        st.markdown("""
        <div class="idle-state">
            <div class="idle-icon">📊</div>
            <div class="idle-text">Set up the match and hit Run Prediction</div>
        </div>
        """, unsafe_allow_html=True)
