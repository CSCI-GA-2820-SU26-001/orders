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
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


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
