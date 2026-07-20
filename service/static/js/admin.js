"use strict";

const createOrderForm = document.querySelector("#create-order-form");
const createCustomerIdInput = document.querySelector("#create-customer-id");
const orderStatusInput = document.querySelector("#order-status");
const createOrderButton = document.querySelector("#create-order-btn");
const ordersTableBody = document.querySelector("#orders-table-body");
const ordersMessage = document.querySelector("#orders-message");
const searchOrdersForm = document.querySelector("#search-orders-form");
const searchOrderStatusInput = document.querySelector("#search-order-status");
const searchOrdersButton = document.querySelector("#search-orders-btn");

const readOrderForm = document.querySelector("#read-order-form");
const readOrderIdInput = document.querySelector("#read-order-id");
const readOrderButton = document.querySelector("#read-order-btn");
const readOrderDetails = document.querySelector("#read-order-details");
const readOrderMessage = document.querySelector("#read-order-message");

const updateOrderForm = document.querySelector("#update-order-form");
const updateOrderIdInput = document.querySelector("#update-order-id");
const updateCustomerIdInput = document.querySelector("#update-customer-id");
const updateOrderStatusInput = document.querySelector("#update-order-status");
const updateOrderButton = document.querySelector("#update-order-btn");
const updateOrderMessage = document.querySelector("#update-order-message");

const readItemForm = document.querySelector("#read-item-form");
const readItemOrderIdInput = document.querySelector("#read-item-order-id");
const readItemItemIdInput = document.querySelector("#read-item-item-id");
const readItemButton = document.querySelector("#read-item-btn");
const readItemDetails = document.querySelector("#read-item-details");
const readItemMessage = document.querySelector("#read-item-message");

const addItemForm = document.querySelector("#add-item-form");
const addItemOrderIdInput = document.querySelector("#add-item-order-id");
const addItemProductIdInput = document.querySelector("#add-item-product-id");
const addItemQuantityInput = document.querySelector("#add-item-quantity");
const addItemPriceInput = document.querySelector("#add-item-price");
const addItemButton = document.querySelector("#add-item-btn");
const addItemMessage = document.querySelector("#add-item-message");

const listItemsForm = document.querySelector("#list-items-form");
const orderIdInput = document.querySelector("#order-id");
const itemsTableBody = document.querySelector("#items-table-body");
const itemsMessage = document.querySelector("#items-message");
const listItemsButton = document.querySelector("#list-items-btn");

const deleteItemForm = document.querySelector("#delete-item-form");
const deleteItemOrderIdInput = document.querySelector("#delete-item-order-id");
const deleteItemIdInput = document.querySelector("#delete-item-id");
const deleteItemButton = document.querySelector("#delete-item-btn");
const deleteItemMessage = document.querySelector("#delete-item-message");

function setOrdersMessage(message, isError = false) {
  ordersMessage.textContent = message;
  ordersMessage.classList.toggle("error", isError);
}

function setItemsMessage(message, isError = false) {
  itemsMessage.textContent = message;
  itemsMessage.classList.toggle("error", isError);
}

function setReadOrderMessage(message, isError = false) {
  readOrderMessage.textContent = message;
  readOrderMessage.classList.toggle("error", isError);
}

function setUpdateOrderMessage(message, isError = false) {
  updateOrderMessage.textContent = message;
  updateOrderMessage.classList.toggle("error", isError);
}

function setAddItemMessage(message, isError = false) {
  addItemMessage.textContent = message;
  addItemMessage.classList.toggle("error", isError);
}

function setDeleteItemMessage(message, isError = false) {
  deleteItemMessage.textContent = message;
  deleteItemMessage.classList.toggle("error", isError);
}

function clearOrdersTable() {
  ordersTableBody.replaceChildren();
}

function clearItemsTable() {
  itemsTableBody.replaceChildren();
}

function clearReadOrderDetails() {
  readOrderDetails.replaceChildren();
}

function setReadItemMessage(message, isError = false) {
  readItemMessage.textContent = message;
  readItemMessage.classList.toggle("error", isError);
}

function clearReadItemDetails() {
  readItemDetails.replaceChildren();
}

function renderReadItemDetails(item) {
  clearReadItemDetails();

  const card = document.createElement("div");
  card.className = "read-order-card";

  const fields = [
    ["Item ID", item.id],
    ["Order ID", item.order_id],
    ["Product ID", item.product_id],
    ["Quantity", item.quantity],
    ["Price", item.price],
  ];

  fields.forEach(([label, value]) => {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    paragraph.appendChild(strong);
    paragraph.appendChild(document.createTextNode(value ?? ""));
    card.appendChild(paragraph);
  });

  readItemDetails.appendChild(card);
}

