"""
Step definitions for the Orders Admin UI BDD scenarios.

Data is seeded through the REST API in the Background (setup only); every
assertion and action goes through the web interface using Selenium.
"""
import requests
from behave import given, when, then
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Message areas on the Admin UI, dumped into the error when an assertion fails
_MESSAGE_IDS = [
    "orders-message",
    "update-order-message",
    "read-order-message",
    "read-item-message",
    "add-item-message",
    "update-item-message",
    "delete-item-message",
    "items-message",
]


def _dump_page_state(context):
    """Collect the visible message texts and save a screenshot for debugging"""
    messages = {}
    for message_id in _MESSAGE_IDS:
        try:
            messages[message_id] = context.driver.find_element(
                By.ID, message_id
            ).text
        except Exception:  # pylint: disable=broad-except
            pass
    try:
        context.driver.save_screenshot("failed_step.png")
    except Exception:  # pylint: disable=broad-except
        pass
    return messages


# Maps the friendly field names used in the .feature file to element ids
FIELD_IDS = {
    "Create Customer ID": "create-customer-id",
    "Create Status": "order-status",
    "Search Status": "search-order-status",
    "Read Order ID": "read-order-id",
    "Update Order ID": "update-order-id",
    "Update Customer ID": "update-customer-id",
    "Update Status": "update-order-status",
}

# Maps the friendly button names used in the .feature file to element ids
BUTTON_IDS = {
    "Create Order": "create-order-btn",
    "Search": "search-orders-btn",
    "Read Order": "read-order-btn",
    "Update Order": "update-order-btn",
}


def _set_value(context, element_id, value):
    """Set an input's value via JavaScript so headless typing is deterministic"""
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    context.driver.execute_script(
        "arguments[0].value = arguments[1];"
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));"
        "arguments[0].dispatchEvent(new Event('change', {bubbles: true}));",
        element,
        value,
    )


def _find_order_row(context, customer_id):
    """Wait for and return the orders table row for the given customer id"""

    def _locate(driver):
        rows = driver.find_elements(
            By.CSS_SELECTOR, "#orders-table-body tr"
        )
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 2 and cells[1].text == customer_id:
                return row
        return False

    return WebDriverWait(context.driver, context.wait_seconds).until(_locate)


@given("the following orders")
def step_seed_orders(context):
    """Reset the orders and seed the table rows through the REST API"""
    rest_endpoint = f"{context.base_url}/api/orders"

    response = requests.get(rest_endpoint, timeout=context.wait_seconds)
    assert response.status_code == 200, f"GET orders failed: {response.status_code}"
    for order in response.json():
        requests.delete(
            f"{rest_endpoint}/{order['id']}", timeout=context.wait_seconds
        )

    for row in context.table:
        payload = {
            "customer_id": int(row["customer_id"]),
            "status": row["status"],
        }
        post = requests.post(
            rest_endpoint, json=payload, timeout=context.wait_seconds
        )
        assert post.status_code == 201, f"POST order failed: {post.status_code}"


@given("I am on the Admin UI")
@when("I am on the Admin UI")
def step_visit_admin(context):
    """Open the Admin UI home page"""
    context.driver.get(f"{context.base_url}/admin")


@when('I set the "{name}" field to "{value}"')
def step_set_field(context, name, value):
    """Set the value of a text/number input identified by its friendly name"""
    _set_value(context, FIELD_IDS[name], value)


@when('I copy the id of the order for customer "{customer_id}"')
def step_copy_order_id(context, customer_id):
    """Remember the order id shown in the table for the given customer"""
    row = _find_order_row(context, customer_id)
    context.copied_id = row.find_elements(By.TAG_NAME, "td")[0].text


@when('I set the "{name}" field to the copied id')
def step_set_field_copied(context, name):
    """Fill a field with the order id copied from the table"""
    _set_value(context, FIELD_IDS[name], context.copied_id)


@when('I press "{action}" on the order for customer "{customer_id}"')
def step_row_action(context, action, customer_id):
    """Click a row-level button (e.g. Delete, Cancel Order) for a customer"""
    row = _find_order_row(context, customer_id)
    for button in row.find_elements(By.TAG_NAME, "button"):
        if button.text == action:
            button.click()
            return
    raise AssertionError(
        f'No "{action}" button on the order row for customer {customer_id}'
    )


@when('I select "{value}" in the "{name}" dropdown')
def step_select_dropdown(context, name, value):
    """Pick an option from a select element identified by its friendly name"""
    element_id = FIELD_IDS[name]
    dropdown = Select(context.driver.find_element(By.ID, element_id))
    dropdown.select_by_visible_text(value)


@when('I press the "{name}" button')
def step_press_button(context, name):
    """Click a button identified by its friendly name"""
    element_id = BUTTON_IDS[name]
    context.driver.find_element(By.ID, element_id).click()


@then('I should see the message "{text}"')
def step_see_message(context, text):
    """Wait until the given text appears anywhere on the page"""
    try:
        WebDriverWait(context.driver, context.wait_seconds).until(
            lambda driver: text in driver.find_element(By.TAG_NAME, "body").text
        )
    except TimeoutException:
        messages = _dump_page_state(context)
        raise AssertionError(
            f'Did not find message "{text}". Current messages: {messages}'
        )


@then('I should see "{text}" in the results')
def step_see_in_results(context, text):
    """Wait until the given text appears in the orders results table"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: text
        in driver.find_element(By.ID, "orders-table-body").text
    )
    assert found, f'Did not find "{text}" in the results table'


@then('I should not see "{text}" in the results')
def step_not_see_in_results(context, text):
    """Wait until the given text is absent from the orders results table"""
    absent = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: text
        not in driver.find_element(By.ID, "orders-table-body").text
    )
    assert absent, f'Unexpectedly found "{text}" in the results table'


@then('I should see the copied order id in the read confirmation')
def step_read_confirmation_has_copied_id(context):
    """The read-order message should confirm the order id that was read"""
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        lambda driver: context.copied_id
        in driver.find_element(By.ID, "read-order-message").text
    )
    assert found, (
        f'Read confirmation did not mention order id {context.copied_id}'
    )
