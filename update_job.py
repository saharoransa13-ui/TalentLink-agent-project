
import json
import re
from pathlib import Path
from datetime import date


# ==================================================
# 1. Configure paths
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
DESCRIPTIONS_DIR = BASE_DIR / "data" / "job_descriptions"
OUTPUT_FILE = BASE_DIR / "data" / "job_ads_extracted.json"


# ==================================================
# 2. Skill dictionaries by role
# ==================================================

SKILLS_BY_ROLE = {
    "backend_developer": [
        "GitHub Actions", "GitLab CI", "Role-Based Access",
        "REST endpoints", "Message Queues", "Unit Testing",
        "Unit Tests", "Async programming", "Microservices",
        "Authentication", "Authorization", "PostgreSQL",
        "SQLAlchemy", "MongoDB", "RabbitMQ", "JavaScript",
        "TypeScript", "Node.js", "Python", "FastAPI",
        "Django", "Flask", "ASP.NET", "MySQL", "REST API",
        "Web API", "Docker", "Redis", "JSON", "pytest",
        "Linux", "JWT", "OAuth2", "CI/CD", "GitHub",
        "Git", "AWS", "Caching", "Agile", "Communication",
        "Ownership", "SQL", "Java", "C#", "PHP", "OOP",
        "Problem-solving", "Attention to detail",
    ],

    "cybersecurity_analyst": [
        "Vulnerability Assessment", "Penetration Testing",
        "Incident Response", "Network Security",
        "Information Security", "Security Operations",
        "Microsoft Sentinel", "Threat Hunting",
        "Risk Assessment", "Cybersecurity", "TCP/IP",
        "Firewalls", "Wireshark", "Splunk", "Nmap",
        "Python", "Linux", "Windows", "SIEM", "SOC",
    ],

    "data_analyst": [
        "Confidence Intervals", "Hypothesis Testing",
        "Window Functions", "Business Intelligence",
        "Data Visualization", "Data Warehousing",
        "Product Analytics", "User Behavior",
        "A/B Testing", "Google Sheets", "BigQuery",
        "PostgreSQL", "Statistics", "Reporting",
        "Dashboards", "Data Cleaning", "Data Analysis",
        "Power BI", "Tableau", "Pandas", "NumPy",
        "Python", "Excel", "Matplotlib", "SQL",
        "Joins", "CTEs", "ETL",
    ],

    "data_engineer": [
        "Infrastructure as Code", "Data Warehousing",
        "Data Pipelines", "Data Modeling", "Apache Spark",
        "Databricks", "PostgreSQL", "MongoDB", "PySpark",
        "Airflow", "Python", "SQL", "ETL", "ELT",
        "Hadoop", "Kafka", "MySQL", "AWS", "Azure",
        "GCP", "Docker", "Linux",
    ],

    "devops_engineer": [
        "Infrastructure as Code", "GitHub Actions",
        "Kubernetes", "Monitoring", "Networking",
        "Terraform", "Ansible", "GitLab CI",
        "Python", "Linux", "Bash", "GitHub", "Git",
        "Docker", "Jenkins", "CI/CD", "AWS", "Azure",
        "GCP",
    ],

    "frontend_developer": [
        "Responsive Design", "Tailwind CSS",
        "JavaScript", "TypeScript", "Accessibility",
        "Bootstrap", "Next.js", "Vue.js", "Angular",
        "React", "HTML", "CSS", "GitHub", "Git",
        "REST API", "UI", "UX",
    ],

    "generative_ai_engineer": [
        "Large Language Models", "Prompt Engineering",
        "Vector Databases", "Fine-tuning", "Hugging Face",
        "Generative AI", "LangChain", "LangGraph",
        "LlamaIndex", "Embeddings", "Transformers",
        "Evaluation", "Agentic AI", "Python", "PyTorch",
        "TensorFlow", "FastAPI", "Agents", "LLM",
        "RAG", "FAISS", "ChromaDB", "OpenAI API",
    ],

    "ml_engineer": [
        "Feature Engineering", "Model Evaluation",
        "Machine Learning", "Deep Learning",
        "Computer Vision", "Scikit-learn", "TensorFlow",
        "PyTorch", "Statistics", "Python", "Pandas",
        "NumPy", "MLOps", "MLflow", "Docker", "SQL",
        "NLP",
    ],

    "mobile_developer": [
        "React Native", "App Testing", "Mobile UI",
        "Android", "Kotlin", "Firebase", "Flutter",
        "SQLite", "REST API", "Java", "Swift", "iOS",
        "Dart", "GitHub", "Git",
    ],

    "software_tester": [
        "Performance Testing", "Regression Testing",
        "Automation Testing", "Manual Testing",
        "Software Testing", "Bug Tracking",
        "API Testing", "Test Cases", "Test Plans",
        "Playwright", "Selenium", "Cypress", "Postman",
        "pytest", "JUnit", "ISTQB", "Python", "Java",
        "Jira", "SQL",
    ],

    "ui_ux_designer": [
        "Information Architecture", "Interaction Design",
        "Usability Testing", "User Research",
        "Design Systems", "Visual Design",
        "Wireframing", "Prototyping", "Accessibility",
        "Adobe XD", "Figma", "UI", "UX",
    ],
}


