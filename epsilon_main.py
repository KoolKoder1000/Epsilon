import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh (30 Seconds) ---
st_autorefresh(interval=30000, key="minimal_refresh")

# --- 3. Supabase Connection ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

STUDENTS = {
    "יונתן": "yonatan", "יותם": "yotam", "מתאו": "mateo", 
    "עמית": "amit", "סול": "sol", "הדר": "hadar", 
    "שלמה": "shlomo", "תמר": "tamar", "אורי": "ori", "אופיר": "ofir"
}

# Labels are now used only for the 'hover' tooltip
STATUS_CONFIG = [
    {"label": "לא התחיל", "class": "m-red"},
    {"label": "בתהליך", "class": "m-orange"},
    {"label": "הוגש", "class": "m-green"}
]

# --- 4. Minimalist CSS ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', sans-serif !important;
        direction: rtl;
    }

    /* Vertical Center Calendar */
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important; left: 50% !important;
        transform: translate(-50%, -50%) !important;
    }

    .main-title { 
        text-align: center; margin-top: -50px !important; 
        font-size: 3rem; font-weight: 900; color: white; 
    }

    .student-header {
        font-size: 1.1rem !important;
        font-weight: 800; color: white;
        text-align: center !important;
        padding-top: 40px; padding-bottom: 5px;
    }

    /* Square Status Buttons */
    div.stButton > button {
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        border-radius: 4px !important;
        margin: auto !important;
        border: none !important;
    }

    /* Trash Button - Small & Subtle */
    .del-btn-container button {
        background-color: transparent !important;
        border: 1px solid #333 !important;
        color: #555 !important;
        font-size: 0.8rem !important;
        width: 28px !important;
        height: 28px !important;
    }
    .del-btn-container button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }

    /* Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; }

    .task-card {
        background-color: #1e1e1e;
        border-right: 4px solid #ffffff;
        padding: 8px 12px;
        border-radius: 4px;
        text-align: right;
        width: 100%;
    }
    
    .row-divider { margin: 8px 0; border-bottom: 1px solid #222; }
</style>
""", unsafe_allow_html=True)

# --- 5. Main UI ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# Header Row
grid_ratios = [3.5] + [1] * len(STUDENTS)
cols = st.columns(grid_ratios, gap="small")

with cols[0]:
    st.markdown("<p class='student-header' style='text-align:right !important; padding-right:15px;'>פרטי המטלה</p>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Task List
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        # Details & Delete
        with r_cols[0]:
            c_text, c_del = st.columns([0.9, 0.1])
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:1rem; color:white;">{task.get('subject','')}</div>
                    <div style="font-size:0.85rem; color:#bbb;">{task.get('desc','')}</div>
                    <div style="font-size:0.75rem; color:#777;">📅 {task.get('due_date','')}</div>
                </div>""", unsafe_allow_html=True)
            with c_del:
                st.markdown('<div class="del-btn-container">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # Color-Only Status Buttons
        for i, db_col in enumerate(STUDENTS.values()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                config = STATUS_CONFIG[val]
                st.markdown(f'<div class="{config["class"]}"></div>', unsafe_allow_html=True)
                # Empty string as label, config["label"] as hover tooltip
                if st.button("", key=f"btn_{task['id']}_{db_col}", help=config["label"]):
                    new_val = (val + 1) % 3
                    supabase.table("tasks").update({db_col: new_val}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.form("new_task", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        if st.form_submit_button("הוסף למערכת", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
