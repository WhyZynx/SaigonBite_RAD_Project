const reportType = document.getElementById("reportType");
const startDate = document.getElementById("startDate");
const endDate = document.getElementById("endDate");
const generateButton = document.getElementById("generateButton");
const validationMessage = document.getElementById("validationMessage");

const reportConfig = {
  sales: {
    title: "Sales Report",
    chartTitle: "Daily Sales Revenue",
    chartSubtitle: "Revenue trend during the selected period",
    legend: "Revenue (VND)",
    tableTitle: "Daily sales breakdown",
    headers: ["Date", "Orders", "Revenue (VND)", "Avg. delivery"],
    kpis: ["₫ 0", "0", "0 min"],
    captions: ["Revenue in selected period", "Orders in selected period", "Average completed delivery"]
  },
  hub: {
    title: "Hub Workload Report",
    chartTitle: "Daily Hub Workload",
    chartSubtitle: "Order volume processed by hubs",
    legend: "Processed orders",
    tableTitle: "Hub workload breakdown",
    headers: ["Hub", "Orders received", "Orders processed", "Pending orders"],
    kpis: ["0", "0", "0"],
    captions: ["Hubs in selected period", "Orders processed", "Orders awaiting processing"]
  },
  delivery: {
    title: "Delivery Performance Report",
    chartTitle: "Daily Delivery Performance",
    chartSubtitle: "Completed deliveries and average delivery time",
    legend: "Completed deliveries",
    tableTitle: "Delivery performance breakdown",
    headers: ["Date", "Completed deliveries", "Avg. delivery time", "On-time rate"],
    kpis: ["0", "0 min", "0%"],
    captions: ["Completed deliveries", "Average delivery time", "Deliveries completed on time"]
  }
};

function formatDate(value) {
  if (!value) return "";
  const date = new Date(`${value}T00:00:00`);
  return new Intl.DateTimeFormat("en-GB", { day: "2-digit", month: "short", year: "numeric" }).format(date);
}

function renderEmptyTable(headers) {
  document.getElementById("tableHead").innerHTML =
    `<tr>${headers.map(header => `<th>${header}</th>`).join("")}</tr>`;
  document.getElementById("tableBody").innerHTML =
    `<tr><td colspan="${headers.length}" class="empty-row">No report data to display.</td></tr>`;
  document.getElementById("rowsLabel").textContent = "0 records";
}

function showEmptyReport() {
  const config = reportConfig[reportType.value];
  document.getElementById("reportHeading").textContent = config.title;
  document.getElementById("chartTitle").textContent = config.chartTitle;
  document.getElementById("chartSubtitle").textContent = config.chartSubtitle;
  document.getElementById("legendLabel").textContent = config.legend;
  document.getElementById("tableTitle").textContent = config.tableTitle;
  document.getElementById("periodLabel").textContent =
    `${formatDate(startDate.value)} — ${formatDate(endDate.value)}`;

  ["kpiOne", "kpiTwo", "kpiThree"].forEach((id, index) => {
    document.getElementById(id).textContent = config.kpis[index];
  });
  ["kpiOneCaption", "kpiTwoCaption", "kpiThreeCaption"].forEach((id, index) => {
    document.getElementById(id).textContent = config.captions[index];
  });

  document.getElementById("emptyState").hidden = false;
  document.getElementById("reportChart").hidden = true;
  renderEmptyTable(config.headers);
}

function generateReport() {
  validationMessage.textContent = "";
  if (!startDate.value || !endDate.value) {
    validationMessage.textContent = "Please select both a start date and an end date.";
    return;
  }
  if (startDate.value > endDate.value) {
    validationMessage.textContent = "Start date must be earlier than or equal to end date.";
    return;
  }
  // UI prototype: no report API/data source is connected yet.
  showEmptyReport();
}

generateButton.addEventListener("click", generateReport);
reportType.addEventListener("change", showEmptyReport);
startDate.addEventListener("change", () => { validationMessage.textContent = ""; });
endDate.addEventListener("change", () => { validationMessage.textContent = ""; });

document.getElementById("logoutButton").addEventListener("click", async () => {
  try {
    await fetch("/api/auth/logout", { method: "POST", credentials: "same-origin" });
  } finally {
    window.location.href = "/";
  }
});

showEmptyReport();
