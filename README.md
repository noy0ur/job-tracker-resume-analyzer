# Job Application Tracker & Resume Analyzer

Python + Streamlit app to track job applications with SQLite and compare resume keywords against job descriptions.

## Features
- Track company, role, location, URL, status, dates, and notes
- SQLite persistence and application dashboard
- Application status chart and CSV export
- PDF text extraction and explainable keyword coverage

## Run locally
Python 3.10+ recommended:
```bash
pip install -r requirements.txt
streamlit run app.py
```
The SQLite database is created automatically and excluded from Git because it may contain personal data.

## Deploy
Upload files to GitHub, visit https://share.streamlit.io/, create an app from the repository, and set main file path to `app.py`.

## Limitations and privacy
The analyzer uses a small skill dictionary and exact keyword matching. Its coverage score is not an ATS score or hiring prediction. Scanned PDFs need OCR, which is not included. This starter has no login system; do not store confidential information in a public repository or use sensitive resumes in a public demo. Streamlit Cloud local files may not persist across restarts; use a managed database for production.

## Skills
Python, SQLite, SQL, Streamlit, Pandas, PDF processing, text matching, CRUD operations, CSV export, Git/GitHub.
