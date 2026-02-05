import streamlit as st
from datetime import datetime
from supabase import create_client

# --- 1. Page Config ---
st.set_page_config(page_title="אפסילון", page_icon="ε", layout="wide")

# --- 2. Supabase Connection ---
# Make sure these match the names in your Streamlit Secrets dashboard!
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

# --- 3. CSS (Sidebar Left & Column Styling) ---
st.markdown("""
<style>
    html, body, [class*="css"], .stApp {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    [data-testid="stSidebar"] { left: 0 !important; right: auto !important; }
    [data-testid="stSidebarCollapsedControl"] { left: 20px !important; right: auto !important; }
    
    [data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;    
        justify-content: center !important;
        padding: 0px 1px !important;
    }
    
    /* FIX: Prevents text from squishing in the buttons */
    div.stButton > button {
        width: 100% !important;
        min-width: 65px !important; 
        font-size: 0.75rem !important;
        padding: 0px !important;
        border-radius: 4px !important;
        font-weight: 700 !important;
        height: 38px !important;
    }

    .main-title { text-align: center; margin-top: -30px !important; font-size: 3rem; font-weight: 800; color: white; }
    
    /* Status Colors */
    div[data-testid*="Column"]:has(.m-red) button { background-color: #ff4b4b !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-orange) button { background-color: #ffa500 !important; color: white !important; }
    div[data-testid*="Column"]:has(.m-green) button { background-color: #28a745 !important; color: white !important; }

    .task-container { background-color: #1e1e1e; border-right: 4px solid white !important; padding: 8px 12px; border-radius: 4px; width: 100%; }
    .task-subject { color: white !important; font-weight: 800; font-size: 0.9rem; }
    .row-divider { margin: 10px 0; border-bottom: 1px solid #333; width: 100%; }
    .m-red, .m-orange, .m-green { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 4. Sidebar: Add Task ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>אפסילון</h2>", unsafe_allow_html=True)
    with st.form("new_task_form", clear_on_submit=True):
        st.write("### ➕ מטלה חדשה")
        subj = st.selectbox("קורס", ["חומרי תעופה", "מדר ח'", "מוצקים", "פיזיקה 2", "חדוא 2", "שרטוט הנדסי"])
        desc = st.text_input("תיאור קצר")
        due = st.date_input("תאריך הגשה", value=datetime.today())
        
        if st.form_submit_button("הוסף למערכת", use_container_width=True):
            if desc:
                new_task = {
                    "subject": subj, "desc": desc, "due_date": str(due),
                    **{col: 0 for col in STUDENTS.values()}
                }
                supabase.table("tasks").insert(new_task).execute()
                st.rerun()

# --- 5. Main Content ---
st.markdown("<h1 class='main-title'>אפסילון</h1>", unsafe_allow_html=True)

response = supabase.table("tasks").select("*").order("due_date").execute()
tasks = response.data

if not tasks:
    st.info("אין כרגע מטלות במערכת.")
else:
    grid_ratios = [3] + [1] * len(STUDENTS)
    h_cols = st.columns(grid_ratios, gap="small")
    with h_cols[0]: st.markdown("<p style='text-align:center; color:white; font-weight:700;'>פרטי המטלה</p>", unsafe_allow_html=True)
    for i, name in enumerate(STUDENTS.keys()):
        with h_cols[i+1]: st.markdown(f"<div style='font-size:0.8rem; font-weight:700; color:white; text-align:center;'>{name}</div>", unsafe_allow_html=True)

    st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)

    for task in tasks:
        row_cols = st.columns(grid_ratios, gap="small")
        with row_cols[0]:
            sub_text, sub_btn = st.columns([5, 1])
            with sub_text:
                st.markdown(f"""<div class="task-container">
                    <div class="task-subject">{task['subject']}</div>
                    <div style="color:#eee; font-size:0.8rem;">{task['desc']}</div>
                    <div style="color:#888; font-size:0.7rem;">📅 {task['due_date']}</div>
                </div>""", unsafe_allow_html=True)
            with sub_btn:
                if st.button("🗑️", key=f"del_{task['id']}"):
                    supabase.table("tasks").delete().eq("id", task['id']).execute()
                    st.rerun()

        for i, (heb_name, db_col) in enumerate(STUDENTS.items()):
            with row_cols[i + 1]:
                s_idx = task[db_col]
                s_data = STATUS_CONFIG[s_idx]
                st.markdown(f'<div class="{s_data["class"]}"></div>', unsafe_allow_html=True)
                if st.button(s_data["label"], key=f"btn_{task['id']}_{db_col}"):
                    new_idx = (s_idx + 1) % 3
                    supabase.table("tasks").update({db_col: new_idx}).eq("id", task['id']).execute()
                    st.rerun()
        st.markdown("<div class='row-divider'></div>", unsafe_allow_html=True)
