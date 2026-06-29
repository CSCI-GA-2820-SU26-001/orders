"""
Order Model
"""

from .persistent_base import db, PersistentBase, DataValidationError


class Order(db.Model, PersistentBase):
    """Class that represents an Order"""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")
    items = db.relationship("OrderItem", backref="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order id={self.id} customer_id={self.customer_id}>"

    def serialize(self):
        """Convert order to dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "status": self.status,
            "items": [item.serialize() for item in self.items],
        }

    def deserialize(self, data):
        """Load order from dictionary"""
        try:
            self.customer_id = data["customer_id"]
            self.status = data.get("status", "open")
        except KeyError as e:
            raise DataValidationError("Missing field: " + str(e)) from e
        return self
