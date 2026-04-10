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
            <td>
                <div class="table-actions">
                    <a href="/devices/${encodeURIComponent(device.client_id)}">View device details</a>
                    <button
                        type="button"
                        class="button table-action-button rename-device-button"
                        data-client-id="${escapeHtml(device.client_id)}"
                        data-device-name="${escapeHtml(device.device_name)}"
                    >
                        Rename
                    </button>
                </div>
            </td>
        </tr>
    `;
}

function showFeedback(message, isError = false) {
    const feedback = document.getElementById("devices-feedback");
    if (!feedback) {
        return;
    }

    feedback.hidden = !message;
    feedback.textContent = message;
    feedback.classList.toggle("error-text", isError);
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

async function renameDevice(clientId, currentName) {
    const nextName = window.prompt(`Rename ${clientId}`, currentName);
    if (nextName === null) {
        return;
    }

    const cleanedName = nextName.trim();
    if (!cleanedName) {
        showFeedback("Device name cannot be empty.", true);
        return;
    }

    const response = await fetch(`/api/devices/${encodeURIComponent(clientId)}/rename`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ device_name: cleanedName })
    });

    const payload = await response.json();
    if (!response.ok) {
        showFeedback(payload.error || "Unable to rename device right now.", true);
        return;
    }

    showFeedback(`Saved display name for ${clientId} as ${payload.device_name}.`);
    await refreshDevicesTable();
}

async function startDevicesPolling() {
    document.addEventListener("click", (event) => {
        const renameButton = event.target.closest(".rename-device-button");
        if (!renameButton) {
            return;
        }

        renameDevice(renameButton.dataset.clientId, renameButton.dataset.deviceName).catch((error) => {
            console.error("device rename failed", error);
            showFeedback("Rename failed. Please try again.", true);
        });
    });

    await refreshDevicesTable();
    window.setInterval(() => {
        refreshDevicesTable().catch((error) => console.error("devices refresh failed", error));
    }, DEVICES_REFRESH_MS);
}

startDevicesPolling().catch((error) => console.error("initial devices refresh failed", error));
