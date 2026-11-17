// SaigonBite Manager Portal — UC06 Management Reports
const reportType = document.getElementById("reportType");
const startDateInput = document.getElementById("startDate");
const endDateInput = document.getElementById("endDate");
const generateReportButton = document.getElementById("generateReportButton");
const reportNotice = document.getElementById("reportNotice");

const chartTitle = document.getElementById("chartTitle");
const chartMeta = document.getElementById("chartMeta");
const chartEmptyState = document.getElementById("chartEmptyState");
const barChartWrapper = document.getElementById("barChartWrapper");
const chartYAxis = document.getElementById("chartYAxis");
const barsContainer = document.getElementById("barsContainer");

const breakdownTitle = document.getElementById("breakdownTitle");
const reportTableHeader = document.getElementById("reportTableHeader");
const reportTableBody = document.getElementById("reportTableBody");
const tableFooter = document.getElementById("tableFooter");
const tablePaginationInfo = document.getElementById("tablePaginationInfo");
const toggleRowsButton = document.getElementById("toggleRowsButton");
const tableTotalSummary = document.getElementById("tableTotalSummary");

let showAllRows = false;
let currentRows = [];

const FIGMA_DEFAULT_DATA = {
    sales: {
        chartTitle: "Daily Sales Revenue",
        breakdownTitle: "Daily sales breakdown",
        unitLabel: "VND million",
        yMax: 45,
        yTicks: ["45m", "30m", "15m", "0m"],
        kpis: [
            { label: "Total Revenue", value: "428,500,000 VND" },
            { label: "Total Orders", value: "3,420" },
            { label: "Avg. Delivery Time", value: "24 mins" }
        ],
        headers: ["Date", "Orders", "Revenue (VND)", "Avg. delivery"],
        totalSummary: "Total: 428,500,000 VND · 3,420 orders",
        rows: [
            { label: "01", date: "01 Nov 2026", orders: 192, revenue: 24000000, chartVal: 24.0, delivery: "24 mins" },
            { label: "02", date: "02 Nov 2026", orders: 208, revenue: 26000000, chartVal: 26.0, delivery: "23 mins" },
            { label: "03", date: "03 Nov 2026", orders: 224, revenue: 28000000, chartVal: 28.0, delivery: "25 mins" },
            { label: "04", date: "04 Nov 2026", orders: 240, revenue: 30000000, chartVal: 30.0, delivery: "24 mins" },
            { label: "05", date: "05 Nov 2026", orders: 280, revenue: 35000000, chartVal: 35.0, delivery: "24 mins" },
            { label: "06", date: "06 Nov 2026", orders: 336, revenue: 42000000, chartVal: 42.0, delivery: "26 mins" },
            { label: "07", date: "07 Nov 2026", orders: 304, revenue: 38000000, chartVal: 38.0, delivery: "25 mins" },
            { label: "08", date: "08 Nov 2026", orders: 176, revenue: 22000000, chartVal: 22.0, delivery: "22 mins" },
            { label: "09", date: "09 Nov 2026", orders: 200, revenue: 25000000, chartVal: 25.0, delivery: "23 mins" },
            { label: "10", date: "10 Nov 2026", orders: 216, revenue: 27000000, chartVal: 27.0, delivery: "24 mins" },
            { label: "11", date: "11 Nov 2026", orders: 232, revenue: 29000000, chartVal: 29.0, delivery: "24 mins" },
            { label: "12", date: "12 Nov 2026", orders: 248, revenue: 31000000, chartVal: 31.0, delivery: "25 mins" },
            { label: "13", date: "13 Nov 2026", orders: 208, revenue: 26000000, chartVal: 26.0, delivery: "23 mins" },
            { label: "14", date: "14 Nov 2026", orders: 192, revenue: 24000000, chartVal: 24.0, delivery: "24 mins" },
            { label: "15", date: "15 Nov 2026", orders: 164, revenue: 21500000, chartVal: 21.5, delivery: "23 mins" }
        ]
    },
    "hub-workload": {
        chartTitle: "Hub Workload Distribution",
        breakdownTitle: "Hub workload breakdown",
        unitLabel: "Orders",
        yMax: 1200,
        yTicks: ["1200", "800", "400", "0"],
        kpis: [
            { label: "Total Hub Orders", value: "3,420" },
            { label: "Completed Orders", value: "3,318" },
            { label: "Avg. Prep Time", value: "11 mins" }
        ],
        headers: ["Hub", "Total Orders", "Completed Orders", "Pending Orders"],
        totalSummary: "Total: 3,420 orders · 97.0% completion rate",
        rows: [
            { label: "D1", col1: "District 1 Central Hub", col2: "1,120", col3: "1,092", col4: "28", chartVal: 1120 },
            { label: "D7", col1: "District 7 Phu My Hung Hub", col2: "890", col3: "865", col4: "25", chartVal: 890 },
            { label: "TD", col1: "Thu Duc Campus Hub", col2: "780", col3: "754", col4: "26", chartVal: 780 },
            { label: "BT", col1: "Binh Thanh Hub", col2: "630", col3: "607", col4: "23", chartVal: 630 }
        ]
    },
    delivery: {
        chartTitle: "Daily Delivery Performance",
        breakdownTitle: "Delivery performance breakdown",
        unitLabel: "On-time %",
        yMax: 100,
        yTicks: ["100%", "75%", "50%", "0%"],
        kpis: [
            { label: "Total Deliveries", value: "3,318" },
            { label: "On-Time Rate", value: "94.6%" },
            { label: "Avg. Delivery Time", value: "24 mins" }
        ],
        headers: ["Date", "Total Deliveries", "On-time Deliveries", "Avg. Delivery Time"],
        totalSummary: "Total: 3,318 deliveries · 94.6% on-time",
        rows: [
            { label: "01", col1: "01 Nov 2026", col2: "188", col3: "179 (95.2%)", col4: "24 mins", chartVal: 95.2 },
            { label: "02", col1: "02 Nov 2026", col2: "204", col3: "195 (95.6%)", col4: "23 mins", chartVal: 95.6 },
            { label: "03", col1: "03 Nov 2026", col2: "218", col3: "204 (93.6%)", col4: "25 mins", chartVal: 93.6 },
            { label: "04", col1: "04 Nov 2026", col2: "234", col3: "222 (94.9%)", col4: "24 mins", chartVal: 94.9 },
            { label: "05", col1: "05 Nov 2026", col2: "272", col3: "257 (94.5%)", col4: "24 mins", chartVal: 94.5 },
            { label: "06", col1: "06 Nov 2026", col2: "326", col3: "304 (93.3%)", col4: "26 mins", chartVal: 93.3 },
            { label: "07", col1: "07 Nov 2026", col2: "295", col3: "278 (94.2%)", col4: "25 mins", chartVal: 94.2 },
            { label: "08", col1: "08 Nov 2026", col2: "172", col3: "166 (96.5%)", col4: "22 mins", chartVal: 96.5 }
        ]
    }
};

