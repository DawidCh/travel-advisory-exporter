# 🌍 US Travel Advisory Prometheus Exporter

A lightweight Python exporter that fetches official **US Department of State Travel Advisory** levels (1 to 4) via RSS (`TAsTWs.xml`) and exposes them as Prometheus metrics with country tags.

## 🚀 Features
- **Prometheus Metric:** Exposes `advisory_level{country="<country_name>"}` (Gauge 1.0 - 4.0).
- **Regex Filtering:** Flexible country matching using regular expressions via the `COUNTRY_PATTERN` environment variable.
- **Kubernetes Ready:** Includes Dockerfile, Helm Chart, ServiceMonitor, and ArgoCD Application manifest.
- **Reliable Scraping:** Uses official RSS feed fetching via `requests` and `feedparser`.

## ⚙️ Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `COUNTRY_PATTERN` | Regex pattern to match target countries (e.g., `poland\|germany`, `^uk.*`, or `.*` for all). | `.*` |
| `SCRAPE_INTERVAL` | Interval in seconds between RSS feed fetches. | `3600` |
| `PORT` | HTTP port on which Prometheus metrics are exposed. | `8000` |

## 🛠️ Quick Start

```bash
docker run -d \
  -p 8000:8000 \
  -e COUNTRY_PATTERN="poland|germany|france|ukraine" \
  -e SCRAPE_INTERVAL=3600 \
  dawidch/travel-advisory-exporter:latest