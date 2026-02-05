/**
 * Stock Threshold Plugin - Admin Settings Panel
 * 
 * This script provides the admin settings UI for the plugin.
 */

/**
 * Render plugin settings in the admin panel
 * 
 * @param {HTMLElement} container - The container element
 * @param {Object} settings - Current plugin settings
 */
function renderPluginSettings(container, settings) {
    if (!container) return;
    
    const html = `
        <div class="threshold-settings">
            <h4>Stock Threshold Configuration</h4>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="enable-warnings" 
                        ${settings.ENABLE_THRESHOLD_WARNINGS ? 'checked' : ''}>
                    Enable Threshold Warnings
                </label>
                <p class="help-text">Show low stock warnings in the user interface</p>
            </div>
            <div class="form-group">
                <label for="default-threshold">Default Threshold</label>
                <input type="number" id="default-threshold" 
                    value="${settings.DEFAULT_THRESHOLD}" min="0" step="1">
                <p class="help-text">Default threshold value for new configurations</p>
            </div>
            <div class="form-group">
                <label>
                    <input type="checkbox" id="show-badge" 
                        ${settings.SHOW_LOW_STOCK_BADGE ? 'checked' : ''}>
                    Show Low Stock Badge
                </label>
                <p class="help-text">Display visual badges for low stock items</p>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Export for use by the plugin system
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        renderPluginSettings
    };
}
