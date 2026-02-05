import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh ---
st_autorefresh(interval=30000, key="epsilon_alignment_reversal")

# --- 3. Supabase ---
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

# --- 4. CSS for Strict Horizontal Centering ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    .main-title { text-align: center; margin-top: -60px !important; font-size: 2.5rem; font-weight: 900; }

    /* THE CORE FIX: Force all column content to share the same horizontal center */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: center !important;
        text-align: center !important;
        padding: 0 !important;
    }

    /* Student Name Header Styling */
    .student-header {
        font-size: 0.85rem !important;
        font-weight: 800;
        color: white;
        margin: 0 !important;
        padding: 0 !important;
        height: 40px; /* Fixed height for top alignment */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Button Styling */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 !important;
    }

    div.stButton > button {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0 !important;
    }

    /* Task Card Alignment (First Column) */
    .task-card {
        background-color: #1e1e1e;
        border-right: 3px solid #ffffff;
        padding: 6px 10px;
        border-radius: 4px;
        text-align: right;
        width: 100%;
    }

    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; }

    .row-divider { margin: 8px 0; border-bottom: 1px solid #333; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# Unified Ratios for BOTH header and data rows
grid_ratios = [1.8] + [0.4] * len(STUDENTS)

# --- 5. THE HEADER ROW ---
h_cols = st.columns(grid_ratios, gap="small")
with h_cols[0]:
    st.markdown("<div class='student-header' style='justify-content: flex-start !important; padding-right:15px;'>פרטי המטלה</div>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with h_cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider' style='margin-top:-5px;'></div>", unsafe_allow_html=True)

# --- 6. THE DATA ROWS ---
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        with r_cols[0]:
            c_bin, c_text = st.columns([0.15, 0.85])
            with c_bin:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:0.85rem; color:white;">{task.get('subject','')}</div>
                    <div style="font-size:0.75rem; color:#aaa;">{task.get('desc','')}</div>
                </div>""", unsafe_allow_html=True)

        for i, (name, db_col) in enumerate(STUDENTS.items()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button("", key=f"btn_{task['id']}_{db_col}"):
                    supabase.table("tasks").update({db_col: (val + 1) % 3}).eq("id", task['id']).execute()
                    st.rerun()
                    
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar for new tasks
with st.sidebar:
    st.title("ניהול")
    with st.form("new_task"):
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך", value=datetime.today())
        if st.form_submit_button("הוסף", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
