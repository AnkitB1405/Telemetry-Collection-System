const NETWORK_REFRESH_MS = 5000;
const networkChartTextColor = getComputedStyle(document.documentElement).getPropertyValue("--text").trim() || "#e8f3ff";
const networkChartMutedColor = getComputedStyle(document.documentElement).getPropertyValue("--muted").trim() || "#91a4c2";
const networkChartGridColor = "rgba(255, 255, 255, 0.08)";

Chart.defaults.color = networkChartTextColor;
Chart.defaults.borderColor = networkChartGridColor;
Chart.defaults.font.family = '"Manrope", sans-serif';

const networkCharts = {};

async function fetchNetworkAnalysis() {
    const response = await fetch("/api/network-analysis");
    return response.json();
}

function buildNetworkOptions() {
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
                    color: networkChartTextColor
                }
            }
        },
        scales: {
            x: {
                ticks: {
                    color: networkChartMutedColor,
                    maxRotation: 0
                },
                grid: {
                    color: networkChartGridColor
                }
            },
            y: {
                ticks: {
                    color: networkChartMutedColor
                },
                grid: {
                    color: networkChartGridColor
                }
            }
        }
    };
}

function updateNetworkChart(elementId, label, labels, data, color) {
    const config = {
        type: "line",
        data: {
            labels,
            datasets: [{
                label,
                data,
                borderColor: color,
                backgroundColor: `${color}24`,
                fill: true,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 3,
                tension: 0.28
            }]
        },
        options: buildNetworkOptions()
    };

    if (networkCharts[elementId]) {
        networkCharts[elementId].data = config.data;
        networkCharts[elementId].options = config.options;
        networkCharts[elementId].update();
        return;
    }

    networkCharts[elementId] = new Chart(document.getElementById(elementId), config);
}

async function refreshNetworkAnalysis() {
    const points = await fetchNetworkAnalysis();
    const labels = points.map((item) => new Date(item.last_updated * 1000).toLocaleTimeString());
    const updateRate = points.map((item, index) => {
        if (index === 0) {
            return 0;
        }
        const delta = points[index].last_updated - points[index - 1].last_updated;
        return delta > 0 ? Number((1 / delta).toFixed(2)) : 0;
    });

    updateNetworkChart("networkPacketLossChart", "Packet Loss %", labels, points.map((item) => item.packet_loss), "#ff6b8f");
    updateNetworkChart("networkThroughputChart", "Throughput pkt/s", labels, points.map((item) => item.throughput), "#3f8cff");
    updateNetworkChart("networkDataRateChart", "Data Rate bytes/s", labels, points.map((item) => item.data_rate), "#4ef4ff");
    updateNetworkChart("networkLatencyChart", "Latency s", labels, points.map((item) => item.latency), "#c084fc");
    updateNetworkChart("networkJitterChart", "Jitter s", labels, points.map((item) => item.jitter), "#7dffc8");
    updateNetworkChart("networkUpdateRateChart", "Update Rate Hz", labels, updateRate, "#ffd166");
}

async function initNetworkAnalysis() {
    await refreshNetworkAnalysis();
    window.setInterval(() => {
        refreshNetworkAnalysis().catch((error) => console.error("network analysis refresh failed", error));
    }, NETWORK_REFRESH_MS);
}

initNetworkAnalysis().catch((error) => console.error("initial network analysis refresh failed", error));
