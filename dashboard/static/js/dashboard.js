const DASHBOARD_REFRESH_MS = 5000;
const resetButton = document.getElementById("reset-dashboard-data");
const resetStatus = document.getElementById("reset-dashboard-status");

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

function setResetStatus(message, isError = false) {
    if (!resetStatus) {
        return;
    }

    resetStatus.textContent = message;
    resetStatus.classList.toggle("error-text", isError);
}

async function resetDashboardData() {
    const confirmed = window.confirm(
        "Clear stored telemetry and network history and start fresh? Registered devices will be kept."
    );
    if (!confirmed) {
        return;
    }

    if (resetButton) {
        resetButton.disabled = true;
    }
    setResetStatus("Clearing stored telemetry and network history...");

    try {
        const response = await fetch("/api/reset-data", { method: "POST" });
        if (!response.ok) {
            throw new Error(`reset failed with status ${response.status}`);
        }

        await refreshDashboardSummary();
        setResetStatus("Telemetry history cleared. New data will appear as clients continue sending.");
    } catch (error) {
        console.error("dashboard reset failed", error);
        setResetStatus("Could not clear telemetry history. Check the server logs and try again.", true);
    } finally {
        if (resetButton) {
            resetButton.disabled = false;
        }
    }
}

async function startDashboardPolling() {
    if (resetButton) {
        resetButton.addEventListener("click", () => {
            resetDashboardData().catch((error) => console.error("dashboard reset failed", error));
        });
    }

    await refreshDashboardSummary();
    window.setInterval(() => {
        refreshDashboardSummary().catch((error) => console.error("dashboard refresh failed", error));
    }, DASHBOARD_REFRESH_MS);
}

startDashboardPolling().catch((error) => console.error("initial dashboard refresh failed", error));
