import copy

from pydantic import ValidationError

from cv_schema import CVProfile

# The ONE complete CV. Every other case copies it and changes one thing.
cv_full = {
    "headline": "Junior Data Analyst",
    "experience": [{
        "title": "Data Intern",
        "company": "Kemet Retail",
        "start": "2025-06",
        "end": "2025-09",
        "is_internship": True,
        "skills_used": ["Excel", "Power BI"],
    }],
    "projects": [{
        "name": "Sales Dashboard",
        "description": "Power BI report for 40 stores",
        "skills_used": ["Power BI", "DAX"],
    }],
    "education": [{
        "degree": "Bachelor of Commerce",
        "institution": "Cairo University",
        "field_of_study": "Accounting",
        "graduation_year": 2024,
    }],
    "certifications": [{
        "name": "Data Analysis Track",
        "year": 2025,
        "status": "in_progress",
        "skills_mentioned": [],
    }],
    "skills": [{"name": "SQL", "level": "basic", "source": "skills_section"}],
}


def should_pass(name, cv):
    try:
        CVProfile.model_validate(cv)
        print(f"PASSED  {name}")
    except ValidationError as error:
        print(f"FAILED  {name}\n{error}")


def should_fail(name, cv):
    try:
        CVProfile.model_validate(cv)
        print(f"FAILED  {name}: it was accepted")
    except ValidationError:
        print(f"PASSED  {name}")


# case 1: the complete CV is accepted
should_pass("case 1: complete CV accepted", cv_full)

# case 2: things the CV does not say are null, and that is accepted
cv_2 = copy.deepcopy(cv_full)
cv_2["education"][0]["graduation_year"] = None
cv_2["certifications"][0]["year"] = None
cv_2["experience"][0]["start"] = None
should_pass("case 2: unknown values as null accepted", cv_2)

# case 3: a job with no "start" field at all is rejected
cv_3 = copy.deepcopy(cv_full)
del cv_3["experience"][0]["start"]
should_fail("case 3: job without 'start' rejected", cv_3)

# case 4: a skill level outside the list is rejected
cv_4 = copy.deepcopy(cv_full)
cv_4["skills"][0]["level"] = "expert"
should_fail("case 4: unknown skill level rejected", cv_4)