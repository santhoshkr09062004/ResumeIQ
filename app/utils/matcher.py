import re

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "Python",
    "C++",
    "Java",
    "SQL",

    "Object-Oriented Programming",
    "OOP",
    "Data Structures",
    "Algorithms",
    "Data Structures and Algorithms",

    "HTML",
    "CSS",
    "JavaScript",
    "FastAPI",
    "Flask",
    "Django",
    "REST API",

    "MySQL",
    "MongoDB",

    "Pandas",
    "NumPy",
    "Scikit-learn",

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",

    "ESP32",
    "Arduino",
    "Arduino IDE",
    "IoT",
    "Sensor Interfacing",
    "DHT11",
    "MQ-2",
    "Soil Moisture",

    "UART",
    "I2C",
    "SPI",

    "Git",
    "GitHub",
    "Visual Studio Code",
    "MATLAB",

    "Cloud Computing",
    "Real-Time Data Monitoring",
    "Data Handling",
    "System Integration",
    "Automation",
]


SKILL_ALIASES = {
    "oop": "Object-Oriented Programming",
    "object-oriented programming": "Object-Oriented Programming",
    "object oriented programming": "Object-Oriented Programming",
    "dsa": "Data Structures and Algorithms",
    "data structures and algorithms": "Data Structures and Algorithms",
    "data structures & algorithms": "Data Structures and Algorithms",
    "data structures & algorithm": "Data Structures and Algorithms",
}


def skill_found_in_text(skill, text):
    text_lower = text.lower()
    skill_lower = skill.lower().strip()

    if skill_lower == "c++":
        pattern = r"(?<!\w)c\+\+(?!\w)"

    elif skill_lower == "mq-2":
        pattern = r"(?<!\w)mq[-\s]?2(?!\w)"

    elif skill_lower == "git":
        pattern = r"(?<!\w)git(?!hub)(?!\w)"

    elif skill_lower == "github":
        pattern = r"(?<!\w)github(?!\w)"

    elif skill_lower == "data structures and algorithms":
        pattern = (
            r"(?<!\w)"
            r"(?:data\s+structures\s*(?:and|&)\s*algorithms|dsa)"
            r"(?!\w)"
        )

    else:
        escaped_skill = re.escape(skill_lower)
        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(pattern, text_lower) is not None


def normalize_skills(skills):
    normalized = []

    for skill in skills:
        skill_lower = skill.lower().strip()

        canonical_skill = SKILL_ALIASES.get(
            skill_lower,
            skill
        )

        if canonical_skill not in normalized:
            normalized.append(canonical_skill)

    if (
        "Data Structures" in normalized
        and "Algorithms" in normalized
    ):
        normalized.remove("Data Structures")
        normalized.remove("Algorithms")

        if "Data Structures and Algorithms" not in normalized:
            normalized.append("Data Structures and Algorithms")

    return normalized


def extract_skills(text):
    found_skills = []

    for skill in SKILLS:

        if skill_found_in_text(skill, text):

            canonical_skill = SKILL_ALIASES.get(
                skill.lower(),
                skill
            )

            if canonical_skill not in found_skills:
                found_skills.append(canonical_skill)

    return normalize_skills(found_skills)


def skill_exists(skill, resume_skills):

    if skill in resume_skills:
        return True

    if skill == "Object-Oriented Programming":
        return (
            "OOP" in resume_skills
            or "Object-Oriented Programming" in resume_skills
        )

    if skill == "Data Structures and Algorithms":

        if "Data Structures and Algorithms" in resume_skills:
            return True

        if (
            "Data Structures" in resume_skills
            and "Algorithms" in resume_skills
        ):
            return True

    return False


