const voucherTableBody = document.getElementById("voucherTableBody");
const voucherCountSummary = document.getElementById("voucherCountSummary");
const voucherSearchInput = document.getElementById("voucherSearchInput");
const statusTabs = document.getElementById("statusTabs");
const modal = document.getElementById("createVoucherModal");
const form = document.getElementById("createVoucherForm");
const modalTitle = document.getElementById("modalTitle");
const saveButton = document.getElementById("saveVoucherButton");
let currentFilter = "ALL";
let searchQuery = "";
let vouchers = [];

function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[char]);
}

function renderVouchers() {
    const filtered = vouchers.filter(v =>
        (currentFilter === "ALL" || v.status === currentFilter) &&
        `${v.code} ${v.hub}`.toLowerCase().includes(searchQuery)
    );
    if (!filtered.length) {
        voucherTableBody.innerHTML = '<tr><td colspan="6" class="empty-table-message">No matching vouchers found.</td></tr>';
        voucherCountSummary.textContent = "Showing 0 vouchers";
        return;
    }
    voucherTableBody.innerHTML = filtered.map(v => {
        const canEdit = ["ACTIVE", "EXPIRED"].includes(v.status);
        const canArchive = ["ACTIVE", "EXPIRED"].includes(v.status);
        return `<tr>
          <td><div class="code-cell"><span class="code-primary">${escapeHtml(v.code)}</span><span class="code-sub">${escapeHtml(v.hub)}</span></div></td>
          <td class="discount-cell">${escapeHtml(v.discount)}</td><td>${escapeHtml(v.min_order)}</td>
          <td><div class="period-cell"><span>${escapeHtml(v.valid_from)}</span><span>${escapeHtml(v.valid_to)}</span></div></td>
          <td><span class="status-badge status-${escapeHtml(v.status)}">${escapeHtml(v.status)}</span></td>
          <td class="action-cell">
            <button type="button" class="edit-btn" data-edit="${v.id}" ${canEdit ? "" : "disabled"}>Edit</button>
            <button type="button" class="archive-btn" data-archive="${v.id}" ${canArchive ? "" : "disabled"}>Archive</button>
          </td></tr>`;
    }).join("");
    voucherCountSummary.textContent = `Showing ${filtered.length} of ${vouchers.length} vouchers`;
}

