"""
Test Factory to make fake objects for testing
"""

import factory
from factory.declarations import Sequence
from service.models import Order


class OrderFactory(factory.Factory):  # pylint: disable=too-few-public-methods
    """Creates fake orders for testing"""

    class Meta:
        """Maps factory to data model"""

        model = Order

    id = Sequence(lambda n: n)
    customer_id = Sequence(lambda n: n + 1)
    status = factory.Faker(
        "random_element", elements=["open", "pending", "shipped", "closed"]
    )
