import logging
from typing import Dict, Any, Optional
import httpx
from app.services.browser.dom_extractor import DOMExtractor

logger = logging.getLogger(__name__)

class BrowserService:
    """
    Browser Service for website content extraction.
    Uses Playwright when available, with automatic robust HTTP fallback.
    """

    async def fetch_page(self, url: str) -> Dict[str, Any]:
        logger.info(f"Fetching website: {url}")
        
        # Try Playwright first if installed
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = await context.new_page()
                await page.goto(url, timeout=15000, wait_until="domcontentloaded")
                content = await page.content()
                await browser.close()
                extracted = DOMExtractor.extract_page_info(content, url)
                extracted["sourceUrl"] = url
                extracted["method"] = "playwright_browser"
                return extracted
        except Exception as e:
            logger.warning(f"Playwright navigation failed or browser binary not installed ({e}). Falling back to async HTTP client.")

        # HTTP Fallback
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                extracted = DOMExtractor.extract_page_info(resp.text, url)
                extracted["sourceUrl"] = url
                extracted["method"] = "http_fallback"
                return extracted
        except Exception as http_err:
            logger.error(f"HTTP fetch failed for {url}: {http_err}")
            return {
                "title": url,
                "metaDescription": "Direct fetch failed. Public website content unavailable.",
                "cleanContent": f"Unable to fetch public URL {url}. Network or domain restriction.",
                "relevantLinks": [],
                "sourceUrl": url,
                "method": "failed",
                "error": str(http_err)
            }

browser_service = BrowserService()
