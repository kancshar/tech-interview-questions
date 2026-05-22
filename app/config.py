"""
Configuration constants for the Interview Question Generator.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Output directory for generated markdown files
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

# Default question counts per category based on seniority
QUESTION_COUNTS = {
    "junior": 3,
    "mid": 4,
    "senior": 5,
    "staff": 5,
}

# Seniority mapping from years of experience
SENIORITY_THRESHOLDS = {
    (0, 2): "junior",
    (2, 5): "mid",
    (5, 10): "senior",
    (10, 100): "staff",
}


def get_seniority(years: int) -> str:
    """Determine seniority level from years of experience."""
    for (low, high), level in SENIORITY_THRESHOLDS.items():
        if low <= years < high:
            return level
    return "staff"
