const DASHBOARD_REFRESH_MS = 5000;

function summaryValue(key, suffix = "") {
    const element = document.getElementById(`summary-${key}`);
    return {
        set(value) {
            if (!element) {
                return;
            }

            element.textContent = `${value}${suffix}`;
        }
    };
}

const summaryBindings = {
    active_clients: summaryValue("active_clients"),
    average_cpu: summaryValue("average_cpu", "%"),
    average_memory: summaryValue("average_memory", "%"),
    average_disk: summaryValue("average_disk", "%"),
    total_packets_received: summaryValue("total_packets_received"),
    total_packets_lost: summaryValue("total_packets_lost"),
    system_throughput: summaryValue("system_throughput", " pkt/s"),
    total_network_traffic: summaryValue("total_network_traffic", " bytes")
};

async function refreshDashboardSummary() {
    const response = await fetch("/api/summary");
    const summary = await response.json();

    Object.entries(summaryBindings).forEach(([key, binding]) => {
        binding.set(summary[key] ?? 0);
    });
}

async function startDashboardPolling() {
    await refreshDashboardSummary();
    window.setInterval(() => {
        refreshDashboardSummary().catch((error) => console.error("dashboard refresh failed", error));
    }, DASHBOARD_REFRESH_MS);
}

startDashboardPolling().catch((error) => console.error("initial dashboard refresh failed", error));
