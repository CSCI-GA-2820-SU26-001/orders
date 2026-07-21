Feature: Orders Admin UI
    As an Orders Administrator
    I need a web user interface to manage customer orders
    So that I can keep orders up to date

Background:
    Given the following orders
        | customer_id | status |
        | 111         | open   |
        | 222         | closed |

Scenario: Create an order
    Given I am on the Admin UI
    When I set the "Create Customer ID" field to "555"
    And I set the "Create Status" field to "open"
    And I press the "Create Order" button
    Then I should see the message "created successfully"

Scenario: List all orders
    Given I am on the Admin UI
    Then I should see "111" in the results
    And I should see "222" in the results

Scenario: Query orders by status
    Given I am on the Admin UI
    When I select "Open" in the "Search Status" dropdown
    And I press the "Search" button
    Then I should see "111" in the results
    And I should not see "222" in the results

Scenario: Read an order
    Given I am on the Admin UI
    When I copy the id of the order for customer "111"
    And I set the "Read Order ID" field to the copied id
    And I press the "Read Order" button
    Then I should see the copied order id in the read confirmation

Scenario: Update an order
    Given I am on the Admin UI
    When I copy the id of the order for customer "111"
    And I set the "Update Order ID" field to the copied id
    And I set the "Update Customer ID" field to "999"
    And I set the "Update Status" field to "confirmed"
    And I press the "Update Order" button
    Then I should see the message "updated successfully"

Scenario: Delete an order
    Given I am on the Admin UI
    When I press "Delete" on the order for customer "111"
    Then I should not see "111" in the results

Scenario: Cancel an order
    Given I am on the Admin UI
    When I press "Cancel Order" on the order for customer "111"
    Then I should see "cancelled" in the results
