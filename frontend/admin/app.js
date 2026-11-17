let vouchers = [
    {
        id: 1,
        code: "BITEWELCOME",
        discountType: "PERCENT",
        discountValue: 20,
        startDate: "2026-01-01",
        endDate: "2027-01-01",
        status: "ACTIVE"
    },
    {
        id: 2,
        code: "SAIGON50K",
        discountType: "FIXED",
        discountValue: 50000,
        startDate: "2026-01-01",
        endDate: "2027-01-01",
        status: "ACTIVE"
    },
    {
        id: 3,
        code: "FREESHIPD1",
        discountType: "FIXED",
        discountValue: 25000,
        startDate: "2026-01-01",
        endDate: "2027-01-01",
        status: "ACTIVE"
    },
    {
        id: 4,
        code: "TET2026",
        discountType: "FIXED",
        discountValue: 50000,
        startDate: "2026-01-01",
        endDate: "2026-02-28",
        status: "EXPIRED"
    }
];

let currentFilter = "ALL";
let editingVoucherId = null;


const voucherTableBody = document.getElementById("voucherTableBody");
const voucherCount = document.getElementById("voucherCount");
const voucherSearch = document.getElementById("voucherSearch");

const voucherModal = document.getElementById("voucherModal");
const voucherForm = document.getElementById("voucherForm");
const modalTitle = document.getElementById("modalTitle");

const createVoucherButton = document.getElementById("createVoucherButton");
const closeVoucherModal = document.getElementById("closeVoucherModal");
const cancelVoucherButton = document.getElementById("cancelVoucherButton");


function formatDiscount(voucher) {
    if (voucher.discountType === "PERCENT") {
        return `${voucher.discountValue}%`;
    }

    return `${Number(voucher.discountValue).toLocaleString("en-US")} VND`;
}

function formatDate(dateString) {
    if (!dateString) return "-";

    const date = new Date(`${dateString}T00:00:00`);

    return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}

function getStatusClass(status) {
    switch (status) {
        case "ACTIVE":
            return "status-active";

        case "EXPIRED":
            return "status-expired";

        case "ARCHIVED":
            return "status-archived";

        default:
            return "";
    }
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => {
        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[character];
    });
}


function renderVouchers() {
    const keyword = voucherSearch.value.trim().toLowerCase();

    let filteredVouchers = vouchers.filter(voucher => {
        const matchesFilter =
            currentFilter === "ALL" ||
            voucher.status === currentFilter;

        const matchesSearch =
            voucher.code.toLowerCase().includes(keyword);

        return matchesFilter && matchesSearch;
    });

    if (filteredVouchers.length === 0) {
        voucherTableBody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-table-message">
                    No vouchers found.
                </td>
            </tr>
        `;
    } else {
        voucherTableBody.innerHTML = filteredVouchers.map(voucher => {
            const canArchive = voucher.status !== "ARCHIVED";
            const canEdit = voucher.status !== "ARCHIVED";

            return `
                <tr>
                    <td>
                        <span class="voucher-code">
                            ${escapeHTML(voucher.code)}
                        </span>
                    </td>

                    <td>${formatDiscount(voucher)}</td>

                    <td>${formatDate(voucher.startDate)}</td>

                    <td>${formatDate(voucher.endDate)}</td>

                    <td>
                        <span class="status-badge ${getStatusClass(voucher.status)}">
                            ${voucher.status}
                        </span>
                    </td>

                    <td>
                        <div class="action-group">
                            <button
                                class="action-button"
                                data-action="edit"
                                data-id="${voucher.id}"
                                ${!canEdit ? "disabled" : ""}
                            >
                                Edit
                            </button>

                            <button
                                class="action-button archive"
                                data-action="archive"
                                data-id="${voucher.id}"
                                ${!canArchive ? "disabled" : ""}
                            >
                                Archive
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");
    }

    voucherCount.textContent =
        `${filteredVouchers.length} voucher${filteredVouchers.length !== 1 ? "s" : ""}`;
}


