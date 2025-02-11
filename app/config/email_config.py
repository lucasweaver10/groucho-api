import os
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

EMAIL_CONFIG = {
    "ieltswritingchecker.com": {
        "api_key": os.getenv("RESEND_API_KEY_IELTS"),
        "from_email": "contact@ieltswritingchecker.com",
        "from_name": "IELTS Writing Checker",
        "local_port": 3002
    },
    "cambridgewritingchecker.com": {
        "api_key": os.getenv("RESEND_API_KEY_CAMBRIDGE"),
        "from_email": "contact@cambridgewritingchecker.com",
        "from_name": "Cambridge Writing Checker",
        "local_port": 3007
    },
    "ptewritingchecker.com": {
        "api_key": os.getenv("RESEND_API_KEY_PTE"),
        "from_email": "contact@ptewritingchecker.com",
        "from_name": "PTE Writing Checker",
        "local_port": 3003
    },
    "toeflwritingchecker.com": {
        "api_key": os.getenv("RESEND_API_KEY_TOEFL"),
        "from_email": "contact@toeflwritingchecker.com",
        "from_name": "TOEFL Writing Checker",
        "local_port": 3004
    },
    "default": {
        "api_key": os.getenv("RESEND_API_KEY"),
        "from_email": "lucas@qwiknotes.com",
        "from_name": "Lucas Weaver",
        "local_port": 5173
    }
}

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    try:
        domain = urlparse(url).netloc
        logger.info(f"Extracted domain from URL: {domain}")
        
        if domain.startswith('localhost:'):
            port = int(domain.split(':')[1])
            logger.info(f"Local development detected. Port: {port}")
            for domain_key, config in EMAIL_CONFIG.items():
                if config['local_port'] == port:
                    logger.info(f"Matched local port {port} to domain: {domain_key}")
                    return domain_key
            logger.info(f"No domain match found for port {port}, using default")
            return "default"
        
        clean_domain = domain.replace('www.', '')
        logger.info(f"Clean domain: {clean_domain}")
        return clean_domain
    except Exception as e:
        logger.error(f"Error processing URL {url}: {str(e)}")
        return "default"

def get_email_config(frontend_url: str):
    """Get email configuration based on frontend URL."""
    domain = get_domain_from_url(frontend_url)
    config = EMAIL_CONFIG.get(domain, EMAIL_CONFIG["default"])
    logger.info(f"Using configuration for domain: {domain}")
    logger.info(f"API Key prefix: {config['api_key'][:8] if config['api_key'] else 'None'}")
    return config
