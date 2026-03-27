async function fetchNetworkAnalysis() {
    const response = await fetch("/api/network-analysis");
    return response.json();
}

function chart(elementId, label, labels, data, color) {
    new Chart(document.getElementById(elementId), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label,
                data,
                borderColor: color,
                backgroundColor: `${color}33`,
                fill: true,
                tension: 0.25
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function initNetworkAnalysis() {
    const points = await fetchNetworkAnalysis();
    const labels = points.map((item) => new Date(item.last_updated * 1000).toLocaleTimeString());
    const updateRate = points.map((item, index) => {
        if (index === 0) {
            return 0;
        }
        const delta = points[index].last_updated - points[index - 1].last_updated;
        return delta > 0 ? Number((1 / delta).toFixed(2)) : 0;
    });

    chart("networkPacketLossChart", "Packet Loss %", labels, points.map((item) => item.packet_loss), "#b91c1c");
    chart("networkThroughputChart", "Throughput pkt/s", labels, points.map((item) => item.throughput), "#1d4ed8");
    chart("networkDataRateChart", "Data Rate bytes/s", labels, points.map((item) => item.data_rate), "#0f766e");
    chart("networkLatencyChart", "Latency s", labels, points.map((item) => item.latency), "#0891b2");
    chart("networkJitterChart", "Jitter s", labels, points.map((item) => item.jitter), "#be185d");
    chart("networkUpdateRateChart", "Update Rate Hz", labels, updateRate, "#a16207");
}

initNetworkAnalysis();
