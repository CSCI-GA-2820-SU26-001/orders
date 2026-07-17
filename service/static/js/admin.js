"use strict";

const listItemsForm = document.querySelector("#list-items-form");
const orderIdInput = document.querySelector("#order-id");
const itemsTableBody = document.querySelector("#items-table-body");
const itemsMessage = document.querySelector("#items-message");
const listItemsButton = document.querySelector("#list-items-btn");

function clearItems() {
  itemsTableBody.replaceChildren();
}

function setMessage(message, isError = false) {
  itemsMessage.textContent = message;
  itemsMessage.classList.toggle("error", isError);
}

function displayName(item) {
  // The current Orders API identifies products by product_id. Supporting name
  // here also makes the UI compatible if the API later exposes a product name.
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

async function errorMessage(response) {
  try {
    const error = await response.json();
    return error.message || `Unable to list items (${response.status}).`;
  } catch (_error) {
    return `Unable to list items (${response.status}).`;
  }
}

async function listItems(orderId) {
  clearItems();
  setMessage("Loading items…");
  listItemsButton.disabled = true;

  try {
    const response = await fetch(`/api/orders/${orderId}/items`, {
      headers: { Accept: "application/json" },
    });

    if (!response.ok) {
      setMessage(await errorMessage(response), true);
      return;
    }

    const items = await response.json();
    items.forEach(appendItemRow);
    setMessage(items.length === 0 ? "This order has no items." : `${items.length} item(s) found.`);
  } catch (_error) {
    setMessage("Unable to reach the Orders service.", true);
  } finally {
    listItemsButton.disabled = false;
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
