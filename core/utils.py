from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from os import system as terminal, name as os_name

from .decorators import safe


def clear():
    terminal('cls' if os_name.lower() == "nt" else 'clear')


def get_browser(url: str):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    from time import sleep

    chromedriver_path = 'chromedriver.exe'
    chromedriver_path = Path(__file__).parent.parent / chromedriver_path
    window_size = "1920,1080"

    options = Options()
    options.add_argument("--window-size=%s" % window_size)
    options.add_argument('--headless')

    browser = webdriver.Chrome(executable_path=chromedriver_path, options=options)
    browser.get(url)

    sleep(1)
    return browser


@safe(None)
def querySelector(selector: str, browser: webdriver):
    return browser.find_element(By.CSS_SELECTOR, selector)


@safe(except_value=[])
def querySelectorAll(selector: str, browser: webdriver):
    return browser.find_elements(By.CSS_SELECTOR, selector)


@safe(None)
def removeElement(element: webdriver, browser: webdriver):
    browser.execute_script("arguments[0].remove()", element)
