import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup

class DOMExtractor:
    @staticmethod
    def extract_page_info(html: str, base_url: str) -> Dict[str, any]:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
            element.decompose()

        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        
        # Extract meta description
        meta_desc = ""
        meta_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
        if meta_tag and meta_tag.get("content"):
            meta_desc = meta_tag["content"].strip()

        # Extract textual content
        text = soup.get_text(separator=" ", strip=True)
        # Collapse whitespace
        clean_text = re.sub(r"\s+", " ", text)
        truncated_text = clean_text[:4000]

        # Extract links
        links: List[str] = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            if any(k in href.lower() for k in ["about", "team", "careers", "jobs", "blog", "engineering"]):
                if href.startswith("http"):
                    links.append(href)
                elif href.startswith("/"):
                    links.append(f"{base_url.rstrip('/')}{href}")

        return {
            "title": title,
            "metaDescription": meta_desc,
            "cleanContent": truncated_text,
            "relevantLinks": list(set(links))[:10]
        }
