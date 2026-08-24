import streamlit as st
import pandas as pd
import time
import gspread
import base64
import os

# 1. Page Configuration
st.set_page_config(page_title="CL Tuesday Scrims", layout="centered")

# --- CONFIGURAZIONE GOOGLE SHEETS & CREDENZIALI ---
SHEET_ID = '1_dKU_GF7gCvaulCoSwL0pTluw7o8MBJe9Pefiqtq3Zk'
GID_PERSONAL_STATS = '327527248'

def ottieni_credenziali():
    """Recupera le credenziali da st.secrets per gspread"""
    try:
        if "gcp_service_account" in st.secrets:
            from google.oauth2.service_account import Credentials
            scope = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds_dict = dict(st.secrets["gcp_service_account"])
            return Credentials.from_service_account_info(creds_dict, scopes=scope)
    except Exception as e:
        st.error(f"Errore configurazione credenziali: {e}")
    return None

def scrivi_cella_per_gid(gid, cell_address, value):
    """Scrive un valore in una cella specifica cercando il foglio tramite GID"""
    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
            ws = next((w for w in sheet.worksheets() if str(w.id).strip() == str(gid).strip()), None)
            if ws:
                ws.update_acell(cell_address, value)
    except Exception as e:
        st.error(f"Errore durante la scrittura su Google Sheets: {e}")

