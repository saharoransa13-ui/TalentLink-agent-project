
"""LLM-assisted CV extraction with deterministic, evidence-validated merging."""

import json
import os
import re
from typing import Tuple

import requests

from backend.llm_client import post_with_retry

from backend.extractor import ALIASES, get_all_aliases, extract_candidate_profile
from backend.schemas import CandidateProfile, SkillEvidence


VALID_LEVELS = {"beginner", "intermediate", "advanced", "unknown"}


def llm_is_configured() -> bool:
    return bool(
        os.getenv("OPENAI_API_KEY")
        and os.getenv("OPENAI_BASE_URL")
        and os.getenv("OPENAI_MODEL")
    )


def _normalise_evidence(items):
    """Remove duplicate evidence while preserving its original order."""
    result = []
    seen = set()

    for item in items:
        if not isinstance(item, str):
            continue

        item = re.sub(r"^[\s•●▪\-\*–·]+", "", item).strip()
        key = re.sub(r"\s+", " ", item).casefold()
        if item and key not in seen:
            seen.add(key)
            result.append(item)

    return result



def _evidence_exists_in_cv(evidence: str, cv_text: str) -> bool:
    """Accept evidence only if the supplied phrase occurs in the CV text."""
    return bool(evidence and evidence.casefold() in cv_text.casefold())


def _skill_aliases(skill_id: str) -> list[str]:
    """Return aliases belonging to the specified skill."""
    return get_all_aliases().get(skill_id, [])


def _evidence_supports_skill(
    evidence: str,
    skill_id: str,
) -> bool:
    """Reject evidence that contains no term relevant to the assigned skill."""
    aliases = _skill_aliases(skill_id)
    if not evidence or not aliases:
        return False

    for alias in aliases:
        pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
        if re.search(pattern, evidence, re.IGNORECASE):
            return True

    return False



def _evidence_is_skill_specific(
    evidence: str,
    skill_id: str,
) -> bool:
    """Accept evidence when it explicitly mentions the assigned skill."""
    return _evidence_supports_skill(evidence, skill_id)

def _is_aspiration(evidence: str) -> bool:
    """Identify common learning intentions, not demonstrated experience."""
    pattern = re.compile(
        r"\b("
        r"would like to|want to|hope to|aspire to|"
        r"looking to learn|seeking to learn|"
        r"interested in learning|gain experience|"
        r"gaining experience|plan to learn|"
        r"currently learning|studying for"
        r")\b",
        re.IGNORECASE,
    )
    return bool(pattern.search(evidence))


