import re

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# =========================================================
# PREDEFINED SKILLS
# =========================================================

SKILLS = [

    # -----------------------------------------------------
    # Programming Languages
    # -----------------------------------------------------

    "Python",
    "C++",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C#",
    "PHP",
    "Go",
    "Rust",

    # -----------------------------------------------------
    # Programming Concepts
    # -----------------------------------------------------

    "Object-Oriented Programming",
    "OOP",
    "Data Structures",
    "Algorithms",
    "Data Structures and Algorithms",
    "Problem Solving",

    # -----------------------------------------------------
    # Web Development
    # -----------------------------------------------------

    "HTML",
    "CSS",
    "JavaScript",
    "React",
    "Node.js",
    "Express.js",
    "TypeScript",
    "Django",
    "Flask",
    "FastAPI",
    "REST API",
    "GraphQL",
    "API Development",

    # -----------------------------------------------------
    # Databases
    # -----------------------------------------------------

    "SQL",
    "MySQL",
    "PostgreSQL",
    "SQLite",
    "Oracle",
    "MongoDB",
    "Redis",

    # -----------------------------------------------------
    # Data Science / Analytics
    # -----------------------------------------------------

    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Scikit-learn",
    "Jupyter",
    "Microsoft Excel",
    "Power BI",
    "Tableau",

    # -----------------------------------------------------
    # Artificial Intelligence / Machine Learning
    # -----------------------------------------------------

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "TensorFlow",
    "PyTorch",
    "OpenCV",

    # -----------------------------------------------------
    # Cloud Computing
    # -----------------------------------------------------

    "Cloud Computing",
    "AWS",
    "Microsoft Azure",
    "Google Cloud",

    # -----------------------------------------------------
    # DevOps / Deployment
    # -----------------------------------------------------

    "Docker",
    "Kubernetes",
    "CI/CD",

    # -----------------------------------------------------
    # Version Control
    # -----------------------------------------------------

    "Git",
    "GitHub",
    "GitLab",

    # -----------------------------------------------------
    # Testing
    # -----------------------------------------------------

    "PyTest",
    "Unit Testing",

    # -----------------------------------------------------
    # Big Data
    # -----------------------------------------------------

    "Apache Spark",
    "Hadoop",

    # -----------------------------------------------------
    # Tools & Platforms
    # -----------------------------------------------------

    "Visual Studio Code",
    "MATLAB",
    "Arduino",
    "Arduino IDE",

    # -----------------------------------------------------
    # IoT / Embedded Systems
    # -----------------------------------------------------

    "ESP32",
    "IoT",
    "Embedded Systems",
    "Sensor Interfacing",
    "DHT11",
    "MQ-2",
    "Soil Moisture",

    # -----------------------------------------------------
    # Communication Protocols
    # -----------------------------------------------------

    "UART",
    "I2C",
    "SPI",

    # -----------------------------------------------------
    # Other Technical Skills
    # -----------------------------------------------------

    "Real-Time Data Monitoring",
    "Data Handling",
    "Data Processing",
    "System Integration",
    "Automation",

]


# =========================================================
# SKILL ALIASES
# =========================================================

SKILL_ALIASES = {

    "oop":
        "Object-Oriented Programming",

    "object-oriented programming":
        "Object-Oriented Programming",

    "object oriented programming":
        "Object-Oriented Programming",

    "dsa":
        "Data Structures and Algorithms",

    "data structures and algorithms":
        "Data Structures and Algorithms",

    "data structures & algorithms":
        "Data Structures and Algorithms",

    "data structures & algorithm":
        "Data Structures and Algorithms",

    "ai":
        "Artificial Intelligence",

    "ml":
        "Machine Learning",

    "js":
        "JavaScript",

    "ts":
        "TypeScript",

    "postgres":
        "PostgreSQL",

    "postgresql":
        "PostgreSQL",

    "gcp":
        "Google Cloud",

}


# =========================================================
# SKILL DETECTION
# =========================================================

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

    elif skill_lower == "rest api":
        pattern = r"(?<!\w)rest\s+apis?(?!\w)"

    elif skill_lower == "data structures and algorithms":

        pattern = (
            r"(?<!\w)"
            r"(?:data\s+structures\s*(?:and|&)\s*algorithms|dsa)"
            r"(?!\w)"
        )

    else:

        escaped_skill = re.escape(skill_lower)

        pattern = rf"(?<!\w){escaped_skill}(?!\w)"

    return re.search(
        pattern,
        text_lower
    ) is not None


