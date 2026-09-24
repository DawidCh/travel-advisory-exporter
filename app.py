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

def fetch_and_update_advisories(target_countries):
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

        # Budujemy słownik { 'poland': 1.0, 'germany': 1.0, ... }
        advisories = {}
        for entry in feed.entries:
            title = entry.get('title', '')
            
            # Dopasowujemy: "Poland Travel Advisory - Level 1: ..." lub "Poland - Level 1: ..."
            match = re.search(r'^(.*?)(?:\s+Travel\s+Advisory)?\s*-\s*Level\s*([1-4])', title, re.IGNORECASE)
            if match:
                country_name = match.group(1).strip().lower()
                level = float(match.group(2))
                advisories[country_name] = level

        # Aktualizujemy metryki Prometheusa dla wskazanych w zmiennej środowiskowej krajów
        for country in target_countries:
            clean_country = country.lower().strip()
            if clean_country in advisories:
                level = advisories[clean_country]
                ADVISORY_LEVEL.labels(country=clean_country).set(level)
                print(f"Uaktualniono: {clean_country} -> Level {int(level)}")
            else:
                print(f"Ostrzeżenie: Nie znaleziono wpisu w RSS dla kraju '{clean_country}'")

    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania RSS: {e}")

def main():
    raw_countries = os.getenv('COUNTRIES', 'poland')
    countries = [c.strip().lower() for c in raw_countries.split(',') if c.strip()]
    
    port = int(os.getenv('PORT', '8000'))
    scrape_interval = int(os.getenv('SCRAPE_INTERVAL', '3600'))

    start_http_server(port)
    print(f"Serwer metryk wystawiony na porcie {port}")
    print(f"Monitorowane kraje: {countries}")

    while True:
        fetch_and_update_advisories(countries)
        time.sleep(scrape_interval)

if __name__ == '__main__':
    main()
