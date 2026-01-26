/**
 * Stock threshold panel for part detail page.
 */

class StockThresholdPanel extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            threshold: 0,
            loading: true,
            error: null
        };
    }

    componentDidMount() {
        this.fetchStockThreshold();
    }

    fetchStockThreshold() {
        const { partId } = this.props.context;
        
        // Fetch stock threshold data from API
        fetch(`/api/plugin/stockthreshold/threshold/${partId}/`)
            .then(response => response.json())
            .then(data => {
                this.setState({ 
                    threshold: data.stock_threshold || 0,
                    loading: false 
                });
            })
            .catch(error => {
                console.error('Error fetching stock threshold:', error);
                this.setState({ 
                    error: 'Failed to load stock threshold',
                    loading: false 
                });
            });
    }

    render() {
        const { threshold, loading, error } = this.state;
        const { part } = this.props.context;
        
        if (loading) {
            return (
                <div className="panel-content">
                    <div className="text-center">
                        <div className="spinner-border" role="status">
                            <span className="sr-only">Loading...</span>
                        </div>
                    </div>
                </div>
            );
        }

        if (error) {
            return (
                <div className="panel-content">
                    <div className="alert alert-danger">
                        {error}
                    </div>
                </div>
            );
        }

        // Calculate current stock level
        const currentStock = part.total_stock || 0;
        const isLowStock = currentStock < threshold;

        return (
            <div className="panel-content">
                <div className="form-group">
                    <label htmlFor="stock_threshold">Stock Threshold</label>
                    <input 
                        type="number" 
                        id="stock_threshold" 
                        className="form-control"
                        value={threshold}
                        min="0"
                        onChange={(e) => this.handleThresholdChange(e.target.value)}
                    />
                    <small className="form-text text-muted">
                        Minimum stock level before notification
                    </small>
                </div>

                <div className={`alert ${isLowStock ? 'alert-danger' : 'alert-success'}`}>
                    <strong>Current Stock: {currentStock} / {threshold}</strong>
                    {isLowStock && (
                        <p className="mb-0">
                            <i className="fas fa-exclamation-triangle"></i> Stock is below threshold!
                        </p>
                    )}
                </div>
            </div>
        );
    }

    handleThresholdChange(value) {
        const { partId } = this.props.context;
        const threshold = parseInt(value) || 0;
        
        // Update stock threshold via API
        fetch(`/api/plugin/stockthreshold/threshold/${partId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ stock_threshold: threshold })
        })
        .then(response => response.json())
        .then(data => {
            this.setState({ threshold: data.stock_threshold });
            // Show success message
            showToast('Stock threshold updated successfully');
        })
        .catch(error => {
            console.error('Error updating stock threshold:', error);
            showToast('Failed to update stock threshold', 'error');
        });
    }
}

// Register the panel
window.pluginRegisterPanel('stock_threshold', StockThresholdPanel);
