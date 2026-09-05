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

### ⚡ Reliability

- Request timeout handling
- Automatic retry for transient failures
- `HEAD` request support
- `GET` fallback when `HEAD` returns `405`
- Redirect-aware checking
- Local development URLs are not treated as broken

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
                  │ Checking            │
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
                  └─────────────────────┘
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

🔄 Retry & Redirect Handling

Some websites may temporarily fail or behave differently depending on the request method.

RepoRadar handles this by:

Sending a HEAD request
Falling back to GET when the server returns 405
Retrying transient request failures
Following redirects
Reporting the final destination URL
Measuring response time
🏠 Local Development Links

README files often contain example URLs such as:

http://127.0.0.1:8000/docs
http://localhost:3000
http://127.0.0.1:8000/api

RepoRadar recognizes these as:

Type: Local/Example
Status: LOCAL

They are not counted as broken links.

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

🗺️ Roadmap

RepoRadar is actively evolving.

✅ Completed
 Markdown link extraction
 HTTP/HTTPS link validation
 Broken link reporting
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
 Improved link classification
🔜 Planned
 More powerful CLI options
 Cleaner report modes
 Additional README quality checks
 Exportable reports
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