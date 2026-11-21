import pytest
from app.engine.planner import AgentPlanner

@pytest.mark.asyncio
async def test_agent_planner_creates_structured_plan():
    planner = AgentPlanner()
    objective = (
        "Find 5 early-stage AI startups in Bengaluru for a computer science student "
        "interested in AI engineering and LLMs. Discover founders and prepare personalized outreach."
    )
    profile = {
        "fullName": "Test Student",
        "college": "IIIT",
        "degree": "B.Tech CS",
        "currentYear": "3rd Year",
        "skills": ["Python", "PyTorch", "FastAPI"]
    }
    preferences = {
        "targetIndustry": "AI Startups",
        "targetRoles": ["Founders", "Engineering Managers"]
    }

    plan = await planner.create_plan(objective, profile, preferences)
    assert plan is not None
    assert len(plan.tasks) >= 3
    assert plan.targetIndustry is not None
    assert len(plan.targetRoles) > 0
