import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh (30 Seconds) ---
st_autorefresh(interval=30000, key="epsilon_aligned_final")

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

# --- 4. CSS for Perfect Alignment ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    /* Force Calendar to Center */
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 9999 !important;
    }

    .main-title { 
        text-align: center; margin-top: -60px !important; 
        font-size: 3rem; font-weight: 900; color: white; 
    }

    /* Heading Alignment */
    .student-header {
        font-size: 0.9rem !important;
        font-weight: 800; 
        color: white;
        text-align: center !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        white-space: nowrap !important;
        height: 50px; /* Fixed height for header area */
        margin: 0 !important;
    }

    /* Force all Column Content to Center Inline */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; /* Centers buttons horizontally */
        justify-content: flex-start !important;
        padding: 0 !important;
    }

    /* Status Buttons Styling */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    div.stButton > button {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 0 !important;
        margin-top: 5px !important; /* Visual spacing between rows */
    }

    /* Trash Bin Area */
    .trash-zone {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-right: 10px;
    }
    .trash-zone button {
        background-color: transparent !important;
        border: 1px solid #333 !important;
        color: #555 !important;
        width: 22px !important;
        height: 22px !important;
    }

    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; }

    /* Task Card */
    .task-card {
        background-color: #1e1e1e;
        border-right: 3px solid #ffffff;
        padding: 4px 8px;
        border-radius: 4px;
        text-align: right;
        width: 100%;
    }
    .row-divider { margin: 8px 0; border-bottom: 1px solid #222; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 5. Main UI ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# grid_ratios: Keep details slim, students equal
grid_ratios = [1.5] + [0.5] * len(STUDENTS)
cols = st.columns(grid_ratios, gap="small")

with cols[0]:
    st.markdown("<p class='student-header' style='justify-content: flex-start !important; padding-right:15px;'>פרטי המטלה</p>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Task Rendering
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        with r_cols[0]:
            c_bin, c_text = st.columns([0.2, 0.8])
            with c_bin:
                st.markdown('<div class="trash-zone">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:0.8rem; color:white;">{task.get('subject','')}</div>
                    <div style="font-size:0.7rem; color:#aaa;">{task.get('desc','')}</div>
                    <div style="font-size:0.6rem; color:#444;">📅 {task.get('due_date','')}</div>
                </div>""", unsafe_allow_html=True)

        for i, db_col in enumerate(STUDENTS.values()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                # This invisible div carries the class that triggers the CSS color
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button("", key=f"btn_{task['id']}_{db_col}", help=STATUS_CONFIG[val]["label"]):
                    supabase.table("tasks").update({db_col: (val + 1) % 3}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    with st.form("new_task_form", clear_on_submit=True):
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        if st.form_submit_button("הוסף", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