# ==================================================
# 3. Section headings
# ==================================================

SECTION_TYPES = {
    "required_skills": [
        "required skills",
        "requirements",
        "qualifications",
        "what you'll need",
        "what you will need",
        "what we need",
        "what we're looking for",
        "what we are looking for",
        "who we're looking for",
        "who we are looking for",
        "must have",
        "minimum qualifications",
        "basic qualifications",
        "required qualifications",
        "your qualifications",
        "what you bring",
        "what you'll bring",
        "you have",
        "your experience",
        "your skills",
        "essential skills",
        "essential requirements",
    ],

    "preferred_skills": [
        "preferred skills",
        "preferred qualifications",
        "preferred experience",
        "desired qualifications",
        "desired skills",
        "nice to have qualifications",
    ],

    "nice_to_have_skills": [
        "nice to have",
        "nice-to-have",
        "bonus points",
        "additional skills",
        "good to have",
        "preferred but not required",
        "it would be great if you also have",
        "it would be great if you have",
        "it would be a plus",
        "it would be nice to have",
    ],
}


OTHER_HEADINGS = [
    "job description",
    "about the role",
    "about the job",
    "about us",
    "responsibilities",
    "what you'll do",
    "what you will do",
    "benefits",
    "what we offer",
    "company overview",
    "who we are",
    "job overview",
    "role overview",
    "description",
    "experience",
    "education",
    "your role",
    "the role",
    "key responsibilities",
    "duties and responsibilities",
]


# ==================================================
# 4. Normalize text and identify headings
# ==================================================

def normalize(text):
    """Normalize case and whitespace."""
    text = str(text).casefold()
    return re.sub(r"\s+", " ", text).strip()


def clean_heading(line):
    """Clean Markdown formatting and numbering from headings."""
    line = line.strip()
    line = re.sub(r"^[#*\s]+", "", line)
    line = re.sub(r"[*#:：\s]+$", "", line)
    line = re.sub(r"^\d+[.)]\s*", "", line)
    return normalize(line)


def identify_section(line):
    """Identify a recognized section heading."""
    heading = clean_heading(line)

    for section_type, headings in SECTION_TYPES.items():
        if heading in [normalize(item) for item in headings]:
            return section_type

    if heading in [normalize(item) for item in OTHER_HEADINGS]:
        return "other"

    return None


# ==================================================
# 5. Split advertisement sections
# ==================================================

def split_sections(description):
    """Split the advertisement according to its headings."""
    sections = {
        "required_skills": [],
        "preferred_skills": [],
        "nice_to_have_skills": [],
    }

    current_section = None

    for line in description.splitlines():
        section = identify_section(line)

        if section is not None:
            current_section = None if section == "other" else section
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        key: "\n".join(lines).strip()
        for key, lines in sections.items()
    }


