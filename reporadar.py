"""RepoRadar - a small CLI tool for checking links in README files."""

import re
import sys
import time
from pathlib import Path

import requests


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
REQUEST_TIMEOUT = 10


def extract_links(readme_path):
    """Extract HTTP and HTTPS links from a Markdown README."""
    content = Path(readme_path).read_text(encoding="utf-8")
    return MARKDOWN_LINK_PATTERN.findall(content)


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
    if is_link_broken(result):
        print(f"{number}. ✗ {result['url']}")

        if result["status"] is not None:
            print(f"   Status: {result['status']}")
        else:
            print(f"   Error: {result['error']}")

    else:
        print(f"{number}. ✓ {result['url']}")
        print(f"   Status: {result['status']}")

        if result["final_url"] != result["url"]:
            print(f"   Redirected to: {result['final_url']}")

    print(f"   Response time: {result['response_time']:.2f}s")


def display_summary(results):
    """Display a summary of working and broken links."""
    broken_links = [result for result in results if is_link_broken(result)]
    working_links = [result for result in results if not is_link_broken(result)]

    print("\n" + "-" * 35)
    print("Link Check Summary")
    print("-" * 35)
    print(f"Total links:   {len(results)}")
    print(f"Working links: {len(working_links)}")
    print(f"Broken links:  {len(broken_links)}")

    if broken_links:
        print("\nBroken Links:")
        for result in broken_links:
            print(f"- {result['url']}")

    print()


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

    results = []

    for number, link in enumerate(links, start=1):
        result = check_link(link)
        results.append(result)
        display_result(number, result)

    display_summary(results)


if __name__ == "__main__":
    main()