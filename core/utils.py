from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from os import system as terminal, name as os_name

from .decorators import safe


def clear():
    terminal('cls' if os_name.lower() == "nt" else 'clear')


def get_browser(url: str):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    base_dir = Path(__file__).parent.parent
    chromedriver_path = str(base_dir / 'chromedriver.exe')

    from time import sleep

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')

    browser = webdriver.Chrome(service=Service(executable_path=chromedriver_path), options=options)
    browser.get(url)

    sleep(1)
    return browser


def click(element: webdriver, browser: webdriver):
    browser.execute_script("arguments[0].click()", element)


@safe(None)
def querySelector(selector: str, browser: webdriver):
    return browser.find_element(By.CSS_SELECTOR, selector)


@safe(except_value=[])
def querySelectorAll(selector: str, browser: webdriver):
    return browser.find_elements(By.CSS_SELECTOR, selector)


@safe(None)
def removeElement(element: webdriver, browser: webdriver):
    browser.execute_script("arguments[0].remove()", element)