function formatCurrency(amount) {
    return Number(amount).toLocaleString("en-US");
}

function formatDateRangeLabel(startStr, endStr) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const s = new Date(startStr + "T00:00:00");
    const e = new Date(endStr + "T00:00:00");
    if (Number.isNaN(s.getTime()) || Number.isNaN(e.getTime())) {
        return `${startStr} – ${endStr}`;
    }
    const sDay = String(s.getDate()).padStart(2, "0");
    const eDay = String(e.getDate()).padStart(2, "0");
    if (s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear()) {
        return `${sDay}–${eDay} ${months[e.getMonth()]} ${e.getFullYear()}`;
    }
    return `${sDay} ${months[s.getMonth()]} – ${eDay} ${months[e.getMonth()]} ${e.getFullYear()}`;
}

function renderBarChart(rows, yMax, yTicks, unitLabel) {
    chartYAxis.innerHTML = yTicks.map(tick => `<span>${tick}</span>`).join("");

    barsContainer.innerHTML = rows
        .map((row, index) => {
            const heightPct = Math.min(100, Math.max(3, (row.chartVal / yMax) * 100));
            const colorClass = index % 2 === 0 ? "bar-dark" : "bar-sage";
            const tooltipText = unitLabel === "VND million"
                ? `${row.chartVal.toFixed(1)}M VND`
                : `${row.chartVal}`;

            return `
                <div class="bar-column">
                    <div class="bar-track">
                        <div class="bar-fill ${colorClass}" style="height: ${heightPct}%;">
                            <span class="bar-tooltip">${tooltipText}</span>
                        </div>
                    </div>
                    <span class="bar-label">${row.label}</span>
                </div>
            `;
        })
        .join("");
}

