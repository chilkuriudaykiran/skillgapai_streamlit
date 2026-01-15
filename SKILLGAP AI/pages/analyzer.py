# pages/analyzer.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import PyPDF2
import docx
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import sqlite3
from datetime import datetime
import json

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from io import BytesIO

# -----------------------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="SkillGapAI – Analyzer",
    page_icon="🎯",
    layout="wide"
)

# -----------------------------------------------------------------------------
# CACHED MODELS / RESOURCES (Python 3.14 friendly)
# -----------------------------------------------------------------------------
@st.cache_resource
def load_sentence_model():
    """
    Load a modern, lightweight Sentence‑Transformer model.
    Compatible with sentence-transformers 5.x and Python 3.14.
    """
    # All-MiniLM-L6-v2 remains a strong general-purpose choice.[web:60][web:52]
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

model = load_sentence_model()

# -----------------------------------------------------------------------------
# UTILS – TEXT EXTRACTION
# -----------------------------------------------------------------------------
def extract_text_from_pdf(file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    except Exception as e:
        st.error(f"PDF read error: {e}")
    return text.strip()

def extract_text_from_docx(file):
    try:
        document = docx.Document(file)
        return "\n".join(p.text for p in document.paragraphs)
    except Exception as e:
        st.error(f"DOCX read error: {e}")
        return ""

def extract_text_from_txt(file):
    try:
        return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        st.error(f"TXT read error: {e}")
        return ""

def extract_text(upload):
    if upload is None:
        return ""
    name = upload.name.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(upload)
    if name.endswith(".docx"):
        return extract_text_from_docx(upload)
    if name.endswith(".txt"):
        return extract_text_from_txt(upload)
    st.error("Unsupported file type. Use PDF / DOCX / TXT.")
    return ""

# -----------------------------------------------------------------------------
# SKILL VOCAB & EXTRACTION (simple but clear)
# -----------------------------------------------------------------------------
COMMON_SKILLS = {
    "Technical": [
        "Python", "Java", "JavaScript", "C++", "C#", "Go", "Rust", "Kotlin",
        "React", "Angular", "Vue", "Node.js", "Django", "Flask", "Spring",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD",
        "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
        "TensorFlow", "PyTorch", "REST API", "GraphQL", "Microservices"
    ],
    "Data": [
        "Data Analysis", "Data Science", "Statistics", "Power BI",
        "Tableau", "Excel", "Pandas", "NumPy", "ETL", "Spark", "Hadoop"
    ],
    "Soft": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Project Management",
        "Presentation", "Negotiation", "Adaptability", "Creativity"
    ]
}

def extract_skills_simple(text: str):
    """Dictionary of skills by category using keyword search."""
    text_low = text.lower()
    result = {k: [] for k in COMMON_SKILLS}
    for cat, skills in COMMON_SKILLS.items():
        for s in skills:
            if s.lower() in text_low:
                result[cat].append(s)
        result[cat] = sorted(set(result[cat]))
    return result

# -----------------------------------------------------------------------------
# EMBEDDING & GAP ANALYSIS (Sentence‑BERT style)
# -----------------------------------------------------------------------------
def skills_to_list(skills_dict):
    lst = []
    for v in skills_dict.values():
        lst.extend(v)
    return sorted(set(lst))

def compute_skill_embeddings(skills):
    if not skills:
        return None
    return model.encode(skills)  # sentence-transformers 5.x API.[web:52]

def compute_similarity_matrix(resume_skills, jd_skills):
    if not resume_skills or not jd_skills:
        return None
    res_emb = compute_skill_embeddings(resume_skills)
    jd_emb = compute_skill_embeddings(jd_skills)
    sim = cosine_similarity(res_emb, jd_emb)
    return sim

def analyze_skill_gap(resume_dict, jd_dict):
    resume_all = skills_to_list(resume_dict)
    jd_all = skills_to_list(jd_dict)

    matched = sorted(set(resume_all) & set(jd_all))
    missing = sorted(set(jd_all) - set(resume_all))
    extra = sorted(set(resume_all) - set(jd_all))

    match_pct = (len(matched) / len(jd_all) * 100) if jd_all else 0.0

    gap_rank = []
    for s in missing:
        prio = "High" if any(k in s.lower() for k in ["python", "ml", "data", "cloud", "react", "docker"]) else "Medium"
        gap_rank.append({"skill": s, "priority": prio})
    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "match_pct": match_pct,
        "total_resume": len(resume_all),
        "total_jd": len(jd_all),
        "gap_rank": gap_rank
    }

