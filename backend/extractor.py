
import json
import re
from pathlib import Path
from typing import List

from backend.schemas import CandidateProfile, SkillEvidence


# Keep general aliases as a fallback if roles.json cannot be read.
ALIASES = {
    "networking": [
        "networking", "tcp/ip", "routing", "switching", "vlan",
        "ospf", "bgp", "firewall", "cisco",
    ],
    "linux": ["linux", "ubuntu", "red hat", "rhel", "bash"],
    "windows_server": [
        "windows server", "active directory", "group policy", "ad ds"
    ],
    "virtualization": [
        "vmware", "vsphere", "esxi", "hyper-v", "virtualization", "nutanix"
    ],
    "cloud": ["aws", "azure", "gcp", "cloud computing", "cloud infrastructure"],
    "python": ["python", "fastapi", "django", "flask"],
    "sql": ["sql", "mysql", "postgresql", "oracle database", "sql server"],
    "data_analysis": ["pandas", "power bi", "tableau", "data analysis", "visualization"],
    "machine_learning": [
        "machine learning", "scikit-learn", "pytorch", "tensorflow", "deep learning"
    ],
    "generative_ai": [
        "generative ai", "llm", "rag", "langchain", "prompt engineering", "transformer"
    ],
    "cybersecurity": [
        "cybersecurity", "siem", "soc", "penetration testing",
        "vulnerability management", "rapid7"
    ],
    "devops": [
        "devops", "docker", "kubernetes", "ci/cd", "jenkins", "terraform", "ansible"
    ],
    "backup": ["veeam", "commvault", "backup", "disaster recovery", "data protection"],
    "storage": ["san", "nas", "iscsi", "storage", "dorado", "powerscale", "netapp"],
    "databases": ["dba", "database administration", "oracle", "sql server", "postgresql"],
    "backend_development": [
        "rest api", "api development", "microservices", "backend", "node.js"
    ],
    "statistics": ["statistics", "hypothesis testing", "regression", "probability"],
    "data_engineering": ["etl", "data pipeline", "spark", "airflow", "data engineering"],
}


def get_all_aliases():
    """Merge general aliases with the aliases configured in roles.json."""
    merged = {
        skill_id: list(terms)
        for skill_id, terms in ALIASES.items()
    }

    roles_path = Path(__file__).resolve().parent.parent / "data" / "roles.json"

    try:
        with roles_path.open("r", encoding="utf-8") as f:
            roles = json.load(f)

        for role in roles:
            for skill in role.get("skills", []):
                skill_id = skill.get("skill_id")
                if not skill_id:
                    continue

                merged.setdefault(skill_id, [])

                for alias in skill.get("aliases", []):
                    if isinstance(alias, str) and alias.strip():
                        if alias.casefold() not in {
                            existing.casefold() for existing in merged[skill_id]
                        }:
                            merged[skill_id].append(alias.strip())

    except (OSError, json.JSONDecodeError):
        # Continue using the general alias dictionary if configuration
        # cannot be loaded. The application can still run.
        pass

    return merged




def extract_candidate_profile(text: str, filename: str = "") -> CandidateProfile:
    found: List[SkillEvidence] = []
    all_aliases = get_all_aliases()

    # Split on sentence boundaries and line breaks.
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)

    for skill_id, terms in all_aliases.items():
        contextual_evidence = []
        matched_aliases = []

        for term in terms:
            pattern = (
                r"(?<![a-z0-9])"
                + re.escape(term)
                + r"(?![a-z0-9])"
            )

            if re.search(pattern, text, flags=re.IGNORECASE):
                matched_aliases.append(term)

        # Preserve relevant context, prioritizing full sentences.
        for sentence in sentences:
            sentence = " ".join(sentence.split()).strip()
            if not sentence:
                continue

            for term in terms:
                pattern = (
                    r"(?<![a-z0-9])"
                    + re.escape(term)
                    + r"(?![a-z0-9])"
                )

                if re.search(pattern, sentence, flags=re.IGNORECASE):
                    if len(sentence) >= 20:
                        contextual_evidence.append(sentence)
                    break

        # Deduplicate while preserving the original order.
        contextual_evidence = list(
            dict.fromkeys(contextual_evidence)
        )
        matched_aliases = list(dict.fromkeys(matched_aliases))

        # Keep contextual sentences first so aliases cannot crowd them out.
        evidence = (
            contextual_evidence[:12]
            if contextual_evidence
            else matched_aliases[:12]
        )

        if evidence:
            found.append(
                SkillEvidence(
                    skill_id=skill_id,
                    name=skill_id.replace("_", " ").title(),
                    level="unknown",
                    evidence=evidence,
                )
            )

    certifications = []

    cert_patterns = [
        r"\bPMP\b",
        r"\bCCNA\b",
        r"\bCCNP\b",
        r"\bAWS Certified[^,\n;]*",
        r"\bMicrosoft Certified[^,\n;]*",
        r"\bHCIE[^,\n;]*",
        r"\bHCIP[^,\n;]*",
        r"\bHCIA[^,\n;]*",
        r"\bCISSP\b",
        r"\bITIL(?:\s+\w+)?",
    ]

    for pattern in cert_patterns:
        certifications.extend(
            re.findall(pattern, text, flags=re.IGNORECASE)
        )

    years = None
    matches = re.findall(
        r"(\d{1,2})\+?\s+years?\s+(?:of\s+)?experience",
        text,
        flags=re.IGNORECASE,
    )

    if matches:
        years = float(max(map(int, matches)))

    return CandidateProfile(
        candidate_name=None,
        skills=found,
        certifications=sorted(set(c.strip() for c in certifications)),
        years_experience=years,
        source_filename=filename or None,
    )