# ==================================================
# 6. Find unique skills and avoid substring matches
# ==================================================

def find_skills(text, skill_dictionary):
    """Find unique skills and prefer longer names over substrings."""
    normalized_text = normalize(text)
    found = []
    matched_spans = []

    skills = sorted(
        set(skill_dictionary),
        key=len,
        reverse=True,
    )

    for skill in skills:
        normalized_skill = normalize(skill)

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        for match in re.finditer(pattern, normalized_text):
            start, end = match.span()

            overlaps = any(
                start < existing_end and end > existing_start
                for existing_start, existing_end in matched_spans
            )

            if overlaps:
                continue

            matched_spans.append((start, end))
            found.append(skill)
            break

    return found


# ==================================================
# 7. Extract experience requirements
# ==================================================

def extract_experience_years(description):
    """Extract experience ranges with or without the word experience."""
    patterns = [
        r"\b\d+\s*[-–]\s*\d+\s+years?"
        r"(?:\s+of\s+experience)?\b",

        r"\b\d+\s+to\s+\d+\s+years?"
        r"(?:\s+of\s+experience)?\b",

        r"\b\d+\+\s+years?"
        r"(?:\s+of\s+experience)?\b",

        r"\b\d+\s+years?"
        r"(?:\s+of\s+experience)?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, description, re.IGNORECASE)

        if match:
            return re.sub(r"\s+", " ", match.group(0)).strip()

    return None


# ==================================================
# 8. Extract skill alternatives
# ==================================================

def extract_skill_alternatives(description):
    """Detect common alternatives expressed using 'or' or 'either'."""
    alternatives = []

    pairs = [
        ("Node.js", "Python"),
        ("FastAPI", "Flask"),
        ("PostgreSQL", "MySQL"),
        ("Power BI", "Tableau"),
        ("GitHub Actions", "GitLab CI"),
    ]

    normalized_description = normalize(description)

    for first, second in pairs:
        first_name = normalize(first)
        second_name = normalize(second)

        patterns = [
            rf"\b{re.escape(first_name)}\s+or\s+"
            rf"{re.escape(second_name)}\b",

            rf"\b{re.escape(second_name)}\s+or\s+"
            rf"{re.escape(first_name)}\b",
        ]

        found_pair = any(
            re.search(pattern, normalized_description)
            for pattern in patterns
        )

        if not found_pair and (
            "either" in normalized_description
            and "background" in normalized_description
        ):
            first_position = normalized_description.find(first_name)
            second_position = normalized_description.find(second_name)

            if first_position != -1 and second_position != -1:
                found_pair = True

        if found_pair:
            alternatives.append([first, second])

    return alternatives


# ==================================================
# 9. Extract source URL
# ==================================================

def extract_source_url(description):
    """Extract the first URL found in the advertisement."""
    match = re.search(
        r"""https?://[^\s<>\]\)"']+""",
        description,
    )

    return match.group(0).rstrip(".,;") if match else ""


# ==================================================
# 10. Split optional text when headings are unavailable
# ==================================================

def split_optional_text(description):
    """Separate explicit optional statements from the main text."""
    optional_phrases = [
        "it would be great if you also have",
        "it would be great if you have",
        "preferred but not required",
        "bonus points",
        "nice to have",
        "nice-to-have",
        "good to have",
        "is a plus",
        "are a plus",
        "would be a plus",
        "is an advantage",
        "are an advantage",
    ]

    section_phrases = [
        "it would be great if you also have",
        "it would be great if you have",
        "preferred but not required",
        "bonus points",
        "nice to have",
        "nice-to-have",
        "good to have",
    ]

    text = re.sub(r"\s+", " ", description).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)

    required_sentences = []
    optional_sentences = []
    optional_section_active = False

    for sentence in sentences:
        normalized_sentence = normalize(sentence)

        starts_optional_section = any(
            phrase in normalized_sentence
            for phrase in section_phrases
        )

        contains_optional_phrase = any(
            phrase in normalized_sentence
            for phrase in optional_phrases
        )

        if starts_optional_section:
            optional_section_active = True

        if contains_optional_phrase or optional_section_active:
            optional_sentences.append(sentence)
        else:
            required_sentences.append(sentence)

    return (
        " ".join(required_sentences).strip(),
        " ".join(optional_sentences).strip(),
    )


