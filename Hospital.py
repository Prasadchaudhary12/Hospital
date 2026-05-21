import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------
# GLOBAL STYLE
# ------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: Calibri;
}
.main {
    background-color: #F5F5F5;
}
.header-box {
    background-color: #000000;
    color: white;
    padding: 10px;
    border-left: 5px solid yellow;
}
.card {
    background-color: white;
    border: 1px solid grey;
    padding: 15px;
    border-radius: 10px;
}
button {
    background-color: yellow !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------
def init_session():
    defaults = {
        "logged_in": False,
        "user": "",
        "clients": [],
        "engagements": [],
        "checklists": {},
        "logs": [],
        "archives": [],
        "doc_archive": []
    }
    for k, v in defaults.items():
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
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username == "admin" and password == "admin":
                st.session_state.logged_in = True
                st.session_state.user = username
                log("Login")
                st.rerun()
            else:
                st.error("Invalid credentials")
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
    <li>Checklist-driven QA System</li>
    <li>Document tagging & archival</li>
    <li>Dashboard analytics</li>
    <li>Audit Logs & Reporting</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------
# CLIENT MANAGEMENT
# ------------------------------
def client_page():
    st.header("Client Management")

    name = st.text_input("Client Name", key="client")
    if st.button("Add Client"):
        if name:
            st.session_state.clients.append(name)
            log("Client Created")

    if st.session_state.clients:
        df = pd.DataFrame(st.session_state.clients, columns=["Clients"])
        st.dataframe(df)

# ------------------------------
# ENGAGEMENT MANAGEMENT
# ------------------------------
def engagement_page():
    st.header("Engagement Management")

    client = st.selectbox("Client", st.session_state.clients if st.session_state.clients else ["None"])
    fy = st.text_input("Financial Year")
    process = st.text_input("Audit Process")
    auditor = st.text_input("Auditor")
    auditee = st.text_input("Auditee")
    dept = st.text_input("Department")
    title = st.text_input("Title")

    if st.button("Create Engagement"):
        eg = {
            "id": len(st.session_state.engagements)+1,
            "client": client,
            "fy": fy,
            "process": process,
            "status": "Not Started"
        }
        st.session_state.engagements.append(eg)
        st.session_state.checklists[eg["id"]] = generate_checklist()
        log("Engagement Created")

# ------------------------------
# MASTER CHECKLIST
# ------------------------------
def generate_checklist():
    steps = ["Planning Review", "Fieldwork Review", "Reporting Review"]
    return [{"step": s, "status": "Not Started", "remarks": "", "doc": None} for s in steps]

# ------------------------------
# CHECKLIST SYSTEM
# ------------------------------
def checklist_page():
    st.header("Checklist")

    if not st.session_state.engagements:
        st.warning("No Engagements")
        return

    eg_ids = [e["id"] for e in st.session_state.engagements]
    selected = st.selectbox("Select Engagement", eg_ids)

    checklist = st.session_state.checklists[selected]

    for i, step in enumerate(checklist):
        with st.expander(step["step"]):
            st.file_uploader("Upload File", key=f"file_{selected}_{i}")
            remarks = st.text_area("Remarks", key=f"remark_{selected}_{i}")

            col1, col2, col3 = st.columns(3)
            if col1.button("Pass", key=f"pass_{i}_{selected}"):
                step["status"] = "Pass"
            if col2.button("Fail", key=f"fail_{i}_{selected}"):
                step["status"] = "Fail"
            if col3.button("N/A", key=f"na_{i}_{selected}"):
                step["status"] = "N/A"

            if st.button("Chat Assist", key=f"chat_{i}_{selected}"):
                st.info("Suggested: Ensure documentation completeness.")

            if st.button("Archive Doc", key=f"arc_{i}_{selected}"):
                st.session_state.doc_archive.append({
                    "Type": step["step"],
                    "User": st.session_state.user,
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                log("Document Archived")

    if st.button("Sign Off"):
        for step in checklist:
            if step["status"] == "Not Started":
                st.error("Complete all steps before sign-off")
                return
        st.success("QA Signed Off")
        log("QA Signed Off")

# ------------------------------
# DASHBOARD
# ------------------------------
def dashboard():
    st.header("Dashboard")

    total = sum(len(c) for c in st.session_state.checklists.values())
    pass_c = fail_c = na_c = 0

    for c in st.session_state.checklists.values():
        for step in c:
            if step["status"] == "Pass":
                pass_c += 1
            elif step["status"] == "Fail":
                fail_c += 1
            elif step["status"] == "N/A":
                na_c += 1

    df = pd.DataFrame({
        "Status": ["Pass", "Fail", "N/A"],
        "Count": [pass_c, fail_c, na_c]
    })

    st.bar_chart(df.set_index("Status"))

    st.metric("Total QA Steps", total)
    st.metric("Pass", pass_c)
    st.metric("Fail", fail_c)

# ------------------------------
# ✅ ENHANCED ARCHIVE PAGE
# ------------------------------
def archive_page():
    st.header("Audit Document Archive")

    doc_types = [
        "Audit Report",
        "RCM",
        "Workpapers",
        "Exhibits",
        "Audit Program",
        "Scoping Memo",
        "Audit Evidence",
        "Final Deliverables"
    ]

    tabs = st.tabs(doc_types)

    for idx, doc in enumerate(doc_types):
        with tabs[idx]:
            st.subheader(f"{doc} Archive Section")

            file = st.file_uploader(f"Upload {doc}", key=f"upload_{idx}")
            notes = st.text_area(f"{doc} Notes / Description", key=f"notes_{idx}")

            if st.button(f"Archive {doc}", key=f"archive_btn_{idx}"):
                st.session_state.doc_archive.append({
                    "Document Type": doc,
                    "User": st.session_state.user,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Notes": notes
                })
                log(f"{doc} Archived")
                st.success(f"{doc} archived successfully")

    if st.session_state.doc_archive:
        st.subheader("Archive Records")
        df = pd.DataFrame(st.session_state.doc_archive)
        st.dataframe(df)

# ------------------------------
# REPORT
# ------------------------------
def report_page():
    st.header("Report")

    data = []
    for eid, checklist in st.session_state.checklists.items():
        for step in checklist:
            data.append({
                "Engagement": eid,
                "Step": step["step"],
                "Status": step["status"]
            })

    if data:
        df = pd.DataFrame(data)
        st.dataframe(df)
        csv = df.to_csv(index=False).encode()
        st.download_button("Download CSV", csv, "report.csv")

# ------------------------------
# LOGS
# ------------------------------
def logs_page():
    st.header("Audit Logs")

    if st.session_state.logs:
        df = pd.DataFrame(st.session_state.logs)
        st.dataframe(df)

# ------------------------------
# MAIN APP
# ------------------------------
if not st.session_state.logged_in:
    login_page()
else:
    st.markdown(f"Logged in as: {st.session_state.user}")

    menu = st.selectbox("Navigation",
        ["Home", "Dashboard", "Clients", "Engagements",
         "Checklist", "Report", "Archive", "Logs"]
    )

    if st.button("Logout"):
        log("Logout")
        st.session_state.logged_in = False
        st.rerun()

    if menu == "Home":
        home()
    elif menu == "Dashboard":
        dashboard()
    elif menu == "Clients":
        client_page()
    elif menu == "Engagements":
        engagement_page()
    elif menu == "Checklist":
        checklist_page()
    elif menu == "Report":
        report_page()
    elif menu == "Archive":
        archive_page()
    elif menu == "Logs":
        logs_page()
