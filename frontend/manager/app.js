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
        yMax: 1,
        yTicks: ["", "", "", "0"],
        headers: ["Hub", "Total Orders", "Completed Orders", "Not Delivered"]
    },
    delivery: {
        chartTitle: "Daily Delivery Performance",
        breakdownTitle: "Delivery performance breakdown",
        unitLabel: "Completed deliveries",
        yMax: 1,
        yTicks: ["", "", "", "0"],
        headers: ["Completion Date", "Total Deliveries", "Avg. Delivery Time"]
    }
};

function formatCurrency(value) {
    return Number(value).toLocaleString("en-US");
}

function formatDateRangeLabel(startStr, endStr) {
    const start = new Date(`${startStr}T00:00:00`);
    const end = new Date(`${endStr}T00:00:00`);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return `${startStr} – ${endStr}`;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const a = String(start.getDate()).padStart(2, "0");
    const b = String(end.getDate()).padStart(2, "0");
    return start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()
        ? `${a}–${b} ${months[end.getMonth()]} ${end.getFullYear()}`
        : `${a} ${months[start.getMonth()]} – ${b} ${months[end.getMonth()]} ${end.getFullYear()}`;
}

function renderBarChart(rows, unitLabel) {
    const maxValue = Math.max(1, ...rows.map(row => Number(row.chartVal) || 0));
    const axis = [maxValue, maxValue * 2 / 3, maxValue / 3, 0].map(value => {
        if (unitLabel === "VND million") return `${value.toFixed(1)}m`;
        return String(Math.round(value));
    });
    chartYAxis.innerHTML = axis.map(label => `<span>${label}</span>`).join("");
    barsContainer.innerHTML = rows.map((row, index) => {
        const value = Number(row.chartVal) || 0;
        const height = Math.max(3, value / maxValue * 100);
        const color = index % 2 === 0 ? "bar-dark" : "bar-sage";
        const tooltip = unitLabel === "VND million" ? `${value.toFixed(1)}M VND` : `${value}`;
        return `<div class="bar-column"><div class="bar-track"><div class="bar-fill ${color}" style="height:${height}%"><span class="bar-tooltip">${tooltip}</span></div></div><span class="bar-label">${row.label}</span></div>`;
    }).join("");
}

function renderTableRows(type) {
    const rows = showAllRows ? currentRows : currentRows.slice(0, 4);
    reportTableBody.innerHTML = rows.map(row => {
        if (type === "sales") {
            return `<tr><td>${row.date}</td><td>${formatCurrency(row.orders)}</td><td>${formatCurrency(row.revenue)}</td><td>${row.delivery}</td></tr>`;
        }
        if (type === "delivery") {
            return `<tr><td>${row.col1}</td><td>${row.col2}</td><td>${row.col3}</td></tr>`;
        }
        return `<tr><td>${row.col1}</td><td>${row.col2}</td><td>${row.col3}</td><td>${row.col4}</td></tr>`;
    }).join("");
    const unit = type === "hub-workload" ? "hubs" : "days";
    tablePaginationInfo.textContent = `Showing ${rows.length ? 1 : 0}–${rows.length} of ${currentRows.length} ${unit}`;
    toggleRowsButton.classList.toggle("hidden", currentRows.length <= 4);
    toggleRowsButton.textContent = showAllRows ? "Show less" : "Show all";
}

async function fetchReport(type, startDate, endDate) {
    const response = await fetch(`/api/reports/${type}?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`, {
        credentials: "same-origin"
    });
    if (!response.ok) {
        let message = `Request failed (${response.status})`;
        try { message = (await response.json()).detail || message; } catch { }
        throw new Error(message);
    }
    return response.json();
}

function setNoData() {
    reportNotice.textContent = "No data available for the selected period";
    reportNotice.classList.remove("hidden");
    chartEmptyState.classList.remove("hidden");
    barChartWrapper.classList.add("hidden");
    tableFooter.classList.add("hidden");
    reportTableBody.innerHTML = "";
    currentRows = [];
    ["totalRevenue", "totalOrders", "averageDelivery"].forEach(id => {
        document.getElementById(id).textContent = "—";
    });
    ["kpiLabel1", "kpiLabel2", "kpiLabel3"].forEach(id => {
        document.getElementById(id).textContent = "—";
    });
    tableTotalSummary.textContent = "";
}

