# Selenium Flask

Deploy an independent Flask scraper on Railway with Selenium running as a separate browser service.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/selenium-flask?referralCode=asepsp&utm_medium=integration&utm_source=template&utm_campaign=generic)

## Architecture

This template is designed for 2 Railway services in the same project:

| Service | Source | Purpose |
| ------- | ------ | ------- |
| `api` | This repository | Independent Flask app and scraper routes |
| `selenium` | `selenium/standalone-chrome` | Independent Remote Chrome browser service |

The Flask service connects to Chrome through Remote WebDriver:

```python
driver = webdriver.Remote(
    command_executor=SELENIUM_URL,
    options=options,
)
```

## Railway Setup

1. Deploy this repository as the Flask service.
2. Add another service from Docker image:

   ```text
   selenium/standalone-chrome
   ```

3. Name the browser service `selenium`.
4. Set the Flask service variables from `.env.example`.

The required Selenium connection value is:

```text
SELENIUM_URL=http://selenium.railway.internal:4444/wd/hub
```

Railway private networking lets services in the same project communicate with
`SERVICE_NAME.railway.internal`, so the Selenium service does not need to be
publicly exposed.

## Environment Variables

Copy `.env.example` to `.env` for local development. On Railway, add the same
values in the Flask service Variables tab.

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `PORT` | `8000` | HTTP port used by Gunicorn |
| `SELENIUM_URL` | `http://selenium.railway.internal:4444/wd/hub` | Selenium Remote WebDriver URL |
| `SCRAPE_URL` | `https://www.scrapethissite.com/` | URL loaded by the example scraper |
| `GUNICORN_HOST` | `0.0.0.0` | Host used when `GUNICORN_BIND` is empty |
| `GUNICORN_BIND` | empty | Optional full bind override, for example `0.0.0.0:8000` |
| `GUNICORN_WORKERS` | `2` | Number of Gunicorn workers |
| `GUNICORN_WORKER_CLASS` | `sync` | Gunicorn worker class for Flask |
| `GUNICORN_TIMEOUT` | `120` | Worker timeout in seconds |
| `GUNICORN_KEEPALIVE` | `5` | Keep-alive timeout in seconds |
| `GUNICORN_LOG_LEVEL` | `info` | Gunicorn log level |
| `GUNICORN_ACCESS_LOG` | `-` | Access log target |
| `GUNICORN_ERROR_LOG` | `-` | Error log target |

## Endpoints

| Route | Description |
| ----- | ----------- |
| `/` | Basic status check |
| `/scrape` | Example scraper using the remote Selenium Chrome service |

## Local Development

Create a local env file:

```bash
cp .env.example .env
```

Run the Flask service independently:

```bash
pip install -r requirements.txt
gunicorn -c settings.py main:app
```

The Selenium browser must be reachable at `SELENIUM_URL`. For Railway, use the
private service URL. For another local or external Selenium service, update
`SELENIUM_URL` in `.env`.

Then open:

```text
http://localhost:8000/scrape
```

## File Structure

```text
.
├── .env.example
├── Dockerfile
├── settings.py
├── main.py
└── requirements.txt
```

## Notes

* The Flask image does not install Chromium or Chromedriver.
* Browser automation runs inside `selenium/standalone-chrome`.
* Gunicorn serves the Flask app through `main:app`.
* Add request throttling, queues, or worker separation if scrape workloads become heavy.
