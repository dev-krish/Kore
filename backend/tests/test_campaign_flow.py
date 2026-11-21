import pytest
from app.engine.planner import PlanOutput
from app.engine.controller import AgentController

@pytest.mark.asyncio
async def test_agent_controller_end_to_end_execution():
    events_received = []

    def handle_event(event):
        events_received.append(event)

    controller = AgentController(event_callback=handle_event)
    plan = PlanOutput(
        tasks=[
            "Discover target AI companies",
            "Deep research and contact discovery",
            "Synthesize personalized drafts"
        ],
        targetIndustry="AI & Software Startups",
        targetRoles=["Founders", "Engineering Managers"],
        reasoning="Test plan"
    )

    profile = {
        "fullName": "Student Tester",
        "college": "Test University",
        "degree": "B.Tech CS",
        "currentYear": "2nd Year",
        "skills": ["Python", "FastAPI", "React"]
    }

    config = {
        "targetIndustry": "AI Startups",
        "targetLocation": "India",
        "targetProspectCount": 2,
        "objective": "AI Engineering Internship"
    }

    result = await controller.execute_plan(
        campaign_id="test_camp_1",
        user_id="test_user_1",
        plan=plan,
        student_profile=profile,
        campaign_config=config
    )

    assert result["status"] == "completed"
    assert len(result["companies"]) > 0
    assert len(result["contacts"]) > 0
    assert len(result["drafts"]) > 0
    assert len(result["steps"]) >= 2
    assert len(events_received) > 0
