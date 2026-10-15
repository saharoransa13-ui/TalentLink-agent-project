import json

def analyze_skill_gap(candidate_skills, required_skills):
    candidate_skills = [
        skill.strip().casefold()
        for skill in candidate_skills
    ]

    missing_skills = []

    for skill in required_skills:
        if skill.strip().casefold() not in candidate_skills:
            missing_skills.append(skill)

    matched_count = len(required_skills) - len(missing_skills)
    total_required = len(required_skills)

    if total_required > 0:
        match_rate = (matched_count / total_required) * 100
    else:
        match_rate = 0

    return missing_skills, match_rate

with open("data/jobs.json", "r",encoding="utf-8") as file:
    jobs=json.load(file)

print("Available Jobs:")
for index, job in enumerate(jobs, start=1):
    print(index, "-", job["title"])


skill_keywords = ["Python", "SQL", "Excel", "Power BI"]

def extract_skills(description, skill_keywords):
    found_skills = []

    for skill in skill_keywords:
        if skill.casefold() in description.casefold():
            found_skills.append(skill)

    return found_skills

while True:
    try:
        choice = int(input("Choose a job number: "))

        if 1 <= choice <= len(jobs):
            selected_job = jobs[choice - 1]
            break
        else:
            print("Invalid choice. Please choose an available job number.")

    except ValueError:
        print("Please enter a valid number.")

skills_input = input(
    "Enter your skills separated by commas: "
)



candidate_skills = [
    skill.strip()
    for skill in skills_input.split(",")
    if skill.strip()
]

target_job = selected_job["title"]
description = selected_job["description"]
skill_keywords = selected_job["required_skills"] 
#skill_keywords = selected_job["required_skills"]
found_skills = extract_skills(description, skill_keywords)

print("Extracted Skills:", found_skills)
missing_skills, match_rate = analyze_skill_gap(
    candidate_skills,
    found_skills
)

print("Target Job:", target_job)
print("Missing Skills:", missing_skills)
print("Match Rate:", match_rate, "%")


from pathlib import Path
description_path = Path("data/job_descriptions/backend_developer.txt")
description=description_path.read_text(encoding="utf-8")
print("Description length:",len(description))
print("Description preview:", description[:100])


