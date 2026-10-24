from pydantic import BaseModel, Field
from typing import Literal

class Experience(BaseModel):
    title: str
    company: str | None
    start: str | None = Field(description="YYYY-MM or YYYY")
    end: str | None = Field(description="YYYY-MM, YYYY or 'present'")
    is_internship: bool
    skills_used: list[str] = Field(description="Skills used in THIS job, as written in the CV")
     
class Education(BaseModel):
    degree: str
    institution: str| None
    field_of_study: str| None
    graduation_year: int | None
    

class Project(BaseModel):
    name: str 
    description: str |None
    skills_used:list[str] 
        

class Certification(BaseModel):
    name: str
    issuer: str | None 
    year: int | None 
    status: Literal["completed", "in_progress"]
     
  
class Skill(BaseModel):
    name: str
    source: Literal["skills_section", "experience", "project",
                    "education", "certification", "summary"]


class CVProfile(BaseModel):           # الآخر دايمًا: بيستخدم كل اللي فوقه
    headline: str | None
    experience: list[Experience]
    projects: list[Project]
    education: list[Education]
    certifications: list[Certification]
    skills: list[Skill]