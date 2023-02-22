from django.http import JsonResponse, HttpResponse
from TableManagement.models import Table
from ReservationManagement.models import Reservation
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import adminOnly

# Create your views here.
@adminOnly
def getTables(request):
    if request.method == "GET":
        tables = Table.objects.all().values()
        tables = json.dumps(list(tables),cls=DjangoJSONEncoder)
        return JsonResponse({'tables':tables})
    else:
        return HttpResponse("invalid method")
@adminOnly
def addTable(request):
    if request.method == "POST":
        body = request.POST
        seats = int(body['seats'])
        number = body['number']
        if seats>=1 and seats<=12:
            table = Table(number=number,seats=seats)
            table.save()
            return HttpResponse("table created successfully")
        else:
            return HttpResponse("table seats should be from 1 to 12")
    else:
        return HttpResponse("invalid method")

@adminOnly
def deleteTable(request):
    if request.method == "DELETE":
        params = request.GET
        number = params['number']
        try:
            table = Table.objects.filter(number=number)[0]
        except:
            return HttpResponse("table doesn't exist")
        reservations = Reservation.objects.filter(
                table=table,
                start__lte=datetime.datetime.now(),
                end__gte=datetime.datetime.now()
            )
        if reservations.exists() == False:
            table.delete()
            return HttpResponse("Table deleted successfully")
        else:
            return HttpResponse("Table is reserved and can't be deleted")
    else:
        return HttpResponse("invalid method")