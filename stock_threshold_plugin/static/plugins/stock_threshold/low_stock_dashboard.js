/**
 * Low Stock Dashboard Item for InvenTree.
 *
 * Displays a summary of stock items below their configured threshold.
 */

export function renderPanel(target, data) {
    if (!target) {
        console.error('No target provided to renderPanel');
        return;
    }

    const context = data.context || {};
    const lowStockCount = context.low_stock_count || 0;
    const alertColor = context.alert_color || '#ef4444';

    target.innerHTML = `
    <div style="
        font-family: system-ui, -apple-system, sans-serif;
        height: 100%;
        display: flex;
        flex-direction: column;
    ">
        <div style="
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: ${lowStockCount > 0 ? `linear-gradient(135deg, ${alertColor}15 0%, ${alertColor}08 100%)` : 'linear-gradient(135deg, #22c55e15 0%, #22c55e08 100%)'};
            border-radius: 0.5rem;
            border: 1px solid ${lowStockCount > 0 ? alertColor + '30' : '#22c55e30'};
        ">
            <div style="
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: ${lowStockCount > 0 ? alertColor : '#22c55e'};
                border-radius: 0.5rem;
                font-size: 1.5rem;
            ">
                ${lowStockCount > 0 ? '⚠️' : '✅'}
            </div>
            <div>
                <div style="font-size: 2rem; font-weight: 700; color: #1e293b;">${lowStockCount}</div>
                <div style="font-size: 0.875rem; color: #64748b;">Items Below Threshold</div>
            </div>
        </div>

        ${lowStockCount > 0 ? `
        <div style="
            margin-top: 1rem;
            flex: 1;
            overflow: auto;
        ">
            <div style="
                font-size: 0.75rem;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 0.5rem;
                padding: 0 0.25rem;
            ">
                Low Stock Items
            </div>
            <div id="low-stock-list" style="
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            ">
                <div style="
                    text-align: center;
                    color: #94a3b8;
                    padding: 1rem;
                ">
                    Loading items...
                </div>
            </div>
        </div>
        ` : `
        <div style="
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #22c55e;
            font-size: 0.875rem;
        ">
            All stock levels are above configured thresholds!
        </div>
        `}

        ${lowStockCount > 0 ? `
        <a
            href="/stock/"
            style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                margin-top: 1rem;
                padding: 0.5rem 1rem;
                background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                color: white;
                text-decoration: none;
                border-radius: 0.375rem;
                font-size: 0.875rem;
                font-weight: 500;
                transition: transform 0.1s, box-shadow 0.2s;
                text-align: center;
            "
            onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.4)'"
            onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none'"
        >
            View Stock List →
        </a>
        ` : ''}
    </div>
    `;

    if (lowStockCount > 0) {
        loadLowStockItems(target.querySelector('#low-stock-list'), alertColor);
    }
}

async function loadLowStockItems(container, alertColor) {
    try {
        const response = await fetch('/api/stock/?is_active=true&offset=0&limit=50');
        if (!response.ok) {
            throw new Error('Failed to load stock data');
        }

        const result = await response.json();
        const stockItems = result.results || [];

        const lowStockItems = [];

        for (const item of stockItems) {
            const threshold = item.metadata?.stock_threshold;
            if (threshold !== undefined) {
                const thresholdVal = parseInt(threshold, 10);
                if (!isNaN(thresholdVal) && item.quantity < thresholdVal) {
                    lowStockItems.push({
                        ...item,
                        configuredThreshold: thresholdVal
                    });
                }
            }
        }

        if (lowStockItems.length === 0) {
            container.innerHTML = `
            <div style="
                text-align: center;
                color: #94a3b8;
                padding: 1rem;
            ">
                Configure thresholds on stock items to see alerts here
            </div>
            `;
            return;
        }

        container.innerHTML = lowStockItems.slice(0, 5).map(item => `
        <a
            href="/stock/item/${item.pk}/"
            style="
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem 0.75rem;
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 0.375rem;
                text-decoration: none;
                transition: all 0.2s;
            "
            onmouseover="this.style.borderColor='${alertColor}60'; this.style.boxShadow='0 2px 8px ${alertColor}20'"
            onmouseout="this.style.borderColor='#e2e8f0'; this.style.boxShadow='none'"
        >
            <div style="
                width: 8px;
                height: 8px;
                background: ${alertColor};
                border-radius: 50%;
            "></div>
            <div style="flex: 1; min-width: 0;">
                <div style="
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: #1e293b;
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                ">${item.part_detail?.name || 'Unknown Part'}</div>
                <div style="
                    font-size: 0.75rem;
                    color: #94a3b8;
                ">${item.location_detail?.pathstring || 'No Location'}</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.875rem; font-weight: 600; color: ${alertColor};">
                    ${item.quantity} / ${item.configuredThreshold}
                </div>
            </div>
        </a>
        `).join('');

    } catch (error) {
        console.error('Error loading low stock items:', error);
        container.innerHTML = `
        <div style="
            text-align: center;
            color: #94a3b8;
            padding: 1rem;
        ">
            Failed to load stock data
        </div>
        `;
    }
}