# -----------------------------------------------------------------------------
# VISUALS – PLOTLY CHARTS (dynamic)
# -----------------------------------------------------------------------------
def gauge_chart(match_pct):
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=match_pct,
        delta={"reference": 80},
        title={"text": "Skill Match %"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#667eea"},
            "steps": [
                {"range": [0, 40], "color": "#ff6b6b"},
                {"range": [40, 70], "color": "#ffa502"},
                {"range": [70, 100], "color": "#2ecc71"},
            ],
        },
    ))
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def category_pie(skills_dict, title):
    counts = {cat: len(v) for cat, v in skills_dict.items()}
    fig = px.pie(
        names=list(counts.keys()),
        values=list(counts.values()),
        title=title,
        color_discrete_sequence=["#667eea", "#764ba2", "#f39c12"],
    )
    fig.update_layout(margin=dict(l=0, r=0, t=50, b=0))
    return fig

def bar_matched_missing_extra(analysis):
    data = {
        "Type": ["Matched", "Missing", "Extra"],
        "Count": [len(analysis["matched"]), len(analysis["missing"]), len(analysis["extra"])],
    }
    fig = px.bar(
        data,
        x="Type",
        y="Count",
        color="Type",
        color_discrete_map={
            "Matched": "#2ecc71",
            "Missing": "#e74c3c",
            "Extra": "#3498db",
        },
        title="Skills Overview",
    )
    fig.update_layout(showlegend=False, margin=dict(l=10, r=10, t=40, b=40))
    return fig

def heatmap_similarity(resume_skills, jd_skills, sim):
    if sim is None:
        return go.Figure()
    fig = go.Figure(
        data=go.Heatmap(
            z=sim,
            x=jd_skills,
            y=resume_skills,
            colorscale="RdYlGn",
            colorbar=dict(title="Cosine sim"),
        )
    )
    fig.update_layout(
        title="Sentence‑BERT Skill Similarity Matrix",
        xaxis_title="Job Description Skills",
        yaxis_title="Resume Skills",
        height=500,
        margin=dict(l=60, r=10, t=40, b=60),
    )
    return fig

def gap_ranking_bar(gaps):
    if not gaps:
        return go.Figure()
    df = pd.DataFrame(gaps)
    df["weight"] = df["priority"].map({"High": 2, "Medium": 1}).fillna(1)
    fig = px.bar(
        df,
        x="skill",
        y="weight",
        color="priority",
        title="Prioritized Skill Gaps",
        color_discrete_map={"High": "#e74c3c", "Medium": "#f1c40f"},
    )
    fig.update_yaxes(visible=False)
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=80))
    return fig

def timeline_chart(analysis):
    x = ["Job Requirements", "Matched", "Missing"]
    y = [analysis["total_jd"], len(analysis["matched"]), len(analysis["missing"])]
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line=dict(color="#667eea", width=3),
            marker=dict(size=10),
            fill="tozeroy",
        )
    )
    fig.update_layout(
        title="Skill Journey Timeline",
        xaxis_title="Stage",
        yaxis_title="Count",
        margin=dict(l=20, r=20, t=40, b=40),
    )
    return fig

