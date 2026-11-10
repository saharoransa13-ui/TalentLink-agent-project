"""Skills that are only listed (skills line or table) get a small partial credit."""

from backend.extractor import extract_candidate_profile
from backend.main import load_roles
from backend.skill_engine import LISTED_ONLY_SCORE, calculate_gaps

LISTED_CV = (
    "Sara Ahmed\n"
    "Skills: Python, SQL, PostgreSQL, Docker, FastAPI\n"
    "Experience: Customer support agent at a telecom company, handled tickets."
)
USED_CV = (
    "Omar Hassan - Backend Developer\n"
    "Developed REST APIs with FastAPI and Django for an e-commerce platform.\n"
    "Designed PostgreSQL schemas and optimized SQL queries.\n"
    "Deployed services with Docker on AWS EC2."
)


def _gaps(cv_text, role_id="backend_developer"):
    profile = extract_candidate_profile(cv_text)
    return calculate_gaps(profile, load_roles()[role_id])


def test_listed_skill_is_partial_not_missing():
    score, gaps = _gaps(LISTED_CV)
    python_gap = next(g for g in gaps if g.skill_id == "python")
    assert python_gap.status == "partial"
    assert python_gap.evidence[0].startswith("Listed only")
    assert 0 < score < 50


def test_listed_only_scores_less_than_real_use():
    listed_score, _ = _gaps(LISTED_CV)
    used_score, _ = _gaps(USED_CV)
    assert listed_score < used_score


def test_listed_only_credit_is_small():
    assert 0 < LISTED_ONLY_SCORE < 0.5
