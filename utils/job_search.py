# job_search.py
import os
import requests
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
CX = os.getenv("GOOGLE_CX")


def parse_relative_date(text: str) -> datetime:
    match = re.match(r"(\d+)\s+(day|week|month|year)s? ago", text)
    if not match:
        return datetime.utcnow()
    num, unit = int(match[1]), match[2]
    days = {"day":1, "week":7, "month":30, "year":365}[unit]
    return datetime.utcnow() - timedelta(days=days * num)


def clean_title(title: str) -> str:
    title = re.sub(r'^\d+[+,]?\s*', '', title)  # Remove leading numbers
    title = re.sub(r'\s*\(\d+\s*new\)$', '', title)  # Remove (X new)
    title = re.sub(r'\s*Jobs?\s*in\s*.*$', '', title)  # Remove "Jobs in Location"
    return title.strip()


def parse_snippet_fields(snippet: str, title: str) -> dict:
    # Extract location
    location_match = re.search(r'in\s+([^,]+(?:,\s*[^,]+)*)', title)
    location = location_match.group(1) if location_match else "Unknown"
    
    # Clean up location
    location = re.sub(r'\s*\(\d+\s*new\)$', '', location)
    location = location.strip()
    
    # Extract job type
    job_type = "Unknown"
    type_keywords = {
        "full": "Full-time",
        "part": "Part-time",
        "intern": "Internship",
        "contract": "Contract",
        "temporary": "Temporary"
    }
    
    for keyword, type_name in type_keywords.items():
        if keyword in snippet.lower():
            job_type = type_name
            break
    
    # Extract date
    date = None
    date_patterns = [
        r'(\d+)\s+(day|week|month|year)s?\s+ago',
        r'posted\s+(\d+)\s+(day|week|month|year)s?\s+ago',
        r'(\d+)\s+(day|week|month|year)s?\s+old'
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, snippet.lower())
        if match:
            date = parse_relative_date(match.group(0))
            break
    
    return {
        "location": location,
        "type": job_type,
        "date": date or datetime.utcnow()
    }


def _search_jobs(domain: str, titles: list[str], num: int, location: str = "Lebanon"):
    url = "https://www.googleapis.com/customsearch/v1"
    results = []
    
    # Adjust search parameters based on domain
    domain_params = {
        "linkedin.com/jobs": {
            "q_format": "{title} {location} jobs site:linkedin.com/jobs",
            "gl": "lb",
            "lr": "lang_en"
        },
        "bayt.com": {
            "q_format": "{title} Lebanon site:bayt.com",
            "gl": "lb",
            "lr": "lang_en"
        }
    }
    
    # Get domain-specific parameters
    params = domain_params.get(domain, {
        "q_format": "{title} {location} site:{domain}",
        "gl": "lb",
        "lr": "lang_en"
    })
    
    for title in titles:
        # Calculate how many results to fetch per query
        queries_needed = (num + 9) // 10  # Ceiling division
        
        for page in range(queries_needed):
            query = params["q_format"].format(
                title=title,
                location=location,
                domain=domain
            )
            
            search_params = {
                "key": API_KEY,
                "cx": CX,
                "q": query,
                "num": min(10, num - len(results)),
                "start": page * 10 + 1,
                "gl": params["gl"],
                "lr": params["lr"],
                "safe": "off"
            }
            
            try:
                r = requests.get(url, params=search_params)
                r.raise_for_status()
                
                items = r.json().get("items", [])
                if not items:
                    print(f"No results found for {query}")
                    break
                
                for item in items:
                    title = clean_title(item.get("title", ""))
                    fields = parse_snippet_fields(item.get("snippet", ""), item.get("title", ""))
                    link = item.get("link")
                    if domain == "bayt.com":
                        results.append({
                            "title": title,
                            "link": link,
                            "desc": item.get("snippet", ""),
                            "location": "Lebanon",
                            "type": fields["type"],
                            "date": fields["date"],
                            "source": "Bayt"
                        })
                    else:
                        # Stricter Lebanon filter: only allow if location is exactly 'Lebanon' or 'Beirut' or similar, and exclude US states
                        location = fields["location"].lower()
                        if location == "lebanon" or location == "beirut" or location.endswith(", lebanon"):
                            results.append({
                                "title": title,
                                "link": link,
                                "desc": item.get("snippet", ""),
                                "location": fields["location"],
                                "type": fields["type"],
                                "date": fields["date"],
                                "source": "LinkedIn"
                            })
                    if len(results) >= num:
                        break
                
                if len(results) >= num:
                    break
                    
            except Exception as e:
                print(f"Error searching {domain} for {title}: {e}")
                break
    print(f"Found {len(results)} results for {domain}")
    return results

def search_linkedin_jobs(titles, num_results=5):
    return _search_jobs("linkedin.com/jobs", titles, num_results)

def search_bayt_jobs(titles, num_results=5):
    return _search_jobs("bayt.com", titles, num_results)
