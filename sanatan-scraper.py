import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urlparse


def title_from_wikipedia_url(url):
    path = urlparse(url).path
    if "/wiki/" not in path:
        return None
    slug = path.split("/wiki/", 1)[1].strip("/")
    if not slug:
        return None
    return unquote(slug).replace("_", " ")


def fetch_article_text_via_api(title, headers):
    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": 2,
        "prop": "extracts",
        "explaintext": 1,
        "titles": title,
    }
    response = requests.get(api_url, params=params, headers=headers, timeout=20)
    if response.status_code != 200:
        return None

    data = response.json()
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None

    page = pages[0]
    extract = page.get("extract", "").strip()
    if not extract:
        return None
    return page.get("title", title), extract

def scrape_wikipedia_deity(url):
    # 1. Send a request to the website
    print(f"Fetching data from: {url}")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    # Prefer the official API (stable output) before HTML scraping.
    page_title = title_from_wikipedia_url(url)
    if page_title:
        try:
            api_result = fetch_article_text_via_api(page_title, headers)
            if api_result:
                title, article_text = api_result
                print(f"\n--- Scraping Data for: {title} ---\n")
                return article_text
        except requests.RequestException:
            pass

    # Fallback: parse raw HTML if API is unavailable.
    try:
        response = requests.get(url, headers=headers, timeout=20)
    except requests.RequestException as exc:
        print(f"Network error while retrieving the page: {exc}")
        return None

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        if response.status_code == 403:
            print("Try again after a short wait or use the Wikipedia API endpoint instead.")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    heading = soup.find("h1", id="firstHeading")
    title = heading.get_text(strip=True) if heading else (page_title or "Unknown")
    print(f"\n--- Scraping Data for: {title} ---\n")

    selectors = [
        "#mw-content-text .mw-parser-output > p",
        "#mw-content-text p",
        "main p",
    ]
    extracted_parts = []
    for selector in selectors:
        paragraphs = soup.select(selector)
        for p in paragraphs:
            text = p.get_text(" ", strip=True)
            if len(text) >= 40:
                extracted_parts.append(text)
        if extracted_parts:
            break

    if not extracted_parts:
        print("No article paragraphs were extracted.")
        return None

    return "\n\n".join(extracted_parts)

# Let's test it with the Wikipedia page for Vishnu
target_url = "https://en.wikipedia.org/wiki/Vishnu"
raw_mythology_data = scrape_wikipedia_deity(target_url)

if raw_mythology_data:
    # Print just the first 1500 characters so we don't flood your screen
    print(raw_mythology_data[:1500])
    print("\n... [Data Truncated for Display] ...")
    
    # In a real app, you would save this to a file (.txt or .json)
    # with open(f"vishnu_data.txt", "w", encoding="utf-8") as file:
    #     file.write(raw_mythology_data)
