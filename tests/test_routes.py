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

# pylint: disable=duplicate-code
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
BASE_URL = "/orders"


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

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delete_an_order(self):
        """It should Delete one Order and leave others intact"""
        order1 = Order(customer_id=1, status="open")
        order1.create()
        order2 = Order(customer_id=2, status="open")
        order2.create()
        self.assertEqual(len(Order.all()), 2)

        resp = self.client.delete(f"/orders/{order1.id}")  # 删一条
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        self.assertIsNone(Order.find(order1.id))
        self.assertIsNotNone(Order.find(order2.id))
        self.assertEqual(len(Order.all()), 1)

    def test_delete_non_existing_order(self):
        """It should Delete a non-existing Order and return 204"""
        resp = self.client.delete("/orders/0")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_order(self):
        """It should Read a single Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        resp = self.client.get(f"/orders/{order.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["customer_id"], 1)
        self.assertEqual(data["status"], "open")

    def test_get_order_not_found(self):
        """It should return 404 for a non existing Order"""
        resp = self.client.get("/orders/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # Todo: Add your test cases here...
    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
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
