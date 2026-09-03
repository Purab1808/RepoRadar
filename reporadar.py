"""RepoRadar - a small CLI tool for checking links in README files."""

import re
import sys
from pathlib import Path


MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")


def extract_links(readme_path):
    """Extract HTTP and HTTPS links from a Markdown README."""
    content = Path(readme_path).read_text(encoding="utf-8")
    return MARKDOWN_LINK_PATTERN.findall(content)


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

    print(f"\nRepoRadar - README Link Checker")
    print("-" * 35)
    print(f"Links found: {len(links)}")

    if not links:
        print("No HTTP/HTTPS Markdown links found.")
        return

    print("\nLinks:")
    for number, link in enumerate(links, start=1):
        print(f"{number}. {link}")


if __name__ == "__main__":
    main()