# ==================================================
# 11. Process one advertisement
# ==================================================

def process_ad(txt_path):
    """Extract structured information from one advertisement."""
    relative_path = txt_path.relative_to(DESCRIPTIONS_DIR)
    role_folder = txt_path.parent.name.casefold()

    description = txt_path.read_text(
        encoding="utf-8-sig"
    ).strip()

    skill_dictionary = SKILLS_BY_ROLE.get(role_folder, [])
    sections = split_sections(description)

    has_section_headings = any(sections.values())

    all_detected_skills = find_skills(
        description,
        skill_dictionary,
    )

    if has_section_headings:
        required_skills = find_skills(
            sections["required_skills"],
            skill_dictionary,
        )

        preferred_skills = find_skills(
            sections["preferred_skills"],
            skill_dictionary,
        )

        nice_to_have_skills = find_skills(
            sections["nice_to_have_skills"],
            skill_dictionary,
        )

    else:
        main_text, optional_text = split_optional_text(description)

        required_skills = find_skills(
            main_text,
            skill_dictionary,
        )

        preferred_skills = []

        nice_to_have_skills = find_skills(
            optional_text,
            skill_dictionary,
        )

    skill_alternatives = extract_skill_alternatives(description)
    experience_years = extract_experience_years(description)

    if not has_section_headings:
        extraction_status = "needs_review"

    elif not required_skills and not preferred_skills and not nice_to_have_skills:
        extraction_status = "needs_review"

    else:
        extraction_status = "section_headings_found"

    return {
        "role_folder": role_folder,
        "title": txt_path.stem.replace("_", " ").replace("-", " ").title(),
        "source_file": str(relative_path),
        "description": description,
        "source_url": extract_source_url(description),
        "collected_at": date.today().isoformat(),
        "experience_years": experience_years,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "nice_to_have_skills": nice_to_have_skills,
        "skill_alternatives": skill_alternatives,
        "all_detected_skills": all_detected_skills,
        "section_texts": sections,
        "extraction_status": extraction_status,
    }


# ==================================================
# 12. Process all advertisements
# ==================================================

def main():
    """Process TXT files and save the extracted JSON catalog."""
    if not DESCRIPTIONS_DIR.exists():
        print("Job descriptions folder not found:")
        print(DESCRIPTIONS_DIR)
        return

    txt_files = sorted(
        path
        for path in DESCRIPTIONS_DIR.rglob("*")
        if path.is_file() and path.suffix.casefold() == ".txt"
    )

    if not txt_files:
        print("No TXT files found.")
        return

    results = []
    errors = []

    print(f"TXT files found: {len(txt_files)}")

    for txt_path in txt_files:
        try:
            ad = process_ad(txt_path)
            results.append(ad)

            print(f"\n{ad['source_file']}")
            print("  Required:", ad["required_skills"])
            print("  Preferred:", ad["preferred_skills"])
            print("  Nice to have:", ad["nice_to_have_skills"])
            print("  Experience:", ad["experience_years"])
            print("  Alternatives:", ad["skill_alternatives"])
            print("  All detected:", len(ad["all_detected_skills"]))
            print("  Status:", ad["extraction_status"])

        except Exception as error:
            errors.append({
                "file": str(txt_path.relative_to(DESCRIPTIONS_DIR)),
                "error": str(error),
            })

            print(f"\nError reading {txt_path.name}: {error}")

    output = {
        "generated_on": date.today().isoformat(),
        "total_files_found": len(txt_files),
        "total_ads_processed": len(results),
        "total_errors": len(errors),
        "ads": results,
        "errors": errors,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=4)

    print("\nProcessing completed.")
    print("Advertisements processed:", len(results))
    print("Errors:", len(errors))
    print("Output file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
