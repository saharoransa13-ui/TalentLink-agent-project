from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class SkillEvidence(BaseModel):
    skill_id: str
    name: str
    level: Literal["beginner", "intermediate", "advanced", "unknown"] = "unknown"
    evidence: List[str] = Field(default_factory=list)

class CandidateProfile(BaseModel):
    candidate_name: Optional[str] = None
    skills: List[SkillEvidence] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    years_experience: Optional[float] = None
    source_filename: Optional[str] = None

class RoleSkill(BaseModel):
    skill_id: str
    name: str
    weight: float = Field(ge=0, le=1)
    aliases: List[str] = Field(default_factory=list)
    prerequisite: bool = False

class JobProfile(BaseModel):
    role_id: str
    title: str
    description: str = ""
    skills: List[RoleSkill]

class SkillGap(BaseModel):
    skill_id: str
    skill_name: str
    weight: float
    status: Literal["matched", "partial", "missing"]
    score: float
    priority: float
    prerequisite: bool = False
    evidence: List[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    item_id: str
    title: str
    item_type: Literal["course", "project", "certification", "workshop"]
    provider: str
    url: str
    skill_ids: List[str]
    level: str = "all"
    duration: str = ""
    reason: str

class RoadmapItem(BaseModel):
    phase: str
    skill_id: str
    skill_name: str
    recommendation: Recommendation
    reason: str

class GapReport(BaseModel):
    request_id: str
    role_id: str
    role_title: str
    match_score: float
    candidate_profile: CandidateProfile
    gaps: List[SkillGap]
    recommendations: List[Recommendation]
    roadmap: List[RoadmapItem]
    warnings: List[str] = Field(default_factory=list)
    # Short codes for the same warnings, so the website can show them in Arabic or English.
    warning_codes: List[str] = Field(default_factory=list)
