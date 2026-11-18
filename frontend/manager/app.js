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

const REPORT_CONFIGS = {
    sales: {
        chartTitle: "Daily Sales Revenue",
        breakdownTitle: "Daily sales breakdown",
        unitLabel: "VND million",
        yMax: 50,
        yTicks: ["50m", "35m", "20m", "0m"],
        headers: ["Date", "Orders", "Revenue (VND)", "Avg. delivery"]
    },
    "hub-workload": {
        chartTitle: "Hub Workload Distribution",
        breakdownTitle: "Hub workload breakdown",
        unitLabel: "Orders",
        yMax: 1500,
        yTicks: ["1500", "1000", "500", "0"],
        headers: ["Hub", "Total Orders", "Completed Orders", "Pending Orders"]
    },
    delivery: {
        chartTitle: "Daily Delivery Performance",
        breakdownTitle: "Delivery performance breakdown",
        unitLabel: "On-time %",
        yMax: 100,
        yTicks: ["100%", "75%", "50%", "0%"],
        headers: ["Date", "Total Deliveries", "On-time Deliveries", "Avg. Delivery Time"]
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

    const config = REPORT_CONFIGS[type];
    chartTitle.textContent = config.chartTitle;
    breakdownTitle.textContent = config.breakdownTitle;
    chartMeta.textContent = `${config.unitLabel} · ${formatDateRangeLabel(startDate, endDate)}`;
    reportTableHeader.innerHTML = config.headers.map(h => `<th>${h}</th>`).join("");

    const apiData = await fetchBackendReport(type, startDate, endDate);

    if (!apiData || !Array.isArray(apiData.rows) || apiData.rows.length === 0) {
        reportNotice.classList.remove("hidden");
        chartEmptyState.classList.remove("hidden");
        barChartWrapper.classList.add("hidden");
        tableFooter.classList.add("hidden");
        reportTableBody.innerHTML = "";
        document.getElementById("kpiLabel1").textContent = "Total Revenue / Orders";
        document.getElementById("totalRevenue").textContent = "0";
        document.getElementById("kpiLabel2").textContent = "Total Count";
        document.getElementById("totalOrders").textContent = "0";
        document.getElementById("kpiLabel3").textContent = "Avg. Time";
        document.getElementById("averageDelivery").textContent = "0 mins";
        tableTotalSummary.textContent = "Total: 0";
        return;
    }

    reportNotice.classList.add("hidden");
    chartEmptyState.classList.add("hidden");
    barChartWrapper.classList.remove("hidden");
    tableFooter.classList.remove("hidden");

    document.getElementById("kpiLabel1").textContent = apiData.kpis[0].label;
    document.getElementById("totalRevenue").textContent = apiData.kpis[0].value;

    document.getElementById("kpiLabel2").textContent = apiData.kpis[1].label;
    document.getElementById("totalOrders").textContent = apiData.kpis[1].value;

    document.getElementById("kpiLabel3").textContent = apiData.kpis[2].label;
    document.getElementById("averageDelivery").textContent = apiData.kpis[2].value;

    tableTotalSummary.textContent = apiData.totalSummary;

    currentRows = apiData.rows;
    renderBarChart(currentRows, config.yMax, config.yTicks, config.unitLabel);
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