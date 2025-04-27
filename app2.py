import streamlit as st
import pdfplumber
import google.generativeai as genai
import bs4
import requests
import json
import os
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# Replace with your actual Gemini API Key

# Initialize Gemini Flash model
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# === Company Career URLs (Intern and Full-time) ===
intern_carrier_distionary_india = {
    "Google": "https://careers.google.com/jobs/results/?employment_type=INTERNSHIP&location=India",
    # ... other internship URLs ...
}
full_time_carrier_distionary_india = {
    "Google": "https://careers.google.com/jobs/results/?employment_type=FULL_TIME&location=India",
    # ... other full-time URLs ...
}

# === Streamlit Page Setup ===
st.set_page_config(page_title="Realtime Job Finder", page_icon=":briefcase:", layout="wide")
st.title("Realtime Job Finder (India)")

# === Helper Functions ===

def find_apply_links(base_url: str) -> list:
    try:
        resp = requests.get(base_url, timeout=10)
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        return [
            urljoin(base_url, a['href'])
            for a in soup.find_all('a', href=True)
            if 'apply' in a['href'].lower()
        ]
    except Exception:
        return []


def find_all_job_links(base_url: str) -> list:
    try:
        resp = requests.get(base_url, timeout=10)
        resp.raise_for_status()
        soup = bs4.BeautifulSoup(resp.text, 'html.parser')
        return [
            urljoin(base_url, a['href'])
            for a in soup.find_all('a', href=True)
            if '/job/' in a['href'].lower() or '/jobs/' in a['href'].lower()
        ]
    except Exception:
        return []


def match_job(resume_text: str, job_desc: str) -> bool:
    prompt = (
        f"Based on the resume text:\n'''{resume_text}'''\n"
        f"and the job description:\n'''{job_desc}'''\n"
        "Return 'MATCH' if the candidate strongly matches the job requirements, otherwise 'NO MATCH'."
    )
    res = model.generate_content(prompt)
    return 'match' in res.text.lower()


def extract_requirements(job_desc: str) -> dict:
    prompt = (
        "Extract the minimum and preferred requirements from the following job description.\n"
        "Return a JSON with keys 'minimum' and 'preferred', each a list.\n"
        f"'''{job_desc}'''"
    )
    res = model.generate_content(prompt)
    try:
        return json.loads(res.text)
    except Exception:
        return {"minimum": [], "preferred": []}


def extract_job_metadata(job_desc: str) -> dict:
    prompt = (
        "Extract job metadata (title, id, location, requirements) from the following job description.\n"
        "Return JSON with keys 'title'(string), 'id'(string), 'location'(string), 'requirements'(list).\n"
        f"'''{job_desc}'''"
    )
    res = model.generate_content(prompt)
    try:
        return json.loads(res.text)
    except Exception:
        return {"title": "N/A", "id": "N/A", "location": "", "requirements": []}


def process_link(link: str, company: str, resume_text: str) -> dict | None:
    try:
        resp = requests.get(link, timeout=10)
        resp.raise_for_status()
        text = bs4.BeautifulSoup(resp.text, 'html.parser').get_text(separator=' ')
        if match_job(resume_text, text):
            return {
                'company': company,
                'link': link,
                'requirements': extract_requirements(text)
            }
    except Exception:
        pass
    return None


def process_company(company: str, base_url: str, resume_text: str) -> list:
    matched = []
    links = find_apply_links(base_url)
    if not links:
        return matched
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_link, link, company, resume_text) for link in links]
        for future in as_completed(futures):
            result = future.result()
            if result:
                matched.append(result)
    return matched

# === Streamlit Main Flow ===

file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
role_type = st.radio("Select Role Type", ["Internship", "Full-Time"])

if file:
    # --- Extract resume text ---
    with open(file.name, "wb") as f:
        f.write(file.getbuffer())
    with pdfplumber.open(file.name) as pdf:
        resume_text = "".join(page.extract_text() or "" for page in pdf.pages)
    os.remove(file.name)

    # --- AI-based company eligibility filter ---
    companies = (
        list(intern_carrier_distionary_india.keys())
        if role_type == 'Internship'
        else list(full_time_carrier_distionary_india.keys())
    )
    response = model.generate_content(
        f"Give me only the array not json of all the companies in string format and in `ascending order of eligible probability` not name, "
        f"where the candidate strictly strongly eligible for {role_type.lower()} roles in 3rd year btech and in india : {resume_text}, "
        f"choose from these companies list: {companies}, only give me the array in string format, don't add any extra formatting or text"
    )
    st.write("Eligible Companies:", response.text)
    arr = [c.strip().strip('"[]\'') for c in response.text.strip().split(',')]

    source = (
        intern_carrier_distionary_india
        if role_type == 'Internship'
        else full_time_carrier_distionary_india
    )
    eligible_dict = {c: source[c] for c in arr if c in source}

    if not eligible_dict:
        st.warning("No eligible companies from AI filter, defaulting to all companies.")
        eligible_dict = source

    st.subheader("Companies to be searched")
    for comp in eligible_dict:
        st.write(f"- {comp}")
    st.caption(f"Search started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # --- Crawl for matches ---
    matched_jobs = []
    status = st.empty()
    with st.spinner("Searching for matching jobs..."):
        max_workers = min(32, (os.cpu_count() or 4) * 2)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_company, comp, url, resume_text): comp
                for comp, url in eligible_dict.items()
            }
            for future in as_completed(futures):
                comp_name = futures[future]
                status.text(f"Searching: {comp_name}")
                matched_jobs.extend(future.result() or [])
    status.empty()

    # --- Display matches or fallback listing ---
    if matched_jobs:
        st.success(f"Found {len(matched_jobs)} matching job(s)")
        for job in matched_jobs:
            st.subheader(job['company'])
            st.write(f"**Apply Link:** {job['link']}")
            reqs = job['requirements']
            st.write("**Minimum Requirements:**")
            for r in reqs.get('minimum', []):
                st.write(f"- {r}")
            st.write("**Preferred Requirements:**")
            for r in reqs.get('preferred', []):
                st.write(f"- {r}")
            st.write("---")
    else:
        # === Fallback: revisit each base URL and parse ALL job links ===
        st.warning("No matching jobs found. Fetching all available listings in India for eligible companies...")
        st.subheader("Available job listings by revisiting each base URL:")
        for company, base_url in eligible_dict.items():
            st.markdown(f"### {company}")
            # Re-scrape the base URL for any job links
            all_links = find_all_job_links(base_url)
            if not all_links:
                st.write(f"No job links scraped — visit: {base_url}")
                continue

            # Extract metadata for each job link
            for link in all_links:
                try:
                    resp = requests.get(link, timeout=10)
                    resp.raise_for_status()
                    text = bs4.BeautifulSoup(resp.text, 'html.parser').get_text(separator=' ')
                    meta = extract_job_metadata(text)
                    if 'india' in meta.get('location', '').lower():
                        st.write(f"**Title:** {meta.get('title')}  |  **ID:** {meta.get('id')}")
                        st.write("Requirements:")
                        for req in meta.get('requirements', []):
                            st.write(f"- {req}")
                        st.write("---")
                except Exception:
                    continue
else:
    st.info("Upload your resume to start searching for jobs!")
