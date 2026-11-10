"""Live discovery via provider APIs; no HTML scraping."""
import os
import re
import requests


def search_jobs(query: str, where: str = "Egypt", page: int = 1, results_per_page: int = 10):
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    if serpapi_key:
        response = requests.get("https://serpapi.com/search.json", params={
            "engine": "google_jobs", "q": query, "location": where,
            "api_key": serpapi_key,
            "start": max(0, (int(page) - 1) * int(results_per_page))
        }, timeout=20)
        response.raise_for_status()
        data = response.json()
        items = []
        for job in data.get("jobs_results", [])[:min(max(int(results_per_page), 1), 25)]:
            ext = job.get("detected_extensions") or {}
            items.append({
                "title": job.get("title", "Untitled role"),
                "company": job.get("company_name", "Not specified"),
                "location": job.get("location", where),
                "url": job.get("share_link") or ((job.get("related_links") or [{}])[0].get("link", "")),
                "description": (job.get("description") or "")[:1200],
                "created": ext.get("posted_at"),
                "source": "Google Jobs via SerpAPI"
            })
        return {"configured": True, "source": "Google Jobs via SerpAPI", "count": len(items), "items": items}

    app_id, app_key = os.getenv("ADZUNA_APP_ID"), os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        return {
            "configured": False, "source": "Job discovery APIs", "items": [],
            "message": "Set SERPAPI_API_KEY for Google Jobs search, or set ADZUNA_APP_ID and ADZUNA_APP_KEY for Adzuna."
        }
    country = os.getenv("ADZUNA_COUNTRY", "gb").lower()
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{max(1, int(page))}"
    response = requests.get(url, params={
        "app_id": app_id, "app_key": app_key, "what": query, "where": where,
        "results_per_page": min(max(int(results_per_page), 1), 25),
        "content-type": "application/json"
    }, timeout=20)
    response.raise_for_status()
    data = response.json()
    items = []
    for job in data.get("results", []):
        items.append({
            "title": job.get("title", "Untitled role"),
            "company": (job.get("company") or {}).get("display_name", "Not specified"),
            "location": (job.get("location") or {}).get("display_name", where),
            "url": job.get("redirect_url", ""),
            "description": (job.get("description") or "")[:1200],
            "created": job.get("created"),
            "source": "Adzuna"
        })
    return {"configured": True, "source": "Adzuna API", "count": data.get("count", len(items)), "items": items}


def _split_skill_queries(query: str):
    """Extract up to three distinct skill phrases without matching nested terms twice."""
    known_skills = [
        "networking and routing", "networking & routing",
        "automation and devops", "automation & devops",
        "linux administration", "backup and recovery",
        "routing and switching", "network automation",
        "network security", "cloud networking",
        "windows server", "cloud computing",
        "cybersecurity", "virtualization",
        "devops", "ansible", "python", "linux"
    ]
    text = (query or "").strip()
    if not text:
        return []

    lowered = text.lower()
    matches = []

    # Match longer phrases first, preventing "Linux" from duplicating
    # "Linux Administration".
    for skill in sorted(known_skills, key=len, reverse=True):
        pattern = r"(?<!\\w)" + re.escape(skill) + r"(?!\\w)"
        match = re.search(pattern, lowered)
        if not match:
            continue

        if any(
            skill in existing or existing in skill
            for existing, _, _ in matches
        ):
            continue

        normalized = skill.replace(" and ", " & ")
        matches.append((normalized, match.start(), match.end()))

    matches.sort(key=lambda item: item[1])
    if matches:
        return [item[0] for item in matches[:3]]

    parts = [
        part.strip() for part in re.split(r"[,;\\n|]+", text)
        if part.strip()
    ]
    return parts[:3] or [text]


def _course_relevance(item, skill):
    """Require a relevant technical topic and an approved learning domain."""
    from urllib.parse import urlparse

    title = item.get("title", "").lower()
    description = item.get("description", "").lower()
    url = item.get("url", "").lower()
    content = f"{title} {description} {url}".lower().replace("&", "and")

    approved_domains = (
        "learn.microsoft.com",
        "netacad.com",
        "veeam.com",
        "commvault.com",
        "cisco.com",
        "redhat.com",
        "linuxfoundation.org",
        "skillsbuild.org",
        "lpi.org",
        "edx.org",
        "coursera.org",
        "datacamp.com",
        "github.com",
        "ansible.com",
    )
    hostname = urlparse(url).hostname or ""
    if not any(
        hostname == domain or hostname.endswith("." + domain)
        for domain in approved_domains
    ):
        return 0

    skill_key = skill.lower().replace("&", "and")

    topic_terms = {
        "network security": [
            "network security", "cybersecurity", "firewall", "network defense"
        ],
        "linux administration": [
            "linux administration", "linux system administration",
            "linux", "red hat", "lpic"
        ],
        "automation and devops": [
            "devops", "automation", "ansible", "ci/cd",
            "continuous integration", "continuous delivery"
        ],
        "networking and routing": ["networking", "routing", "switching"],
        "networking": ["networking", "routing", "switching"],
        "cloud networking": [
            "cloud networking", "azure networking",
            "aws networking", "cloud network"
        ],
        "virtualization": ["virtualization", "vmware", "hyper-v"],
        "windows server": [
            "windows server", "active directory", "windows administration"
        ],
        "backup and recovery": [
            "backup and recovery", "backup", "restore",
            "disaster recovery", "veeam", "data protection"
        ],
        "python": ["python"],
        "ansible": ["ansible"],
        "devops": [
            "devops", "ci/cd", "continuous integration", "continuous delivery"
        ],
    }

    aliases = topic_terms.get(skill_key, [skill_key])
    if not any(term in content for term in aliases):
        return 0

    excluded_terms = (
        "license renewal", "renewal center", "datasheet",
        "press release", "press-release", "blogs/", "community.commvault.com", "buy now", "product overview",
    )
    if any(term in content for term in excluded_terms):
        return 0

    learning_terms = (
        "course", "training", "certification", "tutorial",
        "learning path", "university", "academy", "education",
    )
    learning_target = f"{title} {url}"
    if not any(term in learning_target for term in learning_terms):
        return 0

    score = 3
    if any(term in title for term in aliases):
        score += 3
    if any(term in title for term in learning_terms):
        score += 2
    return score


