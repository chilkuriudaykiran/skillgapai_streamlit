# skillgapai_streamlit
# SkillGapAI – Resume vs Job Description Skill Gap Analyzer

SkillGapAI is a Streamlit application that compares a candidate’s resume with a job description using modern NLP (Sentence‑BERT) to highlight missing skills, visualize gaps with interactive dashboards, and suggest upskilling paths.

---

## 1. Project Overview

SkillGapAI helps:

- **Job seekers** understand how well their resume matches a target role, which skills are missing, and where to focus learning.
- **Recruiters / hiring managers** quickly see candidate–role fit, key strengths, and critical gaps to discuss in interviews.

Core ideas:

- Clean and normalize resume & job‑description text.
- Extract skills (technical, data, and soft skills).
- Use sentence embeddings and cosine similarity to measure how close a candidate’s skill set is to the job.
- Display results in intuitive charts and dashboards inside a web UI.

---

## 2. UI Preview

### 2.1 Home page

![SkillGapAI Home](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/home.png)

The home page:

- Introduces the project and explains the purpose of SkillGapAI.
- Shows a hero section describing the AI‑based skill‑gap analysis.
- Provides **Login** and **Register** buttons for users to access the analyzer.

### 2.2 Login / Register

![Login Page](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/login.png)

The login screen:

- Centered login card with fields for **username/email** and **password**.
- “Don’t have an account? Register” button that opens the registration form.

![Register Page](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/register.png)

The registration screen:

- Centered register card with **username**, **email**, **password**, and **confirm password**.
- On successful registration the user can immediately log in and access the analyzer.

> How to use your own screenshots: create an `assets/` folder in the repo, add PNG/JPG files (home, login, register, analyzer), and update the URLs above to point to those files.

---

## 3. Analyzer Dashboards

### 3.1 Overall match & summary

![Overall Match Dashboard](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/overall_match.png)

This section typically includes:

- An **overall match gauge** showing the percentage alignment between resume and job description.
- A short text summary like “Your profile matches 72% of the required skills for Data Scientist – Junior”.
- Counts of **matched**, **partially matched**, and **missing** skills.

### 3.2 Skill category comparison

![Skill Category Bars](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/category_bars.png)

Bar charts show:

- Match percentage by category: e.g. Programming, Data & Analytics, Cloud, Databases, Soft Skills.
- Each bar compares how many skills you have versus how many are required for the job.
- Helps to quickly see which areas are strong vs weak.

### 3.3 Similarity heatmap

![Similarity Heatmap](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/heatmap.png)

The heatmap:

- Lists **resume skills** on one axis and **job skills** on the other.
- Color intensity represents cosine similarity (from low to high).
- Darker cells indicate stronger semantic matches between your skills and job requirements.

### 3.4 Missing skills & recommendations

![Missing Skills Chart](https://raw.githubusercontent.com/<your-username>/<your-repo-name>/main/assets/missing_skills.png)

This chart:

- Shows a bar chart of **top missing skills**, sorted by importance.
- Each bar may include an importance score or weight based on how often it appears in the JD.
- Used to drive upskilling recommendations (courses, topics, or projects to focus on).

---

## 4. Code Structure and Flow

### 4.1 Project structure

```text
.
├── app.py                 # Main Streamlit entry point (home, login, register, analyzer router)
├── users_db.py            # SQLite helper: init DB, create user, authenticate user
├── pages/
│   └── analyzer.py        # Analyzer page: file upload, NLP, charts, and reports
├── requirements.txt       # Python dependencies
├── .gitignore             # Ignore venv, DB, and temporary files
└── README.md              # Project documentation
