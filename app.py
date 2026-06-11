import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import time
import json

# --- הגדרות תצוגה ---
st.set_page_config(page_title="CS HACK Judging", page_icon="🏆", layout="centered")

# --- הזרקת CSS לעיצוב אישי ---
st.markdown("""
<style>
    /* --- ייבוא הפונט Rubik מגוגל פונטס --- */
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@300;400;500;700;800&display=swap');

    /* החלת הפונט על כל רכיבי האפליקציה */
    html, body, [class*="css"], [class*="st-"] {
        font-family: 'Rubik', sans-serif !important;
    }

    /* 1. הפיכת כל האפליקציה לימין-שמאל (RTL) באופן מוחלט */
    .stApp, [data-testid="stAppViewBlockContainer"] {
        direction: rtl !important;
    }
    
    /* 2. החזרת הסליידרים (שהם באנגלית) למצב משמאל לימין כדי ש-1 יישאר בשמאל ו-10 בימין */
    [data-testid="stSlider"] {
        direction: ltr !important;
    }
    
    /* =========================================
       SLIDER CUSTOMIZATIONS (Clean Inner Fill)
       ========================================= */
       
    div[data-testid="stSlider"] label p {
        font-weight: 700 !important; 
        font-size: 15px !important;
    }

    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #ff4b4b !important; 
        border: 3px solid #ffffff !important; 
        box-shadow: 0px 2px 5px rgba(0,0,0,0.5) !important;
    }

    /* הסתרת התפריט והקרדיט של סטרימליט למטה */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* =========================================
       עיצוב כפתור השליחה (בולט וזוהר למצב כהה)
       ========================================= */
    .stButton>button {
        background-color: #FFD700 !important; 
        color: #000000 !important; 
        border-radius: 12px !important; 
        border: 2px solid #FFC107 !important; 
        box-shadow: 0px 0px 15px rgba(255, 215, 0, 0.3) !important; 
        font-weight: 800 !important; 
        font-size: 22px !important; 
        padding: 15px 30px !important; 
        margin-top: 20px !important; 
        transition: all 0.3s ease-in-out !important; 
        font-family: 'Rubik', sans-serif !important; 
    }
    
    .stButton>button:hover {
        background-color: #FFA500 !important; 
        color: white !important; 
        transform: scale(1.03) !important; 
        box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.6) !important; 
    }
    
    [data-testid="stForm"] {
        border: 2px solid #333333;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
    }
    
    h1 { text-align: center; color: #FFD700; font-family: 'Rubik', sans-serif !important; }
    h3 { text-align: center; color: #bbbbbb; font-family: 'Rubik', sans-serif !important; }
    h4 { text-align: center; color: #bbbbbb; font-family: 'Rubik', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

SHEET_ID = "16rGiFhGTWEah_8ZH36QHFoj1nS_x9hcP0xxKBjkk530"

@st.cache_resource
def get_sheets_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds_dict = json.loads(st.secrets["gcp_credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    except:
        creds = Credentials.from_service_account_file("secrets.json", scopes=scopes)
    return gspread.authorize(creds)

# =====================================================================
# מנגנוני הגנה: Cache Data
# =====================================================================

@st.cache_data(ttl=60)
def get_finalists():
    try:
        client = get_sheets_client()
        workbook = client.open_by_key(SHEET_ID)
        teams_sheet = workbook.worksheet("Finalists")
        teams_data = teams_sheet.col_values(1)[1:]
        live_teams = [int(x.strip()) for x in teams_data if x.strip().isdigit()]
        return live_teams if live_teams else [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    except:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

@st.cache_data(ttl=15)
def get_all_scores():
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        return sheet.get_all_values()
    except:
        return []

@st.cache_data(ttl=60)
def get_team_descriptions():
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).worksheet("Finalists")
        return sheet.get_all_values()
    except:
        return []

# =====================================================================

logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
with logo_col2:
    try:
        st.image("pic.jpeg", use_container_width=True) 
    except:
        pass

st.markdown("### שלב הגמר")

finalist_teams = get_finalists()
all_rows = get_all_scores()

if not all_rows:
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        headers = ["שופט", "קבוצה", "Real Problem", "Solution", "Quality of POC", "Creativity", "Presentation", "Personal Impression", "ציון משוקלל סופי"]
        sheet.append_row(headers)
        get_all_scores.clear() 
    except:
        pass

if "saved_judge_name" not in st.session_state:
    st.session_state.saved_judge_name = ""

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    judge_name = st.text_input("שם השופט:", value=st.session_state.saved_judge_name).strip()

with col2:
    team_num = st.selectbox("בחר קבוצה לדירוג:", finalist_teams)

def find_existing_rating(judge, team, rows):
    if not judge or len(rows) <= 1:
        return None
    for idx, row in enumerate(rows[1:], start=2):
        if len(row) >= 2:
            if row[0].strip().lower() == judge.lower() and str(row[1]).strip() == str(team):
                return idx, row
    return None

existing_record = find_existing_rating(judge_name, team_num, all_rows)

team_desc = ""
for row in get_team_descriptions()[1:]:
    if len(row) >= 2 and str(row[0]).strip() == str(team_num):
        team_desc = f"- {row[1].strip()}"
        break

if existing_record:
    idx, row = existing_record
    st.warning(f"דירגת קבוצה זו בהצלחה - קבוצה {team_num} {team_desc}\n\nשליחת הטופס שוב תעדכן את הציון הקיים")
    try:
        val_real = int(float(row[2]))
        val_soln = int(float(row[3]))
        val_poc = int(float(row[4]))
        val_creat = int(float(row[5]))
        val_pres = int(float(row[6]))
        val_pers = int(float(row[7]))
    except:
        val_real = val_soln = val_poc = val_creat = val_pres = val_pers = 5
else:
    val_real = val_soln = val_poc = val_creat = val_pres = val_pers = 5

st.markdown("---")
st.markdown("<h4 style='text-align: center;'> קריטריוני שיפוט (1-10)</h4>", unsafe_allow_html=True)
st.write("") 

with st.form("judging_form"):
    real_problem = st.slider(" Real Problem (20%)", 1, 10, val_real)
    solution = st.slider(" Does the solution solve it? (20%)", 1, 10, val_soln)
    quality_poc = st.slider(" Quality of POC (20%)", 1, 10, val_poc)
    creativity = st.slider(" Creativity & Novelty (15%)", 1, 10, val_creat)
    presentation = st.slider(" Presentation (10%)", 1, 10, val_pres)
    personal = st.slider(" Personal Impression (15%)", 1, 10, val_pers)

    st.write("") 
    submitted = st.form_submit_button("שלח ציון למערכת", use_container_width=True)

    if submitted:
        if not judge_name:
            st.error("!! חובה להזין שם שופט לפני השמירה !!")
        else:
            st.session_state.saved_judge_name = judge_name
            
            total_score = (real_problem * 0.20) + (solution * 0.20) + \
                          (quality_poc * 0.20) + (creativity * 0.15) + \
                          (presentation * 0.10) + (personal * 0.15)
            
            new_row = [
                judge_name, 
                str(team_num), 
                real_problem, 
                solution, 
                quality_poc, 
                creativity, 
                presentation, 
                personal, 
                round(total_score, 2)
            ]
            
            # =================================================================
            # מנגנון RETRY שקט וסבלני (Exponential Backoff)
            # =================================================================
            max_retries = 10
            success = False
            wait_time = 1.5
            
            with st.spinner("שומר את הציון במערכת... ⏳"):
                for attempt in range(max_retries):
                    try:
                        client = get_sheets_client()
                        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
                        
                        if existing_record:
                            idx, _ = existing_record
                            try:
                                sheet.update(f"A{idx}:I{idx}", [new_row])
                            except:
                                sheet.update([new_row], f"A{idx}:I{idx}")
                            st.success(f"הדירוג של קבוצה {team_num} עודכן בהצלחה במערכת!")
                        else:
                            sheet.append_row(new_row)
                            st.success(f"הציון לקבוצה {team_num} נשמר בהצלחה במערכת!")
                        
                        success = True
                        break # ברגע שהצלחנו, יוצאים מלולאת הניסיונות בשקט
                        
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(wait_time) 
                            wait_time += 1 # הגדלת זמן ההמתנה בין ניסיון לניסיון כדי לתת לשרת אוויר לנשימה
                        else:
                            # הודעה עדינה שלא חושפת תקלות טכניות ומנחה לא לרענן
                            st.warning(" החיבור מעט איטי. הציונים שבחרת שמורים – פשוט לחץ שוב על 'שלח ציון למערכת'.")
            
            if success:
                get_all_scores.clear()
                time.sleep(1.5)
                st.rerun()
