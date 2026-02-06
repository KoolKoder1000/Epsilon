import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh ---
st_autorefresh(interval=3000, key="epsilon_sidebar_final")

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

# --- 4. CSS: The "Double Flip" Strategy ---
st.markdown("""
<style>
    /* 1. Global Reset: Set to LTR to force sidebar to the LEFT */
    html, body, [data-testid="stAppViewContainer"] {
        direction: ltr !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
    }

    /* 2. Content Reset: Force the main data area back to RTL for Hebrew */
    [data-testid="stMain"], [data-testid="column"], .main-title, .task-card {
        direction: rtl !important;
    }

    /* Force Date Picker to Screen Center */
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 999999 !important;
        direction: rtl !important;
    }

    .main-title { text-align: center; margin-top: -60px !important; font-size: 2.5rem; font-weight: 900; }

    /* Vertical Student Names */
    .student-header {
        font-size: 0.8rem !important;
        font-weight: 800;
        color: white;
        height: 85px;
        display: flex;
        align-items: center;
        justify-content: center;
        writing-mode: vertical-rl;
        transform: rotate(180deg);
        white-space: nowrap;
    }

    /* Shrink the column containers */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; 
        justify-content: center !important;
        padding: 0 !important;
    }

    /* Task Card: Maximum Horizontal Shrink */
    .task-card {
        background-color: #1e1e1e;
        border-right: 3px solid #ffffff;
        padding: 4px 8px;
        border-radius: 4px;
        text-align: right;
        display: inline-block !important; /* Shinks to text width */
        width: auto !important;
        min-width: 110px;
    }

    /* Status Buttons (Small Squares) */
    div.stButton > button {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        border-radius: 4px !important;
        border: none !important;
        margin: 0 2px !important;
    }

    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; }

    .row-divider { margin: 6px 0; border-bottom: 1px solid #333; width: 100%; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# Assignment detail is index 0, students follow.
grid_ratios = [1.0] + [0.3] * len(STUDENTS)

# --- 5. THE HEADER ROW ---
h_cols = st.columns(grid_ratios, gap="small")
with h_cols[0]:
    st.markdown("<div style='font-weight:800; color:white; padding-top:55px; text-align:right;'>פרטי המטלה</div>", unsafe_allow_html=True)

for i, name in enumerate(STUDENTS.keys()):
    with h_cols[i+1]:
        st.markdown(f"<div class='student-header'>{name}</div>", unsafe_allow_html=True)

st.markdown("<div class='row-divider' style='margin-top:-5px;'></div>", unsafe_allow_html=True)

# --- 6. THE DATA ROWS ---
if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        with r_cols[0]:
            c_bin, c_text = st.columns([0.2, 0.8])
            with c_bin:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
            with c_text:
                st.markdown(f"""<div class="task-card">
                    <div style="font-weight:800; font-size:0.8rem; color:white;">{task.get('subject','')}</div>
                    <div style="font-size:0.7rem; color:#aaa;">{task.get('desc','')}</div>
                    <div style="font-size:0.6rem; color:#00d4ff; font-weight:bold;">📅 {task.get('due_date','')}</div>
                </div>""", unsafe_allow_html=True)

        for i, (name, db_col) in enumerate(STUDENTS.items()):
            with r_cols[i+1]:
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button("", key=f"btn_{task['id']}_{db_col}"):
                    supabase.table("tasks").update({db_col: (val + 1) % 3}).eq("id", task['id']).execute()
                    st.rerun()
                    
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# --- 7. Sidebar (Should now be on the left) ---
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