# -----------------------------------------------------------------------------
# DB – SIMPLE HISTORY
# -----------------------------------------------------------------------------
def get_db():
    conn = sqlite3.connect("skillgap_ai.db")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            created_at TEXT,
            match_pct REAL,
            payload TEXT
        )
        """
    )
    conn.commit()
    return conn

def save_analysis(username, analysis):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO analyses (username, created_at, match_pct, payload) VALUES (?, ?, ?, ?)",
            (
                username or "guest",
                datetime.utcnow().isoformat(),
                float(analysis["match_pct"]),
                json.dumps(analysis),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        st.warning(f"Could not save analysis: {e}")

def load_history(username):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, created_at, match_pct, payload FROM analyses WHERE username=? ORDER BY id DESC LIMIT 10",
        (username or "guest",),
    )
    rows = cur.fetchall()
    conn.close()
    return rows

# -----------------------------------------------------------------------------
# PDF REPORT – INCLUDE KEY METRICS (charts stay in app, summary in PDF)
# -----------------------------------------------------------------------------
def build_pdf(analysis, resume_skills, jd_skills):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=1,
        textColor=colors.HexColor("#667eea"),
        fontSize=22,
        spaceAfter=20,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#764ba2"),
        spaceAfter=8,
        spaceBefore=12,
    )

    story = []
    story.append(Paragraph("SkillGapAI – Skill Gap Analysis", title_style))
    story.append(Paragraph(datetime.utcnow().strftime("Generated on %Y-%m-%d %H:%M UTC"), styles["Normal"]))
    story.append(Spacer(1, 12))

    # Overview table
    story.append(Paragraph("Overview", heading))
    data = [
        ["Metric", "Value"],
        ["Match %", f"{analysis['match_pct']:.1f}%"],
        ["Job Skills", str(analysis["total_jd"])],
        ["Resume Skills", str(analysis["total_resume"])],
        ["Matched", str(len(analysis["matched"]))],
        ["Missing", str(len(analysis["missing"]))],
        ["Extra", str(len(analysis["extra"]))],
    ]
    tbl = Table(data, hAlign="LEFT")
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Top lists
    story.append(Paragraph("Matched Skills (sample)", heading))
    story.append(Paragraph(", ".join(analysis["matched"][:25]) or "None", styles["Normal"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Missing Skills (prioritized)", heading))
    top_missing = [g["skill"] for g in analysis["gap_rank"][:25]]
    story.append(Paragraph(", ".join(top_missing) or "None", styles["Normal"]))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Extra Resume Skills (sample)", heading))
    story.append(Paragraph(", ".join(analysis["extra"][:25]) or "None", styles["Normal"]))

    story.append(PageBreak())

    # Recommendations
    story.append(Paragraph("Upskilling Recommendations", heading))
    for g in analysis["gap_rank"][:10]:
        skill = g["skill"]
        prio = g["priority"]
        msg = f"<b>{skill}</b> ({prio} priority): Take 1–2 online courses or certifications focused on {skill} and build at least one portfolio project."
        story.append(Paragraph(msg, styles["Normal"]))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer

# -----------------------------------------------------------------------------
# MAIN STREAMLIT LAYOUT
# -----------------------------------------------------------------------------
def main():
    st.title("🎯 SkillGapAI – AI Skill Gap Analyzer")
    st.caption("Upload resume and job description, extract skills with Sentence‑BERT, and explore dynamic dashboards with exportable reports.[file:1]")

    user = st.session_state.get("username", "guest")

    tab_upload, tab_dash, tab_advanced, tab_history = st.tabs(
        ["📤 Upload & Analyze", "📊 Dashboard", "📈 Advanced Charts", "📚 History"]
    )

    # --------------------------------------------------------------
    # TAB 1 – UPLOAD & ANALYZE
    # --------------------------------------------------------------
    with tab_upload:
        col_r, col_j = st.columns(2)

        with col_r:
            st.subheader("📄 Resume")
            r_file = st.file_uploader("Upload resume (PDF / DOCX / TXT)", type=["pdf", "docx", "txt"], key="resume_file")
            r_text = extract_text(r_file)
            if not r_file:
                r_text = st.text_area("Or paste resume text", height=180, key="resume_text")
            if r_text:
                with st.expander("Preview resume text"):
                    st.write(r_text[:1500])

        with col_j:
            st.subheader("💼 Job Description")
            j_file = st.file_uploader("Upload job description", type=["pdf", "docx", "txt"], key="jd_file")
            j_text = extract_text(j_file)
            if not j_file:
                j_text = st.text_area("Or paste JD text", height=180, key="jd_text")
            if j_text:
                with st.expander("Preview JD text"):
                    st.write(j_text[:1500])

        st.markdown("---")
        analyze_btn = st.button("🚀 Run Skill Gap Analysis", use_container_width=True)

        if analyze_btn:
            if not r_text or not j_text:
                st.error("Provide both resume and job description text.")
            else:
                with st.spinner("Extracting skills and computing Sentence‑BERT similarity..."):
                    r_skills = extract_skills_simple(r_text)
                    j_skills = extract_skills_simple(j_text)
                    analysis = analyze_skill_gap(r_skills, j_skills)

                    res_list = skills_to_list(r_skills)
                    jd_list = skills_to_list(j_skills)
                    sim_matrix = compute_similarity_matrix(res_list, jd_list)

                    st.session_state["resume_skills"] = r_skills
                    st.session_state["jd_skills"] = j_skills
                    st.session_state["analysis"] = analysis
                    st.session_state["sim_matrix"] = sim_matrix
                    st.session_state["resume_list"] = res_list
                    st.session_state["jd_list"] = jd_list

                    save_analysis(user, analysis)

                st.success(f"Analysis complete – match: {analysis['match_pct']:.1f}%")
                st.balloons()

    # --------------------------------------------------------------
    # TAB 2 – MAIN DASHBOARD
    # --------------------------------------------------------------
    with tab_dash:
        if "analysis" not in st.session_state:
            st.info("Run an analysis in the **Upload & Analyze** tab first.")
        else:
            analysis = st.session_state["analysis"]
            r_skills = st.session_state["resume_skills"]
            j_skills = st.session_state["jd_skills"]

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Match %", f"{analysis['match_pct']:.1f}%")
            k2.metric("Job Skills", analysis["total_jd"])
            k3.metric("Matched", len(analysis["matched"]))
            k4.metric("Missing", len(analysis["missing"]))

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(gauge_chart(analysis["match_pct"]), use_container_width=True)
            with c2:
                st.plotly_chart(bar_matched_missing_extra(analysis), use_container_width=True)

            st.markdown("---")
            c3, c4 = st.columns(2)
            with c3:
                st.subheader("Resume skill categories")
                st.plotly_chart(category_pie(r_skills, "Resume skill distribution"), use_container_width=True)
            with c4:
                st.subheader("JD skill categories")
                st.plotly_chart(category_pie(j_skills, "JD skill distribution"), use_container_width=True)

            st.markdown("---")
            l1, l2, l3 = st.columns(3)
            with l1:
                st.subheader("Matched skills")
                for s in analysis["matched"][:20]:
                    st.write(f"✅ {s}")
            with l2:
                st.subheader("Missing skills")
                for s in analysis["missing"][:20]:
                    st.write(f"❌ {s}")
            with l3:
                st.subheader("Extra resume skills")
                for s in analysis["extra"][:20]:
                    st.write(f"➕ {s}")

            st.markdown("---")
            pdf_buf = build_pdf(analysis, r_skills, j_skills)
            st.download_button(
                "📥 Download PDF report",
                data=pdf_buf,
                file_name=f"skillgap_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    # --------------------------------------------------------------
    # TAB 3 – ADVANCED CHARTS
    # --------------------------------------------------------------
    with tab_advanced:
        if "analysis" not in st.session_state:
            st.info("Run an analysis in the **Upload & Analyze** tab first.")
        else:
            analysis = st.session_state["analysis"]
            res_list = st.session_state["resume_list"]
            jd_list = st.session_state["jd_list"]
            sim_matrix = st.session_state["sim_matrix"]

            st.subheader("🔍 Sentence‑BERT similarity heatmap")
            st.plotly_chart(heatmap_similarity(res_list, jd_list, sim_matrix), use_container_width=True)

            st.markdown("---")
            st.subheader("📌 Prioritized gap ranking")
            st.plotly_chart(gap_ranking_bar(analysis["gap_rank"]), use_container_width=True)

            st.markdown("---")
            st.subheader("📈 Skill timeline")
            st.plotly_chart(timeline_chart(analysis), use_container_width=True)

            st.markdown("---")
            csv = pd.DataFrame(analysis["gap_rank"]).to_csv(index=False)
            st.download_button("Download gaps as CSV", csv, "skill_gaps.csv", "text/csv")

    # --------------------------------------------------------------
    # TAB 4 – HISTORY
    # --------------------------------------------------------------
    with tab_history:
        st.subheader("Recent analyses")
        rows = load_history(user)
        if not rows:
            st.info("No history yet – run your first analysis!")
        else:
            for rid, created, match_pct, payload in rows:
                with st.expander(f"#{rid} • {created} • {match_pct:.1f}% match"):
                    data = json.loads(payload)
                    st.write(f"Matched: {len(data['matched'])}, Missing: {len(data['missing'])}")
                    st.write("Sample matched skills:", ", ".join(data["matched"][:10]))
                    st.write("Sample missing skills:", ", ".join(data["missing"][:10]))


if __name__ == "__main__":
    main()
