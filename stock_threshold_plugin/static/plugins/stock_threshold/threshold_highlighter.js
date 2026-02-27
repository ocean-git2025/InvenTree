/**
 * Stock Threshold Highlighter for InvenTree.
 *
 * Highlights stock items below configured threshold in stock list views.
 */

let lowStockIds = [];
let isInitialized = false;
let config = {
    apiUrl: '/plugin/stock-threshold/threshold-check/',
    alertColor: '#fef2f2',
    borderColor: '#ef4444',
};

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

async function loadLowStockIds() {
    try {
        const response = await fetch(config.apiUrl, {
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
        });

        if (response.ok) {
            const data = await response.json();
            lowStockIds = data.low_stock_ids || [];
            console.log(`[StockThreshold] Loaded ${lowStockIds.length} low stock items`);
        }
    } catch (error) {
        console.error('[StockThreshold] Failed to load low stock IDs:', error);
        lowStockIds = [];
    }
}

function extractStockIdFromRow(row) {
    const links = row.querySelectorAll('a[href*="/stock/item/"]');
    for (const link of links) {
        const match = link.href.match(/\/stock\/item\/(\d+)/i);
        if (match) {
            return parseInt(match[1], 10);
        }
    }

    const rowId = row.getAttribute('data-row-key') || row.getAttribute('data-pk');
    if (rowId) {
        const parsed = parseInt(rowId, 10);
        if (!isNaN(parsed)) {
            return parsed;
        }
    }

    const dataAttributes = ['data-pk', 'data-id', 'data-item'];
    for (const attr of dataAttributes) {
        const val = row.getAttribute(attr);
        if (val) {
            const parsed = parseInt(val, 10);
            if (!isNaN(parsed)) {
                return parsed;
            }
        }
    }

    return null;
}

function applyHighlightToRow(row, stockId) {
    if (lowStockIds.includes(stockId)) {
        row.style.backgroundColor = config.alertColor + ' !important';
        row.style.setProperty('background-color', config.alertColor, 'important');
        row.style.borderLeft = `4px solid ${config.borderColor}`;
        row.classList.add('stock-threshold-alert');

        const cells = row.querySelectorAll('td');
        cells.forEach((cell) => {
            cell.style.backgroundColor = config.alertColor;
        });
    } else {
        row.style.removeProperty('border-left');
        row.classList.remove('stock-threshold-alert');
    }
}

function highlightTableRows() {
    if (lowStockIds.length === 0) {
        return;
    }

    const selectors = [
        'table tbody tr',
        '[data-testid*="stock"] tr',
        '[class*="TableBody"] tr',
        '[class*="table-row"]',
        '[role="row"]',
    ];

    let highlightedCount = 0;
    for (const selector of selectors) {
        const rows = document.querySelectorAll(selector);
        rows.forEach((row) => {
            const stockId = extractStockIdFromRow(row);
            if (stockId !== null) {
                applyHighlightToRow(row, stockId);
                if (lowStockIds.includes(stockId)) {
                    highlightedCount++;
                }
            }
        });
    }

    if (highlightedCount > 0) {
        console.log(`[StockThreshold] Highlighted ${highlightedCount} table rows`);
    }
}

function injectStyles() {
    if (document.getElementById('stock-threshold-styles')) {
        return;
    }

    const style = document.createElement('style');
    style.id = 'stock-threshold-styles';
    style.textContent = `
        tr.stock-threshold-alert,
        tr.stock-threshold-alert td {
            background-color: ${config.alertColor} !important;
        }
        tr.stock-threshold-alert {
            border-left: 4px solid ${config.borderColor} !important;
        }
    `;
    document.head.appendChild(style);
}

function observeTableChanges() {
    const observer = new MutationObserver((mutations) => {
        let shouldUpdate = false;
        for (const mutation of mutations) {
            if (mutation.addedNodes.length > 0) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === 1) {
                        if (
                            node.tagName === 'TR' ||
                            node.tagName === 'TABLE' ||
                            node.tagName === 'TBODY' ||
                            node.querySelector?.('table') ||
                            node.classList?.contains?.('table')
                        ) {
                            shouldUpdate = true;
                            break;
                        }
                    }
                }
            }
            if (shouldUpdate) break;
        }
        if (shouldUpdate) {
            setTimeout(highlightTableRows, 100);
        }
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true,
    });

    return observer;
}

function isStockPage() {
    const url = window.location.href;
    return (
        url.includes('/stock') ||
        url.includes('/plugin/stock') ||
        document.querySelector('[data-testid*="stock"]') ||
        document.querySelector('h1')?.textContent?.toLowerCase().includes('stock')
    );
}

export function init(target, data) {
    if (isInitialized) {
        return;
    }

    const context = data?.context || {};
    config.apiUrl = context.api_url || config.apiUrl;
    config.alertColor = context.alert_color || config.alertColor;
    config.borderColor = context.border_color || config.borderColor;

    injectStyles();

    let observer = null;

    async function initialize() {
        await loadLowStockIds();
        highlightTableRows();

        if (!observer) {
            observer = observeTableChanges();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
            initialize();
        }
    });

    window.addEventListener('popstate', () => {
        if (isStockPage()) {
            initialize();
        }
    });

    const originalPushState = history.pushState;
    history.pushState = function (...args) {
        originalPushState.apply(this, args);
        setTimeout(() => {
            if (isStockPage()) {
                initialize();
            }
        }, 500);
    };

    isInitialized = true;
    console.log('[StockThreshold] Plugin initialized');
}

export function renderPanel(target, data) {
    init(target, data);
}
