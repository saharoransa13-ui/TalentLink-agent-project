
import re


def extract_skills(text, skill_keywords):
    text_normalized = text.casefold()
    found = []

    # Search for longer skill names first.
    skills = sorted(
        set(skill_keywords),
        key=len,
        reverse=True,
    )

    matched_spans = []

    for skill in skills:
        normalized_skill = skill.casefold()

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        for match in re.finditer(pattern, text_normalized):
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


def analyze_skill_gap(candidate_skills, required_skills):
    candidate_set = {
        skill.strip().casefold()
        for skill in candidate_skills
    }

    matched = [
        skill for skill in required_skills
        if skill.strip().casefold() in candidate_set
    ]

    missing = [
        skill for skill in required_skills
        if skill.strip().casefold() not in candidate_set
    ]

    total = len(required_skills)
    match_rate = len(matched) / total * 100 if total else 0

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "match_rate": round(match_rate, 2),
    }
