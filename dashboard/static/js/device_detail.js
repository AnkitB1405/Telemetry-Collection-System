const DEVICE_REFRESH_MS = 5000;
const chartTextColor = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#e8f3ff";
const chartMutedColor = getComputedStyle(document.documentElement).getPropertyValue("--muted").trim() || "#91a4c2";
const chartGridColor = "rgba(255, 255, 255, 0.08)";

Chart.defaults.color = chartTextColor;
Chart.defaults.borderColor = chartGridColor;
Chart.defaults.font.family = '"Manrope", sans-serif';

const chartRegistry = {};

async function fetchDeviceMetrics(clientId) {
    const response = await fetch(`/api/devices/${clientId}/metrics`);
    return response.json();
}

async function fetchDeviceSummary(clientId) {
    const response = await fetch(`/api/devices/${clientId}`);
    return response.json();
}

function baseChartOptions() {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: "index",
            intersect: false
        },
        plugins: {
            legend: {
                labels: {
                    color: chartTextColor
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: chartMutedColor,
                    maxRotation: 0
                },
                grid: {
                    color: chartGridColor
                }
            },
            y: {
                ticks: {
                    color: chartMutedColor
                },
                grid: {
                    color: chartGridColor
                }
            }
        }
    };
}

function upsertChart(elementId, config) {
    if (chartRegistry[elementId]) {
        chartRegistry[elementId].data = config.data;
        chartRegistry[elementId].options = config.options;
        chartRegistry[elementId].update();
        return;
    }

    chartRegistry[elementId] = new Chart(document.getElementById(elementId), config);
}

function buildSingleDataset(label, data, color) {
    return [{
        label,
        data,
        borderColor: color,
        backgroundColor: `${color}26`,
        fill: true,
        borderWidth: 2,
        pointRadius: 0,
        pointHoverRadius: 3,
        tension: 0.28
    }];
}

function buildDualDataset(firstLabel, firstData, firstColor, secondLabel, secondData, secondColor) {
    return [
        {
            label: firstLabel,
            data: firstData,
            borderColor: firstColor,
            backgroundColor: `${firstColor}22`,
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 3,
            tension: 0.28
        },
        {
            label: secondLabel,
            data: secondData,
            borderColor: secondColor,
            backgroundColor: `${secondColor}18`,
            fill: true,
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 3,
            tension: 0.28
        }
    ];
}

function renderDeviceCharts(history) {
    const telemetry = history.telemetry || [];
    const network = history.network || [];

    const telemetryLabels = telemetry.map((item) => new Date(item.server_time * 1000).toLocaleTimeString());
    const networkLabels = network.map((item) => new Date(item.last_updated * 1000).toLocaleTimeString());

    upsertChart("cpuChart", {
        type: "line",
        data: { labels: telemetryLabels, datasets: buildSingleDataset("CPU %", telemetry.map((item) => item.cpu), "#4ef4ff") },
        options: baseChartOptions()
    });
    upsertChart("memoryChart", {
        type: "line",
        data: { labels: telemetryLabels, datasets: buildSingleDataset("Memory %", telemetry.map((item) => item.memory), "#7dffc8") },
        options: baseChartOptions()
    });
    upsertChart("diskChart", {
        type: "line",
        data: { labels: telemetryLabels, datasets: buildSingleDataset("Disk %", telemetry.map((item) => item.disk), "#ffd166") },
        options: baseChartOptions()
    });
    upsertChart("networkChart", {
        type: "line",
        data: {
            labels: telemetryLabels,
            datasets: buildDualDataset(
                "Net Sent",
                telemetry.map((item) => item.net_sent),
                "#3f8cff",
                "Net Recv",
                telemetry.map((item) => item.net_recv),
                "#4ef4ff"
            )
        },
        options: baseChartOptions()
    });
    upsertChart("packetLossChart", {
        type: "line",
        data: { labels: networkLabels, datasets: buildSingleDataset("Packet Loss %", network.map((item) => item.packet_loss), "#ff6b8f") },
        options: baseChartOptions()
    });
    upsertChart("throughputChart", {
        type: "line",
        data: { labels: networkLabels, datasets: buildSingleDataset("Throughput pkt/s", network.map((item) => item.throughput), "#3f8cff") },
        options: baseChartOptions()
    });
    upsertChart("latencyChart", {
        type: "line",
        data: { labels: networkLabels, datasets: buildSingleDataset("Latency s", network.map((item) => item.latency), "#c084fc") },
        options: baseChartOptions()
    });
    upsertChart("jitterChart", {
        type: "line",
        data: { labels: networkLabels, datasets: buildSingleDataset("Jitter s", network.map((item) => item.jitter), "#7dffc8") },
        options: baseChartOptions()
    });
}

async function refreshDeviceDetail() {
    const [history, device] = await Promise.all([
        fetchDeviceMetrics(window.deviceClientId),
        fetchDeviceSummary(window.deviceClientId)
    ]);

    const nameElement = document.getElementById("device-name");
    const ipElement = document.getElementById("device-ip");
    const statusElement = document.getElementById("device-status");

    if (nameElement && device.device_name) {
        nameElement.textContent = device.device_name;
    }
    if (ipElement && device.ip_address) {
        ipElement.textContent = device.ip_address;
    }
    if (statusElement && device.status) {
        statusElement.textContent = device.status;
        statusElement.className = `status ${device.status}`;
    }

    renderDeviceCharts(history);
}

async function initDeviceDetail() {
    await refreshDeviceDetail();
    window.setInterval(() => {
        refreshDeviceDetail().catch((error) => console.error("device detail refresh failed", error));
    }, DEVICE_REFRESH_MS);
}

initDeviceDetail().catch((error) => console.error("initial device detail refresh failed", error));
