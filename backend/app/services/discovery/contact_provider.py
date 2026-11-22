import logging
import re
from typing import List, Optional
from urllib.parse import urlparse, urljoin
import httpx
from bs4 import BeautifulSoup
from app.services.discovery.providers import DiscoveredContact

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')

ROLE_KEYWORDS = [
    "founder", "co-founder", "cto", "ceo", "chief technology officer",
    "chief executive officer", "head of engineering", "vp engineering",
    "engineering manager", "director of engineering", "technical lead", "tech lead"
]

class BaseContactProvider:
    async def discover_company_contacts(
        self,
        company_name: str,
        company_website: str,
        target_roles: Optional[List[str]] = None
    ) -> List[DiscoveredContact]:
        raise NotImplementedError

class PublicWebsiteContactProvider(BaseContactProvider):
    """
    Discovers publicly disclosed leadership and professional contacts
    from official company websites and team/contact pages.
    Never fabricates or guesses email addresses.
    """

    async def discover_company_contacts(
        self,
        company_name: str,
        company_website: str,
        target_roles: Optional[List[str]] = None
    ) -> List[DiscoveredContact]:
        logger.info(f"Initiating live public contact discovery for {company_name} ({company_website})")
        if not company_website:
            return []

        base_url = company_website.rstrip("/")
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        domain = urlparse(base_url).netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        candidate_paths = ["", "/about", "/team", "/about-us", "/leadership", "/contact"]
        discovered: List[DiscoveredContact] = []
        seen_names = set()

        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, headers={"User-Agent": "KORE-Research-Agent/1.0"}) as client:
            for path in candidate_paths:
                target_url = f"{base_url}{path}" if path else base_url
                try:
                    resp = await client.get(target_url)
                    if resp.status_code != 200:
                        continue

                    html = resp.text
                    soup = BeautifulSoup(html, "html.parser")

                    # 1. Search for mailto links with role/name context
                    for a_tag in soup.find_all("a", href=True):
                        href = a_tag["href"]
                        if href.startswith("mailto:"):
                            email_candidate = href[7:].split("?")[0].strip().lower()
                            if EMAIL_REGEX.match(email_candidate):
                                email_domain = email_candidate.split("@")[-1].lower()
                                is_domain_match = (email_domain == domain or domain.endswith(email_domain))
                                
                                anchor_text = a_tag.get_text(strip=True)
                                parent_text = a_tag.parent.get_text(strip=True) if a_tag.parent else ""
                                
                                # Check for name and role in parent context
                                detected_role = "Leadership / Contact"
                                for rk in (target_roles or ROLE_KEYWORDS):
                                    if rk.lower() in parent_text.lower():
                                        detected_role = rk.title()
                                        break

                                candidate_name = anchor_text if (anchor_text and "@" not in anchor_text) else f"{company_name} Contact"
                                if candidate_name not in seen_names:
                                    seen_names.add(candidate_name)
                                    status = "publicly_disclosed" if path in ("/team", "/leadership", "/about") else ("domain_matched" if is_domain_match else "unverified")
                                    discovered.append(DiscoveredContact(
                                        name=candidate_name,
                                        role=detected_role,
                                        company_name=company_name,
                                        professional_email=email_candidate,
                                        source_url=target_url,
                                        confidence=0.85 if is_domain_match else 0.65,
                                        verification_status=status,
                                        is_demo_record=False,
                                        provenance="live_public_extraction"
                                    ))

                    # 2. Extract structured team cards / headings
                    cards = soup.find_all(["div", "section", "li", "article"], class_=re.compile(r'team|member|leader|bio|profile', re.I))
                    for card in cards:
                        card_text = card.get_text(separator=" ", strip=True)
                        for rk in (target_roles or ROLE_KEYWORDS):
                            if re.search(r'\b' + re.escape(rk) + r'\b', card_text, re.I):
                                # Found a leadership role card
                                name_el = card.find(["h2", "h3", "h4", "strong", "b"])
                                if name_el:
                                    person_name = name_el.get_text(strip=True)
                                    if person_name and person_name not in seen_names and len(person_name) < 40 and not any(kw in person_name.lower() for kw in ["team", "about", "join", "read"]):
                                        seen_names.add(person_name)
                                        
                                        # Look for disclosed email in this card
                                        card_emails = EMAIL_REGEX.findall(str(card))
                                        valid_email = card_emails[0].lower() if card_emails else None
                                        
                                        v_status = "publicly_disclosed" if valid_email else "unverified"
                                        conf = 0.85 if valid_email else 0.60
                                        
                                        discovered.append(DiscoveredContact(
                                            name=person_name,
                                            role=rk.title(),
                                            company_name=company_name,
                                            professional_email=valid_email,
                                            source_url=target_url,
                                            confidence=conf,
                                            verification_status=v_status,
                                            is_demo_record=False,
                                            provenance="live_public_extraction"
                                        ))
                                break

                    if len(discovered) >= 4:
                        break

                except Exception as page_err:
                    logger.debug(f"Could not inspect public page {target_url} for {company_name}: {page_err}")
                    continue

        logger.info(f"Discovered {len(discovered)} live public contacts for {company_name}")
        return discovered
