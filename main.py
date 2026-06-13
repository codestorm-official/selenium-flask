import logging
import os
import time

from dotenv import load_dotenv
from flask import Flask, jsonify
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


load_dotenv()

SELENIUM_URL = os.getenv(
    "SELENIUM_URL",
    "http://selenium.railway.internal:4444/wd/hub",
)
SCRAPE_URL = os.getenv("SCRAPE_URL", "https://www.scrapethissite.com/")

app = Flask(__name__)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


def init_driver() -> webdriver.Remote:
    options = webdriver.ChromeOptions()
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 "
        "Safari/537.36"
    )
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--blink-settings=imagesEnabled=false")

    return webdriver.Remote(
        command_executor=SELENIUM_URL,
        options=options,
    )


@app.get("/")
def home():
    return jsonify(
        {
            "status": "selenium-flask ready",
            "selenium_url": SELENIUM_URL,
            "test_endpoint": "GET /scrape",
        }
    )


@app.get("/scrape")
def scrape():
    driver = None
    started_at = time.monotonic()

    logger.info("Starting scrape url=%s selenium_url=%s", SCRAPE_URL, SELENIUM_URL)

    try:
        driver = init_driver()
        driver.get(SCRAPE_URL)
        title = driver.title
        duration = time.monotonic() - started_at

        logger.info(
            "Finished scrape url=%s title=%r duration=%.2fs",
            SCRAPE_URL,
            title,
            duration,
        )

        return jsonify(
            {
                "url": SCRAPE_URL,
                "title": title,
            }
        )
    except WebDriverException as exc:
        duration = time.monotonic() - started_at
        logger.exception(
            "Failed scrape url=%s duration=%.2fs error=%s",
            SCRAPE_URL,
            duration,
            exc.msg,
        )

        return (
            jsonify(
                {
                    "error": "Could not connect to Selenium Remote WebDriver",
                    "detail": exc.msg,
                }
            ),
            502,
        )
    finally:
        if driver is not None:
            driver.quit()
