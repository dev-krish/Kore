from typing import List, Optional
from app.services.discovery.providers import BaseSearchProvider, DiscoveredCompany, DiscoveredContact

class DemoSearchProvider(BaseSearchProvider):
    """
    Transparent demo search provider containing curated public information
    about top AI/ML and software engineering startups in India and globally.
    Used when live search API keys are not provided.
    All records are explicitly labeled with `is_demo_record=True` and `verification_status='demo_sample'`.
    """

    CURATED_COMPANIES = [
        {
            "name": "Sarvam AI",
            "website": "https://sarvam.ai",
            "description": "Building foundational AI models, voice-first LLMs, and language infrastructure tailored for Indian languages and enterprise workflows.",
            "industry": "Artificial Intelligence / Generative AI",
            "location": "Bengaluru, India",
            "technologies": ["PyTorch", "Transformers", "CUDA", "FastAPI", "Python", "Kubernetes"],
            "source_url": "https://sarvam.ai/about",
            "contacts": [
                {
                    "name": "Pratyush Kumar",
                    "role": "Co-Founder",
                    "professional_email": "pratyush@sarvam.ai",
                    "profile_url": "https://linkedin.com/in/pratyush-kumar-sarvam",
                    "source_url": "https://sarvam.ai/team",
                    "confidence": 0.90,
                    "verification_status": "demo_sample"
                },
                {
                    "name": "Vivek Raghavan",
                    "role": "Co-Founder",
                    "professional_email": "vivek@sarvam.ai",
                    "profile_url": "https://linkedin.com/in/vivek-raghavan-sarvam",
                    "source_url": "https://sarvam.ai/team",
                    "confidence": 0.90,
                    "verification_status": "demo_sample"
                }
            ]
        },
        {
            "name": "SigNoz",
            "website": "https://signoz.io",
            "description": "Open-source observability platform powered by OpenTelemetry and ClickHouse, helping engineering teams monitor distributed applications.",
            "industry": "Developer Tools / Observability",
            "location": "Bengaluru, India / Remote",
            "technologies": ["Go", "React", "TypeScript", "ClickHouse", "Docker", "OpenTelemetry"],
            "source_url": "https://signoz.io/about",
            "contacts": [
                {
                    "name": "Pranay Prateek",
                    "role": "Co-Founder & CEO",
                    "professional_email": "pranay@signoz.io",
                    "profile_url": "https://linkedin.com/in/pranayprateek",
                    "source_url": "https://github.com/signoz/signoz",
                    "confidence": 0.88,
                    "verification_status": "demo_sample"
                },
                {
                    "name": "Ankit Nayan",
                    "role": "Co-Founder & CTO",
                    "professional_email": "ankit@signoz.io",
                    "profile_url": "https://linkedin.com/in/ankitnayan",
                    "source_url": "https://github.com/signoz/signoz",
                    "confidence": 0.88,
                    "verification_status": "demo_sample"
                }
            ]
        },
        {
            "name": "Hasura",
            "website": "https://hasura.io",
            "description": "Instant GraphQL and REST APIs on PostgreSQL, MySQL, and modern data sources with fine-grained role-based access control.",
            "industry": "Developer Infrastructure / Databases",
            "location": "Bengaluru, India / San Francisco",
            "technologies": ["Haskell", "Rust", "TypeScript", "PostgreSQL", "GraphQL", "Docker"],
            "source_url": "https://hasura.io/about-us",
            "contacts": [
                {
                    "name": "Tanmai Gopal",
                    "role": "Co-Founder & CEO",
                    "professional_email": "tanmai@hasura.io",
                    "profile_url": "https://linkedin.com/in/tanmaig",
                    "source_url": "https://hasura.io/team",
                    "confidence": 0.88,
                    "verification_status": "demo_sample"
                },
                {
                    "name": "Rajoshi Ghosh",
                    "role": "Co-Founder & COO",
                    "professional_email": "rajoshi@hasura.io",
                    "profile_url": "https://linkedin.com/in/rajoshighosh",
                    "source_url": "https://hasura.io/team",
                    "confidence": 0.88,
                    "verification_status": "demo_sample"
                }
            ]
        },
        {
            "name": "Krutrim",
            "website": "https://olakrutrim.com",
            "description": "India's first AI unicorn building multilingual LLMs, AI cloud compute infrastructure, and full-stack AI chips.",
            "industry": "Artificial Intelligence / Cloud Infrastructure",
            "location": "Bengaluru, India",
            "technologies": ["Python", "C++", "PyTorch", "Kubernetes", "Distributed Computing"],
            "source_url": "https://olakrutrim.com/about",
            "contacts": [
                {
                    "name": "Bhavish Aggarwal",
                    "role": "Founder",
                    "professional_email": "bhavish@olakrutrim.com",
                    "profile_url": "https://linkedin.com/in/bhavishaggarwal",
                    "source_url": "https://olakrutrim.com/news",
                    "confidence": 0.85,
                    "verification_status": "demo_sample"
                }
            ]
        },
        {
            "name": "Postman",
            "website": "https://postman.com",
            "description": "Leading API platform for building and using APIs, simplifying each step of the API lifecycle and streamlining collaboration.",
            "industry": "Developer Tools / API Platform",
            "location": "Bengaluru, India / San Francisco",
            "technologies": ["Node.js", "React", "TypeScript", "Go", "AWS", "Electron"],
            "source_url": "https://postman.com/company/about-us",
            "contacts": [
                {
                    "name": "Abhinav Asthana",
                    "role": "Co-Founder & CEO",
                    "professional_email": "abhinav@postman.com",
                    "profile_url": "https://linkedin.com/in/abhinavasthana",
                    "source_url": "https://postman.com/company/about-us",
                    "confidence": 0.90,
                    "verification_status": "demo_sample"
                },
                {
                    "name": "Ankit Sobti",
                    "role": "Co-Founder & CTO",
                    "professional_email": "ankit@postman.com",
                    "profile_url": "https://linkedin.com/in/ankitsobti",
                    "source_url": "https://postman.com/company/about-us",
                    "confidence": 0.90,
                    "verification_status": "demo_sample"
                }
            ]
        }
    ]

    async def search_companies(
        self,
        query: str,
        industry: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 5
    ) -> List[DiscoveredCompany]:
        results = []
        for comp in self.CURATED_COMPANIES:
            results.append(
                DiscoveredCompany(
                    name=comp["name"],
                    website=comp["website"],
                    description=comp["description"],
                    industry=comp["industry"],
                    location=comp["location"],
                    technologies=comp["technologies"],
                    source_url=comp["source_url"],
                    is_demo_record=True,
                    provenance="curated_demo"
                )
            )
            if len(results) >= limit:
                break
        return results

    async def search_company_contacts(
        self,
        company_name: str,
        company_website: str,
        target_roles: List[str]
    ) -> List[DiscoveredContact]:
        matched_contacts = []
        for comp in self.CURATED_COMPANIES:
            if comp["name"].lower() == company_name.lower() or comp["website"].lower() in company_website.lower():
                for contact in comp["contacts"]:
                    matched_contacts.append(
                        DiscoveredContact(
                            name=contact["name"],
                            role=contact["role"],
                            company_name=comp["name"],
                            professional_email=contact["professional_email"],
                            profile_url=contact["profile_url"],
                            source_url=contact["source_url"],
                            confidence=contact["confidence"],
                            verification_status=contact["verification_status"],
                            is_demo_record=True,
                            provenance="curated_demo"
                        )
                    )
        return matched_contacts
