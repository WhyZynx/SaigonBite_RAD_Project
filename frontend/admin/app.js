const voucherTableBody = document.getElementById("voucherTableBody");
const voucherCountSummary = document.getElementById("voucherCountSummary");
const voucherSearchInput = document.getElementById("voucherSearchInput");
const statusTabs = document.getElementById("statusTabs");

const createVoucherModal = document.getElementById("createVoucherModal");
const openCreateModalButton = document.getElementById("openCreateModalButton");
const closeModalButton = document.getElementById("closeModalButton");
const cancelModalButton = document.getElementById("cancelModalButton");
const createVoucherForm = document.getElementById("createVoucherForm");

let currentFilter = "ALL";
let searchQuery = "";
let vouchers = [];

function renderVouchers() {
    const filtered = vouchers.filter(v => {
        const matchesStatus = currentFilter === "ALL" || v.status === currentFilter;
        const matchesSearch =
            v.code.toLowerCase().includes(searchQuery) ||
            v.hub.toLowerCase().includes(searchQuery);
        return matchesStatus && matchesSearch;
    });

    if (filtered.length === 0) {
        voucherTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-table-message">No matching vouchers found.</td>
            </tr>
        `;
        voucherCountSummary.textContent = "Showing 0 of 0 vouchers";
        return;
    }

    voucherTableBody.innerHTML = filtered
        .map(v => {
            const isActive = v.status === "ACTIVE";
            return `
                <tr>
                    <td>
                        <div class="code-cell">
                            <span class="code-primary">${v.code}</span>
                            <span class="code-sub">${v.hub}</span>
                        </div>
                    </td>
                    <td class="discount-cell">${v.discount}</td>
                    <td>${v.min_order}</td>
                    <td>
                        <div class="period-cell">
                            <span>${v.valid_from}</span>
                            <span>${v.valid_to}</span>
                        </div>
                    </td>
                    <td>
                        <span class="status-badge status-${v.status}">${v.status}</span>
                    </td>
                    <td>
                        <button
                            type="button"
                            class="archive-btn ${isActive ? "enabled" : ""}"
                            data-id="${v.id}"
                            ${isActive ? "" : "disabled"}
                        >
                            Archive
                        </button>
                    </td>
                </tr>
            `;
        })
        .join("");

    voucherCountSummary.textContent = `Showing 1–${filtered.length} of ${filtered.length} vouchers`;
}

async function loadVouchers() {
    try {
        const response = await fetch("/api/vouchers", { credentials: "same-origin" });
        if (!response.ok) return;
        vouchers = await response.json();
        renderVouchers();
    } catch (error) {
        console.error("Failed to load vouchers:", error);
    }
}

statusTabs.addEventListener("click", event => {
    const btn = event.target.closest(".tab-pill");
    if (!btn) return;
    document.querySelectorAll(".tab-pill").forEach(el => el.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.getAttribute("data-status");
    renderVouchers();
});

voucherSearchInput.addEventListener("input", event => {
    searchQuery = event.target.value.trim().toLowerCase();
    renderVouchers();
});

voucherTableBody.addEventListener("click", async event => {
    const btn = event.target.closest(".archive-btn.enabled");
    if (!btn) return;
    const id = Number(btn.getAttribute("data-id"));

    try {
        const response = await fetch(`/api/vouchers/${id}/archive`, {
            method: "PATCH",
            credentials: "same-origin"
        });
        if (!response.ok) {
            const err = await response.json();
            alert(err.detail || "Unable to archive voucher.");
            return;
        }
        const updated = await response.json();
        const index = vouchers.findIndex(v => v.id === id);
        if (index !== -1) {
            vouchers[index] = updated;
        }
        renderVouchers();
    } catch (error) {
        console.error("Archive failed:", error);
    }
});

openCreateModalButton.addEventListener("click", () => {
    createVoucherModal.classList.remove("hidden");
});

function closeCreateModal() {
    createVoucherModal.classList.add("hidden");
    createVoucherForm.reset();
}

closeModalButton.addEventListener("click", closeCreateModal);
cancelModalButton.addEventListener("click", closeCreateModal);

createVoucherModal.addEventListener("click", event => {
    if (event.target === createVoucherModal) {
        closeCreateModal();
    }
});

createVoucherForm.addEventListener("submit", async event => {
    event.preventDefault();
    const payload = {
        code: document.getElementById("newCode").value.trim().toUpperCase(),
        hub: document.getElementById("newHub").value,
        discount: document.getElementById("newDiscount").value.trim(),
        min_order: Number(document.getElementById("newMinOrder").value || 0),
        start_date: document.getElementById("newStartDate").value,
        end_date: document.getElementById("newEndDate").value
    };

    try {
        const response = await fetch("/api/vouchers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        if (!response.ok) {
            alert(data.detail || "Unable to create voucher.");
            return;
        }
        vouchers.unshift(data);
        closeCreateModal();
        renderVouchers();
    } catch (error) {
        console.error("Create voucher failed:", error);
    }
});

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", event => {
        if (item.getAttribute("data-nav") !== "vouchers") {
            event.preventDefault();
        }
    });
});

document.getElementById("logoutButton").addEventListener("click", async () => {
    try {
        await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "same-origin"
        });
    } finally {
        window.location.assign("/");
    }
});

loadVouchers();