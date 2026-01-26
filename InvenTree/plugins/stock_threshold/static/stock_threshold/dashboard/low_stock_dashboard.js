"""Low stock dashboard item for InvenTree."""

/**
 * Low stock dashboard component
 */
function LowStockDashboard() {
    const [lowStockItems, setLowStockItems] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    // Fetch low stock items
    useEffect(() => {
        const fetchLowStockItems = async () => {
            setIsLoading(true);
            setError(null);

            try {
                // Fetch all parts with minimum_stock > 0
                const partsResponse = await fetch('/api/part/?minimum_stock__gt=0', {
                    headers: {
                        'Authorization': `Token ${getToken()}`,
                    },
                });

                if (!partsResponse.ok) {
                    throw new Error('Failed to fetch parts');
                }

                const partsData = await partsResponse.json();
                const parts = partsData.results;

                // Filter parts with low stock
                const lowStock = parts.filter(part => {
                    return part.available_stock < part.minimum_stock;
                });

                setLowStockItems(lowStock);
            } catch (err) {
                setError('Error fetching low stock items');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchLowStockItems();

        // Refresh every 5 minutes
        const interval = setInterval(fetchLowStockItems, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    if (isLoading) {
        return (
            <div className="text-center py-4">
                <div className="spinner-border" role="status">
                    <span className="sr-only">Loading...</span>
                </div>
                <p className="mt-2">Loading low stock items...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="alert alert-danger">
                {error}
            </div>
        );
    }

    return (
        <div className="low-stock-dashboard">
            <h5 className="text-center mb-3">
                <i className="fas fa-exclamation-triangle text-warning mr-2"></i>
                Low Stock Items
                <span className="badge badge-danger ml-2">{lowStockItems.length}</span>
            </h5>

            {lowStockItems.length === 0 ? (
                <div className="text-center py-4">
                    <i className="fas fa-check-circle text-success fa-2x mb-2"></i>
                    <p>No items with low stock</p>
                </div>
            ) : (
                <div className="list-group" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {lowStockItems.slice(0, 10).map(item => {
                        const stockPercentage = (item.available_stock / item.minimum_stock) * 100;
                        
                        return (
                            <a 
                                href={`/part/${item.id}`} 
                                className="list-group-item list-group-item-action"
                                key={item.id}
                            >
                                <div className="d-flex justify-content-between align-items-center">
                                    <div>
                                        <h6 className="mb-0">{item.name}</h6>
                                        <small className="text-muted">{item.IPN || 'No IPN'}</small>
                                    </div>
                                    <div className="text-right">
                                        <span className="badge badge-danger">
                                            {item.available_stock} / {item.minimum_stock}
                                        </span>
                                    </div>
                                </div>
                                <div className="mt-2">
                                    <div className="progress" style={{ height: '6px' }}>
                                        <div 
                                            className="progress-bar bg-danger" 
                                            role="progressbar"
                                            style={{ width: `${Math.min(100, stockPercentage)}%` }}
                                            aria-valuenow={stockPercentage}
                                            aria-valuemin="0"
                                            aria-valuemax="100"
                                        ></div>
                                    </div>
                                </div>
                            </a>
                        );
                    })}
                    {lowStockItems.length > 10 && (
                        <div className="list-group-item text-center text-muted">
                            ... and {lowStockItems.length - 10} more items
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Register the dashboard item
registerDashboardItem('low-stock-dashboard', LowStockDashboard);
