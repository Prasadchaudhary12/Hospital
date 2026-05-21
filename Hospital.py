import streamlit as st
import pandas as pd
from datetime import datetime

# ------------------------------
# GLOBAL STYLE (UPDATED)
# ------------------------------
st.set_page_config(layout="wide")

st.markdown("""
<style>
body, html, [class*="css"] {
    font-family: Calibri;
}

.header-box {
    background-color: #000000;
    color: white;
    padding: 10px;
    border-left: 5px solid #FFC000;
}

.card {
    background-color: white;
    border: 1px solid #D9D9D9;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
}

.section-title {
    background-color: #F2F2F2;
    padding: 8px;
    border-left: 4px solid #FFC000;
    font-weight: bold;
}

.stButton > button {
    background-color: #333333;
    color: white;
    border-radius: 6px;
}

/* Tabs Styling */
.stTabs [role="tab"] {
    background-color: #E6E6E6;
    padding: 8px;
    border-radius: 6px;
    margin-right: 4px;
}

.stTabs [aria-selected="true"] {
    background-color: #333333;
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
    st.markdown("<div class='header-box'><h3>Welcome</h3></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Enterprise Internal Audit QA Platform</div>", unsafe_allow_html=True)

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
    st.header("Engagement Management")

    client = st.selectbox("Client", st.session_state.clients if st.session_state.clients else ["None"])
    fy = st.text_input("Financial Year")
    process = st.text_input("Process")

    if st.button("Create Engagement"):
        eid = len(st.session_state.engagements) + 1
        st.session_state.engagements.append({
            "id": eid,
            "client": client,
            "fy": fy,
            "process": process,
            "status": "Not Started"
        })
        st.session_state.checklists[eid] = generate_checklist()
        log("Engagement Created")

    if st.session_state.engagements:
        st.dataframe(pd.DataFrame(st.session_state.engagements))

# ------------------------------
# CHECKLIST MASTER
# ------------------------------
def generate_checklist():
    steps = ["Planning Review", "Fieldwork Review", "Reporting Review"]
    return [{"step": s, "status": "Not Started"} for s in steps]

# ------------------------------
# CHECKLIST
# ------------------------------
def checklist_page():
    st.header("Checklist")

    if not st.session_state.engagements:
        return

    eid = st.selectbox("Engagement", [e["id"] for e in st.session_state.engagements])
    checklist = st.session_state.checklists[eid]

    for i, step in enumerate(checklist):
        with st.expander(step["step"]):
            st.file_uploader("Upload Evidence", key=f"file_{eid}_{i}")
            st.text_area("Remarks", key=f"remark_{eid}_{i}")

            c1,c2,c3 = st.columns(3)
            if c1.button("Pass", key=f"pass_{eid}_{i}"):
                step["status"] = "Pass"
            if c2.button("Fail", key=f"fail_{eid}_{i}"):
                step["status"] = "Fail"
            if c3.button("N/A", key=f"na_{eid}_{i}"):
                step["status"] = "N/A"

# ------------------------------
# DASHBOARD
# ------------------------------
def dashboard():
    st.header("Dashboard")

    total = sum(len(c) for c in st.session_state.checklists.values())
    pass_c = fail_c = na_c = 0

    for c in st.session_state.checklists.values():
        for s in c:
            if s["status"] == "Pass":
                pass_c += 1
            elif s["status"] == "Fail":
                fail_c += 1
            elif s["status"] == "N/A":
                na_c += 1

    st.metric("Total QA", total)
    st.metric("Pass", pass_c)
    st.metric("Fail", fail_c)

# ------------------------------
# ✅ ARCHIVE (ENTERPRISE DESIGN)
# ------------------------------
def archive_page():
    st.markdown("<div class='header-box'><h3>Audit Document Archive</h3></div>", unsafe_allow_html=True)

    doc_types = [
        "Audit Report","RCM","Workpapers","Exhibits",
        "Audit Program","Scoping Memo","Audit Evidence","Final Deliverables"
    ]

    tabs = st.tabs(doc_types)

    for idx, doc in enumerate(doc_types):
        with tabs[idx]:

            st.markdown(f"<div class='section-title'>{doc} Archive Section</div>", unsafe_allow_html=True)

            col1, col2 = st.columns([2,1])

            with col1:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                file = st.file_uploader(f"Upload {doc}", key=f"upload_{doc}")
                notes = st.text_area("Document Notes", key=f"notes_{doc}")
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.write("**Metadata**")
                st.write(f"User: {st.session_state.user}")
                st.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

                if st.button(f"Archive {doc}", key=f"archive_btn_{doc}"):
                    st.session_state.doc_archive.append({
                        "Document": doc,
                        "User": st.session_state.user,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Notes": notes
                    })
                    log(f"{doc} Archived")
                    st.success(f"{doc} archived successfully")

                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.doc_archive:
        st.markdown("<div class='section-title'>Archived Records</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(st.session_state.doc_archive), use_container_width=True)

# ------------------------------
# REPORT
# ------------------------------
def report_page():
    st.header("Report")

    data=[]
    for eid, c in st.session_state.checklists.items():
        for s in c:
            data.append({"Engagement":eid,"Step":s["step"],"Status":s["status"]})

    if data:
        df = pd.DataFrame(data)
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
