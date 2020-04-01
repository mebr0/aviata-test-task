from django.core.cache import cache
from django.http import JsonResponse


def get_ticket(request):
    date = request.GET.get('date')
    fly_from = request.GET.get('fly_from')
    fly_to = request.GET.get('fly_to')

    if not date or not fly_to or not fly_from:
        return JsonResponse({'message': 'Not all required fields'}, status=400)

    tickets = cache.get('tickets')

    if not tickets:
        return JsonResponse({'message': 'Tickets not found'}, status=404)

    ticket = tickets.get(f'{date}_{fly_from}_{fly_to}')

    if not ticket:
        return JsonResponse({'message': 'Ticket not in cache'}, status=404)

    return JsonResponse({'data': ticket, 'date': date, 'fly_from': fly_from, 'fly_to': fly_to}, status=200)
