from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_database
from app.api.deps import get_current_user_id
from app.models.profile import ProfileModel, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/me")
async def get_my_profile(user_id: str = Depends(get_current_user_id)):
    db = get_database()
    profile = await db.profiles.find_one({"userId": user_id})
    if not profile:
        # Default profile for initial experience
        default_profile = {
            "userId": user_id,
            "fullName": "Krish Sharma",
            "email": "krish.sharma@college.edu",
            "college": "Indian Institute of Information Technology",
            "degree": "B.Tech in Computer Science and Engineering",
            "branch": "Computer Science",
            "currentYear": "3rd Year",
            "skills": [
                "Python", "TypeScript", "FastAPI", "React", "Next.js", 
                "Docker", "PostgreSQL", "MongoDB", "PyTorch", "LLM Orchestration"
            ],
            "programmingLanguages": ["Python", "TypeScript", "JavaScript", "C++", "SQL"],
            "frameworks": ["FastAPI", "Next.js", "Tailwind CSS", "PyTorch", "Playwright"],
            "projects": [
                {
                    "title": "Autonomous AI Outreach Agent",
                    "description": "Multi-agent engine built with FastAPI, Playwright, and local LLMs to discover startups and synthesize personalized outreach.",
                    "technologies": ["Python", "FastAPI", "Playwright", "Ollama", "Next.js"],
                    "githubUrl": "https://github.com/krish-sharma/kore-agent"
                },
                {
                    "title": "High-Performance Distributed Cache",
                    "description": "In-memory key-value cache engine supporting Redis-compatible serialization and LRU eviction policy.",
                    "technologies": ["C++", "TCP Sockets", "Docker"],
                    "githubUrl": "https://github.com/krish-sharma/distributed-cache"
                }
            ],
            "githubProfile": "https://github.com/krish-sharma",
            "linkedinProfile": "https://linkedin.com/in/krish-sharma-dev",
            "portfolioUrl": "https://krishsharma.dev",
            "resumeText": "Krish Sharma - 3rd Year CS Student passionate about AI Engineering, Systems, and Full-Stack Development.",
            "preferences": {
                "targetRoles": ["Software Engineering Intern", "AI/ML Intern", "Founding Engineer Intern"],
                "preferredLocations": ["Bengaluru", "Remote", "San Francisco"],
                "preferredCompanyTypes": ["Early-stage AI Startups", "Seed / Series A Startups"],
                "outreachObjective": "Summer 2025/2026 Software & AI Internship Opportunities"
            },
            "updatedAt": datetime.now(timezone.utc)
        }
        res = await db.profiles.insert_one(default_profile)
        default_profile["_id"] = str(res.inserted_id)
        return default_profile

    profile["_id"] = str(profile["_id"])
    return profile

@router.put("/me")
async def update_my_profile(update_data: ProfileUpdate, user_id: str = Depends(get_current_user_id)):
    db = get_database()
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    update_dict["updatedAt"] = datetime.now(timezone.utc)

    result = await db.profiles.find_one_and_update(
        {"userId": user_id},
        {"$set": update_dict},
        upsert=True,
        return_document=True
    )
    result["_id"] = str(result["_id"])
    return result
