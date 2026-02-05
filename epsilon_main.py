import streamlit as st
from datetime import datetime
from supabase import create_client
from streamlit_autorefresh import st_autorefresh

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Auto-Refresh (30 Seconds) ---
st_autorefresh(interval=30000, key="epsilon_final_centered_names")

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

# --- 4. CSS for Centering & Compact Layout ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp, button, p, div {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
    }

    /* Force Calendar to the Center */
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

    /* THE FIX: Perfectly Centered Student Headers */
    .student-header {
        font-size: 0.9rem !important;
        font-weight: 800; color: white;
        text-align: center !important; /* Horizontal center */
        display: flex !important;
        justify-content: center !important; /* Flex center */
        white-space: nowrap !important;
        padding-top: 35px;
        width: 100%;
    }

    /* Center the columns themselves */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        padding-left: 1px !important;
        padding-right: 1px !important;
    }

    /* Keep Task Details Aligned Right */
    [data-testid="column"]:first-child {
        align-items: flex-start !important;
    }

    /* Small Square Buttons */
    div.stButton > button {
        width: 24px !important;
        height: 24px !important;
        min-width: 24px !important;
        border-radius: 4px !important;
        margin: auto !important;
        border: none !important;
    }

    /* Trash Bin Area */
    .trash-zone {
        padding-left: 8px !important; 
        display: flex;
        justify-content: center;
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

    /* Minimized Task Card */
    .task-card {
        background-color: #1e1e1e;
        border-right: 3px solid #ffffff;
        padding: 4px 8px;
        border-radius: 4px;
        text-align: right;
        width: 100%;
    }
    .row-divider { margin: 6px 0; border-bottom: 1px solid #222; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 5. Main UI ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    tasks = supabase.table("tasks").select("*").order("due_date").execute().data
except:
    tasks = []

# grid_ratios: 1.5 for assignments makes it minimally wide
grid_ratios = [1.5] + [0.5] * len(STUDENTS)
cols = st.columns(grid_ratios, gap="small")

with cols[0]:
    # Custom alignment for the first header to stay right-aligned
    st.markdown("<p class='student-header' style='justify-content: flex-start !important; padding-right:5px;'>פרטי המטלה</p>", unsafe_allow_html=True)

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
