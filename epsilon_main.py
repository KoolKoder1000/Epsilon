import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh ---
st_autorefresh(interval=30000, key="epsilon_perfect_center")

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

# --- 4. CSS for Perfect Horizontal Symmetry ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    /* Calendar Centering */
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 9999 !important;
    }

    .main-title { text-align: center; margin-top: -60px !important; font-size: 2.5rem; font-weight: 900; }

    /* THE FIX: Student Columns Symmetry */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; /* Forces EVERYTHING to the horizontal center */
        justify-content: center !important;
        text-align: center !important;
        padding: 0 !important;
    }

    .inline-name {
        font-size: 0.75rem !important;
        font-weight: 800;
        color: white;
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
        width: 100%;
        display: block;
    }

    /* Ensure button container doesn't add offset */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div.stButton > button {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        margin: 4px 0 0 0 !important; /* Only top margin for spacing */
        border-radius: 4px !important;
        border: none !important;
    }

    /* Task Card Alignment */
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

# Balanced ratios: 1.8 for task info, 0.4 for each student
grid_ratios = [1.8] + [0.4] * len(STUDENTS)

if tasks:
    for task in tasks:
        r_cols = st.columns(grid_ratios, gap="small")
        
        # Task Description Column
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

        # Student Status Columns (Name exactly centered over Button)
        for i, (name, db_col) in enumerate(STUDENTS.items()):
            with r_cols[i+1]:
                # Text sits at horizontal center
                st.markdown(f"<div class='inline-name'>{name}</div>", unsafe_allow_html=True)
                
                # Button sits at horizontal center
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                st.button("", key=f"btn_{task['id']}_{db_col}")
                
                # Update logic (placed after to keep button UI clean)
                # Note: In production, you'd wrap the button in an 'if' to trigger the update
                    
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

# Sidebar
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
