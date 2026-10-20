from datetime import date
from io import BytesIO
from pathlib import Path
import re, sqlite3
import pandas as pd
import streamlit as st
from pypdf import PdfReader

DB = Path(__file__).parent / "job_tracker.db"
SKILLS = ["python","pandas","numpy","sql","sqlite","postgresql","api","rest api","fastapi","flask","django","pytest","unit testing","git","github","docker","linux","machine learning","scikit-learn","tensorflow","pytorch","nlp","data analysis","data structures","algorithms","object-oriented programming"]
STATUSES = ["Saved","Applied","Assessment","Interview","Offer","Rejected","Withdrawn"]
st.set_page_config(page_title="Job Tracker & Resume Analyzer", page_icon="🎯", layout="wide")

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, role TEXT NOT NULL, location TEXT, job_url TEXT, status TEXT NOT NULL, applied_date TEXT, deadline TEXT, notes TEXT, created_at TEXT NOT NULL)")

def load_rows():
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query("SELECT * FROM applications ORDER BY id DESC", con)

def find_skills(text):
    text = re.sub(r"\s+", " ", text.lower())
    return [s for s in SKILLS if re.search(r"(?<!\w)" + re.escape(s) + r"(?!\w)", text)]

init_db()
st.title("🎯 Job Application Tracker & Resume Analyzer")
st.write("Track job applications and compare resume keywords with job descriptions.")
st.caption("Portfolio demo. Keyword coverage is not an ATS score or a prediction of hiring success.")
dashboard, add_tab, resume_tab = st.tabs(["📊 Dashboard", "➕ Add application", "📄 Resume analyzer"])

with dashboard:
    data = load_rows()
    if data.empty:
        st.info("No applications yet. Add your first application in the next tab.")
    else:
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Applications", len(data))
        c2.metric("Interviews", int((data.status == "Interview").sum()))
        c3.metric("Offers", int((data.status == "Offer").sum()))
        c4.metric("Awaiting response", int(data.status.isin(["Applied","Assessment"]).sum()))
        st.subheader("Applications by status")
        st.bar_chart(data.status.value_counts())
        st.dataframe(data, use_container_width=True, hide_index=True)
        st.download_button("Export applications as CSV", data=data.to_csv(index=False).encode(), file_name="job_applications.csv", mime="text/csv")

with add_tab:
    with st.form("application_form", clear_on_submit=True):
        left,right = st.columns(2)
        company = left.text_input("Company *")
        role = left.text_input("Job title *")
        location = left.text_input("Location")
        url = right.text_input("Job posting URL")
        status = right.selectbox("Status", STATUSES)
        applied = st.date_input("Application date", value=date.today())
        deadline = st.date_input("Deadline (optional)", value=None)
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Save application")
        if submitted:
            if not company.strip() or not role.strip():
                st.error("Company and job title are required.")
            else:
                with sqlite3.connect(DB) as con:
                    con.execute("INSERT INTO applications(company,role,location,job_url,status,applied_date,deadline,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)",
                    (company.strip(),role.strip(),location.strip(),url.strip(),status,applied.isoformat(),deadline.isoformat() if deadline else "",notes.strip(),date.today().isoformat()))
                st.success("Saved to SQLite.")
                st.rerun()

with resume_tab:
    st.write("Upload a text-based PDF resume and paste a job description.")
    pdf = st.file_uploader("Resume PDF", type=["pdf"])
    jd = st.text_area("Job description", height=180)
    if st.button("Analyze resume", type="primary"):
        if not pdf or not jd.strip():
            st.error("Upload a PDF and paste a job description.")
        else:
            try:
                reader = PdfReader(BytesIO(pdf.getvalue()))
                resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                if len(resume_text.strip()) < 20:
                    st.error("Could not extract readable text. Scanned PDFs need OCR, not included in this version.")
                else:
                    resume_skills = find_skills(resume_text)
                    job_skills = find_skills(jd)
                    matched = [s for s in job_skills if s in resume_skills]
                    missing = [s for s in job_skills if s not in resume_skills]
                    score = round(100 * len(matched) / len(job_skills)) if job_skills else 0
                    st.metric("Keyword coverage", f"{score}%")
                    st.caption("Simple keyword coverage, not an ATS score or hiring prediction.")
                    st.write("**Skills detected in job description:**", ", ".join(job_skills) or "None from built-in list")
                    st.write("**Found in resume:**", ", ".join(matched) or "None")
                    st.write("**Not found in resume:**", ", ".join(missing) or "None")
                    st.info("Only add skills to your resume if you genuinely have them.")
            except Exception as exc:
                st.error(f"Could not read PDF: {exc}")
