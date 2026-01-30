export function renderStockThresholdPanel(params) {
    const { context, containerId } = params;
    const container = document.getElementById(containerId);
    
    if (!container) return;
    
    const { quantity, threshold, is_below_threshold, stock_item_id } = context;
    const diff = threshold - quantity;
    
    let statusColor = '#4caf50';
    let statusIcon = '✓';
    let statusText = 'Stock Level OK';
    
    if (is_below_threshold) {
        statusColor = '#d32f2f';
        statusIcon = '⚠️';
        statusText = 'Below Threshold';
    } else if (quantity <= threshold * 1.2) {
        statusColor = '#ff9800';
        statusIcon = '⚡';
        statusText = 'Low Stock Warning';
    }
    
    const html = `
        <div style="padding: 15px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <div style="font-size: 24px; color: ${statusColor};">
                    ${statusIcon} ${statusText}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
                <div style="background-color: #f5f5f5; padding: 12px; border-radius: 8px;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Current Quantity</div>
                    <div style="font-size: 24px; font-weight: bold; color: ${statusColor};">${quantity}</div>
                </div>
                <div style="background-color: #f5f5f5; padding: 12px; border-radius: 8px;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Threshold</div>
                    <div style="font-size: 24px; font-weight: bold;">${threshold}</div>
                </div>
            </div>
            
            <div style="margin-bottom: 10px;">
                <div style="font-size: 12px; color: #666; margin-bottom: 4px;">Stock Level Progress</div>
                <div style="height: 20px; background-color: #e0e0e0; border-radius: 10px; overflow: hidden;">
                    <div style="height: 100%; width: ${Math.min(100, (quantity / threshold) * 100)}%; background-color: ${statusColor}; transition: width 0.3s ease;"></div>
                </div>
            </div>
            
            ${is_below_threshold ? `
            <div style="background-color: #ffebee; color: #d32f2f; padding: 10px; border-radius: 4px; font-size: 14px;">
                ⚠️ Stock is ${diff} units below the threshold. Consider reordering!
            </div>
            ` : ''}
        </div>
    `;
    
    container.innerHTML = html;
}
