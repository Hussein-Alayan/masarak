import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
BASE_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent"


def analyze_cv(cv_text: str) -> dict:
    if not GEMINI_KEY:
        return {
            "error": "GEMINI_API_KEY is missing. Please check your .env file.",
            "error_type": "config"
        }

    url = f"{BASE_URL}?key={GEMINI_KEY}"
    prompt = (
        "You are a career advisor. From this CV, do the following:\n"
        "1. Suggest 3-5 realistic job titles for the user (as a JSON list).\n"
        "2. Give exactly 8 main career advice points. Each point should start with a relevant emoji "
        "(like 🎯 for goals, 💡 for insights, 📚 for learning, 🚀 for growth, or 💼 for career). "
        "Format each point as a single line starting with the emoji followed by the advice.\n\n"
        + cv_text
    )
    
    try:
        resp = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        return {
            "error": "Could not connect to the AI service. Please check your internet connection and try again.",
            "error_type": "connection",
            "details": str(e)
        }
    except requests.exceptions.Timeout:
        return {
            "error": "The AI service took too long to respond. Please try again.",
            "error_type": "timeout"
        }
    except requests.exceptions.RequestException as e:
        return {
            "error": f"Error communicating with the AI service: {str(e)}",
            "error_type": "request"
        }
    except Exception as e:
        return {
            "error": f"An unexpected error occurred: {str(e)}",
            "error_type": "unknown"
        }

    try:
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return {
            "error": "Received invalid response from AI service. Please try again.",
            "error_type": "response",
            "details": str(e)
        }

    # Try parse job titles (JSON array)
    job_titles = []
    try:
        start = text.index('[')
        end = text.index(']', start) + 1
        job_titles = json.loads(text[start:end])
    except Exception:
        # Fallback: pick lines with keywords
        lines = text.splitlines()
        job_titles = [
            ln.strip('-*• ')
            for ln in lines
            if any(w in ln.lower() for w in ["engineer","developer","analyst","manager","designer"])
        ]

    # Extract advice points (lines containing emojis)
    advice_bullets = []
    for line in text.splitlines():
        line = line.strip()
        # Check if line starts with an emoji or contains an emoji followed by text
        if any(emoji in line[:2] for emoji in ["🎯", "💡", "📚", "🚀", "🎓", "💼", "🌟", "📈", "🎨", "🔍", "🧭", "🗨", "🎮", "🌐", "📱"]):
            # Remove any leading dashes or asterisks
            line = line.lstrip('-*• ')
            advice_bullets.append(line)

    # If no advice was found, try to extract any numbered points
    if not advice_bullets:
        for line in text.splitlines():
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')):
                # Add a default emoji if none is present
                if not any(emoji in line for emoji in ["🎯", "💡", "📚", "🚀", "🎓", "💼", "🌟", "📈", "🎨", "🔍", "🧭", "🗨", "🎮", "🌐", "📱"]):
                    line = "💡 " + line
                advice_bullets.append(line)

    # Ensure we have exactly 8 points, pad with default if needed
    default_advice = [
        "🎯 Set clear career goals and milestones",
        "💡 Focus on building relevant technical skills",
        "📚 Consider additional certifications or training",
        "🚀 Look for growth opportunities in your current role",
        "💼 Network and build professional connections",
        "🎮 Build a portfolio of personal projects",
        "🌐 Stay updated with industry trends and technologies",
        "📱 Develop both technical and soft skills"
    ]
    
    while len(advice_bullets) < 8:
        advice_bullets.append(default_advice[len(advice_bullets)])

    return {
        "job_titles": job_titles,
        "advice_bullets": advice_bullets[:8],  # Limit to 8 points
        "titles_markdown": "\n".join(f"- {t}" for t in job_titles) or "- No titles found.",
        "advice_markdown": "\n".join(f"- {a}" for a in advice_bullets[:8]) or "- No advice found."
    }

def match_jobs_with_ai(cv_text, selected_title, jobs, top_n=3):
    """
    Use Gemini to select and explain the top N jobs for the user.
    Returns a markdown-formatted string with the AI's recommendations.
    """
    if not GEMINI_KEY:
        return {"error": "GEMINI_API_KEY missing in .env"}

    # Build job list string for the prompt
    job_list_str = ""
    for i, job in enumerate(jobs, 1):
        job_list_str += (
            f"{i}. Title: {job.get('title', '-')[:60]}\n"
            f"   Description: {job.get('desc', '-')[:200]}\n"
            f"   Location: {job.get('location', '-')}\n"
            f"   Type: {job.get('type', '-')}\n"
            f"   Source: {job.get('source', '-')}\n"
        )

    prompt = (
        f"Here is a user's CV:\n{cv_text}\n\n"
        f"The user is interested in: {selected_title}\n\n"
        f"Here are some job postings:\n{job_list_str}\n\n"
        f"Please select the top {top_n} jobs that best match the user's profile and interest. "
        f"For each, explain why it is a good fit. Organize the results clearly as markdown."
    )

    url = f"{BASE_URL}?key={GEMINI_KEY}"
    try:
        resp = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]})
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        return {"ai_job_matches": text}
    except Exception as e:
        return {"error": f"AI job matching failed: {e}"}
