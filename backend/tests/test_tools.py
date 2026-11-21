import pytest
from app.engine.registry import init_default_tools, tool_registry

@pytest.fixture(autouse=True)
def setup_tools():
    init_default_tools()

@pytest.mark.asyncio
async def test_company_search_tool():
    tool = tool_registry.get_tool("company_search")
    assert tool is not None
    result = await tool.execute(industry="AI", location="India", limit=3)
    assert result.success is True
    assert len(result.data) > 0
    assert "name" in result.data[0]
    assert "website" in result.data[0]

@pytest.mark.asyncio
async def test_fetch_website_tool():
    tool = tool_registry.get_tool("fetch_website")
    assert tool is not None
    result = await tool.execute(website_url="https://sarvam.ai")
    assert result.success is True
    assert "cleanContent" in result.data

@pytest.mark.asyncio
async def test_discover_contacts_tool():
    tool = tool_registry.get_tool("discover_contacts")
    assert tool is not None
    result = await tool.execute(company_name="Sarvam AI", company_website="https://sarvam.ai")
    assert result.success is True
    assert len(result.data) > 0
    assert result.data[0]["name"] is not None
    assert result.data[0]["confidence"] > 0.5
    assert result.data[0]["source_url"] is not None

@pytest.mark.asyncio
async def test_evaluate_relevance_tool():
    tool = tool_registry.get_tool("evaluate_relevance")
    assert tool is not None
    profile = {"fullName": "Alex", "college": "Univ", "degree": "CS", "skills": ["Python"]}
    company = {"name": "Sarvam AI", "description": "Generative AI"}
    contact = {"name": "Pratyush", "role": "Co-Founder"}

    result = await tool.execute(student_profile=profile, company_info=company, contact_info=contact)
    assert result.success is True
    assert "relevanceScore" in result.data
    assert 0.0 <= result.data["relevanceScore"] <= 1.0

@pytest.mark.asyncio
async def test_generate_email_tool():
    tool = tool_registry.get_tool("generate_email")
    assert tool is not None
    profile = {"fullName": "Alex", "college": "Univ", "degree": "CS"}
    recipient = {"name": "Pratyush", "role": "Co-Founder", "company_name": "Sarvam AI"}
    company_research = {"whatTheyBuild": "Foundational AI models"}
    evaluation = {"suggestedOutreachAngle": "Highlight PyTorch projects"}

    result = await tool.execute(
        student_profile=profile,
        recipient_info=recipient,
        company_research=company_research,
        evaluation=evaluation,
        outreach_objective="Summer AI Internship"
    )
    assert result.success is True
    assert "subject" in result.data
    assert "body" in result.data
    assert len(result.data["personalizationEvidence"]) > 0
