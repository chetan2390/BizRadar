# fetcher.py
import feedparser
import requests

feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

#HELPER

def safe_parse(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
        return feed.entries
    except Exception as e:
        print(f"Feed error for {url}: {e}")
        return []


#FETCH INDUSTRY NEWS

def fetch_news(profile):
    news_items = []

    for interest in profile["interests"]:
        query = interest.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}+India&hl=en-IN&gl=IN&ceid=IN:en"
        entries = safe_parse(url)

        for entry in entries[:3]:
            news_items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "Recent"),
                "source": "Google News",
                "topic": interest
            })

    return news_items


#FETCH REGULATIONS

def fetch_regulations(profile):
    regulation_items = []

    # Official RSS feeds
    govt_feeds = [
        {"url": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3", "source": "PIB - Ministry of Finance"},
        {"url": "https://pib.gov.in/RssMain.aspx?ModId=7&Lang=1&Regid=3", "source": "PIB - Ministry of Commerce"},
        {"url": "https://pib.gov.in/RssMain.aspx?ModId=28&Lang=1&Regid=3", "source": "PIB - Ministry of MSME"},
        {"url": "https://www.sebi.gov.in/sebi_data/rss/sebirss.xml", "source": "SEBI"},
        {"url": "https://www.rbi.org.in/Scripts/rss.aspx", "source": "RBI"}
    ]

    for feed_info in govt_feeds:
        entries = safe_parse(feed_info["url"])
        for entry in entries[:3]:
            regulation_items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "Recent"),
                "source": feed_info["source"],
                "topic": "Government Regulation"
            })

    # Google News regulatory topics — built from user's profile
    regulation_topics = [
        f"{profile['industry']} regulation India",
        f"{profile['business_type']} policy India",
        "GST notification India",
        "RBI circular India",
        f"{profile['location']} business policy"
    ]

    for topic in regulation_topics:
        query = topic.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        entries = safe_parse(url)

        for entry in entries[:2]:
            regulation_items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "Recent"),
                "source": "Google News - Regulatory",
                "topic": "Government Regulation"
            })

    return regulation_items


# FETCH SCHEMES

def fetch_schemes(profile):
    scheme_items = []

    # Official schemes feed
    url = "https://pib.gov.in/RssMain.aspx?ModId=28&Lang=1&Regid=3"
    entries = safe_parse(url)

    for entry in entries[:5]:
        scheme_items.append({
            "title": entry.get("title", "No title"),
            "link": entry.get("link", ""),
            "published": entry.get("published", "Recent"),
            "source": "PIB - Government of India",
            "topic": "Government Scheme"
        })

    # Google News schemes - personalised to user profile
    scheme_topics = [
        f"{profile['business_type']} scheme India government",
        f"{profile['industry']} subsidy India",
        "MSME government scheme India"
    ]

    for topic in scheme_topics:
        query = topic.replace(" ", "+")
        url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
        entries = safe_parse(url)

        for entry in entries[:2]:
            scheme_items.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "Recent"),
                "source": "Google News - Schemes",
                "topic": "Government Scheme"
            })

    return scheme_items