import base64
import re
import sys
import time
from collections import Counter

import requests


MARKDOWN_LINK_PATTERN = re.compile(
    r"\[[^\]]*\]\((https?://[^)\s]+)\)"
)

GITHUB_URL_PATTERN = re.compile(
    r"https?://github\.com/([^/\s]+)/([^/\s#?]+)"
)

HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(.+?)\s*$",
    re.MULTILINE,
)

HTML_H1_PATTERN = re.compile(
    r"<h1[^>]*>\s*(.*?)\s*</h1>",
    re.IGNORECASE | re.DOTALL,
)

HTML_IMAGE_ALT_PATTERN = re.compile(
    r"<img\b[^>]*\balt\s*=\s*[\"']([^\"']+)[\"'][^>]*>",
    re.IGNORECASE,
)

REQUEST_TIMEOUT = 10
MAX_RETRIES = 1


SECTION_ALIASES = {
    "Installation": (
        "installation",
        "install",
        "setup",
        "setup instructions",
        "setup guide",
        "installation guide",
        "how to install",
        "installing",
    ),
    "Usage": (
        "usage",
        "usage guide",
        "how to use",
        "running",
        "run",
        "run locally",
        "running locally",
        "run it",
        "example",
        "examples",
        "example usage",
        "how it works",
        "getting started",
        "quick start",
        "quickstart",
        "getting started guide",
    ),
    "Features": (
        "features",
        "feature",
        "key features",
        "main features",
        "functionality",
        "capabilities",
        "what it does",
    ),
    "Demo": (
        "demo",
        "live demo",
        "screenshots",
        "screenshot",
        "preview",
        "live preview",
    ),
    "Contributing / License": (
        "contributing",
        "contribute",
        "contribution",
        "contributions",
        "license",
        "licence",
        "licensing",
    ),
}


SECTION_CONTENT_CUES = {
    "Features": (
        r"^\s*the\s+key\s+features\s+are\s*:?\s*$",
        r"^\s*key\s+features\s*:?\s*$",
        r"^\s*main\s+features\s*:?\s*$",
        r"^\s*features\s+include\s*:?\s*$",
        r"^\s*this\s+project\s+provides\s*:?\s*$",
        r"^\s*the\s+main\s+features\s+include\s*:?\s*$",
    ),
}


def normalize_heading(heading):
    """Normalize a Markdown heading for section matching."""
    heading = heading.lower()
    heading = heading.replace("&", "and")
    heading = re.sub(r"[^a-z0-9\s]", " ", heading)
    heading = re.sub(r"\s+", " ", heading)
    return heading.strip()


def extract_headings(content):
    """Extract normalized Markdown headings."""
    headings = HEADING_PATTERN.findall(content)
    return [normalize_heading(heading) for heading in headings]


def detect_sections(content):
    """
    Detect important README sections using general semantic aliases
    and strong structural content cues.
    """
    headings = extract_headings(content)
    detected_sections = set()

    normalized_aliases = {
        section: {
            normalize_heading(alias)
            for alias in aliases
        }
        for section, aliases in SECTION_ALIASES.items()
    }

    for heading in headings:
        for section, aliases in normalized_aliases.items():
            if heading in aliases:
                detected_sections.add(section)

    for section, patterns in SECTION_CONTENT_CUES.items():
        for pattern in patterns:
            if re.search(
                pattern,
                content,
                re.IGNORECASE | re.MULTILINE,
            ):
                detected_sections.add(section)
                break

    return detected_sections


def extract_links(content):
    """Extract HTTP/HTTPS Markdown links from README content."""
    return MARKDOWN_LINK_PATTERN.findall(content)


def normalize_url(url):
    """
    Normalize a URL for duplicate detection.

    This removes harmless differences such as a trailing slash
    while keeping the actual URL structure intact.
    """
    return url.rstrip("/")


def find_duplicate_links(links):
    """
    Find duplicate URLs and their occurrence counts.

    Returns:
        dict: normalized URL -> number of occurrences
    """
    normalized_links = [
        normalize_url(link)
        for link in links
    ]

    counts = Counter(normalized_links)

    return {
        url: count
        for url, count in counts.items()
        if count > 1
    }


