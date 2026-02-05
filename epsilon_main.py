import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh (30 Seconds) ---
st_autorefresh(interval=5000, key="epsilon_compact_fixed")

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

# --- 4. CSS for Minimal Width & Padding ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    .main-title { 
        text-align: center; margin-top: -60px !important; 
        font-size: 3rem; font-weight: 900; color: white; 
    }

    .student-header {
        font-size: 0.95rem !important;
        font-weight: 800; color: white;
        text-align: center !important;
        white-space: nowrap !important; /* Prevents names from breaking */
        padding-top: 35px;
    }

    /* Small Square Buttons */
    div.stButton > button {
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        border-radius: 6px !important;
        margin: auto !important;
        border: none !important;
    }

    /* Trash Bin Area - Maximizing space */
    .trash-zone {
        padding-left: 10px !important; 
        display: flex;
        justify-content: center;
    }
    .trash-zone button {
        background-color: transparent !important;
        border: 1px solid #333 !important;
        color: #555 !important;
        width: 24px !important;
        height: 24px !important;
    }

    /* Column Gaps */
    [data-testid="column"] {
        padding-left: 1px !important;
        padding-right: 1px !important;
    }

    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; }

    /* Task Card - Minimally Small */
    .task-card {
        background-color: #1e1e1e;
        border-right: 3px solid #ffffff;
        padding: 4px 8px; /* Reduced padding */
        border-radius: 4px;
        text-align: right;
        min-width: 140px; /* Ensures it doesn't disappear completely */
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

# Header Row: Detail column (1.5) vs Student blocks (0.5 each)
grid_ratios = [1.5] + [0.5] * len(STUDENTS)
cols = st.columns(grid_ratios, gap="small")

with cols[0]:
    st.markdown("<p class='student-header' style='text-align:right !important; padding-right:5px;'>פרטי המטלה</p>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Task Data
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        # Details & Trash
        with r_cols[0]:
            c_bin, c_text = st.columns([0.2, 0.8]) # Flipped to keep bin near the border
            with c_bin:
                st.markdown('<div class="trash-zone">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:0.85rem; color:white;">{task.get('subject','')}</div>
                    <div style="font-size:0.75rem; color:#aaa;">{task.get('desc','')}</div>
                    <div style="font-size:0.65rem; color:#555;">📅 {task.get('due_date','')}</div>
                </div>""", unsafe_allow_html=True)

        # Status Grid
        for i, db_col in enumerate(STUDENTS.values()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button("", key=f"btn_{task['id']}_{db_col}", help=STATUS_CONFIG[val]["label"]):
                    supabase.table("tasks").update({db_col: (val + 1) % 3}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    st.markdown("---")
    with st.form("new_task_form", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        if st.form_submit_button("הוסף", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
