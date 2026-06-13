"""
Test cases for Order Model
"""
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Order, OrderItem, DataValidationError, db

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
        """It should create an Order"""
        order = Order(customer_id=1, status="open")
        self.assertIsNotNone(order)
        self.assertEqual(order.customer_id, 1)
        self.assertEqual(order.status, "open")

    def test_add_an_order(self):
        """It should add an Order to the database"""
        order = Order(customer_id=1, status="open")
        order.create()
        self.assertIsNotNone(order.id)
        self.assertEqual(len(Order.all()), 1)

    def test_read_an_order(self):
        """It should read an Order from the database"""
        order = Order(customer_id=1, status="open")
        order.create()
        found = Order.find(order.id)
        self.assertEqual(found.customer_id, 1)

    def test_update_an_order(self):
        """It should update an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        order.status = "shipped"
        order.update()
        found = Order.find(order.id)
        self.assertEqual(found.status, "shipped")

    def test_delete_an_order(self):
        """It should delete an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        order.delete()
        self.assertEqual(len(Order.all()), 0)

    def test_add_order_item(self):
        """It should add an item to an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        self.assertIsNotNone(item.id)
        self.assertEqual(item.order_id, order.id)

    def test_serialize_an_order(self):
        """It should serialize an Order"""
        order = Order(customer_id=1, status="open")
        order.create()
        data = order.serialize()
        self.assertIn("id", data)
        self.assertIn("customer_id", data)
        self.assertIn("status", data)
        self.assertIn("items", data)

    def test_deserialize_an_order(self):
        """It should deserialize an Order"""
        data = {"customer_id": 1, "status": "open"}
        order = Order()
        order.deserialize(data)
        self.assertEqual(order.customer_id, 1)

    def test_deserialize_missing_data(self):
        """It should raise DataValidationError for missing data"""
        data = {"status": "open"}
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, data)

    def test_read_order_item(self):
        """It should read an OrderItem"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        found = OrderItem.find(item.id)
        self.assertIsNotNone(found)
        self.assertEqual(found.product_id, 101)

    def test_update_order_item(self):
        """It should update an OrderItem"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        item.quantity = 5
        item.update()
        found = OrderItem.find(item.id)
        self.assertEqual(found.quantity, 5)

    def test_delete_order_item(self):
        """It should delete an OrderItem"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        item.delete()
        self.assertIsNone(OrderItem.find(item.id))

    def test_serialize_order_item(self):
        """It should serialize an OrderItem"""
        order = Order(customer_id=1, status="open")
        order.create()
        item = OrderItem(order_id=order.id, product_id=101, quantity=2, price=9.99)
        item.create()
        data = item.serialize()
        self.assertIn("id", data)
        self.assertIn("order_id", data)
        self.assertIn("product_id", data)
        self.assertIn("quantity", data)
        self.assertIn("price", data)

    def test_deserialize_order_item(self):
        """It should deserialize an OrderItem"""
        data = {"product_id": 101, "quantity": 2, "price": 9.99}
        item = OrderItem()
        item.deserialize(data)
        self.assertEqual(item.product_id, 101)
        self.assertEqual(item.quantity, 2)

    def test_deserialize_order_item_missing_data(self):
        """It should raise DataValidationError for missing OrderItem data"""
        data = {"product_id": 101}
        item = OrderItem()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_list_all_orders(self):
        """It should list all Orders"""
        Order(customer_id=1, status="open").create()
        Order(customer_id=2, status="shipped").create()
        orders = Order.all()
        self.assertEqual(len(orders), 2)