# =========================================================
# NORMALIZE SKILLS
# =========================================================

def normalize_skills(skills):

    normalized = []

    for skill in skills:

        skill_lower = skill.lower().strip()

        canonical_skill = SKILL_ALIASES.get(
            skill_lower,
            skill
        )

        if canonical_skill not in normalized:

            normalized.append(
                canonical_skill
            )

    # -----------------------------------------------------
    # Combine Data Structures + Algorithms
    # -----------------------------------------------------

    if (
        "Data Structures" in normalized
        and "Algorithms" in normalized
    ):

        normalized.remove(
            "Data Structures"
        )

        normalized.remove(
            "Algorithms"
        )

        if (
            "Data Structures and Algorithms"
            not in normalized
        ):

            normalized.append(
                "Data Structures and Algorithms"
            )

    return normalized


# =========================================================
# EXTRACT SKILLS
# =========================================================

def extract_skills(text):

    found_skills = []

    for skill in SKILLS:

        if skill_found_in_text(
            skill,
            text
        ):

            canonical_skill = SKILL_ALIASES.get(
                skill.lower(),
                skill
            )

            if canonical_skill not in found_skills:

                found_skills.append(
                    canonical_skill
                )

    return normalize_skills(
        found_skills
    )


# =========================================================
# CHECK WHETHER SKILL EXISTS
# =========================================================

def skill_exists(
    skill,
    resume_skills
):

    if skill in resume_skills:

        return True

    if skill == "Object-Oriented Programming":

        return (
            "OOP" in resume_skills
            or
            "Object-Oriented Programming"
            in resume_skills
        )

    if skill == "Data Structures and Algorithms":

        if (
            "Data Structures and Algorithms"
            in resume_skills
        ):

            return True

        if (
            "Data Structures"
            in resume_skills
            and
            "Algorithms"
            in resume_skills
        ):

            return True

    return False


# =========================================================
# MATCH SKILLS
# =========================================================

def match_skills(
    resume_skills,
    job_skills,
    threshold=80
):

    resume_skills = normalize_skills(
        resume_skills
    )

    job_skills = normalize_skills(
        job_skills
    )

    matched = []
    missing = []

    for job_skill in job_skills:

        if skill_exists(
            job_skill,
            resume_skills
        ):

            if job_skill not in matched:

                matched.append(
                    job_skill
                )

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

                matched.append(
                    job_skill
                )

        else:

            if job_skill not in missing:

                missing.append(
                    job_skill
                )

    return matched, missing


# =========================================================
# TEXT SIMILARITY
# =========================================================

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

    return round(
        score,
        2
    )


# =========================================================
# FINAL MATCH SCORE
# =========================================================

def calculate_final_score(
    matched_skills,
    job_skills,
    text_similarity
):

    job_skills = normalize_skills(
        job_skills
    )

    matched_skills = normalize_skills(
        matched_skills
    )

    if len(job_skills) == 0:

        skill_score = 0

    else:

        skill_score = (
            len(matched_skills)
            /
            len(job_skills)
        ) * 100

    # -----------------------------------------------------
    # 70% Skill Match + 30% Text Similarity
    # -----------------------------------------------------

    final_score = (
        skill_score * 0.70
        +
        text_similarity * 0.30
    )

    return round(
        final_score,
        2
    )


# =========================================================
# SKILL SUGGESTIONS
# =========================================================

