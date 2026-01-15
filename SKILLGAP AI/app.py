# app.py – home + DB-based login/register + analyzer (no sidebar nav)

import streamlit as st
from datetime import datetime
from pathlib import Path

from users_db import init_db, create_user, authenticate_user

# ---------- INITIAL SETUP ----------
st.set_page_config(page_title="SkillGapAI – Home", page_icon="🎯", layout="wide")
init_db()  # ensure DB/table exist at startup

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    * { font-family: "Poppins", sans-serif; }
    .hero {
        padding: 60px 40px;
        border-radius: 18px;
        background: radial-gradient(circle at top left,#667eea 0,#764ba2 40%,#0f172a 100%);
        color: white;
        margin-bottom: 32px;
        box-shadow: 0 18px 45px rgba(15,23,42,.5);
    }
    .hero h1 { font-size: 3rem; margin-bottom: 10px; }
    .hero p { font-size: 1.1rem; opacity: 0.9; }
    .feature-card {
        padding: 20px;
        border-radius: 14px;
        background: linear-gradient(135deg,#f5f7fa,#e4ecff);
        box-shadow: 0 8px 25px rgba(15,23,42,.08);
        height: 100%;
    }
    .process-step {
        padding: 16px 18px;
        border-radius: 12px;
        background: #0f172a;
        color: #e5e7eb;
        margin-bottom: 10px;
    }
    .footer {
        margin-top: 48px;
        padding: 26px 12px;
        border-radius: 16px;
        background: linear-gradient(90deg,#0f172a,#111827);
        color: #e5e7eb;
        text-align: center;
        font-size: 0.9rem;
    }
    .footer a {
        color: #38bdf8;
        text-decoration: none;
        margin: 0 10px;
    }
    .footer a:hover { text-decoration: underline; }
    .small-muted { font-size: 0.85rem; opacity: 0.75; }
    .card-center {
        max-width: 420px;
        margin: 40px auto 10px auto;
        padding: 30px 26px 24px 26px;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 18px 45px rgba(15,23,42,.14);
        border: 1px solid #e5e7eb;
    }
    .card-title {
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 6px;
        text-align: center;
    }
    .card-subtitle {
        font-size: 0.9rem;
        color: #6b7280;
        text-align: center;
        margin-bottom: 16px;
    }
    .below-card {
        text-align: center;
        margin-top: 12px;
        font-size: 0.92rem;
        color: #4b5563;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None  # dict with id, username, email


def go(page: str):
    st.session_state.page = page
    st.rerun()


# ---------- HOME ----------
def render_home():
    col_l, col_r = st.columns([4, 1.4])
    with col_l:
        st.markdown("")
    with col_r:
        c1, c2 = st.columns(2)
        if c1.button("Login", use_container_width=True, key="home_login_btn"):
            go("login")
        if c2.button("Register", use_container_width=True, key="home_register_btn"):
            go("register")

    st.markdown(
        """
        <div class="hero">
          <h1>Bridge Your Skill Gaps with AI</h1>
          <p>
            SkillGapAI compares your resume with any job description using modern NLP and Sentence‑BERT,
            then highlights missing skills, visual dashboards, and personalized upskilling paths.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.subheader("What this project does")
        st.markdown(
            """
            - Extracts technical, data, and soft skills from resumes and job descriptions.  
            - Uses Sentence‑BERT embeddings and cosine similarity to find semantic matches and gaps.  
            - Builds interactive dashboards: gauges, heatmaps, bar charts, and timelines.  
            - Exports PDF + CSV reports so users can share their skill‑gap analysis.  
            """
        )
    with c2:
        st.image(
            "https://images.pexels.com/photos/1181675/pexels-photo-1181675.jpeg",
            caption="Sample analytics dashboard concept for candidate vs job requirements.",
            use_column_width=True,
            output_format="PNG",
        )

    st.markdown("---")

    st.subheader("Key features")
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """
            <div class="feature-card">
            <h4>🤖 AI skill extraction</h4>
            <p>Skills are extracted from unstructured text using NLP and a curated skill library.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """
            <div class="feature-card">
            <h4>📊 Role-based dashboards</h4>
            <p>Job seekers see personal gaps; recruiters see match scores and candidate insights.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """
            <div class="feature-card">
            <h4>📄 Reports & exports</h4>
            <p>PDF and CSV reports summarize match %, missing skills, and recommendations.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    st.subheader("Project workflow")
    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            """
            <div class="process-step"><b>1. Upload</b> – Resume and JD (PDF/DOCX/TXT) are uploaded or pasted.</div>
            <div class="process-step"><b>2. NLP preprocessing</b> – Text is cleaned and skills are extracted via rules + NER.</div>
            <div class="process-step"><b>3. Embeddings</b> – Sentence‑BERT converts skills into vectors.</div>
            """,
            unsafe_allow_html=True,
        )
    with p2:
        st.markdown(
            """
            <div class="process-step"><b>4. Matching</b> – Cosine similarity measures resume vs JD alignment.</div>
            <div class="process-step"><b>5. Dashboards</b> – Match gauges, heatmaps, and bars show strengths and gaps.</div>
            <div class="process-step"><b>6. Report</b> – A PDF report with charts and tips is generated.</div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("Start your analysis")
    st.write("Create an account or login to access the analyzer.")
    if st.button("Get Started →", key="home_get_started"):
        go("login")

    st.markdown(
        """
        <div class="footer">
          <div><b>Contact & Support</b></div>
          <div style="margin-top:6px;">
            Email: <a href="mailto:chilkuriudaykiran2002@gmail.com">support@skillgapai.com</a> ·
            Phone: +91-7386510409 ·
            Docs: <a href="https://example.com/skillgapai-docs">Project Guide</a>
          </div>
          <div style="margin-top:8px;" class="small-muted">
            For setup issues, send your error screenshot and environment details to the support email.
          </div>
          <div style="margin-top:8px;" class="small-muted">
            © {year} SkillGapAI · AI‑powered resume vs job‑description skill‑gap analyzer. @developed by uday kiran
          </div>
        </div>
        """.format(
            year=datetime.now().year
        ),
        unsafe_allow_html=True,
    )


# ---------- LOGIN (center card) ----------
def render_login():
    st.markdown("<div class='card-center'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Login</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-subtitle'>Sign in to access the SkillGapAI analyzer.</div>",
        unsafe_allow_html=True,
    )

    with st.form("login_form"):
        username_or_email = st.text_input("Username or Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        user = authenticate_user(username_or_email, password)
        if user:
            st.session_state.user = user
            st.success(f"Welcome, {user['username']}!")
            go("analyzer")
        else:
            st.error("Invalid username/email or password.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="below-card">
          Don't have an account?
        </div>
        """,
        unsafe_allow_html=True,
    )
    col = st.columns([1, 1, 1])[1]
    with col:
        if st.button("Register", key="login_register_link", use_container_width=True):
            go("register")


# ---------- REGISTER (center card) ----------
def render_register():
    st.markdown("<div class='card-center'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>Create account</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='card-subtitle'>Register once to analyze your resume vs job descriptions.</div>",
        unsafe_allow_html=True,
    )

    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        pwd = st.text_input("Password", type="password")
        pwd2 = st.text_input("Confirm password", type="password")
        submit = st.form_submit_button("Sign up")

    if submit:
        if not all([username, email, pwd, pwd2]):
            st.error("Please fill all fields.")
        elif pwd != pwd2:
            st.error("Passwords do not match.")
        else:
            created = create_user(username, email, pwd)
            if not created:
                st.error("Username or email already exists. Try another.")
            else:
                st.success("Account created successfully. You can now login.")
                st.session_state.page = "login"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="below-card">
          Already have an account?
        </div>
        """,
        unsafe_allow_html=True,
    )
    col = st.columns([1, 1, 1])[1]
    with col:
        if st.button("Back to Login", key="register_login_link", use_container_width=True):
            go("login")


# ---------- ANALYZER WRAPPER ----------
def render_analyzer():
    if not st.session_state.user:
        st.warning("Please login before accessing the analyzer.")
        if st.button("Go to Login", key="analyzer_back_to_login"):
            go("login")
        return

    top = st.columns([3, 1])
    with top[0]:
        st.markdown("#### SkillGapAI Analyzer")
        st.caption(
            f"Logged in as {st.session_state.user['username']} · Upload your resume and job description."
        )
    with top[1]:
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.user = None
            go("home")

    import pages.analyzer as analyzer_page
    analyzer_page.main()


# ---------- ROUTER ----------
page = st.session_state.page
if page == "home":
    render_home()
elif page == "login":
    render_login()
elif page == "register":
    render_register()
elif page == "analyzer":
    render_analyzer()
