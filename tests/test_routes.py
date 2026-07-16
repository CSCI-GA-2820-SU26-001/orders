######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
TestOrder API Service Test Suite
"""

# pylint: disable=duplicate-code, unexpected-keyword-arg
import os
import logging
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Order, OrderItem
from tests.factories import OrderFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def assert_json_error(self, response, status_code, error):
        """It should return an error response as JSON"""
        self.assertEqual(response.status_code, status_code)
        self.assertIn("application/json", response.content_type)
        data = response.get_json()
        self.assertIsInstance(data, dict)
        self.assertEqual(data["status"], status_code)
        self.assertEqual(data["error"], error)
        self.assertIn("message", data)

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should return service info and available endpoints"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(data["name"], "Orders REST API Service")
        self.assertEqual(data["version"], "1.0")
        # the new endpoints field should exist and document operations
        self.assertIn("endpoints", data)
        self.assertEqual(data["endpoints"]["list_orders"], "GET /api/orders")
        self.assertEqual(data["endpoints"]["create_order"], "POST /api/orders")
        self.assertIn("cancel_order", data["endpoints"])

    def test_health(self):
        """It should return health status"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, {"status": "OK"})

    def test_delete_an_order(self):
        """It should Delete one Order and leave others intact"""
        order1 = Order(customer_id=1, status="open")
        order1.create()
        order2 = Order(customer_id=2, status="open")
        order2.create()
        self.assertEqual(len(Order.all()), 2)

        resp = self.client.delete(f"/api/orders/{order1.id}")  # 删一条
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        self.assertIsNone(Order.find(order1.id))
        self.assertIsNotNone(Order.find(order2.id))
        self.assertEqual(len(Order.all()), 1)

    def test_delete_non_existing_order(self):
        """It should Delete a non-existing Order and return 204"""
        resp = self.client.delete("/api/orders/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_order(self):
        """It should Read a single Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        resp = self.client.get(f"/api/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], 1)
        self.assertEqual(data["status"], "open")

    def test_get_order_not_found(self):
        """It should return 404 for a non existing Order"""
        resp = self.client.get("/api/orders/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order(self):
        """It should Update an existing Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        new_order = order.serialize()
        new_order["status"] = "closed"

        resp = self.client.put(f"{BASE_URL}/{order.id}", json=new_order)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], order.id)
        self.assertEqual(data["customer_id"], order.customer_id)
        self.assertEqual(data["status"], "closed")

    def test_update_order_not_found(self):
        """It should not Update an Order that was not found"""
        order = OrderFactory()
        resp = self.client.put(f"{BASE_URL}/0", json=order.serialize())
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_wrong_content_type(self):
        """It should not Update an Order with the wrong content type"""
        order = Order(customer_id=1, status="open")
        order.create()
        resp = self.client.put(
            f"{BASE_URL}/{order.id}",
            data=order.serialize(),
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order(self):
        """It should Create a new Order"""
        test_order = OrderFactory()
        logging.debug("Test Order: %s", test_order.serialize())
        response = self.client.post(BASE_URL, json=test_order.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = response.get_json()
        self.assertEqual(new_order["customer_id"], test_order.customer_id)
        self.assertEqual(new_order["status"], test_order.status)
        self.assertIsNotNone(new_order["id"])  # ID should be auto-generated

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        fetched_order = response.get_json()
        self.assertEqual(fetched_order["id"], new_order["id"])
        self.assertEqual(fetched_order["customer_id"], new_order["customer_id"])
        self.assertEqual(fetched_order["status"], new_order["status"])

    def test_create_order_missing_customer_id(self):
        """It should return 400 when creating an Order without customer_id"""
        response = self.client.post(BASE_URL, json={"status": "open"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_customer_id_returns_json_error(self):
        """It should return JSON when creating an Order without customer_id"""
        response = self.client.post(BASE_URL, json={"status": "open"})
        self.assert_json_error(response, status.HTTP_400_BAD_REQUEST, "Bad Request")

    def test_create_order_invalid_status_returns_json_error(self):
        """It should return JSON when creating an Order with an invalid status"""
        response = self.client.post(
            BASE_URL, json={"customer_id": 1, "status": "not-a-status"}
        )
        self.assert_json_error(response, status.HTTP_400_BAD_REQUEST, "Bad Request")

    def test_create_order_no_content_type(self):
        """It should return 415 when creating an Order with no content type"""
        response = self.client.post(BASE_URL, data='{"customer_id": 1}')
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order_no_content_type_returns_json_error(self):
        """It should return JSON when creating an Order with no content type"""
        response = self.client.post(BASE_URL, data='{"customer_id": 1}')
        self.assert_json_error(
            response, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported Media Type"
        )

    def test_method_not_allowed(self):
        """It should return 405 for methods that are not allowed"""
        response = self.client.put(BASE_URL, json={"customer_id": 1})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_method_not_allowed_returns_json_error(self):
        """It should return JSON for methods that are not allowed"""
        response = self.client.put(BASE_URL, json={"customer_id": 1})
        self.assert_json_error(
            response, status.HTTP_405_METHOD_NOT_ALLOWED, "Method Not Allowed"
        )

    def test_list_orders(self):
        """It should List all Orders"""
        # create 3 orders using the factory
        for _ in range(3):
            test_order = OrderFactory()
            self.client.post(BASE_URL, json=test_order.serialize())

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_list_orders_empty(self):
        """It should return an empty list when there are no Orders"""
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])

    def test_add_item_to_order(self):
        """Add an item to an Order"""

        # Create an order first
        order = Order(customer_id=1, status="open")
        order.create()

        # Create item data
        item_data = {"product_id": 100, "quantity": 5, "price": 19.99}

        # Add item to order
        response = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify item was added to order
        updated_order = Order.find(order.id)
        self.assertEqual(len(updated_order.items), 1)
        self.assertEqual(updated_order.items[0].product_id, 100)

    def test_add_item_to_order_not_found(self):
        """It should return 404 when Order does not exist"""
        item_data = {"product_id": 100, "quantity": 5, "price": 19.99}

        response = self.client.post(f"{BASE_URL}/0/items", json=item_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_item_to_order_wrong_content_type(self):
        """It should return 415 with wrong content type"""
        order = Order(customer_id=1, status="open")
        order.create()

        item_data = {"product_id": 100, "quantity": 5, "price": 19.99}

        response = self.client.post(
            f"{BASE_URL}/{order.id}/items", data=item_data, content_type="text/plain"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_add_multiple_items_to_order(self):
        """It should Add multiple items to an Order"""
        order = Order(customer_id=1, status="open")
        order.create()

        # Add first item
        item_data_1 = {"product_id": 100, "quantity": 2, "price": 10.00}
        response1 = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data_1)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Add second item
        item_data_2 = {"product_id": 200, "quantity": 3, "price": 15.50}
        response2 = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data_2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Verify both items in order
        updated_order = Order.find(order.id)
        self.assertEqual(len(updated_order.items), 2)

    def test_add_item_missing_field(self):
        """It should return 400 when required field is missing"""
        order = Order(customer_id=1, status="open")
        order.create()

        # Missing product_id
        item_data = {"quantity": 5, "price": 19.99}

        response = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_invalid_quantity(self):
        """It should return 400 when item quantity is not positive"""
        order = Order(customer_id=1, status="open")
        order.create()

        item_data = {"product_id": 100, "quantity": 0, "price": 19.99}

        response = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_item_negative_price(self):
        """It should return 400 when item price is negative"""
        order = Order(customer_id=1, status="open")
        order.create()

        item_data = {"product_id": 100, "quantity": 5, "price": -1.00}

        response = self.client.post(f"{BASE_URL}/{order.id}/items", json=item_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_order_item(self):
        """It should Read an item from an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        resp = self.client.get(f"/api/orders/{order.id}/items/{item.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["product_id"], 101)
        self.assertEqual(data["quantity"], 2)

    def test_get_order_item_not_found(self):
        """It should return 404 for an item that does not exist"""
        order = Order(customer_id=1, status="open")
        order.create()
        resp = self.client.get(f"/api/orders/{order.id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_order_item_order_not_found(self):
        """It should return 404 when reading an item from an Order that does not exist"""
        resp = self.client.get("/api/orders/0/items/1")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_item(self):
        """It should Update an item in an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(product_id=100, quantity=2, price=9.99)
        order.items.append(item)
        order.update()

        new_item = {"product_id": 200, "quantity": 5, "price": 19.99}
        resp = self.client.put(f"{BASE_URL}/{order.id}/items/{item.id}", json=new_item)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], item.id)
        self.assertEqual(data[0]["product_id"], new_item["product_id"])
        self.assertEqual(data[0]["quantity"], new_item["quantity"])
        self.assertEqual(data[0]["price"], "19.99")

        updated_item = OrderItem.find(item.id)
        self.assertEqual(updated_item.product_id, new_item["product_id"])
        self.assertEqual(updated_item.quantity, new_item["quantity"])

    def test_update_order_item_not_found(self):
        """It should return 404 when updating an item that does not exist"""
        order = Order(customer_id=1, status="open")
        order.create()

        new_item = {"product_id": 200, "quantity": 5, "price": 19.99}
        resp = self.client.put(f"{BASE_URL}/{order.id}/items/0", json=new_item)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_item_order_not_found(self):
        """It should return 404 when updating an item for an Order that does not exist"""
        new_item = {"product_id": 200, "quantity": 5, "price": 19.99}
        resp = self.client.put(f"{BASE_URL}/0/items/1", json=new_item)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_item_wrong_content_type(self):
        """It should return 415 when updating an item with the wrong content type"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(product_id=100, quantity=2, price=9.99)
        order.items.append(item)
        order.update()

        resp = self.client.put(
            f"{BASE_URL}/{order.id}/items/{item.id}",
            data={"product_id": 200, "quantity": 5, "price": 19.99},
            content_type="text/plain",
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_order_item_invalid_quantity(self):
        """It should return 400 when updating an item with an invalid quantity"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(product_id=100, quantity=2, price=9.99)
        order.items.append(item)
        order.update()

        new_item = {"product_id": 200, "quantity": 0, "price": 19.99}
        resp = self.client.put(f"{BASE_URL}/{order.id}/items/{item.id}", json=new_item)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_items_in_order(self):
        """It should List all items in an Order"""
        # create an order
        order = Order(customer_id=1, status="open")
        order.create()
        # add two items to it
        item1 = OrderItem(product_id=100, quantity=2, price=9.99)
        item2 = OrderItem(product_id=200, quantity=1, price=19.99)
        order.items.append(item1)
        order.items.append(item2)
        order.update()

        resp = self.client.get(f"/api/orders/{order.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_list_items_empty_order(self):
        """It should return an empty list for an Order with no items"""
        order = Order(customer_id=1, status="open")
        order.create()

        resp = self.client.get(f"/api/orders/{order.id}/items")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data, [])

    def test_list_items_order_not_found(self):
        """It should return 404 when the Order does not exist"""
        resp = self.client.get("/api/orders/0/items")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item_from_order(self):
        """It should Delete an item from an Order (multiple items)"""
        order = Order(customer_id=1, status="open")
        order.create()
        item1 = OrderItem(product_id=100, quantity=2, price=9.99)
        item2 = OrderItem(product_id=200, quantity=1, price=19.99)
        order.items.append(item1)
        order.items.append(item2)
        order.update()

        resp = self.client.delete(f"/api/orders/{order.id}/items/{item1.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # the deleted item is gone, the other remains
        self.assertIsNone(OrderItem.find(item1.id))
        self.assertIsNotNone(OrderItem.find(item2.id))

    def test_delete_only_item_from_order(self):
        """It should leave an Order with no items after deleting its only item"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(product_id=100, quantity=2, price=9.99)
        order.items.append(item)
        order.update()

        resp = self.client.delete(f"/api/orders/{order.id}/items/{item.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # order still exists but has no items
        updated_order = Order.find(order.id)
        self.assertIsNotNone(updated_order)
        self.assertEqual(len(updated_order.items), 0)

    def test_delete_non_existing_item(self):
        """It should return 204 when deleting an item that does not exist"""
        order = Order(customer_id=1, status="open")
        order.create()

        resp = self.client.delete(f"/api/orders/{order.id}/items/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_order_not_found(self):
        """It should return 404 when the Order does not exist"""
        resp = self.client.delete("/api/orders/0/items/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders_by_status(self):
        """It should list orders filtered by status"""
        Order(customer_id=1, status="open").create()
        Order(customer_id=2, status="closed").create()
        Order(customer_id=3, status="open").create()

        resp = self.client.get(f"{BASE_URL}?status=open")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all(order["status"] == "open" for order in data))

    def test_list_orders_by_customer_id(self):
        """It should list orders filtered by customer_id"""
        Order(customer_id=1, status="open").create()
        Order(customer_id=2, status="closed").create()
        Order(customer_id=1, status="closed").create()

        resp = self.client.get(f"{BASE_URL}?customer_id=1")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)
        self.assertTrue(all(order["customer_id"] == 1 for order in data))

    def test_list_orders_by_id(self):
        """It should list orders filtered by id"""
        order1 = Order(customer_id=1, status="open")
        order1.create()
        order2 = Order(customer_id=2, status="closed")
        order2.create()

        resp = self.client.get(f"{BASE_URL}?id={order1.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], order1.id)

    def test_list_orders_by_item_id(self):
        """It should list orders filtered by item_id"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(product_id=100, quantity=2, price=9.99)
        order.items.append(item)
        order.update()

        resp = self.client.get(f"{BASE_URL}?item_id={item.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], order.id)

    def test_list_orders_customer_id_must_be_integer(self):
        """It should return 400 when customer_id is not an integer"""
        resp = self.client.get(f"{BASE_URL}?customer_id=abc")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("customer_id must be an integer", resp.get_data(as_text=True))

    def test_list_orders_invalid_query_returns_json_error(self):
        """It should return JSON when a query parameter is invalid"""
        resp = self.client.get(f"{BASE_URL}?customer_id=abc")
        self.assert_json_error(resp, status.HTTP_400_BAD_REQUEST, "Bad Request")

    def test_list_orders_id_must_be_integer(self):
        """It should return 400 when id is not an integer"""
        resp = self.client.get(f"{BASE_URL}?id=abc")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("id must be an integer", resp.get_data(as_text=True))

    def test_list_orders_item_id_must_be_integer(self):
        """It should return 400 when item_id is not an integer"""
        resp = self.client.get(f"{BASE_URL}?item_id=abc")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("item_id must be an integer", resp.get_data(as_text=True))

    ######################################################################
    # CANCEL AN ORDER
    ######################################################################
    def test_cancel_order(self):
        """It should Cancel an Order and return status as cancelled"""
        order = Order(customer_id=1, status="open")
        order.create()
        resp = self.client.put(f"/api/orders/{order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "cancelled")

    def test_cancel_order_not_found(self):
        """It should return 404 when cancelling an Order that does not exist"""
        resp = self.client.put("/api/orders/0/cancel")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_order_not_found_returns_json_error(self):
        """It should return JSON when cancelling an Order that does not exist"""
        resp = self.client.put("/api/orders/0/cancel")
        self.assert_json_error(resp, status.HTTP_404_NOT_FOUND, "Not Found")

    def test_cancel_order_already_cancelled(self):
        """It should return 409 when cancelling an Order that is already cancelled"""
        order = Order(customer_id=1, status="cancelled")
        order.create()
        resp = self.client.put(f"/api/orders/{order.id}/cancel")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_swagger_docs_are_available(self):
        """It should return the Swagger UI documentation"""
        response = self.client.get("/apidocs/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("swagger", response.get_data(as_text=True).lower())

    def test_swagger_spec_contains_order_paths_and_models(self):
        """It should return the Swagger specification with Order paths and models"""
        response = self.client.get("/api/swagger.json")
        self.assertEqual(response.status_code, 200)

        data = response.get_json()
        self.assertIn("/orders", data["paths"])
        self.assertIn("/orders/{order_id}", data["paths"])
        self.assertIn("/orders/{order_id}/items", data["paths"])

        definitions = data.get("definitions", {})
        self.assertIn("Order", definitions)
        self.assertIn("OrderItemData", definitions)
        self.assertIn("OrderItem", definitions)
