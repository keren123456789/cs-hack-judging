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
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        border-radius: 8px;
        border: none;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        font-weight: bold;
        font-size: 18px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FFA500;
        color: white;
    }
    
    [data-testid="stForm"] {
        border: 2px solid #333333;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
    }
    
    h1 { text-align: center; color: #FFD700; }
    h3 { text-align: center; color: #bbbbbb; }
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
# פה אנחנו מגדירים שנתונים יישמרו בזיכרון ולא ישגעו את השרת של גוגל
# =====================================================================

@st.cache_data(ttl=60)
def get_finalists():
    """מושך את הקבוצות לגמר רק פעם בדקה"""
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
    """מושך ציונים קיימים ושומר בזיכרון כדי למנוע קריסות 429"""
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        return sheet.get_all_values()
    except:
        return []

# =====================================================================

# --- הוספת הלוגו הרשמי ---
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
with logo_col2:
    try:
        st.image("pic.jpeg", use_container_width=True) 
    except:
        pass

st.markdown("### שלב הגמר")

# משיכת הנתונים בטוחה לחלוטין עכשיו!
finalist_teams = get_finalists()
all_rows = get_all_scores()

# יצירת כותרות בפעם הראשונה בלבד
if not all_rows:
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        headers = ["שופט", "קבוצה", "Real Problem", "Solution", "Scalability", "Quality of POC", "Creativity", "Presentation", "Personal Grade", "ציון משוקלל סופי"]
        sheet.append_row(headers)
        get_all_scores.clear() # מנקה את הזיכרון כדי שהכותרות יטענו
    except:
        pass

if "saved_judge_name" not in st.session_state:
    st.session_state.saved_judge_name = ""

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    judge_name = st.text_input("שם השופט :", value=st.session_state.saved_judge_name).strip()
with col2:
    team_num = st.selectbox(" בחר קבוצה לדירוג:", finalist_teams)

def find_existing_rating(judge, team, rows):
    if not judge or len(rows) <= 1:
        return None
    for idx, row in enumerate(rows[1:], start=2):
        if len(row) >= 2:
            if row[0].strip().lower() == judge.lower() and str(row[1]).strip() == str(team):
                return idx, row
    return None

existing_record = find_existing_rating(judge_name, team_num, all_rows)

if existing_record:
    idx, row = existing_record
    st.warning(f" נמצא דירוג קודם שלך לקבוצה {team_num}! שינוי הציונים יעדכן את השורה הקיימת בטבלה.")
    try:
        val_real = int(float(row[2]))
        val_soln = int(float(row[3]))
        val_scale = int(float(row[4]))
        val_poc = int(float(row[5]))
        val_creat = int(float(row[6]))
        val_pres = int(float(row[7]))
        val_pers = int(float(row[8]))
    except:
        val_real = val_soln = val_scale = val_poc = val_creat = val_pres = val_pers = 5
else:
    val_real = val_soln = val_scale = val_poc = val_creat = val_pres = val_pers = 5

st.markdown("---")
st.markdown("<h4 style='text-align: center;'> קריטריוני שיפוט (1-10)</h4>", unsafe_allow_html=True)
st.write("") 

with st.form("judging_form"):
    real_problem = st.slider(" Real Problem (15%)", 1, 10, val_real)
    solution = st.slider(" Does the solution solve it? (20%)", 1, 10, val_soln)
    scalability = st.slider(" Scalability (10%)", 1, 10, val_scale)
    quality_poc = st.slider(" Quality of POC (20%)", 1, 10, val_poc)
    creativity = st.slider(" Creativity & Novelty (10%)", 1, 10, val_creat)
    presentation = st.slider(" Presentation (10%)", 1, 10, val_pres)
    personal = st.slider(" Personal Grade (15%)", 1, 10, val_pers)

    st.write("") 
    submitted = st.form_submit_button(" שלח ציון למערכת", use_container_width=True)

    if submitted:
        if not judge_name:
            st.error("❗ חובה להזין שם שופט לפני השמירה.")
        else:
            st.session_state.saved_judge_name = judge_name
            
            total_score = (real_problem * 0.15) + (solution * 0.20) + \
                          (scalability * 0.10) + (quality_poc * 0.20) + \
                          (creativity * 0.10) + (presentation * 0.10) + \
                          (personal * 0.15)
            
            new_row = [
                judge_name, 
                str(team_num), 
                real_problem, 
                solution, 
                scalability, 
                quality_poc, 
                creativity, 
                presentation, 
                personal, 
                round(total_score, 2)
            ]
            
            # חיבור טרי לגוגל רק ברגע השמירה הקריטי
            client = get_sheets_client()
            sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
            
            if existing_record:
                idx, _ = existing_record
                try:
                    sheet.update(f"A{idx}:J{idx}", [new_row])
                except:
                    sheet.update([new_row], f"A{idx}:J{idx}")
                st.success(f"✅ הדירוג של קבוצה {team_num} עודכן בהצלחה במערכת!")
            else:
                sheet.append_row(new_row)
                st.success(f"✅ הציון לקבוצה {team_num} נשמר בהצלחה במערכת!")
            
            # מחיקת הזיכרון לאחר שמירה כדי שהמערכת תתעדכן מיד עבור כולם
            get_all_scores.clear()
            
            time.sleep(1.5)
            st.rerun()