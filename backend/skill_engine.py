
import re
from typing import List

from backend.schemas import CandidateProfile, JobProfile, SkillGap
from backend.extractor import get_all_aliases


ACTION_PATTERN = re.compile(
    r"\b("
    r"configured|configure|"
    r"implemented|implement|"
    r"deployed|deploy|"
    r"administered|administer|"
    r"managed|manage|"
    r"designed|design|"
    r"troubleshot|troubleshoot|"
    r"maintained|maintain|"
    r"installed|install|"
    r"migrated|migrate|"
    r"automated|automate|"
    r"monitored|monitor|"
    r"optimized|optimize|"
    r"developed|develop|"
    r"built|build|"
    r"operated|operate|"
    r"supported|support|"
    r"secured|secure|"
    r"led"
    r")\b",
    re.IGNORECASE,
)
ASPIRATION_PATTERN = re.compile(
    r"\b("
    r"would like to|want to|wants to|"
    r"hope to|hopes to|aspire to|"
    r"looking to learn|seeking to learn|"
    r"interested in learning|"
    r"gain experience|gaining experience|"
    r"plan to learn|planning to learn|"
    r"would involve|"
    r"beginner|currently learning|"
    r"studying for|coursework|training course"
    r")\b",
    re.IGNORECASE,
)


# Credit for a skill that is listed in the CV without any supporting sentence.
LISTED_ONLY_SCORE = 0.25


def _skill_terms(skill_id: str, skill_name: str) -> list[str]:
    """Return relevant aliases for a required skill."""
    aliases = get_all_aliases()
    terms = list(aliases.get(skill_id, []))
    terms.append(skill_name)
    return sorted(
        {term.strip() for term in terms if term and term.strip()},
        key=len,
        reverse=True,
    )



def _mentions_skill(sentence: str, terms: list[str]) -> bool:
    """Match skill aliases reliably, including aliases with varied spacing."""
    normalized_sentence = re.sub(r"\s+", " ", sentence).strip()

    for term in terms:
        normalized_term = re.sub(r"\s+", " ", term).strip()
        if not normalized_term:
            continue

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_term)
            + r"(?!\w)"
        )

        if re.search(pattern, normalized_sentence, re.IGNORECASE):
            return True

    return False






def _evidence_score(
    evidence: List[str],
    skill_id: str = "",
    skill_name: str = "",
) -> float:
    if not evidence:
        return 0.0

    terms = _skill_terms(skill_id, skill_name)
    usable = []

    context_pattern = re.compile(
        r"\b("
        r"training|trained|course|courses|coursework|"
        r"scholarship|certification|certified|"
        r"studied|studies|studying|education|"
        r"experience|experienced|knowledge|"
        r"admin|administration|fundamentals|"
        r"workshop|lab|laboratory|"
        r"familiar|proficient|specialized|specialised|"
        r"covered|curriculum|hands-on|"
        r"internship|intern|project|implemented|"
        r"configured|deployed|managed|installed|"
        r"designed|maintained|automated|"
        r"troubleshot|supported"
        r")\b",
        re.IGNORECASE,
    )

    for item in evidence:
        sentence = item.strip()
        if not sentence:
            continue

        # Do not award credit for statements of future learning intent.
        if ASPIRATION_PATTERN.search(sentence):
            continue
        
        # Do not award credit for broad, unsupported self-assessments.
        generic_claim_pattern = re.compile(
            r"^\s*("
            r"strong background in|"
            r"proven expertise in|"
            r"extensive knowledge of|"
            r"good knowledge of|"
            r"knowledge of|"
            r"experienced in|"
            r"skilled in|"
            r"proficient in"
            r")\b",
            re.IGNORECASE,
        )

        if generic_claim_pattern.search(sentence):
            continue


        # The evidence must explicitly relate to the target skill.
        if terms and not _mentions_skill(sentence, terms):
            continue

        usable.append(sentence)

    if not usable:
        return 0.0

    # Full credit requires both a practical action and a skill mention.
    
    concrete_action_pattern = re.compile(
        r"\b("
        r"configured|implemented|deployed|administered|"
        r"managed|designed|troubleshot|maintained|"
        r"installed|migrated|automated|monitored|"
        r"optimized|developed|built|operated|"
        r"secured|"
        r"established|created|provisioned|"
        r"integrated|migrated|upgraded"
        r")\b",
        re.IGNORECASE,
    )

    if any(
        concrete_action_pattern.search(sentence)
        and _mentions_skill(sentence, terms)
        and len(sentence.split()) >= 5
        for sentence in usable
    ):
        return 1.0


    # Partial credit requires contextual evidence, not just a keyword.
    for sentence in usable:
        if context_pattern.search(sentence):
            remaining = sentence.casefold()

            for term in sorted(terms, key=len, reverse=True):
                remaining = remaining.replace(term.casefold(), " ")

            if any(char.isalpha() for char in remaining):
                return 0.5

    # The skill is only listed (for example in a skills line or a table),
    # with no sentence that shows how it was used. Give a small credit.
    return LISTED_ONLY_SCORE
