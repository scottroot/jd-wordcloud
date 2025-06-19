import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Set, Union
import unicodedata
from pathlib import Path
import time
from bs4 import BeautifulSoup
import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse

class JobDescriptionAnalyzer:
    def __init__(self, terms_file: str):
        self.terms_file = terms_file
        self.categories = {}
        self.normalized_terms = defaultdict(set)
        self.original_terms = defaultdict(dict)  # Store original terms for reporting
        self.load_terms()
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

    def normalize_text(self, text: str) -> str:
        """Normalize text by removing punctuation, converting to lowercase, and handling special characters."""
        # Convert to lowercase
        text = text.lower()
        # Remove punctuation except apostrophes within words
        text = re.sub(r'[^\w\s\']', ' ', text)
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text

    def load_terms(self):
        """Load and normalize terms from the JSON file."""
        with open(self.terms_file, 'r', encoding='utf-8') as f:
            self.categories = json.load(f)

        # Create normalized versions of all terms
        for category, terms in self.categories.items():
            for term in terms:
                normalized = self.normalize_text(term)
                self.normalized_terms[category].add(normalized)
                # Store original term for reporting
                self.original_terms[category][normalized] = term

    def find_exact_matches(self, text: str, terms: Set[str]) -> List[str]:
        """Find exact matches of terms in text, handling multi-word terms."""
        matches = []
        normalized_text = self.normalize_text(text)

        for term in terms:
            # For multi-word terms, check for exact phrase match
            if ' ' in term:
                if f" {term} " in f" {normalized_text} ":
                    matches.append(term)
            # For single-word terms, check for exact word match
            else:
                words = set(normalized_text.split())
                if term in words:
                    matches.append(term)

        return matches

    def analyze_job_description(self, text: str) -> Dict[str, List[str]]:
        """Analyze a job description and return found terms by category."""
        found_terms = defaultdict(list)

        for category, terms in self.normalized_terms.items():
            matches = self.find_exact_matches(text, terms)
            # Convert normalized terms back to original form for reporting
            found_terms[category] = [self.original_terms[category][term] for term in matches]

        return dict(found_terms)

    def extract_job_description_text(self, html_content: str) -> str:
        """Extract text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.decompose()

        # Get all text
        text = soup.get_text(separator=' ', strip=True)
        text = html.unescape(text)  # Convert HTML entities
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace

        return text

    def fetch_url_content(self, url: str) -> str:
        """Fetch content from a URL using Selenium."""
        try:
            # Add a small delay to be respectful to servers
            # time.sleep(1)

            # Load the page
            self.driver.get(url)

            # Wait for JavaScript to load (2 seconds should be enough for most sites)
            time.sleep(2)

            # Get the page source after JavaScript execution
            page_source = self.driver.page_source

            # Extract text
            text = self.extract_job_description_text(page_source)

            if not text.strip():
                print(f"Warning: No content found for {url}")

            return text

        except WebDriverException as e:
            print(f"Error fetching {url}: {str(e)}")
            return ""
        except Exception as e:
            print(f"Unexpected error for {url}: {str(e)}")
            return ""

    def analyze_source(self, source: Union[str, List[str]]) -> Dict[str, Dict[str, List[str]]]:
        """Analyze job descriptions from either a directory, single URL, or list of URLs."""
        results = {}

        try:
            if isinstance(source, str):
                # Check if source is a URL
                if source.startswith(('http://', 'https://')):
                    content = self.fetch_url_content(source)
                    if content:
                        results[urlparse(source).netloc] = self.analyze_job_description(content)
                # Check if source is a directory
                elif os.path.isdir(source):
                    for file_path in Path(source).glob('*.txt'):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            results[file_path.name] = self.analyze_job_description(f.read())
                # Assume it's a single file
                else:
                    with open(source, 'r', encoding='utf-8') as f:
                        results[os.path.basename(source)] = self.analyze_job_description(f.read())

            elif isinstance(source, list):
                # Handle list of URLs
                for url in source:
                    if url.startswith(('http://', 'https://')):
                        content = self.fetch_url_content(url)
                        if content:
                            results[urlparse(url).netloc] = self.analyze_job_description(content)

        finally:
            # Clean up Selenium
            self.driver.quit()

        return results

    def generate_report(self, results: Dict[str, Dict[str, List[str]]]):
        """Generate a detailed analysis report."""
        print("\n=== Job Description Analysis Report ===\n")

        # Overall statistics
        total_jobs = len(results)
        category_counts = defaultdict(int)
        term_frequency = defaultdict(int)

        for job_source, categories in results.items():
            print(f"\nAnalyzing: {job_source}")
            print("-" * 50)

            for category, terms in categories.items():
                if terms:
                    category_counts[category] += 1
                    print(f"\n{category}:")
                    for term in sorted(terms):
                        term_frequency[term] += 1
                        print(f"  - {term}")

        print("\n=== Summary Statistics ===")
        print(f"Total job descriptions analyzed: {total_jobs}")
        print("\nCategory Coverage:")
        for category, count in sorted(category_counts.items()):
            percentage = (count / total_jobs) * 100
            print(f"{category}: {count} jobs ({percentage:.1f}%)")

        print("\nMost Common Terms:")
        for term, count in sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{term}: {count} occurrences")

def main():
    analyzer = JobDescriptionAnalyzer('terms.json')

    # Example usage with different sources:
    # 1. Directory of job descriptions
    # results = analyzer.analyze_source('job_descriptions')

    # 2. Single URL
    # results = analyzer.analyze_source('https://example.com/job-description')

    # 3. List of URLs
    urls = [
        'https://www.amazon.jobs/en/jobs/2985075/senior-product-manager--technical-compass-ww-amazon-stores-finance?cmpid=SPLICX0248M&utm_source=linkedin.com&utm_campaign=cxro&utm_medium=social_media&utm_content=job_posting&ss=paid',
        'https://www.google.com/about/careers/applications/jobs/results/73500593615708870-product-manager/?src=Online/LinkedIn/linkedin_us&utm_source=linkedin&utm_medium=jobposting&utm_campaign=contract',
        'https://jobs.ashbyhq.com/pinecone/42fa0a59-016a-4a06-9820-b5263fc8ff2f/application',
        'https://careers.datadoghq.com/detail/6970128/?gh_jid=6970128&gh_src=8363eca61',
        'https://job-boards.greenhouse.io/rockstargames/jobs/6606344003',
        'https://www.sofi.com/careers/job/?gh_jid=6551779003',
    ]
    results = analyzer.analyze_source(urls)

    # # Default to analyzing the job_descriptions directory
    # results = analyzer.analyze_source('job_descriptions')
    analyzer.generate_report(results)

if __name__ == "__main__":
    main()
