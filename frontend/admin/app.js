// SaigonBite Admin Portal — Manage Vouchers
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

const vouchers = [
    {
        id: 1,
        code: "BITEWELCOME",
        hub: "All hubs",
        discount: "20%",
        minOrder: "150,000 VND",
        validFrom: "01 Nov 2026 –",
        validTo: "31 Dec 2026",
        status: "ACTIVE"
    },
    {
        id: 2,
        code: "SAIGON50K",
        hub: "All hubs",
        discount: "50,000 VND",
        minOrder: "250,000 VND",
        validFrom: "01 Nov 2026 –",
        validTo: "30 Nov 2026",
        status: "ACTIVE"
    },
    {
        id: 3,
        code: "FREESHIPD1",
        hub: "Bite Hub D1",
        discount: "25,000 VND",
        minOrder: "100,000 VND",
        validFrom: "10 Nov 2026 –",
        validTo: "30 Nov 2026",
        status: "ACTIVE"
    },
    {
        id: 4,
        code: "D7LUNCH",
        hub: "Bite Hub D7",
        discount: "15%",
        minOrder: "120,000 VND",
        validFrom: "01 Nov 2026 –",
        validTo: "30 Nov 2026",
        status: "ACTIVE"
    },
    {
        id: 5,
        code: "THUDUC30",
        hub: "Bite Hub Thu Duc",
        discount: "30,000 VND",
        minOrder: "180,000 VND",
        validFrom: "01 Nov 2026 –",
        validTo: "31 Dec 2026",
        status: "ACTIVE"
    },
    {
        id: 6,
        code: "TET2026",
        hub: "All hubs",
        discount: "50,000 VND",
        minOrder: "200,000 VND",
        validFrom: "01 Feb 2026 –",
        validTo: "28 Feb 2026",
        status: "EXPIRED"
    },
    {
        id: 7,
        code: "SUMMERBITE",
        hub: "All hubs",
        discount: "10%",
        minOrder: "100,000 VND",
        validFrom: "01 Jun 2026 –",
        validTo: "31 Aug 2026",
        status: "ARCHIVED"
    },
    {
        id: 8,
        code: "D1WEEKEND",
        hub: "Bite Hub D1",
        discount: "20%",
        minOrder: "150,000 VND",
        validFrom: "01 Aug 2026 –",
        validTo: "31 Aug 2026",
        status: "ARCHIVED"
    }
];

function formatDisplayDate(isoStr) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const d = new Date(isoStr + "T00:00:00");
    if (Number.isNaN(d.getTime())) return isoStr;
    const day = String(d.getDate()).padStart(2, "0");
    return `${day} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

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
                    <td>${v.minOrder}</td>
                    <td>
                        <div class="period-cell">
                            <span>${v.validFrom}</span>
                            <span>${v.validTo}</span>
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

voucherTableBody.addEventListener("click", event => {
    const btn = event.target.closest(".archive-btn.enabled");
    if (!btn) return;
    const id = Number(btn.getAttribute("data-id"));
    const target = vouchers.find(v => v.id === id);
    if (target) {
        target.status = "ARCHIVED";
        renderVouchers();
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

createVoucherForm.addEventListener("submit", event => {
    event.preventDefault();
    const code = document.getElementById("newCode").value.trim().toUpperCase();
    const hub = document.getElementById("newHub").value;
    const discount = document.getElementById("newDiscount").value.trim();
    const minOrderNum = Number(document.getElementById("newMinOrder").value || 0);
    const startDate = document.getElementById("newStartDate").value;
    const endDate = document.getElementById("newEndDate").value;

    if (!code || !discount) return;

    vouchers.unshift({
        id: Date.now(),
        code,
        hub,
        discount,
        minOrder: `${minOrderNum.toLocaleString("en-US")} VND`,
        validFrom: `${formatDisplayDate(startDate)} –`,
        validTo: formatDisplayDate(endDate),
        status: "ACTIVE"
    });

    closeCreateModal();
    renderVouchers();
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

renderVouchers();