def search_courses(query: str, limit: int = 10):
    """Search separately for relevant technical skills and remove duplicates/noise."""
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return {
            "configured": False, "source": "Google Search via SerpAPI", "items": [],
            "message": "Set SERPAPI_API_KEY to enable live course discovery."
        }

    max_items = min(max(int(limit), 1), 10)
    skills = _split_skill_queries(query)
    if not skills:
        return {
            "configured": True, "source": "Google Search via SerpAPI",
            "count": 0, "items": [],
            "message": "Provide one or more technical skills to search for."
        }

    # Search provider sites using skill-specific aliases.
    search_profiles = {
        "networking and routing": {
            "domains": ["netacad.com", "cisco.com", "learn.microsoft.com"],
            "terms": [
                "networking course",
                "routing and switching training",
                "network fundamentals",
            ],
        },
        "network security": {
            "domains": ["netacad.com", "cisco.com", "learn.microsoft.com"],
            "terms": [
                "network security training",
                "firewall security course",
                "network defense",
            ],
        },
        "linux administration": {
            "domains": ["redhat.com", "linuxfoundation.org", "lpi.org"],
            "terms": [
                "linux system administration training",
                "linux administration course",
            ],
        },
        "automation and devops": {
            "domains": [
                "learn.microsoft.com",
                "redhat.com",
                "skillsbuild.org",
                "docs.github.com",
                "github.com",
                "ansible.com",
            ],
            "terms": [
                "DevOps learning path",
                "Ansible automation training",
                "GitHub Actions CI/CD tutorial",
                "continuous integration continuous delivery",
            ],
        },
        "cloud networking": {
            "domains": ["learn.microsoft.com", "cisco.com"],
            "terms": [
                "cloud networking training",
                "Azure networking learning path",
                "AWS networking training",
            ],
        },
        "virtualization": {
            "domains": ["learn.microsoft.com", "redhat.com", "edx.org"],
            "terms": [
                "virtualization training",
                "virtual machines course",
            ],
        },
        "windows server": {
            "domains": ["learn.microsoft.com"],
            "terms": [
                "Windows Server training",
                "Windows Server learning path",
                "Active Directory training",
            ],
        },
        "backup and recovery": {
            "domains": [
                "learn.veeam.com",
                "veeam.com",
                "learn.microsoft.com",
                "academy.commvault.com",
                "commvault.com",
            ],
            "terms": [
                "official Veeam backup training course",
                "Veeam University certification training",
                "official Commvault training course",
                "Commvault certification training",
                "Microsoft backup recovery learning path",
                "Microsoft disaster recovery training",
            ],
        },
    }

    results_by_url = {}

    for skill in skills:
        profile_key = skill.lower().replace("&", "and")
        profile = search_profiles.get(profile_key, {
            "domains": ["learn.microsoft.com", "cisco.com", "redhat.com"],
            "terms": [skill],
        })

        for domain in profile["domains"]:
            for term in profile["terms"]:
                q = f'site:{domain} "{term}"'
                response = requests.get("https://serpapi.com/search.json", params={
                    "engine": "google",
                    "q": q,
                    "api_key": api_key,
                    "num": min(max_items, 10)
                }, timeout=20)
                response.raise_for_status()
                data = response.json()

                for result in data.get("organic_results", []):
                    url = result.get("link", "").strip()
                    if not url or url in results_by_url:
                        continue

                    title = result.get("title", "Untitled learning resource")
                    description = (result.get("snippet") or "")[:1000]
                    lower_title = title.lower()
                    lower_url = url.lower()
                    if any(term in lower_url for term in ("/course", "/courses", "/learning-path", "/training/")):
                        resource_type = "Direct Course"
                    elif any(term in lower_url for term in ("/blog/", "/blogs/", "/news", "/press-release", "/resources/")) or "blog" in lower_title:
                        resource_type = "Informational Article"
                    else:
                        resource_type = "Training Portal"

                    item = {
                        "title": title,
                        "provider": result.get("source", result.get("displayed_link", domain)),
                        "url": url,
                        "description": description,
                        "source": "Google Search via SerpAPI",
                        "matched_skill": skill,
                        "resource_type": resource_type
                    }
                    score = _course_relevance(item, skill)
                    if score > 0:
                        item["_relevance"] = score
                        results_by_url[url] = item

    ranked = sorted(
        results_by_url.values(),
        key=lambda item: item.get("_relevance", 0),
        reverse=True
    )[:max_items]

    for item in ranked:
        item.pop("_relevance", None)

    return {
        "configured": True,
        "source": "Google Search via SerpAPI",
        "count": len(ranked),
        "skills_searched": skills,
        "items": ranked,
        "message": "" if ranked else "No sufficiently relevant course results were found. Try a more specific skill name."
    }
