from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import timezone, timedelta

import shutil
import os
os.makedirs("uploads", exist_ok=True)

from app.utils.resume_parser import extract_text_from_pdf

from app.utils.matcher import (
    extract_skills,
    match_skills,
    calculate_text_similarity,
    calculate_final_score,
    generate_suggestions,
    calculate_ats_score
)

from app.database import (
    save_analysis,
    get_analysis_history
)


app = FastAPI(
    title="ResumeIQ",
    description="Intelligent Resume Analysis and Job Matching System",
    version="1.0.0"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/", response_class=HTMLResponse)
def home():

    with open(
        "templates/index.html",
        "r",
        encoding="utf-8"
    ) as file:

        html_content = file.read()

    return html_content


# =========================================================
# ANALYSIS HISTORY PAGE
# =========================================================

@app.get("/history", response_class=HTMLResponse)
def history():

    analyses = get_analysis_history()

    rows = ""

    for analysis in analyses:

        created_at = analysis["created_at"]

        if created_at:
            ist = timezone(timedelta(hours=5, minutes=30))
            created_at = created_at.replace(tzinfo=timezone.utc).astimezone(ist)

            created_at = created_at.strftime(
                "%d %b %Y, %I:%M %p"
            )

        rows += f"""
        <tr>
            <td class="mono">{analysis["id"]}</td>

            <td>{analysis["filename"]}</td>

            <td>
                <strong class="score-pill">
                    {analysis["final_score"]}%
                </strong>
            </td>

            <td>
                <strong class="ats-pill">
                    {analysis["ats_score"] if analysis["ats_score"] is not None else "—"}
                </strong>
            </td>

            <td class="mono">
                {(analysis["matched_count"] / analysis["required_count"] * 100) if analysis["required_count"] else 0:.2f}%
            </td>

            <td class="mono">
                {analysis["matched_count"]}
            </td>

            <td class="mono">
                {analysis["missing_count"]}
            </td>

            <td class="mono">
                {analysis["required_count"]}
            </td>

            <td>
                {created_at}
            </td>
        </tr>
        """

    if not rows:

        rows = """
        <tr>
            <td colspan="8" class="no-data">
                No analysis history available.
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>

    <html lang="en">

    <head>

        <meta charset="UTF-8">

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        >

        <title>ResumeIQ - Analysis History</title>

        <link
            rel="preconnect"
            href="https://fonts.googleapis.com"
        >

        <link
            rel="preconnect"
            href="https://fonts.gstatic.com"
            crossorigin
        >

        <link
            href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
            rel="stylesheet"
        >

        <style>

            :root {{
                --ink: #12141C;
                --slate: #5B6472;
                --line: #E1E4EC;
                --paper: #F5F6FA;
                --surface: #FFFFFF;
                --blue: #2A4FE0;
                --blue-soft: #EDF0FE;
                --green: #12704E;
                --green-soft: #E7F5EE;
                --font-sans: "IBM Plex Sans", Arial, sans-serif;
                --font-mono: "IBM Plex Mono", Consolas, monospace;
            }}

            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: var(--font-sans);
                background: var(--paper);
                color: var(--ink);
            }}

            .topbar {{
                background: var(--surface);
                border-bottom: 1px solid var(--line);
            }}

            .topbar-inner {{
                width: 92%;
                max-width: 1120px;
                margin: auto;
                padding: 20px 0;
                display: flex;
                align-items: baseline;
                gap: 14px;
                flex-wrap: wrap;
            }}

            .brand {{
                font-size: 21px;
                font-weight: 700;
                letter-spacing: -0.02em;
                text-decoration: none;
                color: var(--ink);
            }}

            .brand span {{
                color: var(--blue);
            }}

            .brand-tag {{
                color: var(--slate);
                font-size: 14px;
                flex: 1;
            }}

            .nav-link {{
                text-decoration: none;
                font-size: 14px;
                font-weight: 600;
                color: var(--ink);
                padding: 9px 16px;
                border: 1px solid var(--line);
                border-radius: 999px;
                white-space: nowrap;
            }}

            .nav-link:hover {{
                border-color: var(--blue);
                background: var(--blue-soft);
            }}

            .container {{
                width: 92%;
                max-width: 1120px;
                margin: 36px auto 60px;
            }}

            .page-title h1 {{
                font-size: 25px;
                font-weight: 700;
                margin-bottom: 4px;
            }}

            .page-title p {{
                color: var(--slate);
                font-size: 14px;
                margin-bottom: 22px;
            }}

            .history-card {{
                background: var(--surface);
                border: 1px solid var(--line);
                border-radius: 14px;
                overflow-x: auto;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 900px;
            }}

            th {{
                background: var(--paper);
                padding: 14px 16px;
                text-align: left;
                font-size: 12.5px;
                font-weight: 600;
                color: var(--slate);
                border-bottom: 1px solid var(--line);
            }}

            td {{
                padding: 14px 16px;
                border-bottom: 1px solid var(--line);
                font-size: 14px;
            }}

            .mono {{
                font-family: var(--font-mono);
                font-size: 13px;
            }}

            .score-pill {{
                font-family: var(--font-mono);
                background: var(--green-soft);
                color: var(--green);
                padding: 4px 9px;
                border-radius: 6px;
                font-size: 13px;
            }}

            tr:last-child td {{
                border-bottom: none;
            }}

            tr:hover {{
                background: #FAFBFD;
            }}

            .no-data {{
                text-align: center;
                padding: 48px 20px;
                color: var(--slate);
            }}

            @media (max-width: 700px) {{

                .container {{
                    width: 94%;
                }}

            }}

        </style>

    </head>


    <body>

        <header class="topbar">

            <div class="topbar-inner">

                <a href="/" class="brand">
                    Resume<span>IQ</span>
                </a>

                <p class="brand-tag">
                    Intelligent resume &amp; job matching
                </p>

                <a href="/" class="nav-link">
                    ← Analyze resume
                </a>

            </div>

        </header>


        <div class="container">

            <div class="page-title">

                <h1>
                    Analysis history
                </h1>

                <p>
                    Previous ResumeIQ analyses, stored in MySQL.
                </p>

            </div>


            <div class="history-card">

                <table>

                    <thead>

                        <tr>

                            <th>ID</th>
                            <th>Resume</th>
                            <th>Final score</th>
                            <th>ATS score</th>
                            <th>Skill Match</th>
                            <th>Matched</th>
                            <th>Missing</th>
                            <th>Required</th>
                            <th>Date</th>

                        </tr>

                    </thead>


                    <tbody>

                        {rows}

                    </tbody>

                </table>

            </div>

        </div>

    </body>

    </html>
    """

    return html


# =========================================================
# RESUME ANALYSIS
# =========================================================

@app.post("/analyze-resume")
def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    # -----------------------------------------------------
    # Save uploaded resume
    # -----------------------------------------------------

    file_path = f"uploads/{file.filename}"

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # -----------------------------------------------------
    # Extract resume text
    # -----------------------------------------------------

    resume_text = extract_text_from_pdf(
        file_path
    )

    # -----------------------------------------------------
    # Extract skills
    # -----------------------------------------------------

    resume_skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    # -----------------------------------------------------
    # Match skills
    # -----------------------------------------------------

    matched_skills, missing_skills = match_skills(
        resume_skills,
        job_skills
    )

    # -----------------------------------------------------
    # Calculate text similarity
    # -----------------------------------------------------

    text_similarity = calculate_text_similarity(
        resume_text,
        job_description
    )

    # -----------------------------------------------------
    # Calculate final score
    # -----------------------------------------------------

    final_score = calculate_final_score(
        matched_skills,
        job_skills,
        text_similarity
    )

    # -----------------------------------------------------
    # Generate suggestions
    # -----------------------------------------------------

    suggestions = generate_suggestions(
        missing_skills
    )

    # -----------------------------------------------------
    # ATS COMPATIBILITY
    # -----------------------------------------------------

    ats_analysis = calculate_ats_score(
        resume_text,
        resume_skills,
        job_skills
    )

    # -----------------------------------------------------
    # Count skills
    # -----------------------------------------------------

    matched_count = len(
        matched_skills
    )

    missing_count = len(
        missing_skills
    )

    required_count = len(
        job_skills
    )

    # -----------------------------------------------------
    # SAVE RESULT TO MYSQL
    # -----------------------------------------------------

    save_analysis(
        filename=file.filename,
        final_score=final_score,
        ats_score=ats_analysis["ats_score"],
        text_similarity=text_similarity,
        matched_count=matched_count,
        missing_count=missing_count,
        required_count=required_count
    )

    # -----------------------------------------------------
    # RETURN RESULT
    # -----------------------------------------------------

    return {

        "filename":
            file.filename,

        "resume_skills":
            resume_skills,

        "job_skills":
            job_skills,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "text_similarity":
            text_similarity,

        "final_score":
            final_score,

        "suggestions":
            suggestions,

        "ats_analysis":
            ats_analysis
    }
