"""
Order Model
"""

from enum import Enum
from .persistent_base import db, PersistentBase, DataValidationError


class OrderStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    PENDING = "pending"


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(OrderStatus), nullable=False, default=OrderStatus.OPEN)
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} customer_id={self.customer_id}>"

    def serialize(self):
        """Convert order to dictionary"""
        status = (
            self.status.value if isinstance(self.status, OrderStatus) else self.status
        )

        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": status,
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """Load order from dictionary"""
        try:
            self.customer_id = data["customer_id"]
            status = data.get("status", "open")
            self.status = OrderStatus(status)
        except KeyError as e:
            raise DataValidationError("Missing field: " + str(e)) from e
        return self
