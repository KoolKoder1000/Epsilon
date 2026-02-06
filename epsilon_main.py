import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh ---
st_autorefresh(interval=5000, key="epsilon_centered_cal")

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

# --- 4. CSS for Center Calendar & Shrunk Assignments ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    /* THE FIX: Force Date Picker / Popover to Screen Center */
    div[data-baseweb="popover"], div[data-testid="stDateInput"] + div {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 999999 !important;
    }

    .main-title { text-align: center; margin-top: -60px !important; font-size: 2.5rem; font-weight: 900; }

    /* Vertical Names */
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
        display: block !important;
        width: fit-content !important;
        min-width: 100px;
        margin-right: auto; /* Aligns card to the left of its column (closer to buttons) */
    }

    /* Small Squares */
    div.stButton > button {
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        border-radius: 4px !important;
        border: none !important;
        margin: 0 2px !important;
    }

    /* Trash Bin Styling */
    .trash-btn button {
        padding: 0 !important;
        font-size: 0.8rem !important;
        background: transparent !important;
        border: none !important;
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

# Unified Ratios: Making the details column (0) even smaller to reduce empty space
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
            # Layout: Trash icon and then the details card
            c_bin, c_text = st.columns([0.2, 0.8])
            with c_bin:
                st.markdown('<div class="trash-btn">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with c_text:
                # Date is now inside the card next to description
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

# Sidebar
with st.sidebar:
    st.title("")
    with st.form("new_task"):
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור")
        due = st.date_input("תאריך", value=datetime.today())
        if st.form_submit_button("הוסף", use_container_width=True):
            if desc:
                payload = {"subject": subj, "desc": desc, "due_date": str(due), **{c: 0 for c in STUDENTS.values()}}
                supabase.table("tasks").insert(payload).execute()
                st.rerun()