function appendOrderRow(order) {
  const row = document.createElement("tr");
  const values = [order.id, order.customer_id, order.status];

  values.forEach((value) => {
    const cell = document.createElement("td");
    cell.textContent = value ?? "";
    row.appendChild(cell);
  });

  const actionsCell = document.createElement("td");
  actionsCell.className = "order-actions";

  if (order.status !== "cancelled") {
    const cancelButton = document.createElement("button");
    cancelButton.type = "button";
    cancelButton.className = "cancel-order-btn";
    cancelButton.textContent = "Cancel Order";
    cancelButton.setAttribute("aria-label", `Cancel order ${order.id}`);
    cancelButton.addEventListener("click", () => {
      cancelOrder(order.id, row.cells[2], cancelButton);
    });
    actionsCell.appendChild(cancelButton);
  }

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "delete-order-btn";
  deleteButton.textContent = "Delete";
  deleteButton.setAttribute("aria-label", `Delete order ${order.id}`);
  deleteButton.addEventListener("click", () => {
    deleteOrder(order.id, row, deleteButton);
  });
  actionsCell.appendChild(deleteButton);

  row.appendChild(actionsCell);

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

function renderReadOrderDetails(order, errorMessage = "") {
  clearReadOrderDetails();

  if (errorMessage) {
    const message = document.createElement("p");
    message.className = "message error";
    message.textContent = errorMessage;
    readOrderDetails.appendChild(message);
    return;
  }

  if (!order) {
    return;
  }

  const card = document.createElement("div");
  card.className = "read-order-card";

  const fields = [
    ["Order ID", order.id],
    ["Customer ID", order.customer_id],
    ["Status", order.status],
  ];

  fields.forEach(([label, value]) => {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");
    strong.textContent = `${label}: `;
    paragraph.appendChild(strong);
    paragraph.appendChild(document.createTextNode(value ?? ""));
    card.appendChild(paragraph);
  });

  readOrderDetails.appendChild(card);
}

async function errorMessage(response) {
  try {
    const error = await response.json();
    return error.message || `Unable to process request (${response.status}).`;
  } catch (_error) {
    return `Unable to process request (${response.status}).`;
  }
}

async function loadOrders(status = searchOrderStatusInput.value) {
  clearOrdersTable();
  setOrdersMessage("Searching orders…");
  searchOrdersButton.disabled = true;

  try {
    const url = status
      ? `/api/orders?status=${encodeURIComponent(status)}`
      : "/api/orders";
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setOrdersMessage(await errorMessage(response), true);
      return;
    }

    const orders = await response.json();
    orders.forEach(appendOrderRow);

    if (orders.length === 0 && status) {
      setOrdersMessage(`No orders found with status "${status}".`);
    } else if (orders.length === 0) {
      setOrdersMessage("No orders found.");
    } else {
      setOrdersMessage(`${orders.length} order(s) loaded.`);
    }
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
  } finally {
    searchOrdersButton.disabled = false;
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

async function deleteOrder(orderId, row, deleteButton) {
  setOrdersMessage(`Deleting order ${orderId}…`);

  const actionButtons = row.querySelectorAll("button");
  actionButtons.forEach((button) => {
    button.disabled = true;
  });

  try {
    const response = await fetch(`/api/orders/${orderId}`, {
      method: "DELETE",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setOrdersMessage(await errorMessage(response), true);
      actionButtons.forEach((button) => {
        button.disabled = false;
      });
      return;
    }

    row.remove();
    setOrdersMessage(`Order ${orderId} deleted successfully.`);
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
    actionButtons.forEach((button) => {
      button.disabled = false;
    });
  } finally {
    deleteButton.disabled = false;
  }
}

async function cancelOrder(orderId, statusCell, cancelButton) {
  setOrdersMessage(`Cancelling order ${orderId}…`);
  cancelButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/cancel`, {
      method: "PUT",
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setOrdersMessage(await errorMessage(response), true);
      cancelButton.disabled = false;
      return;
    }

    const order = await response.json();
    statusCell.textContent = order.status;
    cancelButton.remove();
    setOrdersMessage(`Order ${order.id} cancelled successfully.`);
  } catch (_error) {
    setOrdersMessage("Unable to reach the Orders service.", true);
    cancelButton.disabled = false;
  }
}

async function readOrder(orderId) {
  clearReadOrderDetails();
  setReadOrderMessage("Reading order…");
  readOrderButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      setReadOrderMessage(errorPayload.message || `Unable to read order (${response.status}).`, true);
      return;
    }

    const order = await response.json();
    setReadOrderMessage(`Order ${order.id} loaded.`);
  } catch (_error) {
    setReadOrderMessage("Unable to reach the Orders service.", true);
  } finally {
    readOrderButton.disabled = false;
  }
}

async function updateOrder(orderId, customerId, status) {
  setUpdateOrderMessage("Updating order…");
  updateOrderButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        customer_id: Number(customerId),
        status: status,
      }),
    });

    const order = await response.json().catch(() => ({}));

    if (!response.ok) {
      setUpdateOrderMessage(order.message || `Unable to update order (${response.status}).`, true);
      return;
    }

    await loadOrders();
    setUpdateOrderMessage(`Order ${order.id} updated successfully.`);
  } catch (_error) {
    setUpdateOrderMessage("Unable to reach the Orders service.", true);
  } finally {
    updateOrderButton.disabled = false;
  }
}

async function readItem(orderId, itemId) {
  clearReadItemDetails();
  setReadItemMessage("Reading item…");
  readItemButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/items/${itemId}`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => ({}));
      setReadItemMessage(
        errorPayload.message || `Unable to read item (${response.status}).`,
        true
      );
      return;
    }

    const item = await response.json();
    renderReadItemDetails(item);
    setReadItemMessage(`Item ${item.id} loaded.`);
  } catch (_error) {
    setReadItemMessage("Unable to reach the Orders service.", true);
  } finally {
    readItemButton.disabled = false;
  }
}

