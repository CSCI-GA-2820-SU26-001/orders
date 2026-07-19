"use strict";

const createOrderForm = document.querySelector("#create-order-form");
const createCustomerIdInput = document.querySelector("#create-customer-id");
const orderStatusInput = document.querySelector("#order-status");
const createOrderButton = document.querySelector("#create-order-btn");
const ordersTableBody = document.querySelector("#orders-table-body");
const ordersMessage = document.querySelector("#orders-message");

const listItemsForm = document.querySelector("#list-items-form");
const orderIdInput = document.querySelector("#order-id");
const itemsTableBody = document.querySelector("#items-table-body");
const itemsMessage = document.querySelector("#items-message");
const listItemsButton = document.querySelector("#list-items-btn");

function setOrdersMessage(message, isError = false) {
  ordersMessage.textContent = message;
  ordersMessage.classList.toggle("error", isError);
}

function setItemsMessage(message, isError = false) {
  itemsMessage.textContent = message;
  itemsMessage.classList.toggle("error", isError);
}

function clearOrdersTable() {
  ordersTableBody.replaceChildren();
}

function clearItemsTable() {
  itemsTableBody.replaceChildren();
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

function appendItemRow(item) {
  const row = document.createElement("tr");
  const values = [item.id, item.name ?? "", item.quantity ?? ""];

  values.forEach((value) => {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    row.appendChild(cell);
  });

  itemsTableBody.appendChild(row);
}

async function errorMessage(response) {
  try {
    const error = await response.json();
    return error.message || `Unable to process request (${response.status}).`;
  } catch (_error) {
    return `Unable to process request (${response.status}).`;
  }
}

async function loadOrders() {
  clearOrdersTable();
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

    if (orders.length === 0) {
      setOrdersMessage("No orders found.");
    } else {
      setOrdersMessage(`${orders.length} order(s) loaded.`);
    }
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

    await loadOrders();
    setOrdersMessage(`Order ${order.id} created successfully.`);
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
  } finally {
    createOrderButton.disabled = false;
  }
}

async function listItems(orderId) {
  clearItemsTable();
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

    if (items.length === 0) {
      setItemsMessage("This order has no items.");
    } else {
      setItemsMessage(`${items.length} item(s) found.`);
    }
  } catch (_error) {
    setItemsMessage("Unable to reach the Orders service.", true);
  } finally {
    listItemsButton.disabled = false;
  }
}

createOrderForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!createCustomerIdInput.checkValidity()) {
    createCustomerIdInput.reportValidity();
    return;
  }

  createOrder(createCustomerIdInput.value, orderStatusInput.value);
});

listItemsForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!orderIdInput.checkValidity()) {
    orderIdInput.reportValidity();
    return;
  }

  listItems(orderIdInput.value);
});

loadOrders();