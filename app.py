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
       
    /* Make the slider labels bold and slightly larger */
    div[data-testid="stSlider"] label p {
        font-weight: 700 !important; 
        font-size: 15px !important;
    }

    /* The thumb (the circle you drag) */
    div[data-baseweb="slider"] div[role="slider"] {
        background-color: #ff4b4b !important; /* אדום חי וברור */
        border: 3px solid #ffffff !important; /* מסגרת לבנה להבלטה */
        box-shadow: 0px 2px 5px rgba(0,0,0,0.5) !important;
    }
    /* ========================================= */

    /* הסתרת התפריט והקרדיט של סטרימליט למטה */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* =========================================
       עיצוב כפתור השליחה (בולט וזוהר למצב כהה)
       ========================================= */
    .stButton>button {
        background-color: #FFD700 !important; /* צבע זהב חזק */
        color: #000000 !important; /* טקסט שחור קונטרסטי */
        border-radius: 12px !important; /* פינות עגולות ורכות יותר */
        border: 2px solid #FFC107 !important; /* מסגרת שמדגישה את הגבולות */
        box-shadow: 0px 0px 15px rgba(255, 215, 0, 0.3) !important; /* הילה (גלואו) סביב הכפתור */
        font-weight: 800 !important; /* טקסט שמן מאוד */
        font-size: 22px !important; /* פונט גדול יותר משמעותית */
        padding: 15px 30px !important; /* הגדלת שטח הכפתור למגע בטלפון */
        margin-top: 20px !important; /* ריווח נשימה מהסליידר האחרון */
        transition: all 0.3s ease-in-out !important; /* אנימציה חלקה */
        font-family: 'Rubik', sans-serif !important; 
    }
    
    /* אפקט כשהעכבר מרחף (או בלחיצה בטלפון) */
    .stButton>button:hover {
        background-color: #FFA500 !important; /* מתחלף לזהב-כתום */
        color: white !important; /* טקסט הופך ללבן */
        transform: scale(1.03) !important; /* הכפתור "קופץ" מעט החוצה */
        box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.6) !important; /* ההילה מתחזקת */
    }
    /* ========================================= */
    
    /* עיצוב הרקע של הטופס (צל ופינות מעוגלות) */
    [data-testid="stForm"] {
        border: 2px solid #333333;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.1);
    }
    
    /* עיצוב כותרות האפליקציה */
    h1 { 
        text-align: center; 
        color: #FFD700; 
        font-family: 'Rubik', sans-serif !important;
    }
    h3 { 
        text-align: center; 
        color: #bbbbbb; 
        font-family: 'Rubik', sans-serif !important;
    }
    h4 { 
        text-align: center; 
        color: #bbbbbb; 
        font-family: 'Rubik', sans-serif !important;
    }
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
    """שולף את תיאורי הקבוצות ושומר בזיכרון למניעת קריסות"""
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).worksheet("Finalists")
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

finalist_teams = get_finalists()
all_rows = get_all_scores()

if not all_rows:
    try:
        client = get_sheets_client()
        sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
        headers = ["שופט", "קבוצה", "Real Problem", "Solution", "Quality of POC", "Creativity", "Presentation", "Personal Grade", "ציון משוקלל סופי"]
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

# --- שליפת התיאור מהזיכרון החכם ---
team_desc = ""
for row in get_team_descriptions()[1:]:
    if len(row) >= 2 and str(row[0]).strip() == str(team_num):
        team_desc = f"- {row[1].strip()}"
        break

if existing_record:
    idx, row = existing_record
    
    # הודעת האזהרה הצהובה עם התיאור וירידת השורה
    st.warning(f"דירגת קבוצה זו בהצלחה - קבוצה {team_num} {team_desc}\n\nשליחת הטופס שוב תעדכן את הציון הקיים")
    
    try:
        # התאמת המיקומים לאחר הסרת Scalability
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
    personal = st.slider(" Personal Grade (15%)", 1, 10, val_pers)

    st.write("") 
    submitted = st.form_submit_button("שלח ציון למערכת", use_container_width=True)

    if submitted:
        if not judge_name:
            st.error("!! חובה להזין שם שופט לפני השמירה !!")
        else:
            st.session_state.saved_judge_name = judge_name
            
            # חישוב משוקלל עם האחוזים החדשים
            total_score = (real_problem * 0.20) + (solution * 0.20) + \
                          (quality_poc * 0.20) + (creativity * 0.15) + \
                          (presentation * 0.10) + (personal * 0.15)
            
            # בניית שורת הנתונים החדשה (9 עמודות)
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
            
            # חיבור טרי לגוגל רק ברגע השמירה הקריטי
            client = get_sheets_client()
            sheet = client.open_by_key(SHEET_ID).get_worksheet(0)
            
            if existing_record:
                idx, _ = existing_record
                try:
                    # עדכון שורה קיימת לפי הטווח החדש (A עד I במקום J)
                    sheet.update(f"A{idx}:I{idx}", [new_row])
                except:
                    sheet.update([new_row], f"A{idx}:I{idx}")
                # חזרה להודעה הקצרה והמקורית
                st.success(f"הדירוג של קבוצה {team_num} עודכן בהצלחה במערכת!")
            else:
                sheet.append_row(new_row)
                st.success(f"הציון לקבוצה {team_num} נשמר בהצלחה במערכת!")
            
            # מחיקת הזיכרון לאחר שמירה כדי שהמערכת תתעדכן מיד עבור כולם
            get_all_scores.clear()
            
            time.sleep(1.5)
            st.rerun()
            
