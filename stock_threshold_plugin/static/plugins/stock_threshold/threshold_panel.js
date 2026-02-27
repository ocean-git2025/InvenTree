/**
 * Stock Threshold Panel for InvenTree.
 *
 * Displays and manages stock threshold settings for individual stock items.
 */

export function renderPanel(target, data) {
    if (!target) {
        console.error('No target provided to renderPanel');
        return;
    }

    const context = data.context || {};
    const quantity = context.quantity || 0;
    const threshold = context.threshold || 0;
    const isLow = context.is_low || false;
    const alertColor = context.alert_color || '#ef4444';
    const stockId = context.stock_id;

    const statusColor = isLow ? alertColor : '#22c55e';
    const statusText = isLow ? 'Below Threshold!' : 'OK';
    const statusIcon = isLow ? 'alert-triangle' : 'check-circle';

    target.innerHTML = `
    <div style="font-family: system-ui, -apple-system, sans-serif;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem;">
            <h4 style="margin: 0;">Stock Threshold Alert</h4>
            <span style="
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.875rem;
                font-weight: 500;
                color: white;
                background-color: ${statusColor};
            ">
                ${isLow ? '⚠' : '✓'} ${statusText}
            </span>
        </div>

        <div style="
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Current Quantity</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">${quantity}</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">Threshold</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">${threshold}</div>
                </div>
            </div>
        </div>

        <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.875rem; color: #64748b; margin-bottom: 0.5rem;">Stock Level</div>
            <div style="
                height: 0.75rem;
                background-color: #e2e8f0;
                border-radius: 9999px;
                overflow: hidden;
            ">
                <div style="
                    height: 100%;
                    width: ${threshold > 0 ? Math.min(100, (quantity / threshold) * 100) : 100}%;
                    background-color: ${statusColor};
                    border-radius: 9999px;
                    transition: width 0.3s ease;
                "></div>
            </div>
            <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; text-align: right;">
                ${quantity} / ${threshold} (${threshold > 0 ? Math.round((quantity / threshold) * 100) : 100}%)
            </div>
        </div>

        <div>
            <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #334155; margin-bottom: 0.5rem;">
                Set Custom Threshold
            </label>
            <div style="display: flex; gap: 0.5rem;">
                <input
                    type="number"
                    id="threshold-input"
                    value="${threshold}"
                    min="0"
                    style="
                        flex: 1;
                        padding: 0.5rem 0.75rem;
                        border: 1px solid #e2e8f0;
                        border-radius: 0.375rem;
                        font-size: 0.875rem;
                        outline: none;
                        transition: border-color 0.2s, box-shadow 0.2s;
                    "
                    onfocus="this.style.borderColor='#3b82f6'; this.style.boxShadow='0 0 0 3px rgba(59, 130, 246, 0.1)'"
                    onblur="this.style.borderColor='#e2e8f0'; this.style.boxShadow='none'"
                />
                <button
                    id="save-threshold-btn"
                    style="
                        padding: 0.5rem 1rem;
                        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                        color: white;
                        border: none;
                        border-radius: 0.375rem;
                        font-size: 0.875rem;
                        font-weight: 500;
                        cursor: pointer;
                        transition: transform 0.1s, box-shadow 0.2s;
                    "
                    onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.4)'"
                    onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none'"
                    onmousedown="this.style.transform='scale(0.98)'"
                    onmouseup="this.style.transform='scale(1.02)'"
                >
                    Save
                </button>
            </div>
        </div>
    </div>
    `;

    const saveBtn = target.querySelector('#save-threshold-btn');
    const input = target.querySelector('#threshold-input');

    if (saveBtn && input) {
        saveBtn.addEventListener('click', async () => {
            const newThreshold = parseInt(input.value, 10);
            if (isNaN(newThreshold) || newThreshold < 0) {
                alert('Please enter a valid non-negative number');
                return;
            }

            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving...';

            try {
                const response = await fetch(`/api/stock/${stockId}/`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        metadata: {
                            stock_threshold: newThreshold
                        }
                    })
                });

                if (response.ok) {
                    saveBtn.textContent = 'Saved!';
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                } else {
                    throw new Error('Failed to save');
                }
            } catch (error) {
                console.error('Error saving threshold:', error);
                alert('Failed to save threshold. Please try again.');
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save';
            }
        });
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

export function isPanelHidden(context) {
    return false;
}
