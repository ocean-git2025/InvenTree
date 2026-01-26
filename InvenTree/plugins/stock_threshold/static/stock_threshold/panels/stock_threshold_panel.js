/**
 * Stock threshold panel for part detail page
 */

class StockThresholdPanel extends Panel {
    constructor() {
        super();
        
        this.partId = null;
        this.partData = null;
    }
    
    static getPanelName() {
        return 'stock_threshold';
    }
    
    getTitle() {
        return 'Stock Threshold';
    }
    
    async getPanelData() {
        // Get part ID from URL
        const urlParts = window.location.pathname.split('/');
        this.partId = urlParts[urlParts.indexOf('part') + 1];
        
        // Fetch part data
        try {
            const response = await fetch(`/api/part/${this.partId}/`);
            this.partData = await response.json();
            return this.partData;
        } catch (error) {
            console.error('Error fetching part data:', error);
            return null;
        }
    }
    
    render() {
        if (!this.partData) {
            return `<div class="alert alert-info">Loading part data...</div>`;
        }
        
        const currentStock = this.partData.available_stock || 0;
        const currentThreshold = this.partData.minimum_stock || 0;
        const isLowStock = currentStock < currentThreshold;
        
        return `
            <div class="stock-threshold-panel">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <div class="form-group">
                            <label for="stock-threshold-input">Stock Threshold</label>
                            <input 
                                type="number" 
                                id="stock-threshold-input" 
                                class="form-control" 
                                value="${currentThreshold}"
                                min="0"
                                step="1"
                            >
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group">
                            <label>Current Stock</label>
                            <div class="input-group">
                                <input 
                                    type="number" 
                                    class="form-control" 
                                    value="${currentStock}"
                                    disabled
                                >
                                <span class="input-group-text ${isLowStock ? 'bg-danger text-white' : 'bg-success text-white'}">
                                    ${isLowStock ? 'Low Stock' : 'Stock OK'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-12">
                        <button id="save-threshold-btn" class="btn btn-primary">
                            Save Threshold
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    postRender() {
        // Add event listener for save button
        const saveBtn = document.getElementById('save-threshold-btn');
        if (saveBtn) {
            saveBtn.addEventListener('click', this.saveThreshold.bind(this));
        }
    }
    
    async saveThreshold() {
        const thresholdInput = document.getElementById('stock-threshold-input');
        const newThreshold = parseFloat(thresholdInput.value) || 0;
        
        try {
            const response = await fetch(`/api/part/${this.partId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify({
                    minimum_stock: newThreshold,
                }),
            });
            
            if (response.ok) {
                // Update part data
                this.partData = await response.json();
                // Re-render panel
                this.render();
                this.postRender();
                
                // Show success message
                showToast('success', 'Stock threshold updated successfully');
            } else {
                const errorData = await response.json();
                console.error('Error updating threshold:', errorData);
                showToast('error', 'Failed to update stock threshold');
            }
        } catch (error) {
            console.error('Error saving threshold:', error);
            showToast('error', 'Failed to update stock threshold');
        }
    }
}

// Register panel
Panel.registerPanel(StockThresholdPanel);
