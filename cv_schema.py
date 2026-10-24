from typing import Literal

from pydantic import BaseModel, Field


class Experience(BaseModel):
    title: str
    company: str | None
    start: str | None = Field(description="YYYY-MM or YYYY")
    end: str | None = Field(description="YYYY-MM, YYYY or 'present'")
    is_internship: bool
    skills_used: list[str] = Field(
        description="Every tool, technology, method or technique named in this job's bullets")


class Education(BaseModel):
    degree: str
    institution: str | None
    field_of_study: str | None
    graduation_year: int | None


class Project(BaseModel):
    name: str
    description: str | None
    skills_used: list[str] = Field(
        description="Every tool, technology, method or technique named in this project's text")


class Certification(BaseModel):
    name: str
    year: int | None
    status: Literal["completed", "in_progress"]
    skills_mentioned: list[str] = Field(
        description="Tools or skills written inside the certificate's name, e.g. 'Power BI'")


class Skill(BaseModel):
    name: str = Field(
        description="ONE skill only. Split 'Excel (pivot tables, VLOOKUP)' into "
                    "'Excel', 'pivot tables', 'VLOOKUP'")
    level: Literal["basic", "intermediate", "advanced", "unspecified"] = Field(
        description="'SQL (basic)' means level basic. Keep the level when you split a skill.")
    source: Literal["skills_section", "experience", "project",
                    "education", "certification", "summary"]


class CVProfile(BaseModel):           # always last: it uses every class above
    headline: str | None
    experience: list[Experience]
    projects: list[Project]
    education: list[Education]
    certifications: list[Certification]
    skills: list[Skill]