from django.http import JsonResponse
from TableManagement.models import Table
from ReservationManagement.models import Reservation
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import adminOnly
from django.views.decorators.http import require_GET, require_POST, require_http_methods

# Create your views here.
@adminOnly
@require_GET
def getTables(request):
    tables = Table.objects.all().values()
    tables = json.dumps(list(tables),cls=DjangoJSONEncoder)
    return JsonResponse({'tables':tables})


@adminOnly
@require_POST
def addTable(request):
    body = json.loads(request.body.decode('utf-8'))
    try:
        seats = int(body['seats'])
        number = body['number']
    except:
        return JsonResponse({"error":"inputs missing"})
    if seats>=1 and seats<=12:
        if Table.objects.filter(number=number).exists():
            return JsonResponse({"error":"table already exists"})
        table = Table(number=number,seats=seats)
        table.save()
        return JsonResponse({"message":"table created successfully"})
    else:
        return JsonResponse({"error":"table seats should be from 1 to 12"})


@adminOnly
@require_http_methods(['DELETE'])
def deleteTable(request):
    body = json.loads(request.body.decode('utf-8'))
    try:
        number = body['number']
    except:
        return JsonResponse({"error":"table number required"})
    try:
        table = Table.objects.filter(number=number)[0]
    except:
        return JsonResponse({"error":"table doesn't exist"})
    reservations = Reservation.objects.filter(
            table=table,
            start__lte=datetime.datetime.now(),
            end__gte=datetime.datetime.now()
        )
    if reservations.exists() == False:
        table.delete()
        return JsonResponse({"message":"Table deleted successfully"})
    else:
        return JsonResponse({"error":"Table is reserved and can't be deleted"})
