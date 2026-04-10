const DEVICES_REFRESH_MS = 5000;

function formatTimestamp(timestamp) {
    if (!timestamp) {
        return "Never";
    }

    return new Date(timestamp * 1000).toLocaleString();
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderDeviceRow(device) {
    return `
        <tr>
            <td>${escapeHtml(device.device_name)}</td>
            <td>${escapeHtml(device.client_id)}</td>
            <td>${escapeHtml(device.ip_address)}</td>
            <td><span class="status ${escapeHtml(device.status)}">${escapeHtml(device.status)}</span></td>
            <td>${formatTimestamp(device.last_seen)}</td>
            <td>${device.packet_loss}%</td>
            <td>${device.throughput} pkt/s</td>
            <td><a href="/devices/${encodeURIComponent(device.client_id)}">View device details</a></td>
        </tr>
    `;
}

async function refreshDevicesTable() {
    const body = document.getElementById("devices-table-body");
    if (!body) {
        return;
    }

    const response = await fetch("/api/devices");
    const devices = await response.json();

    if (!devices.length) {
        body.innerHTML = '<tr><td colspan="8">No devices registered yet. Start a client to register automatically.</td></tr>';
        return;
    }

    body.innerHTML = devices.map(renderDeviceRow).join("");
}

async function startDevicesPolling() {
    await refreshDevicesTable();
    window.setInterval(() => {
        refreshDevicesTable().catch((error) => console.error("devices refresh failed", error));
    }, DEVICES_REFRESH_MS);
}

startDevicesPolling().catch((error) => console.error("initial devices refresh failed", error));
