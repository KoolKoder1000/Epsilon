import streamlit as st
from datetime import datetime
from supabase import create_client

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Supabase Connection ---
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

# --- 3. Final CSS Polishing ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* Sidebar RTL & Popover Centering */
    [data-testid="stSidebar"] { left: 0 !important; right: auto !important; }
    [data-testid="stSidebarCollapsedControl"] { left: 20px !important; right: auto !important; }
    
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 9999 !important;
    }

    /* Column alignment */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;    
        justify-content: center !important;
        padding: 0px 1px !important;
    }
    
    /* Title & Header Spacing */
    .main-title { 
        text-align: center; 
        margin-top: -30px !important; 
        margin-bottom: 40px !important; /* Added space below title */
        font-size: 3.5rem; 
        font-weight: 800; 
        color: white; 
    }

    .header-text {
        font-size: 1.1rem !important; /* Increased font for names */
        font-weight: 800 !important;
        color: white !important;
        text-align: center;
        padding-top: 20px; /* Space above names */
        padding-bottom: 10px;
    }

    /* Button Styling */
    div.stButton > button {
        width: 100% !important;
        min-width: 60px !important; 
        font-size: 0.75rem !important;
        padding: 0px 2px !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        height: 38px !important;
    }

    /* Delete Button Styling */
    .delete-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 5px;
    }
    .delete-container button {
        background-color: #262730 !important;
        border: 1px solid #444 !important;
        color: #888 !important;
        height: 35px !important;
        width: 35px !important;
        min-width: 35px !important;
    }
    .delete-container button:hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }
    
    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; color: white !important; }

    /* Task Card Styling */
    .task-container { 
        background-color: #1e1e1e; 
        border-right: 4px solid #ffffff; 
        padding: 8px 12px; 
        border-radius: 4px; 
        width: 100%; 
    }
    .task-subject { color: white !important; font-weight: 800; font-size: 0.95rem; }
    .row-divider { margin: 12px 0; border-bottom: 1px solid #333; width: 100%; }
    .m-red, .m-orange, .m-green { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    if st.button("🔄 רענן נתונים", use_container_width=True):
        st.rerun()
    st.markdown("---")
    with st.form("new_task_form", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור קצר")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        if st.form_submit_button("הוסף למערכת", use_container_width=True):
            if desc:
                new_task = {"subject": subj, "desc": desc, "due_date": str(due), **{col: 0 for col in STUDENTS.values()}}
                try:
                    supabase.table("tasks").insert(new_task).execute()
                    st.rerun()
                except Exception as e:
                    st.error(f"שגיאה: {e}")

# --- 5. Main Content ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

try:
    response = supabase.table("tasks").select("*").order("due_date").execute()
    tasks = response.data
except Exception as e:
    st.error(f"שגיאה בטעינה: {e}")
    tasks = []

if not tasks:
    st.info("אין כרגע מטלות במערכת.")
else:
    # Header Row - Reduced details column to 3.0 to minimize empty space
    grid_ratios = [3.0] + [1] * len(STUDENTS)
    h_cols = st.columns(grid_ratios, gap="small")
    with h_cols[0]: st.markdown("<p class='header-text'>פרטי המטלה</p>", unsafe_allow_html=True)
    for i, name in enumerate(STUDENTS.keys()):
        with h_cols[i+1]: st.markdown(f"<div class='header-text'>{name}</div>", unsafe_allow_html=True)

    st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    # Task Rows
    for task in tasks:
        row_cols = st.columns(grid_ratios, gap="small")
        with row_cols[0]:
            main_card, del_area = st.columns([0.88, 0.12])
            with main_card:
                st.markdown(f"""<div class="task-container">
                    <div class="task-subject">{task.get('subject', '')}</div>
                    <div style="color:#eee; font-size:0.8rem;">{task.get('desc', '')}</div>
                    <div style="color:#888; font-size:0.7rem;">📅 {task.get('due_date', '')}</div>
                </div>""", unsafe_allow_html=True)
            with del_area:
                st.markdown('<div class="delete-container">', unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        for i, db_col in enumerate(STUDENTS.values()):
            with row_cols[i + 1]:
                val = task.get(db_col, 0)
                st.markdown(f'<div class="{STATUS_CONFIG[val]["class"]}"></div>', unsafe_allow_html=True)
                if st.button(STATUS_CONFIG[val]["label"], key=f"btn_{task['id']}_{db_col}"):
                    supabase.table("tasks").update({db_col: (val + 1) % 3}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)
