######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Orders Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Orders
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app
from service.models import Order, OrderItem
from service.common import status


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
    return (
        jsonify(
            name="Orders REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Create an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to Create an Order...")
    check_content_type("application/json")

    order = Order()
    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order.deserialize(data)

    # Save the new Order to the database
    order.create()
    app.logger.info("Order with new id [%s] saved!", order.id)

    # Return the location of the new Order
    location_url = url_for("get_orders", order_id=order.id, _external=True)
    return order.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# READ AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["GET"])
def get_orders(order_id):
    """
    Retrieve a single Order
    This endpoint will return an Order based on its id
    """
    app.logger.info("Request to Retrieve an order with id [%s]", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_orders(order_id):
    """
    Update an Order
    This endpoint will update an Order based on its id
    """
    app.logger.info("Request to update order with id: %s", order_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    order.deserialize(request.get_json())
    order.id = order_id
    order.update()

    return jsonify(order.serialize()), status.HTTP_200_OK


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_orders(order_id):
    """
    Delete an Order

    This endpoint will delete an Order based on the id specified in the path
    """
    app.logger.info("Request to delete order with id: %s", order_id)

    order = Order.find(order_id)
    if order:
        order.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# LIST ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """
    List all Orders

    This endpoint will return all Orders in the database
    """
    app.logger.info("Request for order list")

    orders = Order.all()
    results = [order.serialize() for order in orders]

    app.logger.info("Returning %d orders", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# ADD ITEMS TO AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["POST"])
def add_order_item(order_id):
    """
    Add an item to an Order
    This endpoint will add an item to an existing Order based the data in the body that is posted
    """
    app.logger.info("Requesting to add an item to an order...")
    check_content_type("application/json")

    # find the order
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")

    # Get the data from the request and deserialize it
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    order_item = OrderItem()
    order_item.deserialize(data)

    # Update the order with the new item
    order.items.append(order_item)
    order.update()

    app.logger.info("Item added to order [%s]", order.id)

    # Return the location of the new Order
    location_url = url_for(
        "get_order_item", order_id=order_id, item_id=order_item.id, _external=True
    )
    return order_item.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type) -> None:
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# READ AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def get_order_item(order_id, item_id):
    """
    Retrieve an item from an Order
    This endpoint will return an OrderItem based on its id
    """
    app.logger.info("Request to retrieve item %s for order %s", item_id, order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")
    item = OrderItem.find(item_id)
    if not item:
        abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
    return jsonify(item.serialize()), status.HTTP_200_OK


######################################################################
# LIST ALL ITEMS IN AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items", methods=["GET"])
def list_order_items(order_id):
    """
    List all items in an Order

    This endpoint will return all items belonging to an Order
    """
    app.logger.info("Request to list items for order %s", order_id)

    # First make sure the order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    results = [item.serialize() for item in order.items]

    app.logger.info("Returning %d items for order %s", len(results), order_id)
    return jsonify(results), status.HTTP_200_OK


######################################################################
# DELETE AN ITEM FROM AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_order_item(order_id, item_id):
    """
    Delete an item from an Order

    This endpoint will remove an item from an existing Order
    """
    app.logger.info("Request to delete item %s from order %s", item_id, order_id)

    # Make sure the order exists
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    # Find the item; if it exists, delete it
    item = OrderItem.find(item_id)
    if item:
        item.delete()

    return "", status.HTTP_204_NO_CONTENT
