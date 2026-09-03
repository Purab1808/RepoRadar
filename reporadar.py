"""RepoRadar - a small CLI tool for checking links in README files."""

import re
import sys
from pathlib import Path

import requests


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
REQUEST_TIMEOUT = 10


def extract_links(readme_path):
    """Extract HTTP and HTTPS links from a Markdown README."""
    content = Path(readme_path).read_text(encoding="utf-8")
    return MARKDOWN_LINK_PATTERN.findall(content)


def check_link(url):
    """Check whether a URL is reachable and return its status."""
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

        return response.status_code, response.url

    except requests.RequestException as error:
        return None, str(error)


def main():
    """Run the RepoRadar command-line interface."""
    if len(sys.argv) != 2:
        print("Usage: python reporadar.py <README.md>")
        return

    readme_path = sys.argv[1]

    if not Path(readme_path).is_file():
        print(f"Error: File not found: {readme_path}")
        return

    links = extract_links(readme_path)

    print("\nRepoRadar - README Link Checker")
    print("-" * 35)
    print(f"Links found: {len(links)}")

    if not links:
        print("No HTTP/HTTPS Markdown links found.")
        return

    print("\nChecking links...\n")

    for number, link in enumerate(links, start=1):
        status_code, result = check_link(link)

        if status_code is not None:
            print(f"{number}. ✓ {link}")
            print(f"   Status: {status_code}")
        else:
            print(f"{number}. ✗ {link}")
            print(f"   Error: {result}")


if __name__ == "__main__":
    main()