def calculate_gaps(
    candidate: CandidateProfile,
    role: JobProfile,
    semantic_matches=None,
):
    candidate_skills = {s.skill_id: s for s in candidate.skills}
    semantic_matches = semantic_matches or {}

    gaps: List[SkillGap] = []
    weighted_total = 0.0
    total_weight = sum(s.weight for s in role.skills) or 1.0

    for required in role.skills:
        evidence_skill = candidate_skills.get(required.skill_id)

        
        if evidence_skill and evidence_skill.evidence:
            terms = _skill_terms(
                required.skill_id,
                required.name,
            )

            evidence = [
                sentence
                for sentence in evidence_skill.evidence
                if not ASPIRATION_PATTERN.search(sentence)
                and not re.search(
                    r"^\s*(strong background in|"
                    r"proven expertise in|"
                    r"extensive knowledge of|"
                    r"good knowledge of|"
                    r"knowledge of|experienced in|"
                    r"skilled in|proficient in)\b",
                    sentence,
                    re.IGNORECASE,
                )
                and (not terms or _mentions_skill(sentence, terms))
            ]

            score = _evidence_score(
                evidence,
                required.skill_id,
                required.name,
            )


            semantic = semantic_matches.get(required.skill_id)

            if score >= 1.0:
                status = "matched"
            elif score >= 0.5:
                status = "partial"
            elif semantic:
                # Semantic evidence is stronger than a bare listing.
                similarity, sentence = semantic
                evidence = [
                    f"Semantic evidence (similarity {similarity:.2f}): {sentence}"
                ]
                score = 0.5
                status = "partial"
            elif score > 0.0:
                status = "partial"
                evidence = [f"Listed only (no example of use): {evidence[0]}"]
            else:
                evidence = []
                score = 0.0
                status = "missing"
        else:
            semantic = semantic_matches.get(required.skill_id)

            if semantic:
                similarity, sentence = semantic
                score = 0.5
                status = "partial"
                evidence = [
                    f"Semantic evidence (similarity {similarity:.2f}): {sentence}"
                ]
            else:
                score = 0.0
                status = "missing"
                evidence = []

        weighted_total += required.weight * score

        priority = required.weight * (1.0 - score)
        if required.prerequisite and score < 1.0:
            priority += 0.15

        gaps.append(
            SkillGap(
                skill_id=required.skill_id,
                skill_name=required.name,
                weight=required.weight,
                status=status,
                score=score,
                priority=round(priority, 4),
                prerequisite=required.prerequisite,
                evidence=evidence,
            )
        )

    match_score = round(100 * weighted_total / total_weight, 1)

    return match_score, sorted(
        gaps,
        key=lambda g: (-g.priority, g.skill_name),
    )
