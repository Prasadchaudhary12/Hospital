import streamlit as st
import pandas as pd
import datetime

# ------------------------ CONFIG ------------------------
st.set_page_config(page_title="Internal Audit QA Tool", layout="wide")

# ------------------------ STYLING ------------------------
st.markdown("""
<style>
html, body { font-family: Calibri; color: black; }
.stApp { background-color: #e6e6e6; }

/* HEADER */
.header {
    background-color: black;
    color: #f1c40f;
    padding: 14px;
    border-radius: 6px;
    text-align: center;
}

/* LOGIN BOX */
.login-box {
    border: 3px solid #f1c40f;
    padding: 25px;
    border-radius: 10px;
    background-color: white;
}

/* SECTION */
.section {
    background-color: white;
    padding: 15px;
    border-radius: 8px;
    margin-top: 10px;
    border-left: 6px solid #f1c40f;
}

/* BUTTON */
.stButton>button {
    background-color: #f1c40f;
    color: black;
    font-weight: bold;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ------------------------ SESSION INIT ------------------------
def init():
    defaults = {
        "users":{"admin":"admin"},
        "login":False,
        "user":"",
        "clients":[],
        "engagements":[],
        "qa":[] ,
        "logs":[],
        "archive":[],
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k]=v
init()

# ------------------------ LOGGER ------------------------
def log(action):
    st.session_state.logs.append({
        "User":st.session_state.user,
        "Action":action,
        "Time":datetime.datetime.now()
    })

# ------------------------ LOGIN ------------------------
def login():
    st.markdown("<h2 class='header'>Internal Audit QA System</h2>",unsafe_allow_html=True)

    c1,c2,c3 = st.columns([2,2,2])
    with c2:
        st.markdown("<div class='login-box'>",unsafe_allow_html=True)

        u = st.text_input("Username")
        p = st.text_input("Password",type="password")

        if st.button("Login",use_container_width=True):
            if u in st.session_state.users and st.session_state.users[u]==p:
                st.session_state.login=True
                st.session_state.user=u
                log("Login")
                st.rerun()
            else:
                st.error("Invalid credentials")

        st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ HEADER ------------------------
def header():
    col1,col2 = st.columns([8,2])

    col1.markdown("<div class='header'>🚆 Internal Audit QA Tool</div>", unsafe_allow_html=True)

    with col2:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Logout"):
            log("Logout")
            st.session_state.login=False
            st.rerun()

# ------------------------ DASHBOARD ------------------------
def dashboard():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("📊 Dashboard")

    df=pd.DataFrame(st.session_state.qa)

    total=len(df)
    pass_c=len(df[df.result=="Pass"]) if not df.empty else 0
    fail_c=len(df[df.result=="Fail"]) if not df.empty else 0
    na_c=total-pass_c-fail_c

    completed = total
    inprogress = 0
    notstarted = max(0,len(st.session_state.engagements)-completed)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total QA",total)
    c2.metric("Completed",completed)
    c3.metric("In Progress",inprogress)
    c4.metric("Not Started",notstarted)

    # chart
    if total>0:
        chart = pd.DataFrame({
            "Status":["Pass","Fail","N/A"],
            "Count":[pass_c,fail_c,na_c]
        })
        st.bar_chart(chart.set_index("Status"))

    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ CLIENT ------------------------
def client():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("🏢 Client Management")

    name=st.text_input("Client Name")

    if st.button("Add Client") and name:
        st.session_state.clients.append(name)
        log("Client Created")
        st.success("Client Added")

    st.dataframe(pd.DataFrame(st.session_state.clients,columns=["Clients"]))
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ ENGAGEMENT ------------------------
def engagement():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("📁 Create Engagement")

    if not st.session_state.clients:
        st.warning("Create client first")
        return

    client=st.selectbox("Client",st.session_state.clients)
    fy=st.text_input("Financial Year")
    process=st.text_input("Audit Process")
    auditor=st.text_input("Auditor Name")
    auditee=st.text_input("Auditee Name")
    dept=st.text_input("Department")
    title=st.text_input("Title")

    if st.button("Create Engagement"):
        st.session_state.engagements.append({
            "id":len(st.session_state.engagements),
            "client":client,
            "process":process,
            "fy":fy,
            "auditor":auditor,
            "auditee":auditee,
            "dept":dept,
            "title":title,
            "signed":False
        })
        log("Engagement Created")
        st.success("Created")

    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ CHECKLIST ------------------------
CHECKLIST = ["Planning","Risk Assessment","Control Testing","Evidence","Conclusion"]
DOCS = ["Scoping Memo","Audit Report","RCM","Audit Program","Workpapers","Evidence"]

def checklist():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("✅ QA Checklist")

    if not st.session_state.engagements:
        st.warning("Create engagement first")
        return

    eng = st.selectbox(
        "Select Engagement",
        st.session_state.engagements,
        format_func=lambda x: f"{x['client']} - {x['process']}"
    )

    st.write("### 📎 Mandatory Documents + Archive")
    for d in DOCS:
        st.file_uploader(d, key=f"{eng['id']}_{d}")

        if st.button(f"Archive {d}", key=f"{eng['id']}_{d}_archive"):
            st.session_state.archive.append({
                "Document":d,
                "User":st.session_state.user,
                "Time":datetime.datetime.now()
            })
            log(f"{d} archived")
            st.success(f"{d} archived")

    st.divider()

    for step in CHECKLIST:
        st.write(f"### 🔹 {step}")

        st.file_uploader("Upload Evidence", key=f"{eng['id']}_{step}")

        remark = st.text_area("Remarks", key=f"{eng['id']}_{step}_r")

        c1,c2,c3 = st.columns(3)

        if c1.button("Pass", key=f"{eng['id']}_{step}_p"):
            save(step,"Pass",remark)

        if c2.button("Fail", key=f"{eng['id']}_{step}_f"):
            save(step,"Fail",remark)

        if c3.button("N/A", key=f"{eng['id']}_{step}_na"):
            save(step,"NA",remark)

        if st.button("💬 Chat Assist", key=f"{eng['id']}_{step}_chat"):
            st.info("Suggestion: Improve documentation and testing clarity.")

    if st.button("✅ Sign-off QA"):
        eng["signed"]=True
        log("Signed Off")
        st.success("Signed Off")

    st.markdown("</div>",unsafe_allow_html=True)

def save(step,result,remark):
    st.session_state.qa.append({
        "step":step,
        "result":result,
        "remark":remark,
        "user":st.session_state.user,
        "time":datetime.datetime.now()
    })
    log(f"{step} {result}")
    st.success("Saved")

# ------------------------ REPORT ------------------------
def report():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("📄 Final Report")

    df=pd.DataFrame(st.session_state.qa)
    st.dataframe(df)

    st.download_button("Export Excel",df.to_csv(index=False),"QA_Report.csv")

    if st.button("💬 Refine Report"):
        st.info("Improve executive summary and observations.")

    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ LOGS ------------------------
def logs():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("📜 Audit Logs")
    st.dataframe(pd.DataFrame(st.session_state.logs))
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ ARCHIVE ------------------------
def archive():
    st.markdown("<div class='section'>",unsafe_allow_html=True)
    st.subheader("📦 Archive Repository")
    st.dataframe(pd.DataFrame(st.session_state.archive))
    st.markdown("</div>",unsafe_allow_html=True)

# ------------------------ MAIN ------------------------
if not st.session_state.login:
    login()
else:
    header()

    menu = st.selectbox("Navigate",[
        "Home","Dashboard","Client","Engagement",
        "Checklist","Report","Logs","Archive"
    ])

    if menu=="Home":
        st.markdown("<div class='section'>",unsafe_allow_html=True)
        st.subheader("🏠 Home")
        st.write("Enterprise Internal Audit QA System with structured workflow, document controls, and reporting.")
        st.markdown("</div>",unsafe_allow_html=True)

    elif menu=="Dashboard":
        dashboard()

    elif menu=="Client":
        client()

    elif menu=="Engagement":
        engagement()

    elif menu=="Checklist":
        checklist()

    elif menu=="Report":
        report()

    elif menu=="Logs":
        logs()

    elif menu=="Archive":
        archive()
