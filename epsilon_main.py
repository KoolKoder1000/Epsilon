import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh  # <-- New Import

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh Setup ---
# This will refresh the app every 30 seconds (30000 milliseconds)
# We give it a unique key to keep it stable.
st_autorefresh(interval=30000, key="datarefresh")

# --- 3. Supabase Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

STUDENTS = {
    "יונתן": "yonatan", "יותם": "yotam", "מתאו": "mateo", 
    "עמית": "amit", "סול": "sol", "הדר": "hadar", 
    "שלמה": "shlomo", "תמר": "tamar", "אורי": "ori", "אופיר": "ofir"
}

STATUS_CONFIG = [
    {"label": "לא התחיל", "class": "m-red"},
    {"label": "בתהליך", "class": "m-orange"},
    {"label": "הוגש", "class": "m-green"}
]

# --- 4. Refined CSS (Calibri & Centering) ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }

    .main-title { 
        text-align: center; 
        margin-top: -40px !important; 
        font-size: 3.5rem; 
        font-weight: 900; 
        color: white; 
    }

    .student-header {
        font-size: 1.3rem !important;
        font-weight: 800;
        color: white;
        text-align: center !important;
        padding-top: 45px; 
        padding-bottom: 10px;
        width: 100%;
    }

    div.stButton > button {
        width: 100% !important;
        font-size: 0.7rem !important;
        font-weight: 700 !important;
        height: 36px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        border-radius: 6px !important;
    }

    .del-zone {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-left: 20px; 
    }
    .del-zone button {
        background-color: #262730 !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        width: 34px !important;
        min-width: 34px !important;
    }

    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; color: white !important; }

    .task-card {
        background-color: #1e1e1e;
        border-right: 5px solid #ffffff;
        padding: 12px;
        border-radius: 4px;
        width: 100%;
        text-align: right;
    }
    .row-divider { margin: 15px 0; border-bottom: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- 5. Main UI ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    # We use .select("*") to get fresh data on every refresh
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# Header Row
grid_ratios = [2.2] + [1] * len(STUDENTS)
cols = st.columns(grid_ratios, gap="small")

with cols[0]:
    st.markdown("<p class='student-header' style='text-align:right !important;'>פרטי המטלה</p>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Task Data
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        with r_cols[0]:
            c_text, c_del = st.columns([0.8, 0.2])
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:1rem;">{task.get('subject','')}</div>
                    <div style="font-size:0.8rem; color:#ccc;">{task.get('desc','')}</div>
                    <div style="font-size:0.75rem; color:#888;">📅 {task.get('due_date','')}</div>
                </div>""", unsafe_allow_html=True)
            with c_del:
                st.markdown('<div class="del-zone">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        for i, db_col in enumerate(STUDENTS.values()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button(STATUS_CONFIG[val]["label"], key=f"btn_{task['id']}_{db_col}"):
                    new_val = (val + 1) % 3
                    supabase.table("tasks").update({db_col: new_val}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar Form
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    if st.button("🔄 רענן נתונים כעת", use_container_width=True): st.rerun()
    st.markdown("---")
    with st.form("new_task", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך", value=datetime.today())
        if st.form_submit_button("הוסף", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
