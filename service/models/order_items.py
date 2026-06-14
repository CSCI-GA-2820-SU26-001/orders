"""
OrderItem Model
"""

from .persistent_base import db, PersistentBase, DataValidationError


class OrderItem(db.Model, PersistentBase):
    """Class that represents an OrderItem"""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<OrderItem id={self.id} order_id={self.order_id}>"

    def serialize(self):
        """Convert item to dictionary"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "price": str(self.price),
        }

    def deserialize(self, data):
        """Load item from dictionary"""
        try:
            self.product_id = data["product_id"]
            self.quantity = data["quantity"]
            self.price = data["price"]
        except KeyError as e:
            raise DataValidationError("Missing field: " + str(e))
        return self
