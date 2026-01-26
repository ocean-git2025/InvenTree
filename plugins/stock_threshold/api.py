"""API endpoints for stock_threshold plugin."""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from part.models import Part
from plugins.stock_threshold.plugin import StockThreshold


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def threshold_api(request, part_id):
    """API endpoint for stock threshold operations."""
    try:
        part = Part.objects.get(id=part_id)
    except Part.DoesNotExist:
        return JsonResponse({'error': 'Part not found'}, status=404)

    if request.method == 'GET':
        # Get stock threshold
        try:
            threshold = part.stock_threshold
            return JsonResponse({
                'part_id': part.id,
                'part_number': part.part_number,
                'name': part.name,
                'stock_threshold': threshold.stock_threshold
            })
        except StockThreshold.DoesNotExist:
            return JsonResponse({
                'part_id': part.id,
                'part_number': part.part_number,
                'name': part.name,
                'stock_threshold': 0
            })

    elif request.method == 'POST':
        # Update stock threshold
        try:
            data = json.loads(request.body)
            threshold_value = data.get('stock_threshold', 0)
            
            # Ensure threshold is a positive integer
            threshold_value = max(0, int(threshold_value))
            
            # Create or update stock threshold
            threshold, created = StockThreshold.objects.update_or_create(
                part=part,
                defaults={'stock_threshold': threshold_value}
            )
            
            return JsonResponse({
                'part_id': part.id,
                'stock_threshold': threshold.stock_threshold,
                'message': 'Stock threshold updated successfully'
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'Invalid threshold value'}, status=400)


@csrf_exempt
@require_http_methods(['POST'])
def import_thresholds_api(request):
    """API endpoint for importing stock thresholds."""
    if not request.FILES.get('file'):
        return JsonResponse({'error': 'No file provided'}, status=400)

    csv_file = request.FILES['file']
    
    # Import thresholds
    from plugins.stock_threshold.plugin import StockThresholdPlugin
    plugin = StockThresholdPlugin()
    
    # Read CSV file
    import io
    csv_content = io.StringIO(csv_file.read().decode('utf-8'))
    
    result = plugin.import_stock_thresholds(csv_content)
    
    return JsonResponse(result)


@require_http_methods(['GET'])
def export_thresholds_api(request):
    """API endpoint for exporting stock thresholds."""
    # Get version parameter
    version = request.GET.get('version', 'stable')
    
    # Export thresholds
    from plugins.stock_threshold.plugin import StockThresholdPlugin
    plugin = StockThresholdPlugin()
    
    # Get all parts
    from part.models import Part
    parts = Part.objects.all()
    
    # Create export data
    export_data = []
    for part in parts:
        try:
            threshold = part.stock_threshold
            threshold_value = threshold.stock_threshold
        except StockThreshold.DoesNotExist:
            threshold_value = 0
        
        if version == 'v0.12.x':
            # v0.12.x format: id, part_number, stock_threshold
            item = {
                'id': part.id,
                'part_number': part.part_number,
                'stock_threshold': threshold_value,
            }
        else:
            # Stable branch format: id, name, part_number, description, stock_threshold
            item = {
                'id': part.id,
                'name': part.name,
                'part_number': part.part_number,
                'description': part.description or '',
                'stock_threshold': threshold_value,
            }
        
        export_data.append(item)
    
    # Generate CSV
    import csv
    import io
    output = io.StringIO()
    
    if export_data:
        fieldnames = export_data[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(export_data)
    
    # Return CSV response
    response = JsonResponse({'csv': output.getvalue()})
    response['Content-Disposition'] = 'attachment; filename="stock_thresholds.csv"'
    return response
