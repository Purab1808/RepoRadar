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

    api_url = f"https://api.github.com/repos/{owner}/{repository}/readme"

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


def calculate_link_health(results):
    """Calculate the link health score out of 35 points."""
    if not results:
        return 0

    working_links = sum(
        not is_link_broken(result)
        for result in results
    )

    working_ratio = working_links / len(results)

    return round(working_ratio * 35)


def calculate_content_score(content):
    """Calculate README content score out of 30 points."""
    score = 0

    lines = content.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    word_count = len(content.split())

    has_title = bool(re.search(r"^#\s+\S+", content, re.MULTILINE))
    has_description = word_count >= 30
    has_code_block = "```" in content

    if has_title:
        score += 5

    if has_description:
        score += 10

    if word_count >= 100:
        score += 10
    elif word_count >= 50:
        score += 5

    if has_code_block:
        score += 5

    return min(score, 30)


def calculate_section_score(content):
    """Calculate important README section score out of 25 points."""
    content_lower = content.lower()

    section_groups = {
        "Installation": (
            "installation",
            "install",
            "setup",
        ),
        "Usage": (
            "usage",
            "how to use",
            "getting started",
        ),
        "Features": (
            "features",
            "feature",
        ),
        "Demo": (
            "demo",
            "live demo",
            "screenshots",
            "screenshot",
        ),
        "Contributing / License": (
            "contributing",
            "contribute",
            "license",
        ),
    }

    score = 0

    for keywords in section_groups.values():
        if any(keyword in content_lower for keyword in keywords):
            score += 5

    return score


def calculate_quality_score(content):
    """Calculate basic README quality score out of 10 points."""
    score = 0

    lines = content.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]

    heading_count = len(
        re.findall(r"^#{1,6}\s+\S+", content, re.MULTILINE)
    )

    excessive_empty_lines = bool(re.search(r"\n{4,}", content))
    word_count = len(content.split())

    if heading_count >= 2:
        score += 4

    if not excessive_empty_lines:
        score += 2

    if word_count >= 50:
        score += 4

    return min(score, 10)


def calculate_health_score(content, results):
    """Calculate the complete README health score out of 100."""
    link_score = calculate_link_health(results)
    content_score = calculate_content_score(content)
    section_score = calculate_section_score(content)
    quality_score = calculate_quality_score(content)

    total_score = (
        link_score
        + content_score
        + section_score
        + quality_score
    )

    breakdown = {
        "Link Health": link_score,
        "README Content": content_score,
        "Important Sections": section_score,
        "Basic Quality": quality_score,
    }

    return total_score, breakdown


def get_health_label(score):
    """Return a readable label for a README health score."""
    if score >= 90:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 40:
        return "Needs Attention"

    return "Poor"


def generate_suggestions(content, results, breakdown):
    """Generate suggestions based on README health analysis."""
    suggestions = []

    broken_links = [
        result for result in results
        if is_link_broken(result)
    ]

    content_lower = content.lower()

    if broken_links:
        suggestions.append(
            f"Fix {len(broken_links)} broken link"
            f"{'s' if len(broken_links) != 1 else ''}."
        )

    if breakdown["README Content"] < 30:
        if not re.search(r"^#\s+\S+", content, re.MULTILINE):
            suggestions.append("Add a clear README title.")

        if len(content.split()) < 30:
            suggestions.append(
                "Add a short description explaining the project."
            )

        if "```" not in content:
            suggestions.append(
                "Add a code example or usage example."
            )

    section_suggestions = {
        "installation": "Add an Installation section.",
        "usage": "Add a Usage section.",
        "features": "Add a Features section.",
    }

    for keyword, suggestion in section_suggestions.items():
        if keyword not in content_lower:
            suggestions.append(suggestion)

    if not results:
        suggestions.append(
            "Consider adding relevant links such as a live demo "
            "or documentation."
        )

    return suggestions


def display_summary(content, results):
    """Display README health score and analysis."""
    broken_links = [
        result for result in results
        if is_link_broken(result)
    ]

    working_links = [
        result for result in results
        if not is_link_broken(result)
    ]

    health_score, breakdown = calculate_health_score(
        content,
        results,
    )

    health_label = get_health_label(health_score)

    print("\n" + "-" * 35)
    print("README Health Summary")
    print("-" * 35)

    print(f"Total links:   {len(results)}")
    print(f"Working links: {len(working_links)}")
    print(f"Broken links:  {len(broken_links)}")

    print(
        f"README Health: {health_score}% "
        f"({health_label})"
    )

    print("\nScore Breakdown:")
    print(
        f"- Link Health:        {breakdown['Link Health']}/35"
    )
    print(
        f"- README Content:     {breakdown['README Content']}/30"
    )
    print(
        f"- Important Sections: {breakdown['Important Sections']}/25"
    )
    print(
        f"- Basic Quality:      {breakdown['Basic Quality']}/10"
    )

    if broken_links:
        print("\nBroken Links:")

        for result in broken_links:
            print(f"- {result['url']}")

    suggestions = generate_suggestions(
        content,
        results,
        breakdown,
    )

    if suggestions:
        print("\nSuggestions:")

        for suggestion in suggestions:
            print(f"→ {suggestion}")

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

    except (
        OSError,
        ValueError,
        requests.RequestException,
    ) as error:
        print(f"\nError: {error}")
        return

    links = extract_links(content)

    print(f"Links found: {len(links)}")

    if links:
        print("\nChecking links...\n")

        results = []

        for number, link in enumerate(links, start=1):
            result = check_link(link)
            results.append(result)
            display_result(number, result)

    else:
        print("No HTTP/HTTPS Markdown links found.")
        results = []

    display_summary(content, results)


if __name__ == "__main__":
    main()