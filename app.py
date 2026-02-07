import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="IPL Analytics Workbench", layout="wide")

# --------------------------------------------------
# TEAM COLORS
# --------------------------------------------------
team_colors = {
    "Chennai Super Kings": "#F9CD05",
    "Mumbai Indians": "#004BA0",
    "Royal Challengers Bengaluru": "#D71920",
    "Kolkata Knight Riders": "#3A225D",
    "Delhi Capitals": "#17479E",
    "Rajasthan Royals": "#EA1A85",
    "Sunrisers Hyderabad": "#F26522",
    "Punjab Kings": "#D71920",
    "Lucknow Super Giants": "#0057A3",
    "Gujarat Titans": "#0A1D56",
    "Gujarat Lions": "#F15A29",
    "Rising Pune Supergiants": "#6F2DA8",
    "Kochi Tuskers Kerala": "#2E8B57",
    "Deccan Chargers": "#1E90FF"
}

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("IPL.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

df = load_data()

# --------------------------------------------------
# CLEANING
# --------------------------------------------------
df["season"] = df["season"].astype(str)

team_map = {
    "Kings XI Punjab": "Punjab Kings",
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Rising Pune Supergiant": "Rising Pune Supergiants"
}

df["batting_team"] = df["batting_team"].replace(team_map).str.strip()
df["bowling_team"] = df["bowling_team"].replace(team_map).str.strip()

# --------------------------------------------------
# PHASE
# --------------------------------------------------
def phase(over):
    if over <= 6:
        return "Powerplay"
    elif over <= 15:
        return "Middle Overs"
    else:
        return "Death Overs"

df["phase"] = df["over"].apply(phase)

# --------------------------------------------------
# SIDEBAR CONTROLS
# --------------------------------------------------
st.sidebar.header("🎛 Controls")

mode = st.sidebar.radio(
    "Select Mode",
    ["📊 Team Analytics", "⚔️ Batter vs Bowler Matchup"]
)

# --------------------------------------------------
# ================= MODE 1 =========================
# TEAM ANALYTICS
# --------------------------------------------------
if mode == "📊 Team Analytics":

    season = st.sidebar.selectbox(
        "Season",
        sorted(df["season"].unique())
    )

    team = st.sidebar.selectbox(
        "Team",
        sorted(df["batting_team"].unique())
    )

    theme = team_colors.get(team, "#222")

    # Theme
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme}18;
            transition: background-color 0.4s ease;
        }}

        h1, h2, h3 {{
            color: {theme};
        }}

        div[data-testid="metric-container"] {{
            background-color: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.15);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    batting_df = df[(df["season"] == season) & (df["batting_team"] == team)]
    bowling_df = df[(df["season"] == season) & (df["bowling_team"] == team)]

    st.title(f"{team} · IPL Analytics ({season})")

    tab1, tab2, tab3 = st.tabs(
        ["📊 Team Overview", "🧑‍🏏 Batter Lab", "🎯 Bowler Lab"]
    )

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matches", batting_df["match_id"].nunique())
        c2.metric("Runs Scored", int(batting_df["runs_total"].sum()))
        c3.metric("Wickets Taken", int(bowling_df["bowler_wicket"].sum()))
        c4.metric("Batters Used", batting_df["batter"].nunique())

        phase_runs = (
            batting_df.groupby("phase")["runs_total"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            phase_runs,
            x="phase",
            y="runs_total",
            color="phase",
            title="Team Runs by Phase"
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        batter = st.selectbox(
            "Select Batter",
            sorted(batting_df["batter"].dropna().unique())
        )

        bdf = batting_df[batting_df["batter"] == batter]

        r1, r2, r3 = st.columns(3)
        r1.metric("Runs", bdf["runs_batter"].sum())
        r2.metric("Balls", bdf["valid_ball"].sum())
        r3.metric(
            "Strike Rate",
            round((bdf["runs_batter"].sum() / bdf["valid_ball"].sum()) * 100, 2)
        )

        phase_pie = (
            bdf.groupby("phase")["runs_batter"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            phase_pie,
            names="phase",
            values="runs_batter",
            hole=0.45,
            title=f"{batter} — Scoring by Phase"
        )

        fig.update_layout(transition_duration=600)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        bowler = st.selectbox(
            "Select Bowler",
            sorted(bowling_df["bowler"].dropna().unique())
        )

        bdf = bowling_df[bowling_df["bowler"] == bowler]

        o1, o2, o3, o4 = st.columns(4)
        o1.metric("Overs", round(bdf["valid_ball"].sum() / 6, 1))
        o2.metric("Runs", bdf["runs_bowler"].sum())
        o3.metric("Wickets", bdf["bowler_wicket"].sum())
        o4.metric(
            "Economy",
            round(bdf["runs_bowler"].sum() / (bdf["valid_ball"].sum() / 6), 2)
        )

# --------------------------------------------------
# ================= MODE 2 =========================
# GLOBAL BATTER vs BOWLER MATCHUP (ALL YEARS)
# --------------------------------------------------
else:
    st.title("⚔️ Batter vs Bowler Matchup — All Seasons")

    c1, c2 = st.columns(2)

    with c1:
        batter = st.selectbox(
            "Select Batter",
            sorted(df["batter"].dropna().unique())
        )

    with c2:
        bowler = st.selectbox(
            "Select Bowler",
            sorted(df["bowler"].dropna().unique())
        )

    matchup = df[(df["batter"] == batter) & (df["bowler"] == bowler)]

    if matchup.empty:
        st.warning("No matchup data available.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Runs", matchup["runs_batter"].sum())
        m2.metric("Balls", matchup["valid_ball"].sum())
        m3.metric("Wickets", matchup["bowler_wicket"].sum())
        m4.metric(
            "Strike Rate",
            round((matchup["runs_batter"].sum() / matchup["valid_ball"].sum()) * 100, 2)
        )

        phase_breakdown = (
            matchup.groupby("phase")["runs_batter"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            phase_breakdown,
            x="phase",
            y="runs_batter",
            color="phase",
            title="Matchup Runs by Phase (All Seasons)"
        )

        st.plotly_chart(fig, use_container_width=True)

