"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order


class OrderFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""


from factory.declarations import Sequence


class OrderFactory(factory.Factory):
    """Creates fake orders for testing"""

    class Meta:
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n + 1)
    status = factory.Faker(
        "random_element", elements=["open", "pending", "shipped", "closed"]
    )

    # Todo: Add your other attributes here...
    id = Sequence(lambda n: n)
    customer_id = Sequence(lambda n: n + 1)
    status = factory.Faker(
        "random_element", elements=["open", "pending", "shipped", "closed"]
    )
