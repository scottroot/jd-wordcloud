from bs4 import BeautifulSoup
from requests_html import HTMLSession

url = "https://careers.datadoghq.com/detail/6970128/?gh_jid=6970128&gh_src=8363eca61"


session = HTMLSession()

# Set headers to mimic a real browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Get the page with JavaScript rendering
try:
    response = session.get(url, headers=headers, timeout=30)
    response.raise_for_status()
except Exception as e:
    print(f"Error fetching URL {url}: {e}")
    exit(1)

# Try to render JavaScript, but handle cases where it fails
try:
    # Use a shorter timeout and disable some features for better compatibility
    response.html.render(timeout=10, sleep=1, scrolldown=1)
except Exception as render_error:
    # If rendering fails, continue with the static HTML
    print(f"JavaScript rendering failed for {url}, using static HTML content")

html = response.html

soup = BeautifulSoup(html.html, 'html.parser')

# Remove script and style elements
for script in soup(["script", "style", "meta", "link", "noscript"]):
    script.decompose()

# Check if body exists
if not soup.body:
    print("No body element found in the HTML. The page might be empty or malformed.")
    print("HTML content:")
    print(soup.prettify()[:1000])
    exit(1)

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
all_text = soup.body.get_text(separator=' ', strip=True)

# Check if the page indicates the job is not found or unavailable
job_not_found = False

# Check text-based indicators
for indicator in not_found_indicators:
    if indicator.lower() in all_text.lower():
        job_not_found = True
        print(f"Job not found indicator detected: '{indicator}'")
        break

# Check CSS selector-based indicators
if not job_not_found:
    for selector in not_found_selectors:
        elements = soup.select(selector)
        if elements:
            job_not_found = True
            print(f"Job not found selector detected: '{selector}'")
            break

# if job_not_found:
#     print("Job posting appears to be unavailable or not found.")
#     print("Full page text:")
#     print(all_text)
# else:
#     print("Job posting appears to be available.")

    # Extract job description - look for common containers
    job_description = ""

    # Common selectors for job descriptions
    description_selectors = [
        '[class*="job-description"]',
        '[class*="description"]',
        '[class*="content"]',
        '[class*="details"]',
        '[class*="requirements"]',
        '[class*="responsibilities"]',
        'main',
        'article',
        '.content',
        '#content',
        '.job-content',
        '.position-description'
    ]

    for selector in description_selectors:
        elements = soup.select(selector)
        if elements:
            # Get the text from the first matching element
            job_description = elements[0].get_text(separator=' ', strip=True)
            if len(job_description) > 100:  # Ensure we have substantial content
                print(f"Found job description using selector: {selector}")
                break

    if job_description:
        print("\nJob Description:")
        print("=" * 50)
        print(job_description[:1000] + "..." if len(job_description) > 1000 else job_description)
    else:
        print("\nCould not extract job description. Full page text:")
        print("=" * 50)
        print(all_text)
