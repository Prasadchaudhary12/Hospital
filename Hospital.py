import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body, html, [class*="css"] { font-family: Calibri; }
.header-box { background:black; color:white; padding:10px; border-left:5px solid yellow; }
.card { background:white; border:1px solid grey; padding:15px; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------
def init():
    defaults = {
        "logged_in": False,
        "user": "",
        "clients": [],
        "engagements": [],
        "checklists": {},
        "logs": [],
        "doc_archive": [],
        "locks": {}
    }
    for k,v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
init()

# ---------------- LOG ----------------
def log(action):
    st.session_state.logs.append({
        "User": st.session_state.user,
        "Action": action,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# ---------------- LOGIN ----------------
def login():
    st.markdown("<div class='header-box'><h2>QA Tool Login</h2></div>", unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u=="admin" and p=="admin":
            st.session_state.logged_in=True
            st.session_state.user=u
            log("Login")
            st.rerun()
        else:
            st.error("Invalid")

# ---------------- HOME ----------------
def home():
    st.markdown("<div class='header-box'><h3>Welcome</h3></div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>Enterprise Internal Audit QA Platform</div>", unsafe_allow_html=True)

# ---------------- CLIENT ----------------
def clients():
    st.header("Clients")
    name = st.text_input("Client Name")
    if st.button("Add Client"):
        if name:
            st.session_state.clients.append(name)
            log("Client Created")
    if st.session_state.clients:
        st.dataframe(pd.DataFrame(st.session_state.clients, columns=["Clients"]))

# ---------------- ENGAGEMENT ----------------
def engagements():
    st.header("Engagements")

    client = st.selectbox("Client", st.session_state.clients if st.session_state.clients else ["NA"])
    fy = st.text_input("FY")
    process = st.text_input("Process")

    if st.button("Create Engagement"):
        eid = len(st.session_state.engagements)+1
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

# ---------------- CHECKLIST MASTER ----------------
def generate_checklist():
    steps = ["Planning", "Fieldwork", "Reporting"]
    return [{"step":s,"status":"Not Started"} for s in steps]

# ---------------- CHECKLIST ----------------
def checklist():
    st.header("Checklist")

    if not st.session_state.engagements:
        return

    eid = st.selectbox("Engagement", [e["id"] for e in st.session_state.engagements])
    data = st.session_state.checklists[eid]
    locked = st.session_state.locks.get(eid, False)

    complete=0

    for i, s in enumerate(data):
        with st.expander(s["step"]):
            st.file_uploader("Upload Evidence", key=f"file_{eid}_{i}", disabled=locked)
            st.text_area("Remarks", key=f"remark_{eid}_{i}", disabled=locked)

            c1,c2,c3=st.columns(3)
            if c1.button("Pass", key=f"p_{eid}_{i}", disabled=locked):
                s["status"]="Pass"
            if c2.button("Fail", key=f"f_{eid}_{i}", disabled=locked):
                s["status"]="Fail"
            if c3.button("N/A", key=f"na_{eid}_{i}", disabled=locked):
                s["status"]="N/A"

            if s["status"]!="Not Started":
                complete+=1

            if st.button("Chat Assist", key=f"chat_{eid}_{i}"):
                st.info("Suggestion: Validate documentation.")

    progress=int((complete/len(data))*100)
    st.progress(progress)
    st.write(f"{progress}% Completed")

    # update status
    for e in st.session_state.engagements:
        if e["id"]==eid:
            e["status"] = "Completed" if progress==100 else ("In Progress" if progress>0 else "Not Started")

    col1,col2=st.columns(2)

    if col1.button("Sign Off", disabled=locked):
        if progress<100:
            st.error("Complete all steps")
        else:
            st.session_state.locks[eid]=True
            log("QA Signed Off")

    if col2.button("Reopen QA"):
        st.session_state.locks[eid]=False
        log("QA Reopened")

# ---------------- DASHBOARD ----------------
def dashboard():
    st.header("Dashboard")

    total=pass_c=fail_c=na_c=0
    prog=[]

    for c in st.session_state.checklists.values():
        total+=len(c)
        comp=0
        for s in c:
            if s["status"]=="Pass":
                pass_c+=1; comp+=1
            elif s["status"]=="Fail":
                fail_c+=1; comp+=1
            elif s["status"]=="N/A":
                na_c+=1; comp+=1
        if c:
            prog.append(comp/len(c)*100)

    avg=int(sum(prog)/len(prog)) if prog else 0

    c1,c2,c3,c4=st.columns(4)
    c1.metric("Total", total)
    c2.metric("Pass", pass_c)
    c3.metric("Fail", fail_c)
    c4.metric("Completion %", avg)

    df=pd.DataFrame({"Status":["Pass","Fail","NA"],"Count":[pass_c,fail_c,na_c]})
    st.bar_chart(df.set_index("Status"))

# ---------------- ARCHIVE (UPDATED) ----------------
def archive():
    st.header("Audit Document Archive")

    doc_types = [
        "Audit Report","RCM","Workpapers",
        "Exhibits","Audit Program","Scoping Memo"
    ]

    tabs = st.tabs(doc_types)

    for i, doc in enumerate(doc_types):
        with tabs[i]:
            st.subheader(doc)

            st.file_uploader(f"Upload {doc}", key=f"upload_{doc}")

            if st.button(f"Archive {doc}", key=f"arc_{doc}"):
                st.session_state.doc_archive.append({
                    "Document": doc,
                    "User": st.session_state.user,
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                log(f"{doc} Archived")
                st.success(f"{doc} archived")

    if st.session_state.doc_archive:
        st.subheader("Archive Records")
        st.dataframe(pd.DataFrame(st.session_state.doc_archive))

# ---------------- REPORT ----------------
def report():
    st.header("QA Report")

    data=[]
    for eid, c in st.session_state.checklists.items():
        for s in c:
            data.append({
                "Eng": eid,
                "Step": s["step"],
                "Status": s["status"]
            })

    if data:
        df=pd.DataFrame(data)
        st.dataframe(df)
        st.download_button("Download", df.to_csv(index=False), "report.csv")

# ---------------- LOGS ----------------
def logs():
    st.header("Audit Logs")
    if st.session_state.logs:
        st.dataframe(pd.DataFrame(st.session_state.logs))

# ---------------- APP ----------------
if not st.session_state.logged_in:
    login()
else:
    st.write(f"Logged in: {st.session_state.user}")
    menu = st.selectbox("Menu",
        ["Home","Dashboard","Clients","Engagements","Checklist","Archive","Report","Logs"]
    )

    if st.button("Logout"):
        log("Logout")
        st.session_state.logged_in=False
        st.rerun()

    if menu=="Home": home()
    elif menu=="Dashboard": dashboard()
    elif menu=="Clients": clients()
    elif menu=="Engagements": engagements()
    elif menu=="Checklist": checklist()
    elif menu=="Archive": archive()
    elif menu=="Report": report()
    elif menu=="Logs": logs()
