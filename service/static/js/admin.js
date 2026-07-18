"use strict";

const listItemsForm = document.querySelector("#list-items-form");
const orderIdInput = document.querySelector("#order-id");
const itemsTableBody = document.querySelector("#items-table-body");
const itemsMessage = document.querySelector("#items-message");
const listItemsButton = document.querySelector("#list-items-btn");

const createOrderForm = document.querySelector("#create-order-form");
const createCustomerIdInput = document.querySelector("#create-customer-id");
const orderStatusInput = document.querySelector("#order-status");
const ordersTableBody = document.querySelector("#orders-table-body");
const ordersMessage = document.querySelector("#orders-message");
const createOrderButton = document.querySelector("#create-order-btn");

function clearItems() {
  itemsTableBody.replaceChildren();
}

function clearOrders() {
  ordersTableBody.replaceChildren();
}

function setItemsMessage(message, isError = false) {
  itemsMessage.textContent = message;
  itemsMessage.classList.toggle("error", isError);
}

function setOrdersMessage(message, isError = false) {
  ordersMessage.textContent = message;
  ordersMessage.classList.toggle("error", isError);
}

function displayName(item) {
  return item.name ?? item.product_name ?? item.product_id ?? "";
}

function appendItemRow(item) {
  const row = document.createElement("tr");
  const values = [item.id, displayName(item), item.quantity];

  values.forEach((value) => {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    row.appendChild(cell);
  });

  itemsTableBody.appendChild(row);
}

function appendOrderRow(order) {
  const row = document.createElement("tr");
  const values = [order.id, order.customer_id, order.status];

  values.forEach((value) => {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    row.appendChild(cell);
  });

  ordersTableBody.appendChild(row);
}

async function errorMessage(response) {
  try {
    const error = await response.json();
    return error.message || `Unable to process request (${response.status}).`;
  } catch (_error) {
    return `Unable to process request (${response.status}).`;
  }
}

async function listItems(orderId) {
  clearItems();
  setItemsMessage("Loading items…");
  listItemsButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/items`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setItemsMessage(await errorMessage(response), true);
      return;
    }

    const items = await response.json();
    items.forEach(appendItemRow);
    setItemsMessage(
      items.length === 0 ? "This order has no items." : `${items.length} item(s) found.`
    );
  } catch (_error) {
    setItemsMessage("Unable to reach the Orders service.", true);
  } finally {
    listItemsButton.disabled = false;
  }
}

async function loadOrders() {
  clearOrders();
  setOrdersMessage("Loading orders…");

  try {
    const response = await fetch("/api/orders", {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setOrdersMessage(await errorMessage(response), true);
      return;
    }

    const orders = await response.json();
    orders.forEach(appendOrderRow);
    setOrdersMessage(
      orders.length === 0 ? "No orders yet." : `${orders.length} order(s) found.`
    );
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
  }
}

async function createOrder(customerId, status) {
  setOrdersMessage("Creating order…");
  createOrderButton.disabled = true;

  try {
    const response = await fetch("/api/orders", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        customer_id: Number(customerId),
        status: status || "open",
      }),
    });

    const order = await response.json();

    if (!response.ok) {
      setOrdersMessage(order.message || `Unable to create order (${response.status}).`, true);
      return;
    }

    appendOrderRow(order);
    setOrdersMessage(`Order ${order.id} created successfully.`);
    createOrderForm.reset();
    orderStatusInput.value = "open";
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
  } finally {
    createOrderButton.disabled = false;
  }
}

listItemsForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!orderIdInput.checkValidity()) {
    orderIdInput.reportValidity();
    return;
  }

  listItems(orderIdInput.value);
});

createOrderForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!createCustomerIdInput.checkValidity()) {
    createCustomerIdInput.reportValidity();
    return;
  }

  createOrder(createCustomerIdInput.value, orderStatusInput.value);
});

loadOrders();