def _merge_profiles(
    fallback: CandidateProfile,
    llm_data: dict,
    cv_text: str,
    filename: str,
) -> CandidateProfile:
    """Keep rule-based skills and merge only grounded LLM evidence."""
    merged = {}

    # Start with deterministic results so the LLM cannot accidentally
    # remove skills that the local extractor found.
    for skill in fallback.skills:
        merged[skill.skill_id] = {
            "name": skill.name,
            "level": skill.level,
            "evidence": list(skill.evidence),
        }

    for item in llm_data.get("skills", []):
        if not isinstance(item, dict):
            continue

        skill_id = item.get("skill_id")
        if not isinstance(skill_id, str) or skill_id not in ALIASES:
            continue

        raw_evidence = item.get("evidence", [])
        if not isinstance(raw_evidence, list):
            continue

        # Verify that every quoted phrase really occurs in the CV.
        grounded = [
            phrase.strip()
            for phrase in raw_evidence
            if isinstance(phrase, str)
            and phrase.strip()
            and _evidence_exists_in_cv(phrase.strip(), cv_text)
            and _evidence_is_skill_specific(phrase.strip(), skill_id)
            and not _is_aspiration(phrase.strip())
        ]
        grounded = _normalise_evidence(grounded)

        if skill_id not in merged:
            # Do not create a new skill without verifiable evidence.
            if not grounded:
                continue

            merged[skill_id] = {
                "name": str(
                    item.get("name") or skill_id.replace("_", " ").title()
                ),
                "level": "unknown",
                "evidence": [],
            }

        current = merged[skill_id]
        current["evidence"] = _normalise_evidence(
            current["evidence"] + grounded
        )[:12]

        level = item.get("level", "unknown")
        if level in VALID_LEVELS:
            # Do not promote proficiency based only on an LLM prediction.
            # Retain the fallback level unless it was unknown and the LLM
            # supplies a valid, explicit level.
            if current["level"] == "unknown" and level != "unknown":
                current["level"] = level

    skills = [
        SkillEvidence(
            skill_id=skill_id,
            name=details["name"],
            level=details["level"],
            evidence=_normalise_evidence(details["evidence"])[:12],
        )
        for skill_id, details in sorted(merged.items())
    ]

    certifications = fallback.certifications
    if isinstance(llm_data.get("certifications"), list):
        combined_certs = list(certifications)
        for cert in llm_data["certifications"]:
            if not isinstance(cert, str):
                continue
            cert = cert.strip()
            if cert and cert.casefold() in cv_text.casefold():
                combined_certs.append(cert)
        certifications = sorted(
            {cert for cert in combined_certs},
            key=str.casefold,
        )[:30]

    years = fallback.years_experience
    llm_years = llm_data.get("years_experience")
    if (
        years is None
        and isinstance(llm_years, (int, float))
        and not isinstance(llm_years, bool)
        and 0 <= llm_years <= 80
    ):
        years = float(llm_years)

    name = llm_data.get("candidate_name")
    if not isinstance(name, str) or not name.strip():
        name = fallback.candidate_name

    return CandidateProfile(
        candidate_name=name.strip() if isinstance(name, str) else None,
        skills=skills,
        certifications=certifications,
        years_experience=years,
        source_filename=filename or fallback.source_filename,
    )


def extract_candidate_profile_smart(
    text: str, filename: str = ""
) -> Tuple[CandidateProfile, str, str | None]:
    """Return (profile, method, warning), using rules as a stable baseline."""
    fallback = extract_candidate_profile(text, filename)

    if not llm_is_configured():
        return fallback, "rules", None

    known_skills = sorted(ALIASES.keys())
    base_url = os.getenv("OPENAI_BASE_URL", "").rstrip("/")
    endpoint = (
        base_url
        if base_url.endswith("/chat/completions")
        else f"{base_url}/chat/completions"
    )

    prompt = {
        "task": (
            "Extract explicit CV information. Use only the supplied skill IDs. "
            "Return short exact evidence quotes from the CV. "
            "Do not infer experience from aspirations or training intentions."
        ),
        "allowed_skill_ids": known_skills,
        "schema": {
            "candidate_name": "string or null",
            "skills": [
                {
                    "skill_id": "allowed id",
                    "name": "human-readable name",
                    "level": "beginner|intermediate|advanced|unknown",
                    "evidence": ["short exact quote from CV"],
                }
            ],
            "certifications": ["string"],
            "years_experience": "number or null",
        },
        "cv_text": text[:24000],
    }

    try:
        response = post_with_retry(
            endpoint,
            headers={
                "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": os.environ["OPENAI_MODEL"],
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Extract CV data conservatively. Return valid JSON "
                            "only, with no markdown."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(prompt, ensure_ascii=False),
                    },
                ],
            },
            timeout=float(os.getenv("LLM_TIMEOUT_SECONDS", "35")),
        )
        response.raise_for_status()

        payload = response.json()["choices"][0]["message"]["content"]
        llm_data = json.loads(payload)

        if not isinstance(llm_data, dict):
            raise ValueError("LLM response must be a JSON object")

        profile = _merge_profiles(fallback, llm_data, text, filename)

        return profile, "llm+rules", None

    except requests.HTTPError as exc:
        response = exc.response
        status = response.status_code if response is not None else "unknown"
        details = response.text[:300] if response is not None else str(exc)
        return (
            fallback,
            "rules_fallback",
            f"LLM request failed (HTTP {status}): {details}",
        )

    except Exception as exc:
        return (
            fallback,
            "rules_fallback",
            f"LLM extraction was unavailable ({type(exc).__name__}): {exc}",
        )
