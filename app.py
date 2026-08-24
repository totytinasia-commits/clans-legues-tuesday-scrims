# ==========================================
# --- SEZIONE: PERSONAL STATS ---
# ==========================================
elif page == "PERSONAL STATS":
    st.markdown("<div style='background-color: #0e1117; border: 2px solid #262730; border-radius: 12px; padding: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 👤 Personal Stats Dashboard")

    # Inizializzazione sicura delle variabili
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
                # Legge il valore corrente dalla cella D13
                d13_raw = target_ws.acell("D13").value
                if d13_raw is not None and str(d13_raw).strip() != "":
                    current_d13_val = str(d13_raw).strip()
                
                # Estrae la lista dei player dalla colonna C (C12:C60)
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

    # Selectbox unico per il Player configurato in D13
    player_index = 0
    if current_d13_val in extracted_players:
        player_index = extracted_players.index(current_d13_val)

    selected_d13_val = st.selectbox("Select Player", extracted_players, index=player_index, key="sb_player_d13")
    
    # Se il player selezionato cambia, aggiorna D13
    if str(selected_d13_val).strip().lower() != str(current_d13_val).strip().lower():
        try:
            scrivi_cella_per_gid(GID_PERSONAL_STATS, "D13", selected_d13_val)
        except Exception:
            pass
        st.rerun()

    with st.spinner("Updating data..."):
        time.sleep(0.2)

    st.markdown("---")

    def format_val(val, is_percentage=False, decimals=2):
        try:
            if val is None or str(val).strip() == "" or str(val).strip().lower() in ["nan", "none", "#n/a", "#valore!", "#ref!"]:
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
            # 1. Match Summary (Riga 16) - Utilizzo di get() con range esplicito
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

            # 2. Faster Banana (Riga 18)
            j18_l18 = target_ws.get("J18:L18")
            if j18_l18 and len(j18_l18) > 0 and len(j18_l18[0]) > 0:
                faster_banana_val = format_val(j18_l18[0][0])

            # 3. Deadliest Weapon (Righe 20-21)
            h20_l21 = target_ws.get("H20:L21")
            if h20_l21 and len(h20_l21) > 0:
                raw_w = h20_l21[0][0] if len(h20_l21[0]) > 0 else "-"
                deadliest_w = str(raw_w).strip() if raw_w and str(raw_w).strip().lower() not in ["nan", "none", ""] else "-"
                
                if len(h20_l21) > 1:
                    deadliest_d = format_val(h20_l21[1][3] if len(h20_l21[1]) > 3 else 0)
                    deadliest_a = format_val(h20_l21[1][4] if len(h20_l21[1]) > 4 else 0, is_percentage=True)

            # 4. Tabella Armi (F27:L67)
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
        st.markdown(f"<div class='stat-card'><div class='stat-label'>DEATH</div><div class='stat-value'>{summary_death}</div></div>", unsafe_allow_html=Tab := True) # Sostituito con sintassi pulita
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

    st.dataframe(df_weapons_final, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)