def match_skills(
    resume_skills,
    job_skills,
    threshold=80
):
    resume_skills = normalize_skills(resume_skills)
    job_skills = normalize_skills(job_skills)

    matched = []
    missing = []

    for job_skill in job_skills:

        if skill_exists(
            job_skill,
            resume_skills
        ):

            if job_skill not in matched:
                matched.append(job_skill)

            continue

        best_score = 0

        for resume_skill in resume_skills:

            score = fuzz.ratio(
                job_skill.lower(),
                resume_skill.lower()
            )

            if score > best_score:
                best_score = score

        if best_score >= threshold:

            if job_skill not in matched:
                matched.append(job_skill)

        else:

            if job_skill not in missing:
                missing.append(job_skill)

    return matched, missing


def calculate_text_similarity(
    resume_text,
    job_description
):
    documents = [
        resume_text,
        job_description
    ]

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(
        documents
    )

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )

    score = similarity[0][0] * 100

    return round(score, 2)


def calculate_final_score(
    matched_skills,
    job_skills,
    text_similarity
):
    job_skills = normalize_skills(job_skills)
    matched_skills = normalize_skills(matched_skills)

    if len(job_skills) == 0:
        skill_score = 0

    else:
        skill_score = (
            len(matched_skills)
            / len(job_skills)
        ) * 100

    final_score = (
        skill_score * 0.70
        + text_similarity * 0.30
    )

    return round(final_score, 2)


SKILL_SUGGESTIONS = {
    "JavaScript":
        "Learn JavaScript fundamentals, DOM manipulation and browser scripting.",

    "FastAPI":
        "Learn FastAPI with Python and build REST APIs.",

    "REST API":
        "Learn HTTP methods, JSON, API requests, responses and REST principles.",

    "Machine Learning":
        "Learn supervised learning, unsupervised learning and basic scikit-learn algorithms.",

    "Git":
        "Learn Git basics including commit, branch, merge, pull and push.",

    "Cloud Computing":
        "Learn cloud fundamentals such as deployment, storage, networking and virtual machines.",

    "Java":
        "Learn Java fundamentals, OOP, collections and exception handling.",

    "Django":
        "Learn Django fundamentals and build web applications using Python.",

    "Flask":
        "Learn Flask and build lightweight Python web applications and APIs.",

    "MongoDB":
        "Learn NoSQL concepts and MongoDB CRUD operations.",

    "Pandas":
        "Learn Pandas for data manipulation, cleaning and analysis.",

    "NumPy":
        "Learn NumPy arrays, indexing, mathematical operations and numerical computing.",

    "Scikit-learn":
        "Learn scikit-learn for machine learning model training and evaluation.",

    "Deep Learning":
        "Learn neural networks and deep learning fundamentals.",

    "Artificial Intelligence":
        "Learn AI fundamentals including search, reasoning and machine learning.",

    "UART":
        "Learn UART serial communication and microcontroller interfacing.",

    "I2C":
        "Learn I2C communication and sensor interfacing.",

    "SPI":
        "Learn SPI communication and peripheral interfacing."
}


def generate_suggestions(missing_skills):
    suggestions = []

    for skill in missing_skills:

        suggestion = SKILL_SUGGESTIONS.get(
            skill,
            f"Consider learning {skill} and adding a relevant project or experience to your resume."
        )

        suggestions.append({
            "skill": skill,
            "suggestion": suggestion
        })

    return suggestions


# =========================================================
# ATS COMPATIBILITY ANALYSIS
# =========================================================

