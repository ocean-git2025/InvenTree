/**
 * Stock Threshold Plugin - Column Renderer
 * 
 * This script adds a custom column renderer for the StockItem table
 * to display low stock warnings with red highlighting.
 */

/**
 * Render the quantity column with threshold indicator
 * 
 * @param {Object} record - The stock item record
 * @param {Object} options - Rendering options
 * @returns {Object} Rendered cell content
 */
function renderQuantityWithThreshold(record, options) {
    const quantity = record?.quantity ?? 0;
    const threshold = record?.threshold_data?.threshold ?? null;
    const isLowStock = record?.threshold_data?.is_low_stock ?? false;
    const enabled = record?.threshold_data?.enabled ?? false;
    
    // Build the display content
    let content = quantity;
    let className = '';
    let style = {};
    
    // If threshold is configured and enabled
    if (threshold !== null && enabled) {
        if (isLowStock) {
            // Low stock - show red warning
            className = 'threshold-low-stock';
            style = {
                color: '#dc2626',  // Red color
                fontWeight: 'bold',
                backgroundColor: '#fef2f2',  // Light red background
                padding: '2px 8px',
                borderRadius: '4px',
                border: '1px solid #fecaca'
            };
            content = `${quantity} ⚠️`;
        } else {
            // Above threshold - show green indicator
            className = 'threshold-ok';
            style = {
                color: '#16a34a',  // Green color
                fontWeight: '500'
            };
        }
    }
    
    return {
        content: content,
        className: className,
        style: style,
        title: threshold !== null ? `Threshold: ${threshold}` : null
    };
}

/**
 * Add threshold column to stock item table
 * 
 * This function modifies the StockItem table columns to include
 * threshold information and visual indicators.
 */
function addThresholdColumn() {
    // Check if we're on a page with the stock item table
    const stockTable = document.querySelector('[data-table="stock-item"]');
    if (!stockTable) return;
    
    // The actual implementation would hook into the React table component
    // This is a placeholder for the integration pattern
    console.log('Stock Threshold Plugin: Adding threshold column');
}

// Export for use by the plugin system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        renderQuantityWithThreshold,
        addThresholdColumn
    };
}