function setLoadError(message) {
    reportNotice.textContent = `Unable to load report: ${message}`;
    reportNotice.classList.remove("hidden");
    chartEmptyState.classList.add("hidden");
    barChartWrapper.classList.add("hidden");
    tableFooter.classList.add("hidden");
    reportTableBody.innerHTML = "";
}

async function renderReport() {
    const type = reportType.value;
    const start = startDateInput.value;
    const end = endDateInput.value;
    if (!start || !end) {
        alert("Please select both start date and end date.");
        return;
    }
    if (start > end) {
        alert("Invalid time range");
        return;
    }

    const config = REPORT_CONFIGS[type];
    chartTitle.textContent = config.chartTitle;
    breakdownTitle.textContent = config.breakdownTitle;
    chartMeta.textContent = `${config.unitLabel} · ${formatDateRangeLabel(start, end)}`;
    reportTableHeader.innerHTML = config.headers.map(label => `<th>${label}</th>`).join("");
    generateReportButton.disabled = true;
    generateReportButton.textContent = "Loading...";
    reportNotice.classList.add("hidden");

    try {
        const data = await fetchReport(type, start, end);
        if (!data || !Array.isArray(data.rows)) throw new Error("Invalid report response.");
        if (data.rows.length === 0) {
            setNoData();
            return;
        }
        if (!Array.isArray(data.kpis) || data.kpis.length !== 3) throw new Error("Incomplete report metrics.");

        reportNotice.classList.add("hidden");
        chartEmptyState.classList.add("hidden");
        barChartWrapper.classList.remove("hidden");
        tableFooter.classList.remove("hidden");
        document.getElementById("kpiLabel1").textContent = data.kpis[0].label;
        document.getElementById("totalRevenue").textContent = data.kpis[0].value;
        document.getElementById("kpiLabel2").textContent = data.kpis[1].label;
        document.getElementById("totalOrders").textContent = data.kpis[1].value;
        document.getElementById("kpiLabel3").textContent = data.kpis[2].label;
        document.getElementById("averageDelivery").textContent = data.kpis[2].value;
        tableTotalSummary.textContent = data.totalSummary || "";
        currentRows = data.rows;
        showAllRows = false;
        renderBarChart(currentRows, config.unitLabel);
        renderTableRows(type);
    } catch (error) {
        console.error("Report generation failed:", error);
        setLoadError(error.message);
    } finally {
        generateReportButton.disabled = false;
        generateReportButton.textContent = "Generate Report";
    }
}

toggleRowsButton.addEventListener("click", () => {
    showAllRows = !showAllRows;
    renderTableRows(reportType.value);
});
reportType.addEventListener("change", renderReport);
generateReportButton.addEventListener("click", renderReport);

const managerPages = {
    dashboard: document.getElementById("dashboardPage"),
    "hub-operations": document.getElementById("hubOperationsPage"),
    "order-history": document.getElementById("orderHistoryPage"),
    reports: document.getElementById("reportsPage")
};

function showManagerPage(page) {
    Object.values(managerPages).forEach(section => {
        if (section) {
            section.classList.add("hidden");
        }
    });

    const selectedPage = managerPages[page];

    if (!selectedPage) {
        return;
    }

    selectedPage.classList.remove("hidden");

    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.toggle("active", item.dataset.nav === page);
    });

    // Generate a report only when the Reports page is opened.
    if (page === "reports") {
        renderReport();
    }
}

document.querySelectorAll(".nav-item").forEach(item => {
    item.addEventListener("click", event => {
        event.preventDefault();
        showManagerPage(item.dataset.nav);
    });
});

document.getElementById("logoutButton").addEventListener("click", async () => {
    try {
        await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
    } finally {
        window.location.assign("/");
    }
});

function localDateInputValue() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
}

const today = localDateInputValue();
startDateInput.value = today;
endDateInput.value = today;
renderReport();