def calculate_ats_score(
    resume_text,
    resume_skills,
    job_skills
):
    """
    Calculates a project-defined ATS Compatibility Score.

    Structure  = 40%
    Keywords   = 50%
    Text       = 10%

    This is NOT an official ATS score.
    """

    # -----------------------------------------------------
    # NORMALIZE RESUME TEXT
    # -----------------------------------------------------

    lines = []

    for line in resume_text.splitlines():

        line = line.strip().lower()

        if line:
            lines.append(line)

    # -----------------------------------------------------
    # CONTACT INFORMATION
    # -----------------------------------------------------

    email_found = re.search(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        resume_text
    ) is not None

    phone_found = re.search(
        r"(\+?\d[\d\s\-()]{8,}\d)",
        resume_text
    ) is not None

    if email_found or phone_found:

        checks = [{
            "name": "Contact Information",
            "status": "pass",
            "message": "Contact information detected in the resume."
        }]

    else:

        checks = [{
            "name": "Contact Information",
            "status": "warning",
            "message": "Email or phone number was not detected."
        }]

    # -----------------------------------------------------
    # SECTION DETECTION
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # Check complete lines/headings.
    #
    # This prevents "Experienced" in the profile from
    # being incorrectly treated as an Experience section.
    # -----------------------------------------------------

    sections = {

        "Skills Section": [
            "skills",
            "technical skills",
            "core skills"
        ],

        "Education Section": [
            "education",
            "educational background",
            "academic background",
            "qualification",
            "qualifications"
        ],

        "Projects Section": [
            "projects",
            "project"
        ],

        "Experience Section": [
            "experience",
            "work experience",
            "professional experience",
            "employment history",
            "work history"
        ],

        "Certifications Section": [
            "certifications",
            "certification",
            "courses",
            "training"
        ]
    }

    section_results = {}

    for section_name, keywords in sections.items():

        found = False

        for line in lines:

            clean_line = line.strip(
                ":-•·*#_ "
            )

            if clean_line in keywords:

                found = True
                break

        section_results[section_name] = found

        if found:

            checks.append({
                "name": section_name,
                "status": "pass",
                "message": f"{section_name} detected."
            })

        else:

            checks.append({
                "name": section_name,
                "status": "warning",
                "message": f"{section_name} was not detected."
            })

    # -----------------------------------------------------
    # KEYWORD ANALYSIS
    # -----------------------------------------------------
    #
    # Reuse ResumeIQ's skill normalization and matching.
    #
    # This correctly handles:
    # Data Structures & Algorithms
    # Data Structures and Algorithms
    # DSA
    # -----------------------------------------------------

    normalized_resume_skills = normalize_skills(
        resume_skills
    )

    normalized_job_skills = normalize_skills(
        job_skills
    )

    matched_job_keywords = []
    missing_job_keywords = []

    for job_skill in normalized_job_skills:

        if skill_exists(
            job_skill,
            normalized_resume_skills
        ):

            if job_skill not in matched_job_keywords:
                matched_job_keywords.append(
                    job_skill
                )

        else:

            if job_skill not in missing_job_keywords:
                missing_job_keywords.append(
                    job_skill
                )

    # -----------------------------------------------------
    # STRUCTURE SCORE
    # -----------------------------------------------------

    total_structure_checks = 6

    passed_structure_checks = 0

    if email_found or phone_found:
        passed_structure_checks += 1

    for section_name in sections:

        if section_results[section_name]:
            passed_structure_checks += 1

    structure_score = (
        passed_structure_checks
        / total_structure_checks
    ) * 100

    # -----------------------------------------------------
    # KEYWORD SCORE
    # -----------------------------------------------------

    if len(normalized_job_skills) == 0:

        keyword_score = 100

    else:

        keyword_score = (
            len(matched_job_keywords)
            / len(normalized_job_skills)
        ) * 100

    # -----------------------------------------------------
    # TEXT QUALITY SCORE
    # -----------------------------------------------------

    word_count = len(
        resume_text.split()
    )

    if word_count >= 150:

        text_quality_score = 100

    elif word_count >= 80:

        text_quality_score = 75

    elif word_count >= 40:

        text_quality_score = 50

    else:

        text_quality_score = 25

    # -----------------------------------------------------
    # FINAL ATS SCORE
    # -----------------------------------------------------

    ats_score = (
        structure_score * 0.40
        + keyword_score * 0.50
        + text_quality_score * 0.10
    )

    return {

        "ats_score": round(
            ats_score,
            2
        ),

        "checks": checks,

        "missing_keywords":
            missing_job_keywords,

        "structure_score":
            round(
                structure_score,
                2
            ),

        "keyword_score":
            round(
                keyword_score,
                2
            ),

        "text_quality_score":
            round(
                text_quality_score,
                2
            )
    }
