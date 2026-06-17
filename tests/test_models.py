"""
Test cases for Order Model
"""

import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Order, OrderItem, db

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


class TestOrderModel(TestCase):
    """Test Cases for Order Model"""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        db.session.close()

    def setUp(self):
        db.session.query(OrderItem).delete()
        db.session.query(Order).delete()
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def test_create_an_order(self):
        """It should create an Order and add it to the database"""
        order = Order(customer_id=1, status="open")
        order.create()
        self.assertIsNotNone(order.id)

    def test_read_an_order(self):
        """It should read an Order from the database"""
        order = Order(customer_id=1, status="open")
        order.create()
        found = Order.find(order.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.customer_id, 1)
        self.assertEqual(found.status, "open")

    def test_read_order_not_found(self):
        """It should return None for an Order that does not exist"""
        found = Order.find(0)
        self.assertIsNone(found)

    def test_update_an_order(self):
        """It should update an Order in the database"""
        order = Order(customer_id=1, status="open")
        order.create()
        self.assertIsNotNone(order.id)
        order.status = "closed"
        order.update()

        found = Order.find(order.id)
        self.assertEqual(found.status, "closed")

    def test_serialize_an_order(self):
        """It should serialize an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        data = order.serialize()
        self.assertIn("id", data)
        self.assertIn("customer_id", data)
        self.assertIn("status", data)
        self.assertIn("items", data)