async function addItem(orderId, productId, quantity, price) {
  setAddItemMessage("Adding item…");
  addItemButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/items`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        product_id: Number(productId),
        quantity: Number(quantity),
        price: Number(price),
      }),
    });

    const item = await response.json().catch(() => ({}));

    if (!response.ok) {
      setAddItemMessage(item.message || `Unable to add item (${response.status}).`, true);
      return;
    }

    setAddItemMessage(`Item ${item.id} added to order ${orderId} successfully.`);
  } catch (_error) {
    setAddItemMessage("Unable to reach the Orders service.", true);
  } finally {
    addItemButton.disabled = false;
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

async function deleteItem(orderId, itemId) {
  setDeleteItemMessage("Deleting item…");
  deleteItemButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/items/${itemId}`, {
      method: "DELETE",
    });

    if (!response.ok && response.status !== 204) {
      setDeleteItemMessage(await errorMessage(response), true);
      return;
    }

    setDeleteItemMessage(`Item ${itemId} deleted successfully.`);

    if (orderIdInput.value === String(orderId)) {
      await listItems(orderId);
    }
  } catch (_error) {
    setDeleteItemMessage("Unable to reach the Orders service.", true);
  } finally {
    deleteItemButton.disabled = false;
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

searchOrdersForm.addEventListener("submit", (event) => {
  event.preventDefault();
  loadOrders(searchOrderStatusInput.value);
});

readOrderForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!readOrderIdInput.checkValidity()) {
    readOrderIdInput.reportValidity();
    return;
  }

  readOrder(readOrderIdInput.value);
});

updateOrderForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!updateOrderIdInput.checkValidity() || !updateCustomerIdInput.checkValidity()) {
    updateOrderIdInput.reportValidity();
    updateCustomerIdInput.reportValidity();
    return;
  }

  updateOrder(updateOrderIdInput.value, updateCustomerIdInput.value, updateOrderStatusInput.value);
});

readItemForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!readItemOrderIdInput.checkValidity() || !readItemItemIdInput.checkValidity()) {
    readItemOrderIdInput.reportValidity();
    readItemItemIdInput.reportValidity();
    return;
  }

  readItem(readItemOrderIdInput.value, readItemItemIdInput.value);
});

addItemForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const inputs = [
    addItemOrderIdInput,
    addItemProductIdInput,
    addItemQuantityInput,
    addItemPriceInput,
  ];

  if (!inputs.every((input) => input.checkValidity())) {
    inputs.forEach((input) => input.reportValidity());
    return;
  }

  addItem(
    addItemOrderIdInput.value,
    addItemProductIdInput.value,
    addItemQuantityInput.value,
    addItemPriceInput.value
  );
});

listItemsForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!orderIdInput.checkValidity()) {
    orderIdInput.reportValidity();
    return;
  }

  listItems(orderIdInput.value);
});

deleteItemForm.addEventListener("submit", (event) => {
  event.preventDefault();

  if (!deleteItemOrderIdInput.checkValidity() || !deleteItemIdInput.checkValidity()) {
    deleteItemOrderIdInput.reportValidity();
    deleteItemIdInput.reportValidity();
    return;
  }

  deleteItem(deleteItemOrderIdInput.value, deleteItemIdInput.value);
});

loadOrders();
