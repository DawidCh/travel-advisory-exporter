import os
import re
import time
import requests
import feedparser
from prometheus_client import start_http_server, Gauge

# Definicja metryki Prometheusa
ADVISORY_LEVEL = Gauge(
    'advisory_level', 
    'US Travel Advisory Level for specified countries (1 to 4)', 
    ['country']
)

RSS_URL = "https://travel.state.gov/_res/rss/TAsTWs.xml"

def fetch_and_update_advisories(country_regex):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
    }

    try:
        response = requests.get(RSS_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Błąd pobierania RSS: Status HTTP {response.status_code}")
            return

        feed = feedparser.parse(response.content)
        
        if not feed.entries:
            print("Brak wpisów w parsowanym kanale RSS.")
            return

        matched_count = 0
        for entry in feed.entries:
            title = entry.get('title', '')
            
            # Dopasowujemy np.: "Poland Travel Advisory - Level 1: ..." lub "Poland - Level 1: ..."
            match = re.search(r'^(.*?)(?:\s+Travel\s+Advisory)?\s*-\s*Level\s*([1-4])', title, re.IGNORECASE)
            if match:
                country_name = match.group(1).strip()
                level = float(match.group(2))

                # Sprawdzamy, czy nazwa kraju pasuje do przekazanego wzorca regex
                if country_regex.search(country_name):
                    ADVISORY_LEVEL.labels(country=country_name.lower()).set(level)
                    print(f"Uaktualniono: {country_name} -> Level {int(level)}")
                    matched_count += 1

        if matched_count == 0:
            print(f"Ostrzeżenie: Żaden kraj z kanalu RSS nie pasował do podanego regexa.")

    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania RSS: {e}")

def main():
    # Zmienna środowiskowa z wzorcem regex (domyślnie pasuje do wszystkiego)
    pattern_str = os.getenv('COUNTRY_PATTERN', '.*')
    
    try:
        country_regex = re.compile(pattern_str, re.IGNORECASE)
    except re.error as e:
        print(f"Błąd w składni regexa '{pattern_str}': {e}")
        return

    port = int(os.getenv('PORT', '8000'))
    scrape_interval = int(os.getenv('SCRAPE_INTERVAL', '3600'))

    start_http_server(port)
    print(f"Serwer metryk wystawiony na porcie {port}")
    print(f"Użyty wzorzec Regex dla krajów: '{pattern_str}'")

    while True:
        fetch_and_update_advisories(country_regex)
        time.sleep(scrape_interval)

if __name__ == '__main__':
    main()
