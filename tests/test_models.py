"""
Test cases for Order Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models import Order, OrderItem, DataValidationError, db
from service.models.persistent_base import PersistentBase

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

    def test_order_repr(self):
        """It should create a human-readable Order representation"""
        order = Order(id=1, customer_id=1, status="open")
        self.assertEqual(repr(order), "<Order id=1 customer_id=1>")

    def test_order_item_repr(self):
        """It should create a human-readable OrderItem representation"""
        item = OrderItem(id=1, order_id=1, product_id=100, quantity=1, price=9.99)
        self.assertEqual(repr(item), "<OrderItem id=1 order_id=1>")

    def test_persistent_base_init(self):
        """It should initialize a PersistentBase object with no id"""
        base = PersistentBase()
        self.assertIsNone(base.id)

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

    def test_update_order_with_no_id(self):
        """It should not update an Order without an id"""
        order = Order(customer_id=1, status="open")
        self.assertRaises(DataValidationError, order.update)

    def test_create_order_with_database_error(self):
        """It should raise DataValidationError when create fails"""
        order = Order(status="open")
        self.assertRaises(DataValidationError, order.create)

    def test_update_order_with_database_error(self):
        """It should raise DataValidationError when update fails"""
        order = Order(customer_id=1, status="open")
        order.create()
        with patch.object(db.session, "commit", side_effect=Exception("update error")):
            self.assertRaises(DataValidationError, order.update)

    def test_delete_order_with_database_error(self):
        """It should raise DataValidationError when delete fails"""
        order = Order(customer_id=1, status="open")
        order.create()
        with patch.object(db.session, "delete", side_effect=Exception("delete error")):
            self.assertRaises(DataValidationError, order.delete)

    def test_serialize_an_order(self):
        """It should serialize an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        data = order.serialize()
        self.assertIn("id", data)
        self.assertIn("customer_id", data)
        self.assertIn("status", data)
        self.assertIn("items", data)

    def test_deserialize_order_missing_customer_id(self):
        """It should not deserialize an Order without customer_id"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {"status": "open"})

    def test_deserialize_item_invalid_quantity(self):
        """It should not deserialize an OrderItem with invalid quantity"""
        item = OrderItem()
        data = {"product_id": 100, "quantity": 0, "price": 19.99}
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_item_negative_price(self):
        """It should not deserialize an OrderItem with negative price"""
        item = OrderItem()
        data = {"product_id": 100, "quantity": 1, "price": -1.00}
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_item_invalid_price(self):
        """It should not deserialize an OrderItem with invalid price"""
        item = OrderItem()
        data = {"product_id": 100, "quantity": 1, "price": "bad-price"}
        self.assertRaises(DataValidationError, item.deserialize, data)
