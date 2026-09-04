"""RepoRadar - a small CLI tool for checking links in README files."""

import base64
import re
import sys
import time
from pathlib import Path

import requests


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
GITHUB_URL_PATTERN = re.compile(
    r"https?://github\.com/([^/\s]+)/([^/\s#?]+)"
)
REQUEST_TIMEOUT = 10


def extract_links(content):
    """Extract HTTP and HTTPS links from Markdown content."""
    return MARKDOWN_LINK_PATTERN.findall(content)


def fetch_github_readme(repository_url):
    """Fetch a repository README from the GitHub API."""
    match = GITHUB_URL_PATTERN.match(repository_url.rstrip("/"))

    if not match:
        raise ValueError("Invalid GitHub repository URL.")

    owner, repository = match.groups()
    repository = repository.removesuffix(".git")

    api_url = (
        f"https://api.github.com/repos/{owner}/{repository}/readme"
    )

    response = requests.get(
        api_url,
        headers={"Accept": "application/vnd.github+json"},
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code == 404:
        raise ValueError(
            "README not found. Check that the repository is public "
            "and the URL is correct."
        )

    response.raise_for_status()

    data = response.json()

    if data.get("encoding") != "base64":
        raise ValueError("Unsupported README encoding.")

    content = base64.b64decode(data["content"]).decode("utf-8")

    return content


def read_local_readme(readme_path):
    """Read a local Markdown README file."""
    return Path(readme_path).read_text(encoding="utf-8")


def classify_link(url):
    """Classify a URL based on its domain or path."""
    url_lower = url.lower()

    if "linkedin.com" in url_lower:
        return "LinkedIn"

    if "mailto:" in url_lower:
        return "Email"

    if "github.com" in url_lower:
        return "GitHub"

    demo_keywords = (
        "vercel.app",
        "netlify.app",
        "github.io",
    )

    if any(keyword in url_lower for keyword in demo_keywords):
        return "Demo"

    documentation_keywords = (
        "docs.",
        "documentation",
        "/docs",
        "readthedocs.io",
    )

    if any(keyword in url_lower for keyword in documentation_keywords):
        return "Documentation"

    if "demo" in url_lower:
        return "Demo"

    return "External Website"


def check_link(url):
    """Check a URL and return its status, final URL, and response time."""
    start_time = time.perf_counter()

    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 405:
            response = requests.get(
                url,
                allow_redirects=True,
                timeout=REQUEST_TIMEOUT,
                stream=True,
            )

        response_time = time.perf_counter() - start_time

        return {
            "url": url,
            "status": response.status_code,
            "final_url": response.url,
            "response_time": response_time,
            "error": None,
        }

    except requests.RequestException as error:
        response_time = time.perf_counter() - start_time

        return {
            "url": url,
            "status": None,
            "final_url": None,
            "response_time": response_time,
            "error": str(error),
        }


def is_link_broken(result):
    """Return True when a link could not be reached successfully."""
    if result["status"] is None:
        return True

    return result["status"] >= 400


def display_result(number, result):
    """Display the result of a single link check."""
    link_type = classify_link(result["url"])

    if is_link_broken(result):
        print(f"{number}. ✗ {result['url']}")

        if result["status"] is not None:
            print(f"   Status: {result['status']}")
        else:
            print(f"   Error: {result['error']}")

        print(f"   Type: {link_type}")

    else:
        print(f"{number}. ✓ {result['url']}")
        print(f"   Status: {result['status']}")
        print(f"   Type: {link_type}")

        if result["final_url"] != result["url"]:
            print(f"   Redirected to: {result['final_url']}")

    print(f"   Response time: {result['response_time']:.2f}s")


def calculate_health_score(results):
    """Calculate README health score from link check results."""
    if not results:
        return 100

    working_links = sum(
        not is_link_broken(result)
        for result in results
    )

    return round((working_links / len(results)) * 100)


def get_health_label(score):
    """Return a readable label for a README health score."""
    if score >= 90:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 40:
        return "Needs Attention"
    return "Poor"


def display_summary(results):
    """Display a summary of working and broken links."""
    broken_links = [
        result for result in results
        if is_link_broken(result)
    ]
    working_links = [
        result for result in results
        if not is_link_broken(result)
    ]

    health_score = calculate_health_score(results)
    health_label = get_health_label(health_score)

    print("\n" + "-" * 35)
    print("Link Check Summary")
    print("-" * 35)
    print(f"Total links:   {len(results)}")
    print(f"Working links: {len(working_links)}")
    print(f"Broken links:  {len(broken_links)}")
    print(f"README Health: {health_score}% ({health_label})")

    if broken_links:
        print("\nBroken Links:")
        for result in broken_links:
            print(f"- {result['url']}")

    if not results:
        print("\nSuggestion:")
        print(
            "→ Consider adding relevant links such as a live demo,"
        )
        print(
            "  documentation, or related resources for a more complete README."
        )

    print()


def main():
    """Run the RepoRadar command-line interface."""
    if len(sys.argv) != 2:
        print("Usage: python reporadar.py <README.md | GitHub URL>")
        return

    source = sys.argv[1]

    try:
        if source.startswith("https://github.com/"):
            print("\nRepoRadar - GitHub README Link Checker")
            print("-" * 40)
            print(f"Repository: {source}")
            print("\nFetching README...")

            content = fetch_github_readme(source)
        else:
            print("\nRepoRadar - README Link Checker")
            print("-" * 35)
            print(f"File: {source}")
            print("\nReading README...")

            content = read_local_readme(source)

    except (OSError, ValueError, requests.RequestException) as error:
        print(f"\nError: {error}")
        return

    links = extract_links(content)

    print(f"Links found: {len(links)}")

    if not links:
        print("No HTTP/HTTPS Markdown links found.")
        display_summary([])
        return

    print("\nChecking links...\n")

    results = []

    for number, link in enumerate(links, start=1):
        result = check_link(link)
        results.append(result)
        display_result(number, result)

    display_summary(results)


if __name__ == "__main__":
    main()