# 2. CSS Styling
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    h1, h2, h3, p { color: #fff !important; text-align: center; }
    
    /* Navigation buttons custom style */
    div.stButton > button {
        width: 100%;
        background-color: #161616;
        color: white;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px 10px;
        font-weight: bold;
        font-size: 0.85rem;
        margin-bottom: 5px;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #222;
        border-color: #2ecc71;
        color: #2ecc71;
    }

    /* Standard Table Style */
    .custom-table {
        width: 100%;
        max-width: 600px;
        margin: 0 auto 20px auto;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333;
        font-family: sans-serif;
    }
    .custom-table th {
        background-color: #222;
        color: #fff;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid #444;
        font-size: 16px;
    }
    .custom-table td {
        background-color: #111;
        color: #ddd;
        padding: 10px 14px;
        border-bottom: 1px solid #222;
        text-align: center;
    }
    .custom-table td:first-child {
        text-align: left; 
    }
    .custom-table tr:last-child td {
        border-bottom: none;
    }

    /* Leaderboard Table Style */
    .ranking-table {
        width: 100%;
        max-width: 450px;
        margin: 0 auto 20px auto;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #333;
        font-family: sans-serif;
    }
    .ranking-table th {
        background-color: #222;
        color: #fff;
        padding: 10px 14px;
        text-align: center;
        border-bottom: 1px solid #444;
        font-size: 16px;
    }
    .ranking-table td {
        background-color: #111;
        color: #ddd;
        padding: 10px 14px;
        border-bottom: 1px solid #222;
        text-align: center;
    }
    .ranking-table td:first-child {
        text-align: left; 
    }
    .ranking-table tr:last-child td {
        border-bottom: none;
    }
    .ranking-table tbody tr:first-child td {
        color: #2ecc71 !important;
        font-weight: bold !important;
    }

    /* Stat Cards */
    .stat-card {
        background-color: #111;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        margin-bottom: 10px;
    }
    .stat-label {
        color: #888;
        font-size: 0.75rem;
        font-weight: bold;
        margin-bottom: 4px;
    }
    .stat-value {
        color: #fff;
        font-size: 1.1rem;
        font-weight: bold;
    }

    /* Logo dimensionato esattamente quanto un titolo H1 grande */
    .main-logo-container img {
        display: block;
        margin: 0 auto;
        max-height: 2.5rem;
        width: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Initialize session state for pages
if "page" not in st.session_state:
    st.session_state.page = "Leaderboard"

# 4. Main Page Logo & Centered Title
def get_logo_html():
    for ext in ["png", "jpg", "jpeg", "webp"]:
        path = f"logo.{ext}"
        if os.path.exists(path):
            try:
                with open(path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode()
                    return f'<img src="data:image/{ext};base64,{encoded}" style="height: 3.5rem; width: auto; vertical-align: middle; border-radius: 6px;">'
            except Exception:
                pass
    return ""

col_l1, col_l2, col_l3 = st.columns([0.05, 3.9, 0.05])
with col_l2:
    logo_html = get_logo_html()
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 15px; width: 100%;">
            {logo_html}
            <h1 style='color: #fff; font-size: 2.8rem; margin: 0; line-height: 1; white-space: nowrap;'>CL TUESDAY SCRIMS</h1>
        </div>
    """, unsafe_allow_html=True)

# 5. Navigation Buttons
if st.button("🏆 Leaderboard", use_container_width=True):
    st.session_state.page = "Leaderboard"
if st.button("📊 System Score", use_container_width=True):
    st.session_state.page = "System Score"
if st.button("⚔️ Scrims 1", use_container_width=True):
    st.session_state.page = "Scrims 1"
if st.button("⚔️ Scrims 2", use_container_width=True):
    st.session_state.page = "Scrims 2"
if st.button("⚔️ Scrims 3", use_container_width=True):
    st.session_state.page = "Scrims 3"
if st.button("👤 Player Results", use_container_width=True):
    st.session_state.page = "Risultati Giocatore"
if st.button("🎯 Personal Stats", use_container_width=True):
    st.session_state.page = "PERSONAL STATS"

st.write("---")

# 6. Data loading function
@st.cache_data(ttl=600)
def load_data(gid):
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}'
    return pd.read_csv(url)

# Standard table renderer
def render_custom_table(df_sub, headers):
    html = f'<table class="custom-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df_sub.iterrows():
        html += '<tr>'
        for val in row:
            v_str = "" if pd.isna(val) or str(val).lower() == "nan" else str(val)
            html += f'<td>{v_str}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# Leaderboard table renderer
def render_ranking_table(df_sub, headers):
    html = f'<table class="ranking-table"><thead><tr>'
    for h in headers:
        html += f'<th>{h}</th>'
    html += '</tr></thead><tbody>'
    for _, row in df_sub.iterrows():
        html += '<tr>'
        for val in row:
            v_str = "" if pd.isna(val) or str(val).lower() == "nan" else str(val)
            html += f'<td>{v_str}</td>'
        html += '</tr>'
    html += '</tbody></table>'
    return html

# General function to render Scrims tables
def render_scrims_tables(gid, scrim_subtitle, team_coords, game_coords_list, overall_coords):
    st.markdown(f"<h1 style='text-align: center;'>⚔️ Scrims Tuesday - {scrim_subtitle}</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df = load_data(gid)
    
    try:
        t_start, t_end, t_col = team_coords
        teams = df.iloc[t_start:t_end, t_col].dropna().astype(str).reset_index(drop=True)
        teams = teams[teams.str.strip() != ""]
    except Exception:
        teams = pd.Series(["Team"] * 4)

    num_rows = len(teams)

    for idx, (r_start, r_end, c_start, c_end) in enumerate(game_coords_list, start=1):
        st.markdown(f"<h3 style='text-align: center;'>Game {idx}</h3>", unsafe_allow_html=True)
        try:
            val_df = df.iloc[r_start:r_start+num_rows, c_start:c_end].copy().fillna("")
            val_df.columns = ["Position", "Kills", "DMG", "Revive"]
            
            combined_df = pd.DataFrame({"Team": teams})
            for i, col in enumerate(val_df.columns):
                combined_df[col] = val_df.iloc[:, i].values

            st.markdown(render_custom_table(combined_df, ["Team", "Position", "Kills", "DMG", "Revive"]), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading Game {idx} data: {e}")

    st.markdown("<h3 style='text-align: center;'>Overall Stats</h3>", unsafe_allow_html=True)
    try:
        t8_r_start, _, t8_c_start, t8_c_end = overall_coords
        val_df = df.iloc[t8_r_start:t8_r_start+num_rows, t8_c_start:t8_c_end].copy().fillna("")
        
        combined_df = pd.DataFrame()
        if val_df.shape[1] > 0:
            combined_df["Team"] = val_df.iloc[:, 0].values
            cols_t8 = ["Revive", "Kills", "DMG"]
            for i, col in enumerate(cols_t8, start=1):
                if i < val_df.shape[1]:
                    col_data = val_df.iloc[:, i].values
                    if len(col_data) < num_rows:
                        col_data = list(col_data) + [""] * (num_rows - len(col_data))
                    combined_df[col] = col_data[:num_rows]
                else:
                    combined_df[col] = [""] * num_rows
            
        st.markdown(render_custom_table(combined_df, ["Team", "Revive", "Kills", "DMG"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Overall data: {e}")

# 7. Page Logic
page = st.session_state.page

if page == "Leaderboard":
    st.markdown("<h1 style='text-align: center;'>🏆 Leaderboard</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df = load_data('316677537')
    
    st.markdown("<h3 style='text-align: center;'>Lobby 1</h3>", unsafe_allow_html=True)
    try:
        lobby1 = df.iloc[12:17, [2, 3]].copy()
        lobby1.columns = ["Team", "Points"]
        lobby1["Points"] = pd.to_numeric(lobby1["Points"], errors='coerce').fillna(0).astype(int)
        st.markdown(render_ranking_table(lobby1, ["Team", "Points"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error Lobby 1 Data: {e}")
        
    st.markdown("<h3 style='text-align: center;'>Lobby 2</h3>", unsafe_allow_html=True)
    try:
        lobby2 = df.iloc[12:17, [5, 6]].copy()
        lobby2.columns = ["Team", "Points"]
        lobby2["Points"] = pd.to_numeric(lobby2["Points"], errors='coerce').fillna(0).astype(int)
        st.markdown(render_ranking_table(lobby2, ["Team", "Points"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error Lobby 2 Data: {e}")

    st.markdown("<h3 style='text-align: center;'>Lobby 3</h3>", unsafe_allow_html=True)
    try:
        lobby3 = df.iloc[12:17, [8, 9]].copy()
        lobby3.columns = ["Team", "Points"]
        lobby3["Points"] = pd.to_numeric(lobby3["Points"], errors='coerce').fillna(0).astype(int)
        st.markdown(render_ranking_table(lobby3, ["Team", "Points"]), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error Lobby 3 Data: {e}")

elif page == "System Score":
    st.markdown("<h1 style='text-align: center;'>📊 System Score</h1>", unsafe_allow_html=True)
    st.write("---")
    
    scoring_html = """
    <table class="custom-table">
        <thead><tr><th colspan="4">SCORE SYSTEM</th></tr></thead>
        <tbody>
            <tr><td></td><td><b>Placement</b></td><td><b>Kills</b></td><td><b>Damage</b></td></tr>
            <tr><td><b>1st</b></td><td>7</td><td>6</td><td>6</td></tr>
            <tr><td><b>2nd</b></td><td>5</td><td>4</td><td>4</td></tr>
            <tr><td><b>3rd</b></td><td>3</td><td>2</td><td>2</td></tr>
            <tr><td><b>4th</b></td><td>1</td><td>0</td><td>0</td></tr>
        </tbody>
    </table>
    """
    st.markdown(scoring_html, unsafe_allow_html=True)

elif page == "Scrims 1":
    s1_teams = (8, 12, 4) 
    s1_games = [
        (8, 12, 5, 9),    
        (8, 12, 10, 14),    
        (8, 12, 15, 19),    
        (8, 12, 20, 24),    
        (8, 12, 25, 29)     
    ]
    s1_overall = (8, 12, 37, 41)  
    render_scrims_tables('547827980', "Scrims 1", s1_teams, s1_games, s1_overall)

elif page == "Scrims 2":
    s2_teams = (17, 21, 4) 
    s2_games = [
        (17, 21, 5, 9),    
        (17, 21, 10, 14),    
        (17, 21, 15, 19),    
        (17, 21, 20, 24),    
        (17, 21, 25, 29)     
    ]
    s2_overall = (17, 21, 37, 41)  
    render_scrims_tables('547827980', "Scrims 2", s2_teams, s2_games, s2_overall)

elif page == "Scrims 3":
    s3_teams = (26, 30, 4) 
    s3_games = [
        (26, 30, 5, 9),    
        (26, 30, 10, 14),    
        (26, 30, 15, 19),    
        (26, 30, 20, 24),    
        (26, 30, 25, 29)     
    ]
    s3_overall = (26, 30, 37, 41)  
    render_scrims_tables('547827980', "Scrims 3", s3_teams, s3_games, s3_overall)

elif page == "Risultati Giocatore":
    st.markdown("<h1 style='text-align: center;'>👤 Player Results</h1>", unsafe_allow_html=True)
    st.write("---")
    
    df_player = load_data('1376346730')
    
    def get_lobby_table(df, start_row, end_row):
        try:
            sub_df = df.iloc[start_row:end_row, 9:15].copy()
            sub_df = sub_df.dropna(how='all').reset_index(drop=True)
            return sub_df
        except Exception as e:
            st.error(f"Errore nel caricamento della tabella: {e}")
            return pd.DataFrame()

    headers_player = ["Player", "Kill", "DMG", "MVP", "DHAT", "ACC%"]
    
    st.markdown("<h3 style='text-align: center;'>Lobby 1</h3>", unsafe_allow_html=True)
    try:
        lobby1_df = get_lobby_table(df_player, 0, 20)
        if not lobby1_df.empty:
            lobby1_df.columns = headers_player[:len(lobby1_df.columns)]
            st.markdown(render_custom_table(lobby1_df, list(lobby1_df.columns)), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Lobby 1 Player Data: {e}")
        
    st.markdown("<h3 style='text-align: center;'>Lobby 2</h3>", unsafe_allow_html=True)
    try:
        lobby2_df = get_lobby_table(df_player, 23, 44)
        if not lobby2_df.empty:
            lobby2_df.columns = headers_player[:len(lobby2_df.columns)]
            st.markdown(render_custom_table(lobby2_df, list(lobby2_df.columns)), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Lobby 2 Player Data: {e}")

    st.markdown("<h3 style='text-align: center;'>Lobby 3</h3>", unsafe_allow_html=True)
    try:
        lobby3_df = get_lobby_table(df_player, 45, 66)
        if not lobby3_df.empty:
            lobby3_df.columns = headers_player[:len(lobby3_df.columns)]
            st.markdown(render_custom_table(lobby3_df, list(lobby3_df.columns)), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading Lobby 3 Player Data: {e}")

# ==========================================
# --- SEZIONE: PERSONAL STATS ---
# ==========================================
elif page == "PERSONAL STATS":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 👤 Personal Stats Dashboard")

    target_ws = None
    current_d13_val = ""
    extracted_players = []

    try:
        creds = ottieni_credenziali()
        if creds:
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
            target_ws = next((ws for ws in sheet.worksheets() if str(ws.id).strip() == str(GID_PERSONAL_STATS).strip()), None)
            
            if target_ws:
                d13_raw = target_ws.acell("D13").value
                if d13_raw is not None and str(d13_raw).strip() != "":
                    current_d13_val = str(d13_raw).strip()
                
                col_c_values = target_ws.get("C12:C60")
                for row in col_c_values:
                    if row and len(row) > 0:
                        p = str(row[0]).strip()
                        if p and p.lower() not in ["nan", "none", ""]:
                            extracted_players.append(p)
                extracted_players = list(dict.fromkeys(extracted_players))
    except Exception as e:
        st.warning(f"Error reading initial Personal Stats sheet: {e}")

    if not extracted_players:
        extracted_players = ["No players available"]

    player_index = 0
    if current_d13_val in extracted_players:
        player_index = extracted_players.index(current_d13_val)

    selected_d13_val = st.selectbox("Select Player", extracted_players, index=player_index, key="sb_player_d13")
    
    if str(selected_d13_val).strip().lower() != str(current_d13_val).strip().lower():
        scrivi_cella_per_gid(GID_PERSONAL_STATS, "D13", selected_d13_val)
        st.rerun()

    with st.spinner("Updating data..."):
        time.sleep(0.2)

    st.markdown("---")

    def format_val(val, is_percentage=False, decimals=2):
        try:
            if val is None or str(val).strip() == "" or str(val).strip().lower() in ["nan", "none", "#n/a", "#valore!"]:
                return "0.00%" if is_percentage else "0"
            clean_val = str(val).replace("%", "").strip().replace(",", ".")
            num = float(clean_val)
            factor = 10 ** decimals
            truncated = int(num * factor) / factor
            if is_percentage:
                return f"{truncated:.{decimals}f}%"
            elif truncated.is_integer():
                return str(int(truncated))
            else:
                return f"{truncated:.{decimals}f}"
        except Exception:
            return str(val) if val is not None and str(val).strip() != "" else ("0.00%" if is_percentage else "0")

    summary_fired, summary_hit, summary_acc, summary_kill, summary_dmg, summary_mvp, summary_death = "0", "0", "0.00%", "0", "0", "0", "0"
    faster_banana_val = "-"
    deadliest_w, deadliest_d, deadliest_a = "-", "0", "0.00%"
    weapon_rows_data = []

    try:
        if target_ws:
            f16_l16 = target_ws.get("F16:L16")
            if f16_l16 and len(f16_l16) > 0:
                row_vals = f16_l16[0]
                summary_fired = format_val(row_vals[0] if len(row_vals) > 0 else 0)
                summary_hit = format_val(row_vals[1] if len(row_vals) > 1 else 0)
                summary_acc = format_val(row_vals[2] if len(row_vals) > 2 else 0, is_percentage=True)
                summary_kill = format_val(row_vals[3] if len(row_vals) > 3 else 0)
                summary_dmg = format_val(row_vals[4] if len(row_vals) > 4 else 0)
                summary_mvp = format_val(row_vals[5] if len(row_vals) > 5 else 0)
                summary_death = format_val(row_vals[6] if len(row_vals) > 6 else 0)

            j18_l18 = target_ws.get("J18:L18")
            if j18_l18 and len(j18_l18) > 0 and len(j18_l18[0]) > 0:
                faster_banana_val = format_val(j18_l18[0][0])

            h20_l21 = target_ws.get("H20:L21")
            if h20_l21 and len(h20_l21) > 0:
                raw_w = h20_l21[0][0] if len(h20_l21[0]) > 0 else "-"
                deadliest_w = str(raw_w).strip() if raw_w and str(raw_w).strip().lower() not in ["nan", "none", ""] else "-"
                
                if len(h20_l21) > 1:
                    deadliest_d = format_val(h20_l21[1][3] if len(h20_l21[1]) > 3 else 0)
                    deadliest_a = format_val(h20_l21[1][4] if len(h20_l21[1]) > 4 else 0, is_percentage=True)

            weapons_raw = target_ws.get("F27:L67")
            if weapons_raw:
                for r_data in weapons_raw:
                    if r_data and len(r_data) > 0:
                        w_name = str(r_data[0]).strip()
                        if w_name and w_name.upper() not in ["NAN", "NONE", ""]:
                            weapon_rows_data.append({
                                "WEAPON": w_name,
                                "TOT SHOTS": format_val(r_data[1] if len(r_data) > 1 else 0, is_percentage=False),
                                "SHOT HIT": format_val(r_data[2] if len(r_data) > 2 else 0, is_percentage=False),
                                "ACC%": format_val(r_data[3] if len(r_data) > 3 else 0, is_percentage=True),
                                "DMG": format_val(r_data[4] if len(r_data) > 4 else 0, is_percentage=False),
                                "HEADSHOT": format_val(r_data[5] if len(r_data) > 5 else 0, is_percentage=False),
                                "MAX DISTANCE": format_val(r_data[6] if len(r_data) > 6 else 0, is_percentage=False)
                            })
    except Exception as e:
        st.warning(f"Error reading dashboard data: {e}")

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>MATCH SUMMARY</h4>", unsafe_allow_html=True)
    c_grid1, c_grid2, c_grid3 = st.columns(3)
    
    with c_grid1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FIRED</div><div class='stat-value'>{summary_fired}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACCURACY</div><div class='stat-value'>{summary_acc}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{summary_dmg}</div></div>", unsafe_allow_html=True)
    with c_grid2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>SHOT HIT</div><div class='stat-value'>{summary_hit}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>KILL</div><div class='stat-value'>{summary_kill}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>MVP</div><div class='stat-value'>{summary_mvp}</div></div>", unsafe_allow_html=True)
    with c_grid3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DEATH</div><div class='stat-value'>{summary_death}</div></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-card'><div class='stat-label'>FASTER BANANA</div><div class='stat-value'>{faster_banana_val}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; font-size: 1rem;'>DEADLIEST WEAPON</h4>", unsafe_allow_html=True)
    dw_col1, dw_col2, dw_col3 = st.columns(3)
    with dw_col1:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>WEAPON</div><div class='stat-value' style='font-size: 0.85rem;'>{deadliest_w}</div></div>", unsafe_allow_html=True)
    with dw_col2:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DMG</div><div class='stat-value'>{deadliest_d}</div></div>", unsafe_allow_html=True)
    with dw_col3:
        st.markdown(f"<div class='stat-card'><div class='stat-label'>ACC%</div><div class='stat-value'>{deadliest_a}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<h4 style='color: #93c5fd; text-align: center;'>WEAPON PERFORMANCE</h4>", unsafe_allow_html=True)
    
    if weapon_rows_data:
        df_weapons_final = pd.DataFrame(weapon_rows_data)
    else:
        df_weapons_final = pd.DataFrame(columns=["WEAPON", "TOT SHOTS", "SHOT HIT", "ACC%", "DMG", "HEADSHOT", "MAX DISTANCE"])

    st.dataframe(df_weapons_final, width="stretch", hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)