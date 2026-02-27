/**
 * Stock Threshold Spotlight Action for InvenTree.
 *
 * Provides a quick action to navigate to the stock list
 * to view items that are below their threshold.
 */

export function viewLowStockItems(target, data) {
    if (!target) {
        console.error('StockThresholdPlugin: No target provided');
        return;
    }

    // Navigate to stock list page
    // The frontend will need to handle filtering based on threshold data
    const url = '/stock/items/';
    window.location.href = url;
}
