async function fetchDeviceMetrics(clientId) {
    const response = await fetch(`/api/devices/${clientId}/metrics`);
    return response.json();
}

function buildChart(elementId, label, labels, data, color) {
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

function buildDualChart(elementId, labels, firstLabel, firstData, secondLabel, secondData) {
    new Chart(document.getElementById(elementId), {
        type: "line",
        data: {
            labels,
            datasets: [
                { label: firstLabel, data: firstData, borderColor: "#0f766e", backgroundColor: "#0f766e22", fill: true, tension: 0.25 },
                { label: secondLabel, data: secondData, borderColor: "#c2410c", backgroundColor: "#c2410c22", fill: true, tension: 0.25 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

async function initDeviceDetail() {
    const history = await fetchDeviceMetrics(window.deviceClientId);
    const telemetry = history.telemetry || [];
    const network = history.network || [];

    const telemetryLabels = telemetry.map((item) => new Date(item.server_time * 1000).toLocaleTimeString());
    const networkLabels = network.map((item) => new Date(item.last_updated * 1000).toLocaleTimeString());
    const updateRate = network.map((item, index) => {
        if (index === 0) {
            return 0;
        }
        const delta = network[index].last_updated - network[index - 1].last_updated;
        return delta > 0 ? Number((1 / delta).toFixed(2)) : 0;
    });

    buildChart("cpuChart", "CPU %", telemetryLabels, telemetry.map((item) => item.cpu), "#0f766e");
    buildChart("memoryChart", "Memory %", telemetryLabels, telemetry.map((item) => item.memory), "#a16207");
    buildChart("diskChart", "Disk %", telemetryLabels, telemetry.map((item) => item.disk), "#7c3aed");
    buildDualChart("networkChart", telemetryLabels, "Net Sent", telemetry.map((item) => item.net_sent), "Net Recv", telemetry.map((item) => item.net_recv));
    buildChart("packetLossChart", "Packet Loss %", networkLabels, network.map((item) => item.packet_loss), "#b91c1c");
    buildChart("throughputChart", "Throughput pkt/s", networkLabels, network.map((item) => item.throughput), "#1d4ed8");
    buildChart("latencyChart", "Latency s", networkLabels, network.map((item) => item.latency), "#0891b2");
    buildChart("jitterChart", "Jitter s", networkLabels, network.map((item) => item.jitter), "#be185d");
}

initDeviceDetail();
