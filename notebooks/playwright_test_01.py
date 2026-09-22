from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)   # headless=False면 창이 보임
    page = browser.new_page()

    page.goto("https://www.python.org")

    time.sleep(3)

    print(page.title())

    browser.close()