export function renderStockThresholdDashboard(params) {
    const { context, containerId } = params;
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    const { alert_count, items } = context;
    
    let html = `
        <div style="padding: 10px;">
            <div style="font-size: 18px; font-weight: bold; color: #d32f2f; margin-bottom: 10px;">
                ⚠️ Low Stock Alert: ${alert_count} items below threshold
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Part Name</th>
                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Quantity</th>
                        <th style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">Threshold</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const item of items) {
        const diff = item.threshold - item.quantity;
        html += `
            <tr style="background-color: #ffebee;">
                <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                    <a href="/stock/item/${item.pk}/" style="color: #d32f2f;">${item.part_name}</a>
                </td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd; color: #d32f2f; font-weight: bold;">
                    ${item.quantity}
                </td>
                <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">
                    ${item.threshold}
                </td>
            </tr>
        `;
    }
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}
