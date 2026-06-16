"""
Test Factory to make fake objects for testing
"""

import factory
from service.models import Order


class OrderFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Order

    id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n + 1)
    status = factory.Faker(
        "random_element", elements=["open", "pending", "shipped", "closed"]
    )


# Todo: Add your other attributes here...
