import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------
# GLOBAL STYLE (PURE YELLOW)
# ------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] { font-family: Calibri; }

.header-box {
    background-color: black;
    color: white;
    padding: 12px;
    border-left: 6px solid #FFFF00;
}

.card {
    background-color: white;
    border: 1px solid #D9D9D9;
    padding: 15px;
    border-radius: 8px;
}

.section-title {
    background-color: #FFFFE0;
    padding: 8px;
    border-left: 5px solid #FFFF00;
    font-weight: bold;
}

.stButton > button {
    background-color: #FFFF00;
    color: black;
}

/* Archive clean theme */
.stTabs [role="tab"] { background:#E6E6E6; }
.stTabs [aria-selected="true"] { background:#333; color:white; }
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION INIT
# ------------------------------
def init():
    defaults = {
        "logged_in": False,
        "user": "",
        "clients": [],
        "engagements": [],
        "checklists": {},
        "logs": [],
        "doc_archive": []
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v

init()

# ------------------------------
# LOG
# ------------------------------
def log(action):
    st.session_state.logs.append({
        "User": st.session_state.user,
        "Action": action,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ------------------------------
# LOGIN
# ------------------------------
def login():
    st.markdown("<div class='header-box'><h2>QA Tool Login</h2></div>",unsafe_allow_html=True)

    col1,col2,col3=st.columns([2,3,2])
    with col2:
        st.markdown("<div class='card'>",unsafe_allow_html=True)
        u=st.text_input("Username")
        p=st.text_input("Password",type="password")

        if st.button("Login"):
            if u=="admin" and p=="admin":
                st.session_state.logged_in=True
                st.session_state.user=u
                log("Login")
                st.rerun()
            else:
                st.error("Invalid")
        st.markdown("</div>",unsafe_allow_html=True)

# ------------------------------
# HOME
# ------------------------------
def home():
    st.markdown("<div class='header-box'><h3>Welcome</h3></div>",unsafe_allow_html=True)
    st.markdown("<div class='card'>Enterprise Internal Audit QA Platform</div>",unsafe_allow_html=True)

# ------------------------------
# ✅ FANCY DASHBOARD
# ------------------------------
def dashboard():
    st.markdown("<div class='header-box'><h3>Dashboard</h3></div>",unsafe_allow_html=True)

    # Dummy Data
    df = pd.DataFrame({
        "Engagement": ["E1","E2","E3","E4","E5"],
        "Total QA": [10,15,12,8,20],
        "Completed": [7,10,6,3,12],
        "In Progress": [2,3,4,3,5],
        "Not Started": [1,2,2,2,3],
        "Pass": [5,7,4,2,8],
        "Fail": [2,2,1,1,2],
        "N/A": [3,6,7,5,10]
    })

    # KPIs
    total = df["Total QA"].sum()
    comp = df["Completed"].sum()
    prog = df["In Progress"].sum()
    nots = df["Not Started"].sum()

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Total QA", total)
    col2.metric("Completed", comp)
    col3.metric("In Progress", prog)
    col4.metric("Not Started", nots)

    st.markdown("<div class='section-title'>QA Status Distribution</div>",unsafe_allow_html=True)

    status_df = df[["Pass","Fail","N/A"]].sum().reset_index()
    status_df.columns=["Status","Count"]

    st.bar_chart(status_df.set_index("Status"))

    st.markdown("<div class='section-title'>Engagement Progress</div>",unsafe_allow_html=True)

    progress = df.copy()
    progress["Completion %"] = (progress["Completed"]/progress["Total QA"])*100

    st.bar_chart(progress.set_index("Engagement")["Completion %"])

    st.markdown("<div class='section-title'>Detailed QA Table</div>",unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

# ------------------------------
# CLIENTS
# ------------------------------
def clients():
    st.header("Clients")
    name=st.text_input("Client Name")
    if st.button("Add Client"):
        st.session_state.clients.append(name)
        log("Client Created")

    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients,columns=["Clients"]))

# ------------------------------
# CHECKLIST
# ------------------------------
def checklist():
    st.header("Checklist")

    if not st.session_state.engagements:
        return

# ------------------------------
# ARCHIVE
# ------------------------------
def archive():
    st.markdown("<div class='header-box'><h3>Archive</h3></div>",unsafe_allow_html=True)

    docs=["Audit Report","RCM","Workpapers","Exhibits"]
    tabs=st.tabs(docs)

    for i,doc in enumerate(docs):
        with tabs[i]:
            st.file_uploader(f"Upload {doc}",key=doc)

# ------------------------------
# MAIN
# ------------------------------
if not st.session_state.logged_in:
    login()
else:
    st.write(f"Logged in: {st.session_state.user}")

    menu=st.selectbox("Navigation",
        ["Home","Dashboard","Clients","Archive"]
    )

    if st.button("Logout"):
        log("Logout")
        st.session_state.logged_in=False
        st.rerun()

    if menu=="Home": home()
    elif menu=="Dashboard": dashboard()
    elif menu=="Clients": clients()
    elif menu=="Archive": archive()
