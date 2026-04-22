# analyzer.py
from google import genai
import json
import time

# SETUP GEMINI
from config import GEMINI_API_KEY
client = genai.Client(api_key=GEMINI_API_KEY)

# ANALYZE A SINGLE ITEM

def analyze_item(item, profile):
    
    prompt = f"""
You are a business intelligence advisor for the following business:

Business Name: {profile['name']}
Industry: {profile['industry']}
Business Type: {profile['business_type']}
Location: {profile['location']}
Sectors: {', '.join(profile['sectors'])}

Analyze this news/regulation item for this specific business:
Title: {item['title']}
Source: {item['source']}

Return ONLY a JSON object with exactly these fields, no extra text, no markdown, no backticks:
{{
    "relevant": true,
    "relevance_score": 7,
    "summary": "2 sentence plain English summary",
    "impact": "opportunity",
    "impact_reason": "one sentence explaining why",
    "action_required": false,
    "action_steps": "none",
    "priority": "MEDIUM"
}}
"""

    try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                break
            except Exception as retry_error:
                if attempt < 2:
                    time.sleep(5)
                else:
                    raise retry_error

        response_text = response.text.strip()

        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]

        analysis = json.loads(response_text.strip())

        # Normalize impact values
        if analysis.get("impact", "").lower() in ["none", ""]:
            analysis["impact"] = "neutral"

        analysis["title"] = item["title"]
        analysis["link"] = item.get("link", "")
        analysis["published"] = item.get("published", "")
        analysis["source"] = item["source"]
        analysis["topic"] = item["topic"]

        return analysis

    except Exception as e:
        print(f"Analysis error: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'no response'}")
        return {
            "relevant": False,
            "relevance_score": 0,
            "summary": "Could not analyze this item.",
            "impact": "neutral",
            "impact_reason": "Analysis failed.",
            "action_required": False,
            "action_steps": "none",
            "priority": "LOW",
            "title": item["title"],
            "link": item.get("link", ""),
            "published": item.get("published", ""),
            "source": item["source"],
            "topic": item["topic"]
        }


# ANALYZE A BATCH

def analyze_batch(items, profile):
    analyzed = []

    for i, item in enumerate(items):
        result = analyze_item(item, profile)
        if result["relevant"] or result["relevance_score"] >= 3:
            analyzed.append(result)

        if i >= 7:
            break
        time.sleep(1)

    analyzed.sort(key=lambda x: x["relevance_score"], reverse=True)
    return analyzed


#ANSWER A BUSINESS QUESTION

def answer_question(question, profile, recent_news=[], recent_regulations=[]):

    news_context = ""
    if recent_news:
        news_context = "Recent relevant news:\n"
        for item in recent_news[:5]:
            news_context += f"- {item['title']}\n"

    regulations_context = ""
    if recent_regulations:
        regulations_context = "Recent regulations:\n"
        for item in recent_regulations[:5]:
            regulations_context += f"- {item['title']}\n"

    prompt = f"""
You are BizRadar, a smart business advisor for the following business:

Business Name: {profile['name']}
Industry: {profile['industry']}
Business Type: {profile['business_type']}
Location: {profile['location']}
Sectors: {', '.join(profile['sectors'])}

{news_context}
{regulations_context}

The business owner is asking:
{question}

Give a helpful, specific, practical answer tailored to this exact business.
Be direct and actionable. Write in plain English.
Keep your answer under 300 words.
"""

    try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=prompt
                )
                break
            except Exception as retry_error:
                if attempt < 2:
                    time.sleep(5)
                else:
                    raise retry_error

        return response.text

    except Exception as e:
        print(f"Q&A error: {e}")
        return "Sorry, I could not process your question right now. Please try again."