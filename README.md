# 🌍 US Travel Advisory Prometheus Exporter

A lightweight Python exporter that fetches official **US Department of State Travel Advisory** levels (1 to 4) via RSS (`TAsTWs.xml`) and exposes them as Prometheus metrics with country tags.

## 🚀 Features
- **Prometheus Metric:** Exposes `advisory_level{country="<country_name>"}` (Gauge 1.0 - 4.0).
- **Configurable:** Monitor multiple comma-separated countries via the `COUNTRIES` environment variable.
- **Kubernetes Ready:** Includes Dockerfile, Helm Chart, ServiceMonitor, and ArgoCD Application manifest.
- **Reliable Scraping:** Uses official RSS feed fetching via `requests` and `feedparser`.

## 🛠️ Quick Start

```bash
docker run -d \
  -p 8000:8000 \
  -e COUNTRIES="poland,germany,france,ukraine" \
  -e SCRAPE_INTERVAL=3600 \
  dawidch/travel-advisory-exporter:latest
