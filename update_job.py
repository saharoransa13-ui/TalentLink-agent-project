import json
from pathlib import Path
from datetime import date
import shutil

# 1. تحديد أماكن الملفات
jobs_path = Path("data/jobs.json")
description_path = Path("data/job_descriptions/backend_developer.txt")

# 2. إنشاء نسخة احتياطية قبل التعديل
backup_path = Path("data/jobs_backup.json")
shutil.copy2(jobs_path, backup_path)

# 3. قراءة الوظائف والإعلان
with jobs_path.open("r", encoding="utf-8") as file:
    jobs = json.load(file)

description = description_path.read_text(encoding="utf-8").strip()

# 4. البحث عن وظيفة Backend Developer وتحديثها فقط
for job in jobs:
    if job["title"] == "Backend Developer":
        job["description"] = description
        job["source"] = "Craft Crew - LinkedIn job advertisement"
        job["source_url"] = (
            "https://eg.linkedin.com/jobs/view/"
            "junior-backend-developer-python-fastapi-pacs-at-craft-crew-4303452407"
        )
        job["collected_at"] = date.today().isoformat()
        break
else:
    raise ValueError("Backend Developer job was not found.")

# 5. حفظ البيانات بعد التحديث
with jobs_path.open("w", encoding="utf-8") as file:
    json.dump(jobs, file, ensure_ascii=False, indent=4)

print("Job description updated successfully.")
print("Backup saved to:", backup_path)

def extract_section(description, start_heading, end_heading=None):

    lower_description = description.casefold()
    start = lower_description.find(start_heading.casefold())
    if start==-1:
       return ""
    start +=len(start_heading)
    if not end_heading:
       return description[start:].strip()

    end=  lower_description.find(end_heading.casefold(), start)
    if end ==-1:
       return description[start:].strip()
        
    return  description[start:end].strip()

def find_skills(section_text,skill_dictionary):
    found_skills=[]
    for skill in skill_dictionary:
        if skill.casefold() in section_text.casefold():
            found_skills.append(skill)
    return found_skills


required_section = extract_section(
    description,
    "Required Skills",
    "Preferred Skills"
)

preferred_section = extract_section(
    description,
    "Preferred Skills",
    "Nice to Have"
)

required_dictionary = [
    "Python",
    "web API",
    "SQL",
    "Git",
    "Problem-solving",
    "attention to detail"
]

preferred_dictionary = [
    "FastAPI",
    "SQLAlchemy",
    "REST API",
    "Redis",
    "JSON",
    "pytest",
    "Docker"
]

required_skills = find_skills(
    required_section, required_dictionary
)

preferred_skills = find_skills(
    preferred_section, preferred_dictionary
)

# استخراج قسم Nice to Have
nice_to_have_section = extract_section(
    description,
    "Nice to Have"
)

nice_to_have_dictionary = [
    "Healthcare",
    "DICOM",
    "Linux/Unix",
    "Async programming"
]

nice_to_have_skills = find_skills(
    nice_to_have_section,
    nice_to_have_dictionary
)

print("Nice to have skills:", nice_to_have_skills)

# حفظ القوائم الثلاث في وظيفة Backend Developer
for job in jobs:
    if job["title"] == "Backend Developer":
        job["required_skills"] = required_skills
        job["preferred_skills"] = preferred_skills
        job["nice_to_have_skills"] = nice_to_have_skills
        break

# كتابة التعديلات داخل jobs.json
with jobs_path.open("w", encoding="utf-8") as file:
    json.dump(jobs, file, ensure_ascii=False, indent=4)

print("All skill lists saved successfully.")
print("Required skills:", required_skills)
print("Preferred skills:", preferred_skills)
print("Found job:", job["title"])
print("Description length:", len(job["description"]))
