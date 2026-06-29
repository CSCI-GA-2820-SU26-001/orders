"""
Test Factory to make fake objects for testing
"""
import factory
from factory.declarations import Sequence
from service.models import Order


class OrderFactory(factory.Factory):
    """Creates fake orders for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""
        model = Order

    id = Sequence(lambda n: n)
    customer_id = Sequence(lambda n: n + 1)
    status = factory.Faker(
        "random_element", elements=["open", "pending", "shipped", "closed"]
    )