async function loadVouchers() {
    const response = await fetch("/api/vouchers", { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Unable to load vouchers (${response.status}).`);
    vouchers = await response.json();
    renderVouchers();
}

function openModal(voucher = null) {
    form.reset();
    document.getElementById("editingVoucherId").value = voucher ? voucher.id : "";
    modalTitle.textContent = voucher ? "Update Voucher" : "Create New Voucher";
    saveButton.textContent = voucher ? "Save Changes" : "Create Voucher";
    if (voucher) {
        document.getElementById("newCode").value = voucher.code;
        document.getElementById("newDiscount").value = voucher.discount;
        document.getElementById("newMinOrder").value = String(Number(voucher.min_order.replace(/[^0-9]/g, "")) || 0);
        document.getElementById("newStartDate").value = voucher.start_date;
        document.getElementById("newEndDate").value = voucher.end_date;
    } else {
        const today = new Date().toISOString().slice(0, 10);
        document.getElementById("newStartDate").value = today;
        document.getElementById("newEndDate").value = today;
    }
    modal.classList.remove("hidden");
}

function closeModal() {
    modal.classList.add("hidden");
    form.reset();
}

document.getElementById("openCreateModalButton").addEventListener("click", () => openModal());
document.getElementById("closeModalButton").addEventListener("click", closeModal);
document.getElementById("cancelModalButton").addEventListener("click", closeModal);
modal.addEventListener("click", event => { if (event.target === modal) closeModal(); });

statusTabs.addEventListener("click", event => {
    const button = event.target.closest(".tab-pill");
    if (!button) return;
    statusTabs.querySelectorAll(".tab-pill").forEach(item => item.classList.remove("active"));
    button.classList.add("active");
    currentFilter = button.dataset.status;
    renderVouchers();
});
voucherSearchInput.addEventListener("input", event => {
    searchQuery = event.target.value.trim().toLowerCase();
    renderVouchers();
});

voucherTableBody.addEventListener("click", async event => {
    const editButton = event.target.closest("[data-edit]");
    const archiveButton = event.target.closest("[data-archive]");
    if (editButton && !editButton.disabled) {
        const voucher = vouchers.find(item => item.id === Number(editButton.dataset.edit));
        if (voucher) openModal(voucher);
        return;
    }
    if (archiveButton && !archiveButton.disabled) {
        if (!confirm("Archive this voucher?")) return;
        const id = Number(archiveButton.dataset.archive);
        const response = await fetch(`/api/vouchers/${id}/archive`, {
            method: "PATCH", credentials: "same-origin"
        });
        const body = await response.json();
        if (!response.ok) { alert(body.detail || "Unable to archive voucher."); return; }
        const index = vouchers.findIndex(item => item.id === id);
        if (index >= 0) vouchers[index] = body;
        renderVouchers();
    }
});

form.addEventListener("submit", async event => {
    event.preventDefault();
    const id = document.getElementById("editingVoucherId").value;
    const payload = {
        code: document.getElementById("newCode").value.trim().toUpperCase(),
        discount: document.getElementById("newDiscount").value.trim(),
        min_order: Number(document.getElementById("newMinOrder").value || 0),
        start_date: document.getElementById("newStartDate").value,
        end_date: document.getElementById("newEndDate").value
    };
    const response = await fetch(id ? `/api/vouchers/${id}` : "/api/vouchers", {
        method: id ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "same-origin",
        body: JSON.stringify(payload)
    });
    const body = await response.json();
    if (!response.ok) { alert(body.detail || "Unable to save voucher."); return; }
    closeModal();
    await loadVouchers();
});


const vouchersPage = document.getElementById("vouchersPage");
const deliveriesPage = document.getElementById("deliveriesPage");
const readyOrdersTableBody = document.getElementById("readyOrdersTableBody");
const readyOrdersCount = document.getElementById("readyOrdersCount");
const refreshReadyOrdersButton = document.getElementById("refreshReadyOrdersButton");

function showAdminPage(page) {
    const isDeliveries = page === "deliveries";

    vouchersPage.classList.toggle("hidden", isDeliveries);
    deliveriesPage.classList.toggle("hidden", !isDeliveries);

    document.querySelectorAll(".nav-item").forEach(item => {
        const active = item.dataset.nav === page;
        item.classList.toggle("active", active);
    });

    if (isDeliveries) {
        loadReadyOrders();
    }
}

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", event => {
        event.preventDefault();
        showAdminPage(item.dataset.nav);
    });
});

function renderReadyOrders(orders) {
    if (!orders.length) {
        readyOrdersTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-table-message">
                    No READY orders available.
                </td>
            </tr>`;
        readyOrdersCount.textContent = "Showing 0 orders";
        return;
    }

    readyOrdersTableBody.innerHTML = orders.map(order => `
        <tr>
            <td>#${order.id}</td>
            <td>
                <div class="code-cell">
                    <span class="code-primary">${escapeHtml(order.customer_name)}</span>
                    <span class="code-sub">${escapeHtml(order.customer_phone)}</span>
                </div>
            </td>
            <td>${escapeHtml(order.hub_name)}</td>
            <td>${escapeHtml(order.delivery_address)}</td>
            <td>${Number(order.total).toLocaleString("en-US")} VND</td>
            <td><span class="status-badge status-ACTIVE">READY</span></td>
            <td class="action-cell">
                <button
                    type="button"
                    class="deliver-btn"
                    data-deliver="${order.id}">
                    Mark Delivered
                </button>
            </td>
        </tr>
    `).join("");

    readyOrdersCount.textContent = `Showing ${orders.length} READY orders`;
}

async function loadReadyOrders() {
    readyOrdersTableBody.innerHTML = `
        <tr>
            <td colspan="7" class="empty-table-message">Loading orders...</td>
        </tr>`;
    readyOrdersCount.textContent = "Loading orders...";

    try {
        const response = await fetch("/api/admin/orders/ready", {
            credentials: "same-origin"
        });

        const body = await response.json();

        if (!response.ok) {
            throw new Error(body.detail || "Unable to load READY orders.");
        }

        renderReadyOrders(body);
    } catch (error) {
        readyOrdersTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-table-message">
                    ${escapeHtml(error.message)}
                </td>
            </tr>`;
        readyOrdersCount.textContent = "Unable to load orders";
    }
}

readyOrdersTableBody.addEventListener("click", async event => {
    const button = event.target.closest("[data-deliver]");
    if (!button || button.disabled) return;

    const orderId = Number(button.dataset.deliver);

    if (!confirm(`Confirm that order #${orderId} has been delivered?`)) {
        return;
    }

    button.disabled = true;
    button.textContent = "Processing...";

    try {
        const response = await fetch(
            `/api/admin/orders/${orderId}/deliver`,
            {
                method: "PATCH",
                credentials: "same-origin"
            }
        );

        const body = await response.json();

        if (!response.ok) {
            throw new Error(body.detail || "Unable to mark order as delivered.");
        }

        alert(`Order #${orderId} has been marked as DELIVERED.`);
        await loadReadyOrders();
    } catch (error) {
        alert(error.message);
        button.disabled = false;
        button.textContent = "Mark Delivered";
    }
});

refreshReadyOrdersButton.addEventListener("click", loadReadyOrders);

document.getElementById("logoutButton").addEventListener("click", async () => {
    try { await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" }); }
    finally { window.location.assign("/"); }
});

loadVouchers().catch(error => {
    voucherTableBody.innerHTML = `<tr><td colspan="6" class="empty-table-message">${escapeHtml(error.message)}</td></tr>`;
    voucherCountSummary.textContent = "Unable to load vouchers";
});
