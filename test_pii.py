from pii import redact_pii


SAMPLE = """Sara Ahmed Hassan 
Cairo, Egypt | sara.ahmed99@gmail.com | 010 1234 5678 | +201112223333
linkedin.com/in/sara-ahmed | https://github.com/sara-a

Data Intern, Kemet Retail (2023-06 to 2024-09)
- Built dashboards for 40 stores with Python 3.12 and Power BI
"""
SAMPLE_2 = """Curriculum Vitae
   Name: Sara Ahmed Hassan
   Project name: Sales Dashboard
   """
result = redact_pii(SAMPLE)
print(result)
result_2 = redact_pii(SAMPLE_2)
print(result_2)


# personal data must be gone
assert "sara.ahmed99@gmail.com" not in result, "email was not removed"
assert "010 1234 5678" not in result, "phone was not removed"
assert "+201112223333" not in result, "phone was not removed"
assert "linkedin.com/in/sara-ahmed" not in result, "linkedin was not removed"
assert "github.com/sara-a" not in result, "github was not removed"
assert "Sara Ahmed Hassan" not in result, "name was not removed"
assert "Sara Ahmed Hassan" not in result_2, "labelled name was not removed"
# everything else must stay
assert "2023-06 to 2024-09" in result, "dates were removed by mistake"
assert "Python 3.12" in result, "Python 3.12"
assert "40 stores" in result,"40 stores"
assert "Project name: Sales Dashboard" in result_2, "project name was removed by mistake"

print("All PII checks passed")