SKILL_SUGGESTIONS = {

    "JavaScript":
        "Learn JavaScript fundamentals, DOM manipulation and browser scripting.",

    "TypeScript":
        "Learn TypeScript fundamentals, types, interfaces and modern JavaScript development.",

    "React":
        "Learn React components, props, state, hooks and frontend development.",

    "Node.js":
        "Learn Node.js fundamentals and build backend applications using JavaScript.",

    "Express.js":
        "Learn Express.js and build REST APIs using Node.js.",

    "FastAPI":
        "Learn FastAPI with Python and build REST APIs.",

    "REST API":
        "Learn HTTP methods, JSON, API requests, responses and REST principles.",

    "GraphQL":
        "Learn GraphQL queries, mutations and API development.",

    "MySQL":
        "Learn MySQL database concepts, SQL queries, joins and database design.",

    "PostgreSQL":
        "Learn PostgreSQL, relational database concepts and advanced SQL queries.",

    "MongoDB":
        "Learn NoSQL concepts and MongoDB CRUD operations.",

    "Machine Learning":
        "Learn supervised learning, unsupervised learning and basic scikit-learn algorithms.",

    "Artificial Intelligence":
        "Learn AI fundamentals including search, reasoning and machine learning.",

    "Deep Learning":
        "Learn neural networks and deep learning fundamentals.",

    "TensorFlow":
        "Learn TensorFlow fundamentals and build machine learning and deep learning models.",

    "PyTorch":
        "Learn PyTorch for machine learning and deep learning model development.",

    "AWS":
        "Learn AWS fundamentals including EC2, S3, IAM and cloud deployment.",

    "Microsoft Azure":
        "Learn Azure cloud services, deployment and cloud infrastructure.",

    "Google Cloud":
        "Learn Google Cloud fundamentals and cloud deployment.",

    "Docker":
        "Learn Docker containers, images and containerized application deployment.",

    "Kubernetes":
        "Learn Kubernetes fundamentals, pods, deployments and container orchestration.",

    "Git":
        "Learn Git basics including commit, branch, merge, pull and push.",

    "GitLab":
        "Learn GitLab repositories, version control and CI/CD workflows.",

    "Power BI":
        "Learn Power BI dashboards, data visualization and business analytics.",

    "Tableau":
        "Learn Tableau dashboards, visualization and data analysis.",

    "Pandas":
        "Learn Pandas for data manipulation, cleaning and analysis.",

    "NumPy":
        "Learn NumPy arrays, indexing, mathematical operations and numerical computing.",

    "Scikit-learn":
        "Learn scikit-learn for machine learning model training and evaluation.",

    "OpenCV":
        "Learn OpenCV for image processing and computer vision.",

    "UART":
        "Learn UART serial communication and microcontroller interfacing.",

    "I2C":
        "Learn I2C communication and sensor interfacing.",

    "SPI":
        "Learn SPI communication and peripheral interfacing.",

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

    "Cloud Computing":
        "Learn cloud fundamentals such as deployment, storage, networking and virtual machines."
}


def generate_suggestions(
    missing_skills
):

    suggestions = []

    for skill in missing_skills:

        suggestion = SKILL_SUGGESTIONS.get(
            skill,
            f"Consider learning {skill} and adding a relevant project or experience to your resume."
        )

        suggestions.append({

            "skill":
                skill,

            "suggestion":
                suggestion

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

            lines.append(
                line
            )

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

            "name":
                "Contact Information",

            "status":
                "pass",

            "message":
                "Contact information detected in the resume."

        }]

    else:

        checks = [{

            "name":
                "Contact Information",

            "status":
                "warning",

            "message":
                "Email or phone number was not detected."

        }]

    # -----------------------------------------------------
    # SECTION DETECTION
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

        section_results[
            section_name
        ] = found

        if found:

            checks.append({

                "name":
                    section_name,

                "status":
                    "pass",

                "message":
                    f"{section_name} detected."

            })

        else:

            checks.append({

                "name":
                    section_name,

                "status":
                    "warning",

                "message":
                    f"{section_name} was not detected."

            })

    # -----------------------------------------------------
    # KEYWORD ANALYSIS
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

        if section_results[
            section_name
        ]:

            passed_structure_checks += 1

    structure_score = (
        passed_structure_checks
        /
        total_structure_checks
    ) * 100

    # -----------------------------------------------------
    # KEYWORD SCORE
    # -----------------------------------------------------

    if len(normalized_job_skills) == 0:

        keyword_score = 100

    else:

        keyword_score = (
            len(matched_job_keywords)
            /
            len(normalized_job_skills)
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
        +
        keyword_score * 0.50
        +
        text_quality_score * 0.10
    )

    return {

        "ats_score":
            round(
                ats_score,
                2
            ),

        "checks":
            checks,

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