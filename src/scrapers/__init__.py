"""
Scrapers package initialization
"""

from .scraper_69shu import Scraper69Shu
from .scraper_ximalaya import ScraperXimalaya
from .scraper_syosetu import ScraperSyosetu
from .scraper_baobao88 import ScraperBaobao88
from .scraper_quanben import ScraperQuanben

# Registry of available scrapers
SCRAPERS = {
    "69shu": Scraper69Shu,
    "ximalaya": ScraperXimalaya,
    "syosetu": ScraperSyosetu,
    "baobao88": ScraperBaobao88,
    "quanben": ScraperQuanben
}

def get_scraper(name):
    """Get a scraper by name"""
    return SCRAPERS.get(name)