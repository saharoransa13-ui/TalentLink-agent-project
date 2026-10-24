from pydantic import ValidationError

from cv_schema import CVProfile


# ------------------------------------------------------------ case 1: a complete CV -> accepted
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
        "issuer": "DEPI",
        "year": 2025,
        "status": "in_progress",
    }],
    "skills": [{"name": "SQL", "source": "skills_section"}],
}

try:
    CVProfile.model_validate(cv_full)
    print("Case 1 PASSED: complete CV accepted")
except ValidationError as error:
    print("Case 1 FAILED:", error)


# ------------------------------------------------------------ case 2: a complete CV -> accepted
cv_full = {
    "headline": "Junior Data Analyst",
    "experience": [{
        "title": "Data Intern",
        "company": "Kemet Retail",
        "start": None,
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
        "issuer": "DEPI",
        "year": " ",
        "status": "in_progress",
    }],
    "skills": [{"name": "SQL", "source": "skills_section"}],
}

try:
    CVProfile.model_validate(cv_full)
    print("Case 2 PASSED: complete CV accepted")
except ValidationError as error:
    print("Case 2 FAILED:", error)


# ------------------------------------------------------------ case 3: a complete CV -> accepted
cv_full = {
    "headline": "Junior Data Analyst",
    "experience": [{
        "title": "Data Intern",
        "company": "Kemet Retail",
        "start": None,
        "end": None,
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
        "graduation_year": None
    }],
    "certifications": [{
        "name": "Data Analysis Track",
        "issuer": "DEPI",
        "year": None,
        "status": "in_progress",
    }],
    "skills": [{"name": "SQL", "source": "skills_section"}],
}

try:
    CVProfile.model_validate(cv_full)
    print("Case 3 PASSED: complete CV accepted")
except ValidationError as error:
    print("Case 3 FAILED:", error)


# ------------------------------------------------------------ case 4: a complete CV -> accepted
cv_full = {
    "headline": "Junior Data Analyst",
    "experience": [{
        "title": "Data Intern",
        "company": "Kemet Retail",
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
        "graduation_year": None,
    }],
    "certifications": [{
        "name": "Data Analysis Track",
        "issuer": "DEPI",
        "year": None,
        "status": "in_progress",
    }],
    "skills": [{"name": "SQL", "source": "skills_section"}],
}

try:
    CVProfile.model_validate(cv_full)
    print("Case 3 PASSED: complete CV accepted")
except ValidationError as error:
    print("Case 4 FAILED:", error)