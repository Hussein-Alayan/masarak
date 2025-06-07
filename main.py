import os
import sys
import re
from dotenv import load_dotenv
import streamlit as st
from streamlit_lottie import st_lottie
from utils.ai_advice import analyze_cv, match_jobs_with_ai
from utils.job_search import search_linkedin_jobs, search_bayt_jobs
from PIL import Image
from pathlib import Path

# ─── Load ENV ─────────────────────────────────────────────────
load_dotenv()

# ─── Streamlit Config ──────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Matcher",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Custom CSS ───────────────────────────────────────────────
st.markdown("""
    <style>
    /* Overall Page Styling */
    .main {
        background-color: #1e1e1e;
        color: #cccccc;
        padding: 2rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    /* Section Headers */
    .section-header {
        font-size: 2.8em;
        font-weight: bold;
        margin: 3rem 0 2rem 0;
        color: #00aaff; /* Accent color */
        padding-bottom: 0.7rem;
        border-bottom: 3px solid #00aaff;
        text-align: center;
    }
    /* Subsection Headers */
    .subsection-header {
        font-size: 2em;
        font-weight: bold;
        margin: 2rem 0 1.5rem 0;
        color: #eeeeee;
    }
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        font-size: 1.3em;
        background-color: #00aaff;
        color: #1e1e1e; /* Dark text on bright button */
        border: none;
        transition: background-color 0.3s ease, transform 0.2s ease;
        font-weight: bold;
        letter-spacing: 0.05em;
    }
    .stButton>button:hover {
        background-color: #0077cc;
        transform: translateY(-3px);
    }
    /* File Uploader */
    .stFileUploader>label {
        font-size: 1.2em;
        color: #cccccc;
    }
    .upload-section {
        background-color: #282c34;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 3rem;
        border: 1px dashed #555;
    }
    /* Advice Section */
    .advice-section {
        background-color: #282c34;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 3rem;
        border: 1px solid #555;
    }
    .advice-text {
        font-size: 1.3em;
        line-height: 1.8;
        margin: 1.5rem 0;
        color: #dddddd;
    }
     .advice-text li {
        margin-bottom: 1em; /* Space out list items */
     }
    /* Job Search Section */
     .job-section {
        background-color: #282c34;
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 3rem;
        border: 1px solid #555;
    }
    /* Job Cards */
    .job-card {
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        background-color: #3a404b; /* Slightly lighter card background */
        border: 1px solid #555;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .job-card:hover {
        transform: translateY(-5px);
        border-color: #00aaff; /* Highlight on hover */
    }
    .job-card h4 a {
        color: #00aaff; /* Link color */
        text-decoration: none;
    }
    .job-card h4 a:hover {
        text-decoration: underline;
    }
    .job-card div {
        margin: 0.5rem 0;
        font-size: 1em;
        color: #cccccc;
    }
     .job-card strong {
        color: #eeeeee;
     }
    /* Expander */
    .stExpander {
        border-radius: 10px;
        border: 1px solid #555;
        background-color: #282c34; /* Match section background */
        margin-bottom: 2rem;
    }
    .stExpander:hover {
        border-color: #00aaff;
    }
    .stExpander div[data-baseweb="accordion-header"] {
        background-color: #3a404b; /* Match card background for header */
        color: #eeeeee;
        font-size: 1.1em;
        border-bottom: none;
    }
    .stExpander div[data-baseweb="accordion-content"] {
        color: #cccccc;
    }
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #1e1e1e; /* Match main background */
        color: #cccccc;
    }
    .sidebar .subsection-header {
        color: #eeeeee;
    }
    /* Adjust Streamlit elements for dark theme */
    label {
        color: #cccccc;
        font-size: 1.1em;
    }
    input[type="text"], textarea {
        background-color: #3a404b;
        color: #eeeeee;
        border-radius: 8px;
        border: 1px solid #555;
    }
    .stMultiSelect>div>div[data-baseweb="select"] div {
         background-color: #3a404b;
         color: #eeeeee;
         border-radius: 8px;
         border: 1px solid #555;
    }
     .stMultiSelect>div>div[data-baseweb="select"] div:hover {
         border-color: #00aaff;
     }
     .stMultiSelect>div>div[data-baseweb="select"] div[aria-selected="true"] {
          background-color: #00aaff;
          color: #1e1e1e;
     }
    .stSlider>div>div {
        background-color: #00aaff;
    }
    .stSuccess, .stError, .stWarning {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stSuccess {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24;
        border-color: #f5c6cb;
    }
    .stWarning {
        background-color: #fff3cd;
        color: #856404;
        border-color: #ffeeba;
    }
    </style>
""", unsafe_allow_html=True)

