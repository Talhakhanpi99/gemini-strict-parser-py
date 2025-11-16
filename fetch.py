import feedparser
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import List
from datetime import datetime, timedelta
from pathlib import Path
from newspaper import Article # pip install newspaper3k
import sys

# Cache file
CACHE_FILE = Path("cache.json")

def log_message(message):
    """Print log messages with timestamps"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    # Replace Unicode characters that might cause issues
    safe_message = message.replace('✅', '[SUCCESS]')
    print(f"[{timestamp}] {safe_message}")
    sys.stdout.flush()

def load_cache():
    log_message("Loading cache...")
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        log_message(f"Loaded {len(cache)} items from cache")
        return cache
    log_message("No cache found, starting fresh")
    return {}

def save_cache(cache):
    log_message(f"Saving {len(cache)} items to cache...")
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    log_message("Cache saved")

# RSS feeds list
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://bitcoinmagazine.com/feed",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://www.newsbtc.com/feed/",
    "https://www.ccn.com/feed/",
    "https://www.fxstreet.com/cryptocurrencies/rss",
    "https://www.theblock.co/rss",
]

# CryptoPanic API key - Using your actual key from the error message
CRYPTOPANIC_API_KEY = "34f5736b96c4c6aa74522bce23db1801ce9efa1f"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                 "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Source authority weighting
SOURCE_SCORES = {
    "cointelegraph.com": 4,
    "coindesk.com": 4,
    "theblock.co": 3,
    "bitcoinmagazine.com": 2,
    "newsbtc.com": 1,
    "ccn.com": 1,
    "fxstreet.com": 1,
    "cryptopanic.com": 5,
}

# High-value keywords (entities, SEO terms, evergreen)
HIGH_VALUE_KEYWORDS = [ "sec", "etf", "binance", "coinbase", "lawsuit", "regulation", "approval", "funding", "hack", "security breach", "partnership", "ipo", "launch", "court", "fraud", "ceo", "listing", "exchange", "blackrock", "wall street" ]

# Low-value / generic keywords
LOW_VALUE_KEYWORDS = [ "today", "update", "roundup", "prediction", "forecast", "top 10", "live price", "pump", "dump", "price today", "live update", "market roundup" ]

def clean_paragraph(text: str) -> bool:
    if not text or len(text) < 30:
        return False
    if re.match(r'^[\d\$\.\s,%–\-:]+$', text):
        return False
    if any(word in text.lower() for word in [
        "cookie", "advertisement", "subscribe", "sign up", "related:", "sponsored"
    ]):
        return False
    return True

def fetch_full_text(url: str) -> str:
    log_message(f"Fetching full text from: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        log_message(f"Error fetching article: {e}")
        return f"[Error fetching article: {e}]"

    soup = BeautifulSoup(r.text, "html.parser")
    domain = re.sub(r"^www\.", "", url.split("/")[2])

    container = None

    # ---- Site-specific rules ----
    if "coindesk.com" in domain:
        container = soup.find("div", class_=re.compile("at-text|article-text"))
    elif "cointelegraph.com" in domain:
        container = soup.find("div", class_=re.compile("post-content|article__content"))
    elif "newsbtc.com" in domain:
        # More specific selectors for newsbtc.com
        container = soup.find("div", class_="td-post-content")
        if not container:
            container = soup.find("div", class_=re.compile("td-post-content"))
        if not container:
            # Try to find by itemprop="articleBody" which is more reliable
            container = soup.find("div", itemprop="articleBody")
    elif "theblock.co" in domain:
        container = soup.find("div", class_=re.compile("article-body"))

    # ---- Extract paragraphs ----
    paragraphs = []
    if container:
        paragraphs = container.find_all("p")
    else:
        # If no container found, try common article content selectors
        selectors = [
            "article div", 
            "[itemprop='articleBody']",
            ".article-content",
            ".post-content",
            ".entry-content",
            ".content-inner"
        ]
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                paragraphs.extend(element.find_all("p"))
    
    clean_paras = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)
        if clean_paragraph(text):
            # Filter out author bios and related content
            if not is_author_content(text):
                clean_paras.append(text)

    # If we have paragraphs but they might include author content, try to filter
    if clean_paras and len(clean_paras) > 3:
        # Look for patterns that indicate the start/end of actual article
        article_text = filter_article_content(clean_paras)
        if article_text:
            log_message(f"Extracted {len(article_text)} characters after filtering")
            return article_text

    # ---- If site-specific failed, fallback to newspaper3k with filtering ----
    if not clean_paras or len(clean_paras) < 3:
        try:
            log_message("Using newspaper3k fallback...")
            art = Article(url)
            art.download()
            art.parse()
            result = art.text.strip() if art.text else "[No clean content found]"
            
            # Filter author content from newspaper3k result too
            filtered_result = filter_author_content(result)
            log_message(f"Fallback returned {len(filtered_result)} characters after filtering")
            return filtered_result
        except Exception as e:
            log_message(f"Error parsing fallback: {e}")
            return f"[Error parsing fallback: {e}]"

    result = "\n\n".join(clean_paras).strip() if clean_paras else "[No clean content found]"
    log_message(f"Extracted {len(result)} characters")
    return result

def is_author_content(text: str) -> bool:
    """Check if text appears to be author bio or related content"""
    author_indicators = [
        "my name is", "i was born", "i grew up", "my parents", 
        "my siblings", "i've always", "i am", "i'm from",
        "about the author", "author bio", "disclaimer",
        "contact me at", "follow me on", "my journey",
        "my experience", "i started", "years ago"
    ]
    
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in author_indicators)

def filter_author_content(text: str) -> str:
    """Filter out author bio content from article text"""
    lines = text.split('\n')
    filtered_lines = []
    in_author_section = False
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if this line starts author content
        if any(indicator in line_lower for indicator in [
            "my name is", "about the author", "author bio", "disclaimer"
        ]):
            in_author_section = True
            continue
            
        # Check if we're in author section and should continue skipping
        if in_author_section:
            if line.strip() and not line_lower.startswith(('related:', 'also read:', 'read more:')):
                continue
            else:
                in_author_section = False
                
        filtered_lines.append(line)
    
    return '\n'.join(filtered_lines).strip()

def filter_article_content(paragraphs: list) -> str:
    """Filter paragraphs to find the actual article content"""
    article_paragraphs = []
    in_article = False
    author_detected = False
    
    for i, para in enumerate(paragraphs):
        para_lower = para.lower()
        
        # Skip author bio sections
        if is_author_content(para):
            author_detected = True
            continue
            
        # Look for the start of actual article content
        if not in_article and not author_detected and i < len(paragraphs) - 2:
            # Check if this could be the beginning of an article
            if (len(para) > 100 and 
                not para_lower.startswith(('by ', 'published ', 'updated ', 'last modified')) and
                not 'disclaimer' in para_lower):
                in_article = True
                
        if in_article:
            article_paragraphs.append(para)
            
        # Check for end of article (disclaimers, author bios, etc.)
        if (in_article and 
            (para_lower.startswith('disclaimer') or 
             'about the author' in para_lower or
             'contact us' in para_lower)):
            break
            
    return "\n\n".join(article_paragraphs).strip()

def score_article(article: dict) -> int:
    score = 0
    title = (article.get("title") or "").lower()
    link = article.get("link") or ""
    body = (article.get("full_text") or "").lower()

    # Authority (source weight)
    for domain, weight in SOURCE_SCORES.items():
        if domain in link:
            score += weight

    # High-value keywords
    has_high_value = False
    for kw in HIGH_VALUE_KEYWORDS:
        if kw in title or kw in body:
            score += 4 # stronger bonus
            has_high_value = True

    # Low-value keywords (penalty)
    for kw in LOW_VALUE_KEYWORDS:
        if kw in title or kw in body:
            score -= 5 # stronger penalty

    # If no high-value keyword -> heavy penalty
    if not has_high_value:
        score -= 10

    # Recency (last 24 hours preferred)
    try:
        published_dt = datetime(*article["published_parsed"][:6])
        if published_dt > datetime.utcnow() - timedelta(hours=24):
            score += 2
    except Exception:
        pass

    # Title length (very short titles are usually weak)
    if len(title.split()) >= 6:
        score += 1

    # Body length (drop thin content)
    if len(body) < 200:
        score -= 10

    # Entity boost (major coins, institutions, regulators)
    ENTITY_KEYWORDS = ["bitcoin", "btc", "ethereum", "eth", "sec", "binance", "coinbase", "blackrock"]
    for kw in ENTITY_KEYWORDS:
        if kw in title or kw in body:
            score += 5

    log_message(f"Article '{title[:50]}...' scored: {score}")
    return score

def fetch_cryptopanic_news():
    log_message("Fetching CryptoPanic news...")
    # Using the correct API endpoint from your error message
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTOPANIC_API_KEY}&public=true"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 429:
            log_message("CryptoPanic API rate limit exceeded. Skipping...")
            return []
        resp.raise_for_status()
        data = resp.json()
        log_message(f"Retrieved {len(data.get('results', []))} items from CryptoPanic")
    except Exception as e:
        log_message(f"Error fetching CryptoPanic: {e}")
        return []

    articles = []
    for item in data.get("results", []):
        link = item.get("url")
        title = item.get("title")
        published = item.get("published_at")

        try:
            published_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            published_parsed = published_dt.timetuple()
        except Exception:
            published_parsed = None

        # ✅ Skip articles older than 24 hours
        if published_dt and published_dt < datetime.utcnow() - timedelta(hours=24):
            continue

        article = {
            "title": title,
            "link": link,
            "published": published,
            "published_parsed": published_parsed,
            "source": "cryptopanic",
            "full_text": fetch_full_text(link),
        }
        article["score"] = score_article(article)
        articles.append(article)

    return articles

def fetch_news():
    log_message("Starting news fetch process")
    all_articles = []
    cache = load_cache() # Load existing cache to prevent duplicates

    # RSS feeds
    log_message(f"Checking {len(RSS_FEEDS)} RSS feeds...")
    for feed in RSS_FEEDS: # Corrected this line
        log_message(f"Processing feed: {feed}")
        try:
            parsed = feedparser.parse(feed)
            log_message(f"Found {len(parsed.entries)} entries in feed")
            
            for entry in parsed.entries:
                link = entry.get("link")
                if link in cache: # Skip already seen articles
                    continue

                log_message(f"Processing entry: {entry.get('title', 'No title')[:50]}...")
                article = {
                    "title": entry.get("title"),
                    "link": link,
                    "published": entry.get("published"),
                    "published_parsed": entry.get("published_parsed"),
                    "source": feed,
                    "full_text": fetch_full_text(link),
                }
                article["score"] = score_article(article)
                all_articles.append(article)

                # Add to cache
                cache[link] = {"title": article["title"], "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            log_message(f"Error processing feed {feed}: {e}")
            # Correctly handle the case where a feed might be empty or malformed
            continue

    # CryptoPanic
    log_message("Fetching CryptoPanic articles...")
    cryptopanic_articles = fetch_cryptopanic_news()
    for article in cryptopanic_articles:
        if article["link"] not in cache:
            all_articles.append(article)
            cache[article["link"]] = {"title": article["title"], "timestamp": datetime.utcnow().isoformat()}

    # Remove duplicates (same title or link) just in case
    seen = set()
    unique_articles = []
    for a in all_articles:
        key = (a["title"], a["link"])
        if key not in seen:
            seen.add(key)
            unique_articles.append(a)

    # Sort by score and recency
    unique_articles.sort(key=lambda x: (x["score"], x.get("published_parsed", ())), reverse=True)

    # Drop weak ones (score < 5)
    filtered_articles = [a for a in unique_articles if a["score"] >= 5]
    log_message(f"Filtered from {len(unique_articles)} to {len(filtered_articles)} articles (score >= 5)")

    # Keep top 10 strong articles
    final_articles = filtered_articles[:10]
    log_message(f"Keeping top {len(final_articles)} articles")
    
    # Save cache after processing all feeds, even if an error occurred
    save_cache(cache) 
    return final_articles

if __name__ == "__main__":
    log_message("Starting news fetch script")
    try:
        articles = fetch_news()
        with open("news.json", "w", encoding="utf-8") as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)

        log_message(f"Saved {len(articles)} high-quality, SEO-worthy articles to news.json [SUCCESS]")
    except Exception as e:
        log_message(f"Error in main execution: {e}")
        sys.exit(1)
