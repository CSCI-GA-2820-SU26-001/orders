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
and Delete Orders, using Flask-RESTX so Swagger docs are generated
automatically at /apidocs.
"""

from typing import NoReturn
from http import HTTPStatus
from flask import request
from flask import current_app as app
from flask_restx import Api, Resource, fields
from werkzeug.exceptions import HTTPException
from service.models import Order, OrderItem, DataValidationError
from service.common import status

######################################################################
# CONFIGURE FLASK-RESTX
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Orders REST API Service",
    description="This service manages Orders and the Items inside them.",
    default="orders",
    default_label="Order operations",
    doc="/apidocs",
    prefix="/api",
)


######################################################################
# API MODELS (used for Swagger docs and input validation)
######################################################################
create_item_model = api.model(
    "OrderItemData",
    {
        "product_id": fields.Integer(required=True, description="The product id"),
        "quantity": fields.Integer(required=True, description="Quantity ordered"),
        "price": fields.Fixed(decimals=2, required=True, description="Unit price"),
    },
)

item_model = api.inherit(
    "OrderItem",
    create_item_model,
    {
        "id": fields.Integer(readOnly=True, description="The item's unique id"),
        "order_id": fields.Integer(
            readOnly=True, description="The id of the order this item belongs to"
        ),
    },
)

create_order_model = api.model(
    "OrderData",
    {
        "customer_id": fields.Integer(required=True, description="The customer id"),
        "status": fields.String(
            required=False, description="Order status (defaults to 'open')"
        ),
    },
)

order_model = api.inherit(
    "Order",
    create_order_model,
    {
        "id": fields.Integer(readOnly=True, description="The order's unique id"),
        "items": fields.List(
            fields.Nested(item_model), description="Items in this order"
        ),
    },
)


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response with service info and available endpoints"""
    app.logger.info("Request for Root URL")
    return (
        {
            "name": "Orders REST API Service",
            "version": "1.0",
            "paths": api.url_for(OrderCollection, _external=True),
            "endpoints": {
                "list_orders": "GET /api/orders",
                "create_order": "POST /api/orders",
                "read_order": "GET /api/orders/{id}",
                "update_order": "PUT /api/orders/{id}",
                "delete_order": "DELETE /api/orders/{id}",
                "list_items": "GET /api/orders/{id}/items",
                "add_item": "POST /api/orders/{id}/items",
                "read_item": "GET /api/orders/{id}/items/{item_id}",
                "update_item": "PUT /api/orders/{id}/items/{item_id}",
                "delete_item": "DELETE /api/orders/{id}/items/{item_id}",
                "cancel_order": "PUT /api/orders/{id}/cancel",
            },
        },
        status.HTTP_200_OK,
    )


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health", methods=["GET"])
def health():
    """Health Check Endpoint"""
    app.logger.info("Request for Health Check")
    return {"status": "OK"}, status.HTTP_200_OK


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
# QUERY HELPERS (unchanged from the original routes.py)
######################################################################
def _get_int_query_param(name):
    value = request.args.get(name)
    if value is None:
        return None

    try:
        return int(value)
    except ValueError:
        abort(status.HTTP_400_BAD_REQUEST, f"{name} must be an integer")


def _apply_order_filters(query):
    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter(Order.status == status_filter)

    customer_id = _get_int_query_param("customer_id")
    if customer_id is not None:
        query = query.filter(Order.customer_id == customer_id)

    order_id = _get_int_query_param("id")
    if order_id is not None:
        query = query.filter(Order.id == order_id)

    item_id = _get_int_query_param("item_id")
    if item_id is not None:
        query = query.join(Order.items).filter(OrderItem.id == item_id)

    return query


######################################################################
#  O R D E R   C O L L E C T I O N   ( /orders )
######################################################################
@api.route("/orders")
class OrderCollection(Resource):
    """Handles listing all Orders and creating a new Order"""

    @api.doc("list_orders")
    @api.marshal_list_with(order_model)
    def get(self):
        """
        List all Orders

        Supports filtering by query string: status, customer_id, id, item_id
        """
        app.logger.info("Request for order list")

        query = _apply_order_filters(Order.query)
        orders = query.all()
        results = [order.serialize() for order in orders]

        app.logger.info("Returning %d orders", len(results))
        return results, status.HTTP_200_OK

    @api.doc("create_orders")
    @api.expect(create_order_model)
    @api.response(400, "The posted Order data was not valid")
    @api.marshal_with(order_model, code=201)
    def post(self):
        """Create an Order based on the data in the request body"""
        app.logger.info("Request to Create an Order...")
        check_content_type("application/json")

        order = Order()
        app.logger.debug("Payload = %s", api.payload)
        order.deserialize(api.payload)

        order.create()
        app.logger.info("Order with new id [%s] saved!", order.id)

        location_url = api.url_for(OrderResource, order_id=order.id, _external=True)
        return order.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  O R D E R   R E S O U R C E   ( /orders/<order_id> )