def fetch_github_readme(repository_url):
    """Fetch a public GitHub repository README through the GitHub API."""
    match = GITHUB_URL_PATTERN.fullmatch(
        repository_url.rstrip("/")
    )

    if not match:
        raise ValueError(
            "Invalid GitHub repository URL."
        )

    owner, repository = match.groups()

    api_url = (
        f"https://api.github.com/repos/"
        f"{owner}/{repository}/readme"
    )

    response = requests.get(
        api_url,
        headers={
            "Accept": "application/vnd.github+json"
        },
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code == 404:
        raise ValueError(
            "README not found or repository does not exist."
        )

    response.raise_for_status()

    data = response.json()

    if data.get("encoding") != "base64":
        raise ValueError(
            "Unsupported README encoding."
        )

    return base64.b64decode(
        data["content"]
    ).decode("utf-8")


def read_local_readme(readme_path):
    """Read a local README Markdown file."""
    with open(
        readme_path,
        "r",
        encoding="utf-8",
    ) as file:
        return file.read()


def is_local_or_example_url(url):
    """Check whether a URL points to a local development example."""
    url_lower = url.lower()

    local_hosts = (
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
    )

    return any(
        host in url_lower
        for host in local_hosts
    )


def classify_link(url):
    """Classify a URL based on its domain or path."""
    url_lower = url.lower()

    if is_local_or_example_url(url):
        return "Local/Example"

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

    if any(
        keyword in url_lower
        for keyword in demo_keywords
    ):
        return "Demo"

    documentation_keywords = (
        "docs.",
        "documentation",
        "/docs",
        "readthedocs.io",
    )

    if any(
        keyword in url_lower
        for keyword in documentation_keywords
    ):
        return "Documentation"

    if "demo" in url_lower:
        return "Demo"

    return "External Website"


def check_link(url):
    """Check whether a URL is reachable with one retry for transient failures."""
    if is_local_or_example_url(url):
        return {
            "url": url,
            "status": "LOCAL",
            "final_url": url,
            "response_time": 0,
            "error": "Local development/example URL",
            "attempts": 0,
        }

    start_time = time.perf_counter()
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
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
                    stream=True,
                    timeout=REQUEST_TIMEOUT,
                )

            response_time = (
                time.perf_counter() - start_time
            )

            return {
                "url": url,
                "status": response.status_code,
                "final_url": response.url,
                "response_time": response_time,
                "error": None,
                "attempts": attempt + 1,
            }

        except requests.RequestException as error:
            last_error = error

            if attempt < MAX_RETRIES:
                time.sleep(0.5)

    response_time = time.perf_counter() - start_time

    return {
        "url": url,
        "status": None,
        "final_url": url,
        "response_time": response_time,
        "error": str(last_error),
        "attempts": MAX_RETRIES + 1,
    }


def is_link_broken(result):
    """Determine whether a link should count as broken."""
    if result["status"] == "LOCAL":
        return False

    return (
        result["status"] is None
        or result["status"] >= 400
    )


def calculate_link_health(results):
    """Calculate the link health score out of 35."""
    if not results:
        return 25

    working_links = sum(
        not is_link_broken(result)
        for result in results
    )

    total_links = len(results)

    return round(
        (working_links / total_links) * 35
    )


def detect_readme_context(content, links):
    """Estimate the README's context from multiple README signals."""
    content_lower = content.lower()

    scores = {
        "Application / Portfolio": 0,
        "Library / Package": 0,
        "Documentation / Tutorial": 0,
        "Utility / Tool": 0,
        "General Project": 0,
    }

    if any(
        phrase in content_lower
        for phrase in (
            "web application",
            "application",
            "portfolio",
            "dashboard",
            "frontend",
            "full stack",
            "full-stack",
        )
    ):
        scores["Application / Portfolio"] += 3

    if any(
        phrase in content_lower
        for phrase in (
            "library",
            "package",
            "pip install",
            "npm install",
            "install via",
        )
    ):
        scores["Library / Package"] += 3

    if any(
        phrase in content_lower
        for phrase in (
            "documentation",
            "tutorial",
            "guide",
            "api reference",
            "api documentation",
        )
    ):
        scores["Documentation / Tutorial"] += 3

    if any(
        phrase in content_lower
        for phrase in (
            "cli",
            "command line",
            "command-line",
            "utility",
            "tool",
        )
    ):
        scores["Utility / Tool"] += 3

    if len(content) > 3000:
        scores["Documentation / Tutorial"] += 1

    if len(content) < 1200:
        scores["General Project"] += 1

    if any(
        "docs." in link.lower()
        or "/docs" in link.lower()
        or "readthedocs.io" in link.lower()
        for link in links
    ):
        scores["Documentation / Tutorial"] += 2

    if any(
        "github.io" in link.lower()
        or "vercel.app" in link.lower()
        or "netlify.app" in link.lower()
        for link in links
    ):
        scores["Application / Portfolio"] += 2

    return max(scores, key=scores.get)


