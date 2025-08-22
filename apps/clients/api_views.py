from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Client


@login_required
@require_http_methods(["GET"])
def client_detail_api(request, client_id):
    """API endpoint to get client details"""
    try:
        # Get the client for the current user's company
        company_profile = request.user.company_profile
        if company_profile:
            client = Client.objects.get(id=client_id, company=company_profile)
            
            # Return client data as JSON
            client_data = {
                'id': client.id,
                'name': client.name,
                'email': client.email or '',
                'phone': client.phone or '',
                'address': client.address or '',
                'created_at': client.created_at.strftime('%B %d, %Y') if client.created_at else '',
            }
            
            return JsonResponse({
                'success': True,
                'client': client_data
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Company profile not found'
            }, status=404)
            
    except Client.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Client not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 