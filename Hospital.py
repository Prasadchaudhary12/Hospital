import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------
# GLOBAL STYLE (PURE YELLOW)
# ------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: Calibri;
}

/* Header */
.header-box {
    background-color: #000000;
    color: white;
    padding: 12px;
    border-left: 6px solid #FFFF00;
}

/* Cards */
.card {
    background-color: white;
    border: 1px solid #D9D9D9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}

/* Section Titles */
.section-title {
    background-color: #FFFFE0;
    padding: 8px;
    border-left: 5px solid #FFFF00;
    font-weight: bold;
}

/* Buttons (Yellow Theme) */
.stButton > button {
    background-color: #FFFF00;
    color: black;
    border-radius: 6px;
    font-weight: bold;
}

/* Archive buttons override */
.archive-btn > button {
    background-color: #333333 !important;
    color: white !important;
}

/* Tabs Styling */
.stTabs [role="tab"] {
    background-color: #E6E6E6;
}
.stTabs [aria-selected="true"] {
    background-color: #333;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION INIT
# ------------------------------
def init_session():
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
            st.session_state[k] = v

init_session()

# ------------------------------
# LOGGING
# ------------------------------
def log(action):
    st.session_state.logs.append({
        "user": st.session_state.user,
        "action": action,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ------------------------------
# LOGIN
# ------------------------------
def login_page():
    st.markdown("<div class='header-box'><h2>Internal Audit QA Tool Login</h2></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2,3,2])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u == "admin" and p == "admin":
                st.session_state.logged_in = True
                st.session_state.user = u
                log("Login")
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# ------------------------------
# HOME
# ------------------------------
def home():
    st.markdown("<div class='header-box'><h3>Welcome to Internal Audit QA Tool</h3></div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='card'>
    <b>Capabilities:</b>
    <ul>
    <li>Client & Engagement Management</li>
    <li>Checklist QA System</li>
    <li>Audit Document Archival</li>
    <li>Dashboard Analytics</li>
    <li>Audit Logs & Reporting</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# ✅ ENHANCED DASHBOARD
# ------------------------------
def dashboard():
    st.markdown("<div class='header-box'><h3>Dashboard</h3></div>", unsafe_allow_html=True)

    # Dummy dataset (rich analytics)
    df = pd.DataFrame({
        "Engagement": ["E1","E2","E3","E4","E5"],
        "Total QA": [12, 15, 10, 18, 14],
        "Completed": [8, 10, 6, 12, 9],
        "In Progress": [3, 3, 2, 4, 3],
        "Not Started": [1, 2, 2, 2, 2],
        "Pass": [6, 7, 4, 9, 6],
        "Fail": [2, 2, 1, 1, 2],
        "N/A": [4, 6, 5, 8, 6]
    })

    total = df["Total QA"].sum()
    completed = df["Completed"].sum()
    in_progress = df["In Progress"].sum()
    not_started = df["Not Started"].sum()

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total QA", total)
    col2.metric("Completed", completed)
    col3.metric("In Progress", in_progress)
    col4.metric("Not Started", not_started)

    # Status Chart
    st.markdown("<div class='section-title'>QA Status Distribution</div>", unsafe_allow_html=True)

    status_df = df[["Pass","Fail","N/A"]].sum().reset_index()
    status_df.columns = ["Status","Count"]
    st.bar_chart(status_df.set_index("Status"))

    # Progress Chart
    st.markdown("<div class='section-title'>Engagement Completion %</div>", unsafe_allow_html=True)

    df["Completion %"] = (df["Completed"] / df["Total QA"]) * 100
    st.bar_chart(df.set_index("Engagement")["Completion %"])

    # Tabular View
    st.markdown("<div class='section-title'>Detailed QA Summary</div>", unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True)

# ------------------------------
# CLIENTS
# ------------------------------
def client_page():
    st.header("Client Management")

    name = st.text_input("Client Name")

    if st.button("Add Client"):
        if name:
            st.session_state.clients.append(name)
            log("Client Created")

    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients, columns=["Clients"]))

# ------------------------------
# ENGAGEMENTS
# ------------------------------
def engagement_page():
    st.header("Engagements")

    client = st.selectbox("Client", st.session_state.clients if st.session_state.clients else ["None"])
    fy = st.text_input("Financial Year")
    process = st.text_input("Process")

    if st.button("Create Engagement"):
        eid = len(st.session_state.engagements)+1
        st.session_state.engagements.append({
            "id": eid,
            "client": client,
            "fy": fy,
            "process": process,
            "status":"Not Started"
        })
        st.session_state.checklists[eid] = generate_checklist()
        log("Engagement Created")

    if st.session_state.engagements:
        st.dataframe(pd.DataFrame(st.session_state.engagements))

# ------------------------------
# CHECKLIST MASTER
# ------------------------------
def generate_checklist():
    steps = ["Planning Review","Fieldwork Review","Reporting Review"]
    return [{"step":s,"status":"Not Started"} for s in steps]

# ------------------------------
# CHECKLIST
# ------------------------------
def checklist_page():
    st.header("Checklist")

    if not st.session_state.engagements:
        return

    eid = st.selectbox("Engagement", [e["id"] for e in st.session_state.engagements])

    checklist = st.session_state.checklists[eid]

    for i, s in enumerate(checklist):
        with st.expander(s["step"]):
            st.file_uploader("Upload Evidence", key=f"file_{eid}_{i}")
            st.text_area("Remarks", key=f"remark_{eid}_{i}")

            c1,c2,c3 = st.columns(3)
            if c1.button("Pass", key=f"p_{eid}_{i}"):
                s["status"]="Pass"
            if c2.button("Fail", key=f"f_{eid}_{i}"):
                s["status"]="Fail"
            if c3.button("N/A", key=f"na_{eid}_{i}"):
                s["status"]="N/A"

# ------------------------------
# ARCHIVE
# ------------------------------
def archive_page():
    st.markdown("<div class='header-box'><h3>Audit Document Archive</h3></div>", unsafe_allow_html=True)

    docs = ["Audit Report","RCM","Workpapers","Exhibits","Audit Program","Scoping Memo","Audit Evidence","Final Deliverables"]

    tabs = st.tabs(docs)

    for i, doc in enumerate(docs):
        with tabs[i]:
            st.markdown(f"<div class='section-title'>{doc} Section</div>", unsafe_allow_html=True)

            col1,col2 = st.columns([2,1])

            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.file_uploader(f"Upload {doc}", key=f"{doc}_upload")
                notes = st.text_area("Notes", key=f"{doc}_notes")
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.write(f"User: {st.session_state.user}")
                st.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

                st.markdown("<div class='archive-btn'>", unsafe_allow_html=True)
                if st.button(f"Archive {doc}", key=f"{doc}_btn"):
                    st.session_state.doc_archive.append({
                        "Document": doc,
                        "User": st.session_state.user,
                        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Notes": notes
                    })
                    log(f"{doc} Archived")
                    st.success(f"{doc} archived")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.doc_archive:
        st.markdown("<div class='section-title'>Archive Records</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.doc_archive), use_container_width=True)

# ------------------------------
# REPORT
# ------------------------------
def report_page():
    st.header("Report")

    data=[]
    for eid,c in st.session_state.checklists.items():
        for s in c:
            data.append({"Engagement":eid,"Step":s["step"],"Status":s["status"]})

    if data:
        df=pd.DataFrame(data)
        st.dataframe(df)
        st.download_button("Download CSV", df.to_csv(index=False), "report.csv")

# ------------------------------
# LOGS
# ------------------------------
def logs_page():
    st.header("Audit Logs")
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs))

# ------------------------------
# MAIN
# ------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    st.write(f"Logged in as: {st.session_state.user}")

    menu = st.selectbox("Navigation",
        ["Home","Dashboard","Clients","Engagements","Checklist","Archive","Report","Logs"]
    )

    if st.button("Logout"):
        log("Logout")
        st.session_state.logged_in=False
        st.rerun()

    if menu=="Home": home()
    elif menu=="Dashboard": dashboard()
    elif menu=="Clients": client_page()
    elif menu=="Engagements": engagement_page()
    elif menu=="Checklist": checklist_page()
    elif menu=="Archive": archive_page()
    elif menu=="Report": report_page()
    elif menu=="Logs": logs_page()
