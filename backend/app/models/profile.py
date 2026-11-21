from datetime import datetime, timezone
from typing import List, Optional
from pydantic import Field, HttpUrl
from app.models.common import BaseDBModel

class ProjectItem(BaseDBModel):
    title: str
    description: str
    technologies: List[str] = []
    githubUrl: Optional[str] = None
    liveUrl: Optional[str] = None

class ProfilePreferences(BaseDBModel):
    targetRoles: List[str] = ["Software Engineering Intern", "AI/ML Intern"]
    preferredLocations: List[str] = ["Remote", "Bengaluru", "San Francisco"]
    preferredCompanyTypes: List[str] = ["Early-stage Startup", "Seed / Series A", "High Growth Tech"]
    outreachObjective: Optional[str] = "Summer 2025/2026 Software & AI Internship"

class ProfileModel(BaseDBModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    fullName: str
    email: str
    college: str
    degree: str
    branch: str
    currentYear: str  # e.g., "2nd Year", "3rd Year"
    skills: List[str] = []
    programmingLanguages: List[str] = []
    frameworks: List[str] = []
    projects: List[ProjectItem] = []
    githubProfile: Optional[str] = None
    linkedinProfile: Optional[str] = None
    portfolioUrl: Optional[str] = None
    resumeText: Optional[str] = None
    preferences: ProfilePreferences = Field(default_factory=ProfilePreferences)
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProfileUpdate(BaseDBModel):
    fullName: Optional[str] = None
    email: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    branch: Optional[str] = None
    currentYear: Optional[str] = None
    skills: Optional[List[str]] = None
    programmingLanguages: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None
    projects: Optional[List[ProjectItem]] = None
    githubProfile: Optional[str] = None
    linkedinProfile: Optional[str] = None
    portfolioUrl: Optional[str] = None
    resumeText: Optional[str] = None
    preferences: Optional[ProfilePreferences] = None
