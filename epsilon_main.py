import streamlit as st
from datetime import datetime

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. CSS Refinement ---
st.markdown("""
<style>
    /* 1) Change Font and RTL Direction */
    html, body, [class*="css"], .stApp {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
        text-align: right;
    }

    /* --- SIDEBAR LEFT-SIDE FIX --- */
    /* This forces the sidebar container to stay on the left despite RTL direction */
    [data-testid="stSidebar"] {
        left: 0 !important;
        right: auto !important;
    }

    /* Ensures the 'collapsed' sidebar button also stays on the left */
    [data-testid="stSidebarCollapsedControl"] {
        left: 20px !important;
        right: auto !important;
    }

    /* Fixes alignment of widgets inside the sidebar for Hebrew */
    [data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stTextInput, [data-testid="stSidebar"] .stDateInput {
        direction: rtl !important;
        text-align: right !important;
    }
    /* ----------------------------- */

    /* FIX: Calendar Repositioning */
    div[data-baseweb="popover"] {
        position: fixed !important;
        top: 50% !important;
        left: 50% !important;
        transform: translate(-50%, -50%) !important;
        z-index: 999999 !important;
        direction: ltr !important;
    }
    div[data-baseweb="calendar"] { direction: ltr !important; }

    /* Absolute Button & Header Centering */
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;    
        justify-content: center !important;
    }

    /* 2) FIX: Centering the Rubbish Button Vertically */
    [data-testid="column"] div[data-testid="stVerticalBlock"] > div:has(button[key*="del_"]) {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    /* Target the internal container Streamlit uses for widgets */
    [data-testid="column"] [data-testid="stVerticalBlock"] {
        align-items: center !important;
        width: 100% !important;
    }

    /* Headers (White & Centered) */
    .task-header-custom {
        color: white !important;
        font-size: 1.1rem;
        font-weight: 700;
        text-align: center !important;
        width: 100%;
        display: block;
        margin-bottom: 10px;
    }

    .student-label {
        font-size: 1rem !important;
        font-weight: 700;
        color: white;
        text-align: center !important;
        width: 100%;
        margin-bottom: 12px;
    }

    /* Status Buttons Styling */
    div.stButton > button {
        width: 100% !important;
        max-width: 110px !important;
        margin: 0 auto !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 700 !important;
        height: 45px !important;
        white-space: nowrap !important;
        display: block !important;
    }

    /* Main Title */
    .main-title {
        text-align: center;
        margin-top: -40px !important; 
        margin-bottom: 20px !important;
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
    }

    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; color: white !important; }

    /* 3) Task Card - Changed border and subject to White */
    .task-container {
        background-color: #1e1e1e;
        border-right: 4px solid white !important;
        padding: 10px 15px;
        border-radius: 4px;
        width: 100%;
        text-align: right;
    }
    .task-subject { color: white !important; font-weight: 800; }
    .task-desc { color: #eee; }
    .task-date { color: #888; font-size: 0.8rem; }

    /* Divider and Reset */
    .row-divider {
        margin: 15px 0;
        border-bottom: 1px solid #333;
        width: 100%;
    }

    div.stButton > button[kind="primary"] {
        background-color: #d1d1d1 !important;
        color: #1e1e1e !important;
        max-width: none !important;
    }

    .m-red, .m-orange, .m-green { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. Logic ---
STUDENTS = ["יונתן", "יותם", "מתאו", "עמית", "סול", "הדר", "שלמה", "תמר", "אורי", "אופיר"]
STATUS_CONFIG = [
    {"label": "לא התחיל", "class": "m-red"},
    {"label": "בתהליך", "class": "m-orange"},
    {"label": "הוגש", "class": "m-green"}
]

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

# --- 4. Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    with st.form("new_task_form", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור קצר")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        if st.form_submit_button("הוסף למערכת", use_container_width=True):
            if desc:
                st.session_state.tasks.append({
                    "id": str(datetime.now().timestamp()),
                    "subject": subj, "desc": desc, "date": due,
                    "statuses": {name: 0 for name in STUDENTS}
                })
                st.rerun()
    st.write("---")
    if st.button("איפוס מערכת", type="primary", use_container_width=True):
        st.session_state.tasks = []
        st.rerun()

# --- 5. Main Content ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

if not st.session_state.tasks:
    st.info("אין כרגע מטלות במערכת.")
else:
    grid_ratios = [2.8] + [1] * len(STUDENTS)
    h_cols = st.columns(grid_ratios)

    with h_cols[0]:
        st.markdown("<p class='task-header-custom'>פרטי המטלה</p>", unsafe_allow_html=True)

    for i, name in enumerate(STUDENTS):
        with h_cols[i + 1]:
            st.markdown(f"<div class='student-label'>{name}</div>", unsafe_allow_html=True)

    st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    for task in sorted(st.session_state.tasks, key=lambda x: x['date']):
        row_cols = st.columns(grid_ratios)

        with row_cols[0]:
            sub_text, sub_btn = st.columns([5, 1])
            with sub_text:
                st.markdown(f"""
                    <div class="task-container">
                        <div class="task-subject">{task['subject']}</div>
                        <div class="task-desc">{task['desc']}</div>
                        <div class="task-date">📅 {task['date'].strftime('%d/%m/%Y')}</div>
                    </div>
                """, unsafe_allow_html=True)
            with sub_btn:
                if st.button("🗑️ ", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    st.rerun()

        for i, name in enumerate(STUDENTS):
            with row_cols[i + 1]:
                s_idx = task['statuses'][name]
                s_data = STATUS_CONFIG[s_idx]
                st.markdown(f'<div class="{s_data["class"]}"></div>', unsafe_allow_html=True)
                if st.button(s_data["label"], key=f"btn_{task['id']}_{name}"):
                    task['statuses'][name] = (s_idx + 1) % 3
                    st.rerun()

        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)