def calculate_content_score(content):
    """Calculate README content score out of 30."""
    content_lower = content.lower()
    score = 0

    if len(content.strip()) >= 300:
        score += 5

    if len(content.strip()) >= 1000:
        score += 5

    if any(
        word in content_lower
        for word in (
            "feature",
            "functionality",
            "capabilities",
        )
    ):
        score += 5

    if any(
        word in content_lower
        for word in (
            "installation",
            "install",
            "setup",
            "getting started",
        )
    ):
        score += 5

    if any(
        word in content_lower
        for word in (
            "usage",
            "how to use",
            "example",
            "run locally",
        )
    ):
        score += 5

    if any(
        word in content_lower
        for word in (
            "license",
            "licence",
            "contributing",
        )
    ):
        score += 5

    return min(score, 30)


def calculate_section_score(detected_sections):
    """Calculate important section score out of 25."""
    section_points = {
        "Installation": 5,
        "Usage": 5,
        "Features": 5,
        "Demo": 5,
        "Contributing / License": 5,
    }

    score = sum(
        section_points[section]
        for section in detected_sections
    )

    return min(score, 25)


def has_readme_title(content):
    """Detect whether the README has a clear project title."""
    lines = content.splitlines()

    for line in lines:
        stripped = line.strip()

        if re.match(
            r"^#\s+\S+",
            stripped,
        ):
            return True

    if HTML_H1_PATTERN.search(content):
        return True

    for index in range(len(lines) - 1):
        current_line = lines[index].strip()
        next_line = lines[index + 1].strip()

        if (
            current_line
            and re.match(
                r"^=+\s*$",
                next_line,
            )
        ):
            return True

    beginning = "\n".join(lines[:40])

    image_alts = HTML_IMAGE_ALT_PATTERN.findall(
        beginning
    )

    ignored_alt_text = {
        "logo",
        "image",
        "screenshot",
        "test",
        "coverage",
        "badge",
        "package version",
        "supported python versions",
    }

    for alt_text in image_alts:
        normalized_alt = alt_text.strip().lower()

        if (
            normalized_alt
            and normalized_alt not in ignored_alt_text
            and len(normalized_alt) <= 80
        ):
            return True

    return False


def calculate_quality_score(content):
    """Calculate basic README quality score out of 10."""
    score = 0

    lines = content.splitlines()

    if lines:
        score += 2

    if has_readme_title(content):
        score += 3

    if "```" in content:
        score += 2

    if len(content.strip()) >= 500:
        score += 3

    return min(score, 10)


def calculate_health_score(
    results,
    content,
    detected_sections,
    context,
):
    """Calculate the overall README health score out of 100."""
    link_health = calculate_link_health(results)

    content_score = calculate_content_score(
        content
    )

    section_score = calculate_section_score(
        detected_sections
    )

    quality_score = calculate_quality_score(
        content
    )

    if not results:
        context_link_scores = {
            "Application / Portfolio": 20,
            "Library / Package": 20,
            "Utility / Tool": 25,
            "Documentation / Tutorial": 30,
            "General Project": 25,
        }

        link_health = context_link_scores.get(
            context,
            25,
        )

    total_score = (
        link_health
        + content_score
        + section_score
        + quality_score
    )

    breakdown = {
        "Link Health": link_health,
        "README Content": content_score,
        "Important Sections": section_score,
        "Basic Quality": quality_score,
    }

    return total_score, breakdown


