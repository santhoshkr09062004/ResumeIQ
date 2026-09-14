from app.utils.matcher import (
    extract_skills,
    match_skills,
    calculate_text_similarity,
    calculate_final_score
)


resume_text = """
Electronics and Communication Engineering student
with strong skills in Python, SQL, C++, Data Structures
and Algorithms. Experienced in ESP32, IoT, Arduino,
real-time data monitoring and system integration.
"""


job_description = """
We are looking for a Python developer with strong SQL,
Data Structures and Git skills. Experience with FastAPI,
REST API and data processing is preferred.
"""


resume_skills = extract_skills(resume_text)

job_skills = extract_skills(job_description)


matched, missing = match_skills(
    resume_skills,
    job_skills
)


similarity_score = calculate_text_similarity(
    resume_text,
    job_description
)


final_score = calculate_final_score(
    matched,
    job_skills,
    similarity_score
)


print("Resume Skills:")
print(resume_skills)

print("\nJob Skills:")
print(job_skills)

print("\nMatched Skills:")
print(matched)

print("\nMissing Skills:")
print(missing)

print("\nText Similarity Score:")
print(f"{similarity_score}%")

print("\nFinal Match Score:")
print(f"{final_score}%")