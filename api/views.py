from django.core.cache import cache
from django.http import JsonResponse


def search_ticket(request):
    date = request.GET.get('date')
    fly_from = request.GET.get('fly_from')
    fly_to = request.GET.get('fly_to')

    if not date or not fly_to or not fly_from:
        return JsonResponse({'status': 'OK', 'message': 'Not all required fields'})

    tickets = cache.get(date)

    if not tickets:
        return JsonResponse({'status': 'OK', 'message': 'Ticket not in cache'})

    for ticket in tickets:
        if ticket.get('from') == fly_from and ticket.get('to') == fly_to:
            return JsonResponse({'status': 'OK', 'data': ticket, 'date': date})

    return JsonResponse({'status': 'OK', 'message': 'Ticket not found'})