def get_health_label(score):
    """Return a label for the README health score."""
    if score >= 90:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 40:
        return "Needs Attention"

    return "Poor"


def display_result(index, result):
    """Display the result of a single link check."""
    link_type = classify_link(result["url"])

    if result["status"] == "LOCAL":
        print(
            f"{index}. ~ {result['url']}"
        )
        print("   Status: LOCAL")
        print(f"   Type: {link_type}")
        print(
            "   Note: Local development/example URL"
        )
        return

    if is_link_broken(result):
        print(
            f"{index}. ✗ {result['url']}"
        )

        if result["error"]:
            print(
                f"   Error: {result['error']}"
            )

        print(f"   Type: {link_type}")
        print(
            f"   Attempts: {result['attempts']}"
        )
        print(
            f"   Response time: "
            f"{result['response_time']:.2f}s"
        )

    else:
        print(
            f"{index}. ✓ {result['url']}"
        )
        print(
            f"   Status: {result['status']}"
        )
        print(f"   Type: {link_type}")

        if result["attempts"] > 1:
            print(
                f"   Retry successful "
                f"(attempt {result['attempts']})"
            )

        if result["final_url"] != result["url"]:
            print(
                f"   Redirected to: "
                f"{result['final_url']}"
            )

        print(
            f"   Response time: "
            f"{result['response_time']:.2f}s"
        )


def display_link_statistics(
    links,
    duplicate_links,
):
    """Display link counts and duplicate URL information."""
    total_links = len(links)

    unique_links = len(
        set(
            normalize_url(link)
            for link in links
        )
    )

    duplicate_occurrences = (
        total_links - unique_links
    )

    print()
    print("Link Statistics")
    print("----------------")
    print(f"Total links:      {total_links}")
    print(f"Unique links:     {unique_links}")
    print(
        f"Duplicate links:  {duplicate_occurrences}"
    )

    if duplicate_links:
        print()
        print("Duplicate Links:")

        for url, count in duplicate_links.items():
            print(f"→ {url}")
            print(
                f"  Found {count} times"
            )


def display_link_type_breakdown(links):
    """Display the distribution of link types."""
    type_counts = Counter(
        classify_link(link)
        for link in links
    )

    print()
    print("Link Type Breakdown")
    print("--------------------")

    preferred_order = (
        "GitHub",
        "Documentation",
        "Demo",
        "LinkedIn",
        "Email",
        "Local/Example",
        "External Website",
    )

    for link_type in preferred_order:
        count = type_counts.get(
            link_type,
            0,
        )

        if count:
            print(
                f"{link_type + ':':<20}{count}"
            )


def display_summary(
    results,
    content,
    detected_sections,
    context,
    links,
    duplicate_links,
):
    """Display the complete README health summary."""
    total_links = len(links)

    working_links = sum(
        not is_link_broken(result)
        for result in results
    )

    broken_links = sum(
        is_link_broken(result)
        for result in results
    )

    local_links = sum(
        result["status"] == "LOCAL"
        for result in results
    )

    health_score, breakdown = calculate_health_score(
        results,
        content,
        detected_sections,
        context,
    )

    health_label = get_health_label(
        health_score
    )

    display_link_statistics(
        links,
        duplicate_links,
    )

    display_link_type_breakdown(
        links
    )

    print()
    print("-----------------------------------")
    print("README Health Summary")
    print("-----------------------------------")

    print(f"README Context: {context}")
    print(f"Total links:   {total_links}")
    print(f"Working links: {working_links}")
    print(f"Broken links:  {broken_links}")

    if local_links:
        print(
            f"Local/example: {local_links}"
        )

    print(
        f"README Health: {health_score}% "
        f"({health_label})"
    )

    print()
    print("Score Breakdown:")

    print(
        f"- Link Health:        "
        f"{breakdown['Link Health']}/35"
    )

    print(
        f"- README Content:     "
        f"{breakdown['README Content']}/30"
    )

    print(
        f"- Important Sections: "
        f"{breakdown['Important Sections']}/25"
    )

    print(
        f"- Basic Quality:      "
        f"{breakdown['Basic Quality']}/10"
    )

    if broken_links:
        print()
        print("Broken Links:")

        for result in results:
            if is_link_broken(result):
                print(
                    f"- {result['url']}"
                )

    suggestions = generate_suggestions(
        results,
        content,
        detected_sections,
        context,
    )

    if suggestions:
        print()
        print("Suggestions:")

        for suggestion in suggestions:
            print(f"→ {suggestion}")


