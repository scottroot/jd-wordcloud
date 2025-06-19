import os
import re
import unicodedata
from pathlib import Path
import time
from bs4 import BeautifulSoup
import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse
from typing import List, Dict

class JobDescriptionScraper:
    def __init__(self):
        self.setup_selenium()

    def setup_selenium(self):
        """Setup Selenium WebDriver with Chrome."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

        self.driver = webdriver.Chrome(options=chrome_options)

    def extract_job_description_text(self, html_content: str) -> tuple[str, str]:
        """Extract text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.decompose()

        # Check for common "not found" or "job unavailable" indicators
        not_found_indicators = [
            # Common text patterns
            "job you're looking for isn't available",
            "job not found",
            "position no longer available",
            "job has been filled",
            "position has been closed",
            "job posting has expired",
            "this job is no longer available",
            "position is no longer open",
            "job has been removed",
            "position has been withdrawn",
            "sorry, the job you're looking for",
            "this position is no longer accepting applications",
            "job posting has been removed",
            "position has been filled",
            "job is no longer active",
            "position is no longer available",
            "job has been closed",
            "position has been cancelled",
            "job posting has been deleted",
            "position has been terminated"
        ]

        # Check for common CSS selectors that indicate "not found"
        not_found_selectors = [
            '[id*="not-found"]',
            '[class*="not-found"]',
            '[id*="error"]',
            '[class*="error"]',
            '[id*="unavailable"]',
            '[class*="unavailable"]',
            '[id*="expired"]',
            '[class*="expired"]',
            '[id*="closed"]',
            '[class*="closed"]',
            '[id*="filled"]',
            '[class*="filled"]',
            '[id*="removed"]',
            '[class*="removed"]',
            '[id*="404"]',
            '[class*="404"]'
        ]

        # Get all text first
        all_text = soup.get_text(separator=' ', strip=True).lower()

        # Check for not found text patterns
        for indicator in not_found_indicators:
            if indicator.lower() in all_text:
                return "", f"Job not found: {indicator}"

        # Check for not found CSS selectors
        for selector in not_found_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Check if any of these elements have substantial content
                    for element in elements:
                        element_text = element.get_text(separator=' ', strip=True)
                        if len(element_text) > 10:  # Must have some content
                            return "", f"Job not found: Found {selector} element with content"
            except:
                continue

        # If we didn't find any "not found" indicators, proceed with normal extraction
        # Try to find job description specific content first
        # Look for common job description selectors
        job_selectors = [
            '[data-testid*="job"]',
            '[class*="job"]',
            '[class*="description"]',
            '[id*="job"]',
            '[id*="description"]',
            'main',
            'article',
            '.content',
            '#content',
            '.job-description',
            '#job-description'
        ]

        job_content = None
        for selector in job_selectors:
            try:
                elements = soup.select(selector)
                if elements:
                    # Find the element with the most text content
                    best_element = max(elements, key=lambda el: len(el.get_text()))
                    if len(best_element.get_text().strip()) > 100:  # Must have substantial content
                        job_content = best_element
                        break
            except:
                continue

        # If we found job-specific content, use it
        if job_content:
            text = job_content.get_text(separator=' ', strip=True)
        else:
            # Fall back to all text
            text = soup.get_text(separator=' ', strip=True)

        text = html.unescape(text)  # Convert HTML entities
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        return text, ""

    def fetch_url_content(self, url: str) -> tuple[str, str]:
        """Fetch content from a URL using Selenium."""
        try:
            # Load the page
            self.driver.get(url)

            # Wait for JavaScript to load and content to appear
            # Try multiple strategies to ensure we get the actual content

            # Wait longer for dynamic content to load
            time.sleep(5)

            # Scroll down to trigger any lazy loading
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Scroll back up
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)

            # Get the page source after JavaScript execution
            page_source = self.driver.page_source

            # Extract text and check for errors
            text, error = self.extract_job_description_text(page_source)

            # If we found a specific error (like "not found"), return it
            if error:
                return "", error

            # Only check for empty content if we didn't find a specific error
            if not text.strip():
                return "", f"No content found for {url}"

            return text, ""

        except WebDriverException as e:
            return "", f"WebDriver error fetching {url}: {str(e)}"
        except Exception as e:
            return "", f"Unexpected error for {url}: {str(e)}"

    def scrape_urls(self, urls: List[str]) -> Dict[str, tuple[str, str]]:
        """Scrape job descriptions from a list of URLs and return the parsed text and error messages."""
        results = {}

        try:
            for url in urls:
                if url.startswith(('http://', 'https://')):
                    content, error = self.fetch_url_content(url)
                    # Use domain name as key for better readability
                    domain = urlparse(url).netloc
                    results[domain] = (content, error)

        finally:
            # Clean up Selenium
            self.driver.quit()

        return results

def scrape_job_descriptions(urls: List[str]) -> Dict[str, tuple[str, str]]:
    """
    Scrape job descriptions from a list of URLs and return the parsed text and error messages.

    Args:
        urls: List of URLs to scrape

    Returns:
        Dictionary with domain names as keys and tuples of (text, error) as values.
        If successful, text contains the parsed content and error is empty string.
        If failed, text is empty string and error contains the error message.
    """
    scraper = JobDescriptionScraper()
    return scraper.scrape_urls(urls)

if __name__ == "__main__":
    urls = [
        'https://www.amazon.jobs/en/jobs/2985075/senior-product-manager--technical-compass-ww-amazon-stores-finance?cmpid=SPLICX0248M&utm_source=linkedin.com&utm_campaign=cxro&utm_medium=social_media&utm_content=job_posting&ss=paid',
        # 'https://www.google.com/about/careers/applications/jobs/results/73500593615708870-product-manager/?src=Online/LinkedIn/linkedin_us&utm_source=linkedin&utm_medium=jobposting&utm_campaign=contract',
        # 'https://jobs.ashbyhq.com/pinecone/42fa0a59-016a-4a06-9820-b5263fc8ff2f/application',
        # 'https://careers.datadoghq.com/detail/6970128/?gh_jid=6970128&gh_src=8363eca61',
        # 'https://job-boards.greenhouse.io/rockstargames/jobs/6606344003',
        # 'https://www.sofi.com/careers/job/?gh_jid=6551779003',
    ]

    results = scrape_job_descriptions(urls)

    # Print results
    for domain, (text, error) in results.items():
        print(f"\n=== {domain} ===")
        if error:
            print(f"ERROR: {error}")
        else:
            print(f"Text length: {len(text)} characters")
            print(f"{text}")
        print("-" * 50)
