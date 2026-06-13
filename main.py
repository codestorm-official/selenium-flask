import os

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
        }
    )


@app.get("/scrape")
def scrape():
    driver = None

    try:
        driver = init_driver()
        driver.get(SCRAPE_URL)

        return jsonify(
            {
                "url": SCRAPE_URL,
                "title": driver.title,
            }
        )
    except WebDriverException as exc:
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