function renderTableRows(type) {
    const visibleRows = showAllRows ? currentRows : currentRows.slice(0, 4);

    reportTableBody.innerHTML = visibleRows
        .map(row => {
            if (type === "sales") {
                return `
                    <tr>
                        <td>${row.date}</td>
                        <td>${formatCurrency(row.orders)}</td>
                        <td>${formatCurrency(row.revenue)}</td>
                        <td>${row.delivery}</td>
                    </tr>
                `;
            }
            return `
                <tr>
                    <td>${row.col1}</td>
                    <td>${row.col2}</td>
                    <td>${row.col3}</td>
                    <td>${row.col4}</td>
                </tr>
            `;
        })
        .join("");

    const unit = type === "hub-workload" ? "hubs" : "days";
    tablePaginationInfo.textContent = `Showing 1–${visibleRows.length} of ${currentRows.length} ${unit}`;

    if (currentRows.length <= 4) {
        toggleRowsButton.classList.add("hidden");
    } else {
        toggleRowsButton.classList.remove("hidden");
        toggleRowsButton.textContent = showAllRows ? "Show less" : "Show all";
    }
}

async function fetchBackendReport(type, startDate, endDate) {
    try {
        const res = await fetch(
            `/api/reports/${type}?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`,
            { credentials: "same-origin" }
        );
        if (!res.ok) return null;
        return await res.json();
    } catch {
        return null;
    }
}

async function renderReport() {
    const type = reportType.value;
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;

    if (!startDate || !endDate) {
        alert("Please select both start date and end date.");
        return;
    }
    if (endDate < startDate) {
        alert("End date cannot be earlier than start date.");
        return;
    }

    reportNotice.classList.add("hidden");
    chartEmptyState.classList.add("hidden");
    barChartWrapper.classList.remove("hidden");
    tableFooter.classList.remove("hidden");

    const config = FIGMA_DEFAULT_DATA[type];
    const apiData = await fetchBackendReport(type, startDate, endDate);

    const dataset = apiData && Array.isArray(apiData.rows) && apiData.rows.length > 0
        ? { ...config, ...apiData }
        : config;

    document.getElementById("kpiLabel1").textContent = dataset.kpis[0].label;
    document.getElementById("totalRevenue").textContent = dataset.kpis[0].value;

    document.getElementById("kpiLabel2").textContent = dataset.kpis[1].label;
    document.getElementById("totalOrders").textContent = dataset.kpis[1].value;

    document.getElementById("kpiLabel3").textContent = dataset.kpis[2].label;
    document.getElementById("averageDelivery").textContent = dataset.kpis[2].value;

    chartTitle.textContent = dataset.chartTitle;
    chartMeta.textContent = `${dataset.unitLabel} · ${formatDateRangeLabel(startDate, endDate)}`;
    breakdownTitle.textContent = dataset.breakdownTitle;

    reportTableHeader.innerHTML = dataset.headers.map(h => `<th>${h}</th>`).join("");
    tableTotalSummary.textContent = dataset.totalSummary;

    currentRows = dataset.rows;
    renderBarChart(currentRows, dataset.yMax, dataset.yTicks, dataset.unitLabel);
    renderTableRows(type);
}

toggleRowsButton.addEventListener("click", () => {
    showAllRows = !showAllRows;
    renderTableRows(reportType.value);
});

reportType.addEventListener("change", () => {
    showAllRows = false;
    renderReport();
});

generateReportButton.addEventListener("click", () => {
    showAllRows = false;
    renderReport();
});

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", event => {
        if (item.getAttribute("data-nav") !== "reports") {
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

renderReport();