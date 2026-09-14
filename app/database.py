import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()


def get_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "resumeiq"),
        port=int(os.getenv("DB_PORT", "3306"))
    )

    return connection


# =========================================================
# SAVE ANALYSIS
# =========================================================

def save_analysis(
    filename,
    final_score,
    ats_score,
    text_similarity,
    matched_count,
    missing_count,
    required_count
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO analyses (
            filename,
            final_score,
            ats_score,
            text_similarity,
            matched_count,
            missing_count,
            required_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        filename,
        final_score,
        ats_score,
        text_similarity,
        matched_count,
        missing_count,
        required_count
    )

    cursor.execute(
        query,
        values
    )

    connection.commit()

    cursor.close()

    connection.close()


# =========================================================
# GET ANALYSIS HISTORY
# =========================================================

def get_analysis_history():

    connection = get_connection()

    cursor = connection.cursor(
        dictionary=True
    )

    query = """
        SELECT
            id,
            filename,
            final_score,
            ats_score,
            text_similarity,
            matched_count,
            missing_count,
            required_count,
            created_at
        FROM analyses
        ORDER BY id DESC
    """

    cursor.execute(query)

    results = cursor.fetchall()

    cursor.close()

    connection.close()

    return results