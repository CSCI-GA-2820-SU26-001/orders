"""
BDD Environment for Selenium testing of the Orders Admin UI

Starts a headless Chrome browser before all scenarios and shuts it down
afterwards. The service under test is reached through BASE_URL so the same
suite can run against a local server or a deployed route.
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

WAIT_SECONDS = int(os.getenv("WAIT_SECONDS", "15"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

# Message areas on the Admin UI, printed on a failed step to aid debugging
MESSAGE_IDS = [
    "orders-message",
    "update-order-message",
    "read-order-message",
    "read-item-message",
    "add-item-message",
    "update-item-message",
    "delete-item-message",
    "items-message",
]


def before_all(context):
    """Start the browser before any scenarios run"""
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    context.driver = webdriver.Chrome(options=options)
    # Rely on explicit WebDriverWait everywhere; avoid mixing in an implicit wait
    context.driver.implicitly_wait(0)


def after_step(context, step):
    """On a failed step, print the visible message areas and save a screenshot"""
    if step.status != "failed" or not hasattr(context, "driver"):
        return
    for message_id in MESSAGE_IDS:
        try:
            text = context.driver.find_element(By.ID, message_id).text
            print(f"[DEBUG] #{message_id} = {text!r}")
        except Exception:  # pylint: disable=broad-except
            pass
    try:
        context.driver.save_screenshot("failed_step.png")
        print("[DEBUG] saved screenshot to failed_step.png")
    except Exception as error:  # pylint: disable=broad-except
        print(f"[DEBUG] could not save screenshot: {error}")


def after_all(context):
    """Shut the browser down after all scenarios have run"""
    context.driver.quit()