document.getElementById("voucherFilters").addEventListener("click", event => {
    const button = event.target.closest("[data-filter]");

    if (!button) return;

    currentFilter = button.dataset.filter;

    document.querySelectorAll(".filter-tab").forEach(tab => {
        tab.classList.remove("active");
    });

    button.classList.add("active");

    renderVouchers();
});

voucherSearch.addEventListener("input", renderVouchers);


function openVoucherModal(voucher = null) {
    voucherForm.reset();

    editingVoucherId = voucher ? voucher.id : null;

    document.getElementById("voucherId").value =
        voucher ? voucher.id : "";

    if (voucher) {
        modalTitle.textContent = "Edit Voucher";

        document.getElementById("voucherCode").value = voucher.code;
        document.getElementById("discountType").value = voucher.discountType;
        document.getElementById("discountValue").value = voucher.discountValue;
        document.getElementById("voucherStartDate").value = voucher.startDate;
        document.getElementById("voucherEndDate").value = voucher.endDate;
    } else {
        modalTitle.textContent = "Create Voucher";
    }

    voucherModal.classList.remove("hidden");
}

function closeModal() {
    voucherModal.classList.add("hidden");
    voucherForm.reset();
    editingVoucherId = null;
}

createVoucherButton.addEventListener("click", () => {
    openVoucherModal();
});

closeVoucherModal.addEventListener("click", closeModal);

cancelVoucherButton.addEventListener("click", closeModal);

voucherModal.addEventListener("click", event => {
    if (event.target === voucherModal) {
        closeModal();
    }
});


voucherForm.addEventListener("submit", event => {
    event.preventDefault();

    const code = document.getElementById("voucherCode").value
        .trim()
        .toUpperCase();

    const discountType = document.getElementById("discountType").value;

    const discountValue = Number(
        document.getElementById("discountValue").value
    );

    const startDate = document.getElementById("voucherStartDate").value;
    const endDate = document.getElementById("voucherEndDate").value;

    if (!code) {
        alert("Please enter a voucher code.");
        return;
    }

    if (!Number.isFinite(discountValue) || discountValue <= 0) {
        alert("Discount value must be greater than zero.");
        return;
    }

    if (discountType === "PERCENT" && discountValue > 100) {
        alert("Percentage discount cannot exceed 100%.");
        return;
    }

    if (startDate && endDate && endDate < startDate) {
        alert("End date cannot be earlier than start date.");
        return;
    }

    const duplicate = vouchers.some(voucher => {
        return voucher.code.toLowerCase() === code.toLowerCase() &&
            voucher.id !== editingVoucherId &&
            voucher.status !== "ARCHIVED";
    });

    if (duplicate) {
        alert("This voucher code already exists.");
        return;
    }

    if (editingVoucherId !== null) {
        const voucher = vouchers.find(
            item => item.id === editingVoucherId
        );

        if (!voucher) return;

        voucher.code = code;
        voucher.discountType = discountType;
        voucher.discountValue = discountValue;
        voucher.startDate = startDate;
        voucher.endDate = endDate;

        alert("Voucher updated successfully!");
    } else {
        const newVoucher = {
            id: Date.now(),
            code,
            discountType,
            discountValue,
            startDate,
            endDate,
            status: "ACTIVE"
        };

        vouchers.push(newVoucher);

        alert("Voucher created successfully!");
    }

    closeModal();
    renderVouchers();
});


voucherTableBody.addEventListener("click", event => {
    const button = event.target.closest("[data-action]");

    if (!button || button.disabled) return;

    const id = Number(button.dataset.id);
    const action = button.dataset.action;

    const voucher = vouchers.find(item => item.id === id);

    if (!voucher) return;

    if (action === "edit") {
        openVoucherModal(voucher);
    }

    if (action === "archive") {
        const confirmed = confirm(
            `Are you sure you want to archive voucher "${voucher.code}"?`
        );

        if (!confirmed) return;

        voucher.status = "ARCHIVED";

        renderVouchers();

        alert("Voucher archived successfully!");
    }
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


renderVouchers();
