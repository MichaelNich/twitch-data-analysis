import time
import datetime
import json
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database_manager import DatabaseManager


class WebScrapping:
    def __init__(self):
        # selenium configs
        with open("config.json") as config_file:
            config = json.load(config_file)
        self.chrome_driver_path = config["chrome_driver_path"]
        self.user_data_dir = config["user_data_dir"]
        self.headless = config["headless"]
        self.backup_folder = config["backup_folder"]
        self.log_level = config["log_level"]

        service = Service(self.chrome_driver_path)
        chrome_options = Options()
        chrome_options.add_argument(self.log_level)
        chrome_options.add_argument("--headless" if self.headless else "")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")
        # initialize Driver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def scroll_page(self):
        body_element = self.driver.find_element(By.TAG_NAME, "body")
        body_element.click()
        body_element.send_keys(Keys.END)
        # Scroll down five times
        for _ in range(5):
            body_element.send_keys(Keys.END)
            time.sleep(1)

    def access_games_url(self, url):
        # Open the Twitch directory page with viewer count descending
        self.driver.get(url)
        # Wait 5 seconds for the page to load
        time.sleep(5)
        # scroll page to load more content
        self.scroll_page()
        # Extract the HTML content after scrolling
        html = self.driver.page_source
        return self.get_games_data(html)

    def get_games_data(self, html):
        # DATA CLEANING
        soup = BeautifulSoup(html, "html.parser")
        views = []
        names = []

        categories = []
        for div in soup.find_all("div", class_="Layout-sc-1xcs6mc-0 BcKcx"):
            tags = []
            for button in div.find_all(
                "button", class_="ScTag-sc-14s7ciu-0 bOVWlO tw-tag"
            ):
                span = button.find("span")
                if span is not None:
                    tags.append(span.text)
            categories.append(tags)

        games = {}

        date = datetime.datetime.now()
        date = date.strftime("%d/%m/%Y %H:%M")

        # Iterate over the divs and extract the text
        for view in soup.find_all("p", class_="CoreText-sc-1txzju1-0 jiepBC"):
            t = view.text.replace("\xa0", " ")
            t = t.replace(",", ".")
            views.append(t)

        for name in soup.find_all("h2", class_="CoreText-sc-1txzju1-0 eYbmNi"):
            n = name.text.replace("'", "")
            names.append(n)

        for name, view, category in zip(names, views, categories):
            games[name] = {"views": view, "category": category, "date": date}
        # Return twitch dictionary
        return games

    def access_streamers_url(self, language):
        self.driver.get("https://www.twitch.tv/directory/all")
        self.driver.execute_cdp_cmd(
            "Storage.clearDataForOrigin",
            {
                "origin": "*",
                "storageTypes": "all",
            },
        )
        # self.driver.delete_all_cookies()
        self.driver.refresh()
        # Wait for the language dropdown button to be visible
        wait = WebDriverWait(self.driver, 10)
        language_dropdown_button = wait.until(
            EC.visibility_of_element_located(
                (
                    By.XPATH,
                    '//button[contains(@class, "ScCoreButton-sc-ocjdkq-0") and contains(@class, "tw-select-button")]',
                )
            )
        )

        # Click the language dropdown button
        language_dropdown_button.click()
        time.sleep(1)
        checkbox = self.driver.find_element(
            By.XPATH,
            f'//label[contains(.,"{language}")]/preceding-sibling::input[@data-a-target="tw-checkbox"]',
        )

        self.driver.execute_script("arguments[0].scrollIntoView();", checkbox)
        # Click the checkbox using JavaScript
        self.driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(1)
        language_dropdown_button.click()
        # wait 5 seconds for page to load
        time.sleep(5)
        # scroll page to load more content
        self.scroll_page()
        html = self.driver.page_source
        return self.get_streamers_data(html, language)

    def get_streamers_data(self, html, language):
        soup = BeautifulSoup(html, "html.parser")
        views = []
        names = []
        date = datetime.datetime.now()
        date = date.strftime("%d/%m/%Y %H:%M")
        aux = 0

        categories = []
        for div in soup.find_all(
            "div", class_="ScMediaCardStatWrapper-sc-anph5i-0 eBmJxH tw-media-card-stat"
        ):
            views.append(div.text)

        for p in soup.find_all("p", class_="CoreText-sc-1txzju1-0 jiepBC"):
            if aux % 2 == 0:
                n = p.text.replace("'", "")
                names.append(n)
            else:
                c = p.text.replace("'", "")
                categories.append(c)
            aux += 1

        streamers = {}
        for name, view, category in zip(names, views, categories):
            streamers[name] = {
                "views": view,
                "category": category,
                "date": date,
                "lang": language,
            }
        return streamers

    def close(self):
        self.driver.quit()


languages = [
    "Português",
    "English",
    "Español",
    "Français",
    "Italiano",
    "한국어",
    "日本語",
    "中文",
    "Polski",
    "Deutsch",
    "Türkçe",
    "Русский",
    "Українська",
]


def main():
    # set selenium logging to print out only WARNING+
    selenium_logger = logging.getLogger("selenium")
    selenium_logger.setLevel(logging.WARNING)
    # initialize the script
    driver = WebScrapping()
    db_manager = DatabaseManager()
    db_manager.connect_to_db()
    games = driver.access_games_url("https://www.twitch.tv/directory?sort=VIEWER_COUNT")
    db_manager.save_to_db(games)
    for language in languages:
        streamers = driver.access_streamers_url(language)
        db_manager.insert_streamers_to_db(streamers)
    driver.close()
    db_manager.insert_backup_files()
    db_manager.close_connection()


if __name__ == "__main__":
    target_date_string = "31/07/2023 00:00"
    target_date = datetime.datetime.strptime(target_date_string, "%d/%m/%Y %H:%M")
    current_date = datetime.datetime.now()
    while current_date < target_date:
        # runs the script every 15 minutes so it does not get request limited!
        try:
            main()
        except Exception as e:
            print("Web Scrapping found an error, ", e)
        time.sleep(600)
        current_date = datetime.datetime.now()
    # main()