def generate_suggestions(
    results,
    content,
    detected_sections,
    context,
):
    """Generate context-aware README improvement suggestions."""
    suggestions = []

    broken_links = [
        result
        for result in results
        if is_link_broken(result)
    ]

    if broken_links:
        suggestions.append(
            f"Fix {len(broken_links)} broken links."
        )

    if not has_readme_title(content):
        suggestions.append(
            "Add a clear README title."
        )

    if context == "Application / Portfolio":
        link_types = {
            classify_link(result["url"])
            for result in results
            if not is_link_broken(result)
        }

        if "Demo" not in link_types:
            suggestions.append(
                "Consider adding a live demo link."
            )

        if "Documentation" not in link_types:
            suggestions.append(
                "Consider adding a documentation "
                "or setup link."
            )

    elif context == "Library / Package":
        if "Installation" not in detected_sections:
            suggestions.append(
                "Add a clear installation section."
            )

        if "Usage" not in detected_sections:
            suggestions.append(
                "Add a usage section with examples."
            )

    elif context == "Documentation / Tutorial":
        if "Usage" not in detected_sections:
            suggestions.append(
                "Add a clear usage or getting "
                "started section."
            )

        if "Installation" not in detected_sections:
            suggestions.append(
                "Add installation or setup instructions."
            )

    elif context == "Utility / Tool":
        if "Installation" not in detected_sections:
            suggestions.append(
                "Add clear installation instructions."
            )

        if "Usage" not in detected_sections:
            suggestions.append(
                "Add usage examples for the tool."
            )

    elif context == "General Project":
        if "Features" not in detected_sections:
            suggestions.append(
                "Add a clear features section."
            )

        if "Usage" not in detected_sections:
            suggestions.append(
                "Add a usage section with examples."
            )

    if not results:
        suggestions.append(
            "Consider adding relevant links such as "
            "a live demo, documentation, or related "
            "resources for a more complete README."
        )

    return suggestions


def main():
    """Run RepoRadar from the command line."""
    if len(sys.argv) != 2:
        print(
            "Usage: python reporadar.py "
            "<README path or GitHub repository URL>"
        )
        sys.exit(1)

    target = sys.argv[1]

    print(
        "RepoRadar - GitHub README Link Checker"
    )
    print("----------------------------------------")

    if target.startswith(
        "https://github.com/"
    ):
        print(f"Repository: {target}")
        print()
        print("Fetching README...")

        try:
            content = fetch_github_readme(
                target
            )

        except (
            requests.RequestException,
            ValueError,
        ) as error:
            print(f"Error: {error}")
            sys.exit(1)

    else:
        print(f"README: {target}")
        print()
        print("Reading README...")

        try:
            content = read_local_readme(
                target
            )

        except OSError as error:
            print(f"Error: {error}")
            sys.exit(1)

    links = extract_links(content)

    duplicate_links = find_duplicate_links(
        links
    )

    print(
        f"Links found: {len(links)}"
    )

    if not links:
        print(
            "No HTTP/HTTPS Markdown links found."
        )

    results = []

    unique_links = []
    seen_links = set()

    for link in links:
        normalized_link = normalize_url(link)

        if normalized_link not in seen_links:
            seen_links.add(normalized_link)
            unique_links.append(link)

    if unique_links:
        print()
        print("Checking links...")
        print()

        for index, link in enumerate(
            unique_links,
            start=1,
        ):
            result = check_link(link)
            results.append(result)
            display_result(index, result)

    detected_sections = detect_sections(
        content
    )

    context = detect_readme_context(
        content,
        links,
    )

    display_summary(
        results,
        content,
        detected_sections,
        context,
        links,
        duplicate_links,
    )


if __name__ == "__main__":
    main()