######################################################################
@api.route("/orders/<int:order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """Handles Read, Update, and Delete for a single Order"""

    @api.doc("get_orders")
    @api.response(404, "Order not found")
    @api.marshal_with(order_model)
    def get(self, order_id):
        """Retrieve a single Order by its id"""
        app.logger.info("Request to Retrieve an order with id [%s]", order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )
        return order.serialize(), status.HTTP_200_OK

    @api.doc("update_orders")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(create_order_model)
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Update an Order based on its id"""
        app.logger.info("Request to update order with id: %s", order_id)
        check_content_type("application/json")

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        app.logger.debug("Payload = %s", api.payload)
        order.deserialize(api.payload)
        order.id = order_id
        order.update()

        return order.serialize(), status.HTTP_200_OK

    @api.doc("delete_orders")
    @api.response(204, "Order deleted")
    def delete(self, order_id):
        """Delete an Order based on the id specified in the path"""
        app.logger.info("Request to delete order with id: %s", order_id)

        order = Order.find(order_id)
        if order:
            order.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  O R D E R   C A N C E L   A C T I O N   ( /orders/<order_id>/cancel )
######################################################################
@api.route("/orders/<int:order_id>/cancel")
@api.param("order_id", "The Order identifier")
class OrderCancelResource(Resource):
    """Handles cancelling an Order"""

    @api.doc("cancel_order")
    @api.response(404, "Order not found")
    @api.response(409, "The Order is already cancelled")
    @api.marshal_with(order_model)
    def put(self, order_id):
        """Cancel an Order based on its id"""
        app.logger.info("Request to cancel order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        if order.status == "cancelled":
            abort(
                status.HTTP_409_CONFLICT,
                f"Order with id '{order_id}' is already cancelled.",
            )

        order.status = "cancelled"
        order.update()

        return order.serialize(), status.HTTP_200_OK


######################################################################
#  O R D E R   I T E M   C O L L E C T I O N   ( /orders/<order_id>/items )
######################################################################
@api.route("/orders/<int:order_id>/items")
@api.param("order_id", "The Order identifier")
class OrderItemCollection(Resource):
    """Handles listing all Items in an Order and adding a new Item"""

    @api.doc("list_order_items")
    @api.response(404, "Order not found")
    @api.marshal_list_with(item_model)
    def get(self, order_id):
        """List all items in an Order"""
        app.logger.info("Request to list items for order %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        results = [item.serialize() for item in order.items]
        app.logger.info("Returning %d items for order %s", len(results), order_id)
        return results, status.HTTP_200_OK

    @api.doc("add_order_item")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(create_item_model)
    @api.marshal_with(item_model, code=201)
    def post(self, order_id):
        """Add an item to an existing Order"""
        app.logger.info("Requesting to add an item to an order...")
        check_content_type("application/json")

        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, "Order not found")

        app.logger.debug("Payload = %s", api.payload)
        order_item = OrderItem()
        order_item.deserialize(api.payload)

        order.items.append(order_item)
        order.update()

        app.logger.info("Item added to order [%s]", order.id)

        location_url = api.url_for(
            OrderItemResource, order_id=order_id, item_id=order_item.id, _external=True
        )
        return (
            order_item.serialize(),
            status.HTTP_201_CREATED,
            {"Location": location_url},
        )


######################################################################
#  O R D E R   I T E M   R E S O U R C E   ( /orders/<order_id>/items/<item_id> )
######################################################################
@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class OrderItemResource(Resource):
    """Handles Read, Update, and Delete for a single Item in an Order"""

    @api.doc("get_order_item")
    @api.response(404, "Order or Item not found")
    @api.marshal_with(item_model)
    def get(self, order_id, item_id):
        """Retrieve a single Item from an Order"""
        app.logger.info("Request to retrieve item %s for order %s", item_id, order_id)
        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )
        item = OrderItem.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
        return item.serialize(), status.HTTP_200_OK

    @api.doc("update_order_item")
    @api.response(404, "Order or Item not found")
    @api.response(400, "The posted Item data was not valid")
    @api.expect(create_item_model)
    @api.marshal_list_with(item_model)
    def put(self, order_id, item_id):
        """Update an Item belonging to an existing Order"""
        app.logger.info("Request to update item %s for order %s", item_id, order_id)
        check_content_type("application/json")

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        item = OrderItem.find(item_id)
        if not item or item.order_id != order.id:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")

        app.logger.debug("Payload = %s", api.payload)
        item.deserialize(api.payload)
        item.id = item_id
        item.order_id = order_id
        item.update()

        app.logger.info("Item %s updated for order %s", item_id, order_id)
        results = [order_item.serialize() for order_item in order.items]
        return results, status.HTTP_200_OK

    @api.doc("delete_order_item")
    @api.response(204, "Item deleted")
    def delete(self, order_id, item_id):
        """Delete an Item from an Order"""
        app.logger.info("Request to delete item %s from order %s", item_id, order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Order with id '{order_id}' was not found.",
            )

        item = OrderItem.find(item_id)
        if item:
            item.delete()

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str) -> NoReturn:
    """Logs errors before aborting, matching the RESTX error response shape"""
    app.logger.error(message)
    api.abort(
        error_code,
        message,
        status=error_code,
        error=_error_name(error_code),
    )


def _error_name(error_code: int) -> str:
    """Return the standard HTTP reason phrase for a status code"""
    return HTTPStatus(error_code).phrase


@api.errorhandler(DataValidationError)
def handle_validation_error(error):
    """
    Handles DataValidationError as a 400 Bad Request.

    Flask-RESTX intercepts exceptions raised inside Resource methods before
    Flask's own @app.errorhandler gets a chance, so this needs its own
    handler registered on `api`, not on `app`.
    """
    message = str(error)
    app.logger.warning(message)
    return {
        "status": status.HTTP_400_BAD_REQUEST,
        "error": "Bad Request",
        "message": message,
    }, status.HTTP_400_BAD_REQUEST


@api.errorhandler(HTTPException)
def handle_http_exception(error):
    """Handles HTTP errors as JSON using the service error response shape"""
    error_code = getattr(error, "code", status.HTTP_500_INTERNAL_SERVER_ERROR)
    data = getattr(error, "data", {}) or {}
    message = data.get("message", getattr(error, "description", str(error)))
    app.logger.warning(message)
    return {
        "status": error_code,
        "error": _error_name(error_code),
        "message": message,
    }, error_code
