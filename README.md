<div align="center">

# 🔎 RepoRadar

### A lightweight CLI tool for analyzing and validating GitHub README files.

Extract links • Detect duplicates • Check availability • Classify links • Score README health

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Requests](https://img.shields.io/badge/Requests-HTTP%20Client-2C2D72?style=for-the-badge)
![CLI](https://img.shields.io/badge/Interface-CLI-black?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

## 📌 What is RepoRadar?

**RepoRadar** is a lightweight Python CLI tool that analyzes Markdown README files and helps identify problems with project links and README structure.

Give RepoRadar either a **local README file** or a **public GitHub repository URL**, and it will:

- 🔗 Extract Markdown links
- ♻️ Detect duplicate URLs
- 🌐 Check link availability
- 🔁 Detect redirects
- 🔄 Retry transient request failures
- 🏷️ Classify links by type
- 🏠 Detect local/example development URLs
- 📊 Generate link statistics
- ❤️ Calculate a README health score
- 🧠 Detect README context and important sections
- 💡 Generate improvement suggestions
- ⚠️ Explain why broken links failed
- 📄 Generate machine-readable JSON reports
- ⚙️ Provide CLI controls for analysis behavior

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔗 Link Analysis

- Markdown HTTP/HTTPS link extraction
- Unique link detection
- Duplicate link detection
- Link availability checking
- Broken link detection
- HTTP status reporting
- Response time measurement
- Redirect detection
- Detailed failure reason detection

</td>

<td width="50%">

### 🧠 README Analysis

- README title detection
- Section detection
- Project context detection
- README content scoring
- Basic quality scoring
- Overall health score
- Context-aware suggestions

</td>
</tr>

<tr>
<td width="50%">

### 🏷️ Link Classification

RepoRadar currently recognizes:

- GitHub
- Documentation
- Demo
- LinkedIn
- Email
- Social Media
- Package / Dependency
- Local / Example
- External Website

</td>

<td width="50%">

### ⚡ Reliability & Control

- Request timeout handling
- Automatic retry for transient failures
- Optional retry disabling
- `HEAD` request support
- `GET` fallback when `HEAD` returns `405`
- Redirect-aware checking
- Local development URLs are not treated as broken
- Optional link checking

</td>
</tr>

<tr>
<td width="50%">

### 📊 Reporting

- Human-readable CLI reports
- Link statistics
- Link type breakdown
- Broken link summaries
- Failure reason reporting
- README health score
- Improvement suggestions

</td>

<td width="50%">

### 📄 JSON Output

RepoRadar can generate structured JSON reports containing:

- Link statistics
- Duplicate URLs
- Health score
- Score breakdown
- Suggestions
- Individual link results
- Failure reasons
- Request configuration

</td>
</tr>
</table>

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Purab1808/RepoRadar.git
cd RepoRadar
2. Install dependencies
pip install -r requirements.txt
3. Run RepoRadar

You can analyze either a local README or a public GitHub repository.

Local README
python reporadar.py README.md
GitHub repository
python reporadar.py https://github.com/fastapi/fastapi
⚙️ CLI Options

RepoRadar provides several options to control how the analysis runs.

--timeout

Set the HTTP request timeout in seconds.

python reporadar.py README.md --timeout 5

Default:

10 seconds
--no-check

Skip HTTP link checking.

Useful when you only want README analysis without making network requests.

python reporadar.py README.md --no-check
--no-retry

Disable automatic retry attempts for failed requests.

python reporadar.py README.md --no-retry

By default, RepoRadar allows one retry after a failed request.

--json

Output the complete analysis report as JSON.

python reporadar.py README.md --json

JSON output can also be combined with other CLI options:

python reporadar.py README.md --json --timeout 5
python reporadar.py README.md --json --no-check

When --no-check is used with --json, link checking fields such as working and broken link counts are reported as null.

View all available options
python reporadar.py --help
🔍 How It Works

RepoRadar follows a simple analysis pipeline:

                  ┌─────────────────────┐
                  │   README Input      │
                  │ Local / GitHub URL  │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Read README        │
                  │  Extract Content    │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │  Extract Links      │
                  └──────────┬──────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
      ┌──────────────────┐       ┌──────────────────┐
      │ Duplicate        │       │ Link             │
      │ Detection        │       │ Classification   │
      └────────┬─────────┘       └────────┬─────────┘
               │                          │
               └────────────┬─────────────┘
                            ▼
                  ┌─────────────────────┐
                  │ Link Availability   │
                  │ Checking             │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Failure Analysis    │
                  │ • HTTP Status       │
                  │ • Timeout           │
                  │ • Connection Error  │
                  │ • DNS Error         │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ README Analysis     │
                  │ • Context           │
                  │ • Sections          │
                  │ • Content           │
                  │ • Quality            │
                  └──────────┬──────────┘
                             │
                             ▼
                  ┌─────────────────────┐
                  │ Health Score +      │
                  │ Suggestions         │
                  └──────────┬──────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
        ┌─────────────────┐     ┌─────────────────┐
        │ Human-readable  │     │ JSON Report     │
        │ CLI Report      │     │ (--json)        │
        └─────────────────┘     └─────────────────┘
📊 Example Output

Running RepoRadar against a public repository:

RepoRadar - GitHub README Link Checker
----------------------------------------
Repository: https://github.com/fastapi/fastapi

Fetching README...
Links found: 42

Checking links...

1. ✓ https://fastapi.tiangolo.com
   Status: 200
   Type: External Website
   Response time: 0.57s

2. ✓ https://github.com/fastapi/fastapi
   Status: 200
   Type: GitHub
   Response time: 1.15s

3. ✓ https://github.com/OAI/OpenAPI-Specification
   Status: 200
   Type: GitHub
   Response time: 1.16s

...

14. ~ http://127.0.0.1:8000/items/5?q=somequery
   Status: LOCAL
   Type: Local/Example
   Note: Local development/example URL
Link Statistics
Link Statistics
----------------
Total links:      42
Unique links:     37
Duplicate links:  5

Duplicate Links:
→ https://uvicorn.dev
  Found 2 times

→ http://127.0.0.1:8000/docs
  Found 2 times

→ https://fastapicloud.com
  Found 3 times
Link Type Breakdown
Link Type Breakdown
--------------------
GitHub:                 9
Documentation:          3
Social Media:           1
Local/Example:          5
External Website:       24
README Health
-----------------------------------
README Health Summary
-----------------------------------

README Context: Documentation / Tutorial
Total links:   42
Working links: 37
Broken links:  0
Local/example: 3

README Health: 95% (Excellent)

Score Breakdown:

- Link Health:        35/35
- README Content:     30/30
- Important Sections: 20/25
- Basic Quality:      10/10
⚠️ Broken Link & Failure Analysis

When RepoRadar detects a broken link, it provides additional information about why the request failed.

For example:

2. ✗ https://example.com/old-page
   Reason: HTTP 404 - Not Found
   Type: External Website
   Attempts: 1
   Response time: 0.84s

RepoRadar can identify common failure reasons such as:

Failure Reason	Description
HTTP 400 - Bad Request	The server rejected the request
HTTP 401 - Unauthorized	Authentication is required
HTTP 403 - Forbidden	Access to the resource is forbidden
HTTP 404 - Not Found	The requested resource does not exist
HTTP 408 - Request Timeout	The server timed out the request
HTTP 429 - Too Many Requests	Rate limit or request throttling
HTTP 500 - Internal Server Error	Server-side failure
HTTP 502 - Bad Gateway	Invalid response from an upstream server
HTTP 503 - Service Unavailable	Server is temporarily unavailable
HTTP 504 - Gateway Timeout	Upstream server timed out
Request Timeout	The HTTP request timed out
Connection Error	Connection to the server failed
DNS Resolution Error	The domain could not be resolved
SSL Error	SSL/TLS connection problem

This makes broken-link reports more useful than simply reporting that a URL failed.

📄 JSON Reports

RepoRadar supports machine-readable JSON output using:

python reporadar.py README.md --json

A JSON report contains structured information such as:

{
  "target": "README.md",
  "context": "Documentation / Tutorial",
  "links": {
    "total": 4,
    "unique": 4,
    "duplicate_occurrences": 0,
    "working": 4,
    "broken": 0,
    "local_or_example": 0,
    "type_breakdown": {
      "External Website": 4
    }
  },
  "health": {
    "score": 85,
    "label": "Good"
  },
  "suggestions": [],
  "link_results": []
}

Individual link results can contain:

{
  "url": "https://example.com/old-page",
  "status": 404,
  "final_url": "https://example.com/old-page",
  "response_time": 0.84,
  "error": null,
  "attempts": 1,
  "type": "External Website",
  "broken": true,
  "failure_reason": "HTTP 404 - Not Found"
}

JSON output is useful for future automation, integrations, scripts, and web-based interfaces.

❤️ README Health Score

RepoRadar calculates a score out of 100 using four areas:

Category	Maximum
🔗 Link Health	35
📝 README Content	30
📚 Important Sections	25
✨ Basic Quality	10
Total	100
Health Ratings
Score	Rating
90–100	🟢 Excellent
70–89	🔵 Good
40–69	🟡 Needs Attention
0–39	🔴 Poor

The Link Health component also adapts its baseline when a README contains no checkable links, based on the detected README context.

🏷️ Link Classification

RepoRadar categorizes README links to make the report easier to understand.

Type	Examples
GitHub	Repository and GitHub project links
Documentation	Documentation and API reference links
Demo	Deployed/live project links
LinkedIn	LinkedIn profiles
Email	Email links
Social Media	YouTube, X, Instagram, Discord, etc.
Package / Dependency	PyPI, npm, Docker Hub, etc.
Local / Example	localhost, 127.0.0.1, etc.
External Website	Other external resources
♻️ Duplicate Detection

RepoRadar does not repeatedly check the same normalized URL.

For example:

https://example.com
https://example.com/

are treated as the same URL for duplicate detection.

This helps reduce unnecessary HTTP requests while still reporting how many times a link appears in the README.

Example:

Total links:      42
Unique links:     37
Duplicate links:  5

The tool checks each unique normalized URL once.

🔄 Retry & Redirect Handling

Some websites may temporarily fail or behave differently depending on the request method.

RepoRadar handles this by:

Sending a HEAD request
Falling back to GET when the server returns 405
Retrying failed requests when retry is enabled
Following redirects
Reporting the final destination URL
Measuring response time
Reporting the number of attempts

By default, RepoRadar allows one retry for failed requests.

Retry behavior can be disabled:

python reporadar.py README.md --no-retry
🏠 Local Development Links

README files often contain example URLs such as:

http://127.0.0.1:8000/docs
http://localhost:3000
http://127.0.0.1:8000/api

RepoRadar recognizes these as:

Type: Local/Example
Status: LOCAL

They are not counted as broken links.

This prevents normal development/example URLs from negatively affecting the README health score.

📊 Link Statistics

RepoRadar provides statistics about the links found in a README.

The report includes:

Total link occurrences
Unique normalized links
Duplicate occurrences
Link type distribution
Working links
Broken links
Local/example links

Link type breakdown counts the original link occurrences, while availability checking is performed once per unique normalized URL.

🧠 README Context Detection

RepoRadar estimates the purpose of a README using multiple signals.

Current contexts include:

Application / Portfolio
Library / Package
Documentation / Tutorial
Utility / Tool
General Project

The detected context is used to make suggestions more relevant.

For example, a library README may receive suggestions for:

Add a clear installation section.
Add a usage section with examples.

while an application README may receive suggestions for:

Consider adding a live demo link.
Consider adding a documentation or setup link.
💡 README Improvement Suggestions

RepoRadar generates suggestions based on the README's detected context and analysis results.

Examples include:

→ Fix 2 broken links.
→ Add a clear README title.
→ Add a clear installation section.
→ Add a usage section with examples.
→ Consider adding a live demo link.

Suggestions are designed to highlight practical README improvements rather than only reporting raw statistics.

📁 Project Structure
RepoRadar/
│
├── reporadar.py
├── README.md
├── requirements.txt
└── .gitignore
reporadar.py

Contains the complete RepoRadar CLI and analysis engine.

requirements.txt

Contains the external Python dependency used by RepoRadar.

.gitignore

Prevents generated Python files, virtual environments, and environment files from being committed.

🛠️ Tech Stack
Python
Requests
Regular Expressions
GitHub REST API
argparse
JSON
Command Line Interface

No frontend or database is required for the current CLI version.

💡 Why RepoRadar?

README files are often treated as an afterthought, but they are one of the first things people see when visiting a GitHub project.

A README can contain:

Broken links
Duplicate links
Missing sections
Poor documentation
Outdated demos
Unclear project information

RepoRadar provides a quick way to inspect these areas from the command line.

It is designed to be:

Lightweight
Easy to run
Useful for developers
Automation-friendly
Extensible toward future web-based analysis
🗺️ Roadmap

RepoRadar is actively evolving.

✅ Completed
Markdown link extraction
HTTP/HTTPS link validation
Broken link reporting
Detailed broken-link failure reasons
HTTP status reporting
Response time measurement
README health scoring
GitHub repository URL support
Link classification
Context-aware README analysis
README section detection
Local development link detection
Retry handling
README title detection
Duplicate link detection
Link statistics
Redirect detection
--timeout CLI option
--no-check CLI option
--no-retry CLI option
--json output mode
Machine-readable JSON reports
🔜 Planned
Cleaner report modes
Additional README quality checks
Exportable report files
More advanced link analysis
Modular project architecture
Web API
Web interface
Interactive README analysis dashboard
🤝 Contributing

Contributions, suggestions, and ideas are welcome.

If you find a bug or have an idea for improving RepoRadar:

Fork the repository
Create a feature branch
Make your changes
Test the changes
Open a Pull Request
📄 License

This project is open source.

See the repository for the current license information.

🔎 RepoRadar

Scan it. Check it. Understand it.

Made with ❤️ using Python.

⭐ If you find RepoRadar useful, consider starring the repository.