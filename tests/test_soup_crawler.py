"""Test the pdfs from html crawl code."""
# TODO: remove sys when done.
import sys
sys.path.append("./src")

from paper_crawler.crawl_links_soup import get_icml_2024_pdf, get_icml_2023_pdf


def test_icml24() -> None:
    """Check if we got all ICML papers."""
    assert len(get_icml_2024_pdf()) == 2610

def test_icml23() -> None:
    """Check if we got all ICML papers."""
    assert len(get_icml_2023_pdf()) == 1828