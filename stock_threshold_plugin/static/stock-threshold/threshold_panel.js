/**
 * Stock Threshold Panel for InvenTree.
 *
 * This file is loaded dynamically by the plugin system and renders
 * a panel showing threshold information on stock item detail pages.
 *
 * The panel displays:
 * - Current quantity vs threshold
 * - Visual warning when below threshold
 * - Difference calculation
 */

export function renderPanel(target, data) {
    if (!target) {
        console.error('StockThresholdPlugin: No target provided to renderPanel');
        return;
    }

    const context = data?.context || {};
    const threshold = context.threshold ?? 0;
    const quantity = context.quantity ?? 0;
    const isBelowThreshold = context.is_below_threshold ?? false;
    const warningEnabled = context.warning_enabled !== false;
    const warningColor = context.warning_color || '#ff4444';

    let statusClass = '';
    let statusText = '';
    let statusIcon = '';

    if (!warningEnabled) {
        statusClass = 'threshold-disabled';
        statusText = 'Threshold warnings disabled';
        statusIcon = 'ti:minus-circle';
    } else if (isBelowThreshold) {
        statusClass = 'threshold-warning';
        statusText = 'BELOW THRESHOLD - Action required!';
        statusIcon = 'ti:alert-triangle';
    } else {
        statusClass = 'threshold-ok';
        statusText = 'Stock level OK';
        statusIcon = 'ti:check-circle';
    }

    const difference = quantity - threshold;
    const differenceClass = difference < 0 ? 'negative' : 'positive';
    const differenceText = difference >= 0 ? `+${difference}` : `${difference}`;

    target.innerHTML = `
    <div class="threshold-panel ${statusClass}" style="--warning-color: ${warningColor}">
        <div class="threshold-header">
            <span class="threshold-icon"><i class="${statusIcon}"></i></span>
            <span class="threshold-status">${statusText}</span>
        </div>
        <hr>
        <div class="threshold-details">
            <table class="threshold-table">
                <tr>
                    <td><strong>Current Quantity:</strong></td>
                    <td>${quantity}</td>
                </tr>
                <tr>
                    <td><strong>Threshold:</strong></td>
                    <td>${threshold}</td>
                </tr>
                <tr>
                    <td><strong>Difference:</strong></td>
                    <td class="${differenceClass}">${differenceText}</td>
                </tr>
            </table>
        </div>
    </div>
    <style>
        .threshold-panel {
            padding: 12px;
            border-radius: 4px;
            margin: 8px 0;
        }
        .threshold-warning {
            background-color: #fff5f5;
            border-left: 4px solid var(--warning-color, #ff4444);
        }
        .threshold-warning .threshold-icon {
            color: var(--warning-color, #ff4444);
        }
        .threshold-warning .threshold-status {
            color: var(--warning-color, #ff4444);
            font-weight: bold;
        }
        .threshold-ok {
            background-color: #f0fff4;
            border-left: 4px solid #48bb78;
        }
        .threshold-ok .threshold-icon {
            color: #48bb78;
        }
        .threshold-ok .threshold-status {
            color: #48bb78;
            font-weight: bold;
        }
        .threshold-disabled {
            background-color: #f7fafc;
            border-left: 4px solid #a0aec0;
        }
        .threshold-disabled .threshold-icon {
            color: #a0aec0;
        }
        .threshold-header {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .threshold-icon {
            font-size: 1.2em;
        }
        .threshold-table {
            width: 100%;
            margin-top: 8px;
        }
        .threshold-table td {
            padding: 4px 8px;
        }
        .negative {
            color: var(--warning-color, #ff4444);
            font-weight: bold;
        }
        .positive {
            color: #48bb78;
        }
    </style>
    `;
}