# ─── Lottie Animation Loader ─────────────────────────────────
def load_lottie_url(url: str):
    import requests
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None
    return None

# ─── SESSION STATE INIT ───────────────────────────────────────
for key, default in [
    ("cv_text", None),
    ("advice", {}),
    ("jobs", []),
    ("show_animation", False)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Header Section with Logo and Lottie Animation ───────────
logo_path = "assets/logo.png"
hero_lottie_url = "https://assets2.lottiefiles.com/packages/lf20_1pxqjqps.json"  # Job search animation
hero_lottie = load_lottie_url(hero_lottie_url)

# Use Streamlit's st.image for the logo (works with local files)
st.image(logo_path, width=110)
st.markdown("""
<div style='display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 2rem;'>
    <h1 style='font-size: 3.5em; color: #eeeeee; margin-bottom: 0.2em; text-align: center;'>AI Job Matcher 🚀</h1>
    <p style='font-size: 1.3em; color: #aaaaaa; margin-bottom: 1.5em; text-align: center;'>Upload your CV and get personalized career advice</p>
</div>
""", unsafe_allow_html=True)
if hero_lottie:
    st_lottie(hero_lottie, speed=1, reverse=False, loop=True, quality="high", height=220, key="hero_lottie")

# ─── CV Upload Section ────────────────────────────────────────
st.markdown("<div class='section-header'>📄 Upload Your CV</div>", unsafe_allow_html=True)
with st.container():
    st.markdown("<div class='upload-section'>", unsafe_allow_html=True)
    if not st.session_state.cv_text:
        # Show Lottie animation and instruction if no CV uploaded
        upload_lottie_url = "https://assets2.lottiefiles.com/packages/lf20_j1adxtyb.json"  # upload animation
        upload_lottie = load_lottie_url(upload_lottie_url)
        if upload_lottie:
            st_lottie(upload_lottie, speed=1, reverse=False, loop=True, quality="high", height=120, key="upload_lottie")
        st.markdown("<div style='text-align:center; color:#cccccc; font-size:1.1em; margin-bottom:1em;'>Please upload your PDF CV to get started.</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Drag and drop your PDF CV here", type="pdf", label_visibility="visible")
    if uploaded:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=uploaded.read(), filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            st.session_state.cv_text = text
            st.success("CV uploaded and parsed successfully!")
        except Exception as ex:
            st.error(f"Failed to parse PDF: {ex}")
    if st.session_state.cv_text:
        with st.expander("🔍 View Parsed CV Text", expanded=False):
            st.text_area("CV Text", st.session_state.cv_text, height=250)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── AI Career Advice Section ─────────────────────────────────
if st.session_state.cv_text:
    st.markdown("<div class='section-header'>💡 AI Career Advice</div>", unsafe_allow_html=True)
    with st.container():
        st.markdown("<div class='advice-section'>", unsafe_allow_html=True)
        advice_container = st.empty()
        if st.button("Get AI Career Advice", key="get_advice"):
            with st.spinner("AI is analyzing your CV..."):
                advice = analyze_cv(st.session_state.cv_text)
                if advice.get("error"):
                    st.error(advice["error"])
                else:
                    st.session_state.advice = advice
        if st.session_state.advice.get("advice_bullets"):
            st.markdown("<ul class='advice-text'>" + "".join(f"<li>{a}</li>" for a in st.session_state.advice["advice_bullets"]) + "</ul>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ─── Job Search Section ──────────────────────────────────────
if st.session_state.advice.get("job_titles"):
    st.markdown("<div class='section-header'>🔎 Search Matching Jobs</div>", unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("<div class='subsection-header'>Search Settings</div>", unsafe_allow_html=True)
        query_titles = st.session_state.advice["job_titles"]
        selected_title = st.selectbox("Job Title", query_titles, index=0)
        # Remove custom CSS for the slider to avoid blue background
        num_results = st.slider("Number of jobs per source", 3, 15, 5)
        if st.button("Search Jobs", key="search_jobs"):
            with st.spinner("Searching LinkedIn and Bayt jobs..."):
                jobs = search_linkedin_jobs([selected_title], num_results) + search_bayt_jobs([selected_title], num_results)
                # Deduplicate jobs by title+link
                seen = set()
                deduped = []
                for job in jobs:
                    key = (job.get('title','').lower(), job.get('link',''))
                    if key not in seen and job.get('title') and job.get('link'):
                        seen.add(key)
                        deduped.append(job)
                st.session_state.jobs = deduped
    # Display results & filters
    if st.session_state.jobs:
        jobs = st.session_state.jobs
        with st.sidebar:
            st.markdown("<div class='subsection-header'>Filters</div>", unsafe_allow_html=True)
            locs = sorted({j.get("location", "Unknown") for j in jobs})
            types = sorted({j.get("type", "Unknown") for j in jobs})
            sources = sorted({j.get("source", "Unknown") for j in jobs})
            sel_locs = st.multiselect("Location", locs, default=locs, help="Filter jobs by location")
            sel_types = st.multiselect("Job Type", types, default=types, help="Filter jobs by type (e.g., Full-time, Part-time)")
            sel_sources = st.multiselect("Source", sources, default=sources, help="Filter jobs by source platform")
        filtered = [
            j for j in jobs
            if j.get("location") in sel_locs 
            and j.get("type") in sel_types
            and j.get("source") in sel_sources
        ]
        st.markdown(f"<div style='font-size:1.2em; margin:1.5em 0 0.5em 0; color:#00aaff;'><b>Found {len(filtered)} matching jobs</b></div>", unsafe_allow_html=True)
        # Show source distribution
        source_counts = {}
        for job in filtered:
            source = job.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1
        st.markdown("<div style='font-size:1.1em; margin-bottom:0.5em; color:#eeeeee;'><b>Jobs by source:</b></div>", unsafe_allow_html=True)
        st.markdown("<ul style='margin-top:0; margin-bottom:1.5em;'>" + "".join(f"<li style='color:#cccccc;'>{source}: <b>{count}</b> jobs</li>" for source, count in source_counts.items()) + "</ul>", unsafe_allow_html=True)
        # AI-powered job matching
        if filtered:
            with st.spinner("AI is analyzing jobs..."):
                ai_result = match_jobs_with_ai(st.session_state.cv_text, selected_title, filtered, top_n=3)
            if ai_result.get("error"):
                st.error("AI job matching failed. Please try again later or check your API key.")
            elif not ai_result.get("ai_job_matches"):
                st.warning("No AI job recommendations were returned. Try a different job title or check your connection.")
            else:
                ai_text = ai_result["ai_job_matches"]
                ai_titles = re.findall(r'Title: (.+)', ai_text)
                ai_titles = [t.strip() for t in ai_titles]
                ai_recommended_jobs = []
                for t in ai_titles:
                    for job in filtered:
                        if job.get('title') == t and job not in ai_recommended_jobs:
                            ai_recommended_jobs.append(job)
                            break
                if ai_recommended_jobs:
                    st.markdown("<div class='subsection-header'>🤖 AI-Recommended Jobs</div>", unsafe_allow_html=True)
                    cols = st.columns(3)
                    for idx, job in enumerate(ai_recommended_jobs[:3]):
                        if not job.get('title') or not job.get('desc') or job['title'].strip().lower() == 'jobs':
                            continue
                        with cols[idx]:
                            desc = job.get('desc', '')
                            desc = re.sub(r'\s+', ' ', desc)
                            desc = re.sub(r'\.{2,}', '...', desc)
                            desc = desc[:180] + '...' if len(desc) > 180 else desc
                            source_icons = {"linkedin": "🔗", "bayt": "💼"}
                            source_icon = source_icons.get(job.get("source", "").lower(), "")
                            st.markdown(f"""
                            <div class='job-card' style='border:3px solid #00ffff; background: linear-gradient(135deg, #0a3d62 60%, #00aaff 100%); box-shadow: 0 4px 16px rgba(0,255,255,0.18); position:relative;'>
                                <div style='position:absolute; top:10px; right:10px; background-color:#00ffff; color:#0a3d62; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8em;'>
                                    ⭐ Top AI Match
                                </div>
                                <h4 style='margin:0 0 0.5rem 0; font-size:1.3rem; padding-right:100px;'>
                                    <a href=\"{job['link']}\" target=\"_blank\" style='color:#00ffff; text-decoration:none;'>
                                        {job['title']}
                                    </a>
                                </h4>
                                <div style='margin:0.25rem 0; font-size:0.9em;'>
                                    <span style='color:#00ffff;'>📍</span> <strong>Location:</strong> {job.get('location', '-')}
                                </div>
                                <div style='margin:0.25rem 0; font-size:0.9em;'>
                                    <span style='color:#00ffff;'>💼</span> <strong>Type:</strong> {job.get('type', '-')}
                                </div>
                                <div style='margin:0.25rem 0; font-size:0.9em;'>
                                    <span style='color:#00ffff;'>{source_icon}</span> <strong>Source:</strong> {job.get('source', '-')}
                                </div>
                                <div style='margin:0.5rem 0; font-size:0.9em; color:#cccccc; line-height:1.4;'>
                                    {desc}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown("<hr style='margin: 2rem 0; border: 1px solid #555;'>", unsafe_allow_html=True)
                other_jobs = [job for job in filtered if job.get('title') not in ai_titles]
                if other_jobs:
                    st.markdown("<div class='subsection-header'>All Matching Jobs</div>", unsafe_allow_html=True)
                    cols_per_row = 2
                    if other_jobs:
                        cols_other = st.columns(cols_per_row)
                        for idx, job in enumerate(other_jobs):
                            if not job.get('title') or not job.get('desc') or job['title'].strip().lower() == 'jobs':
                                continue
                            col_idx = idx % cols_per_row
                            with cols_other[col_idx]:
                                desc = job.get('desc', '')
                                desc = re.sub(r'\s+', ' ', desc)
                                desc = re.sub(r'\.{2,}', '...', desc)
                                desc = desc[:150] + '...' if len(desc) > 150 else desc
                                source_icons = {"linkedin": "🔗", "bayt": "💼"}
                                source_icon = source_icons.get(job.get("source", "").lower(), "")
                                source_colors = {"linkedin": "#0e4a6f", "bayt": "#4a4a00"}
                                bg_color = source_colors.get(job.get("source", "").lower(), "#3a404b")
                                border_color = "#555"
                                st.markdown(f"""
                                <div class='job-card' style='border:2px solid {border_color}; background-color:{bg_color};'>
                                    <h4 style='margin:0 0 0.5rem 0; font-size:1.2rem;'>
                                        <a href=\"{job['link']}\" target=\"_blank\" style='color:#00aaff; text-decoration:none;'>
                                            {job['title']}
                                        </a>
                                    </h4>
                                    <div style='margin:0.25rem 0; font-size:0.9em;'>
                                        <span style='color:#aaaaaa;'>📍</span> <strong>Location:</strong> {job.get('location', '-')}
                                    </div>
                                    <div style='margin:0.25rem 0; font-size:0.9em;'>
                                        <span style='color:#aaaaaa;'>💼</span> <strong>Type:</strong> {job.get('type', '-')}
                                    </div>
                                    <div style='margin:0.25rem 0; font-size:0.9em;'>
                                        <span style='color:#aaaaaa;'>{source_icon}</span> <strong>Source:</strong> {job.get('source', '-')}
                                    </div>
                                    <div style='margin:0.5rem 0; font-size:0.9em; color:#cccccc; line-height:1.4;'>
                                        {desc}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
