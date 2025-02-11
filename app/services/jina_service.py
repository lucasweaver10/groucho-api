import os
import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def scrape_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Scrape content from a URL using Jina's API.
    Returns a tuple of (content, error).
    """
    api_key = os.getenv("JINA_API_KEY")
    if not api_key:
        logger.error("JINA_API_KEY not found in environment variables")
        return None, "JINA_API_KEY not found in environment variables"
    
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        logger.info(f"Attempting to scrape URL: {url}")
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get('https://r.jina.ai/' + url, headers=headers)
            response.raise_for_status()
            
        logger.info(f"Successfully scraped URL: {url}")
        return response.text, None
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error occurred: {e.response.status_code} {e.response.reason_phrase}"
        logger.error(f"HTTP error occurred while scraping {url}: {error_msg}")
        return None, error_msg
        
    except httpx.ReadTimeout:
        error_msg = "Timeout while scraping the URL"
        logger.error(f"{error_msg}: {url}")
        return None, error_msg
        
    except httpx.RequestError as e:
        error_msg = f"Request error occurred: {str(e)}"
        logger.error(f"Error requesting {url}: {error_msg}")
        return None, error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.exception(f"Error scraping {url}: {error_msg}")
        return None, error_msg
