from django.http import JsonResponse, HttpResponse
from TableManagement.models import Table
from ReservationManagement.models import Reservation
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import authorized, adminOnly

@authorized
def checkAvailableTimeSlots(request):
    if request.method == 'GET':
        params = request.GET
        requiredSeats = params['seats']
        tables = Table.objects.filter(seats__gte=requiredSeats)
        if len(tables)==0:
            return HttpResponse("no tables available")
        minimumTable = tables[0]
        for table in tables:
            if minimumTable.seats>table.seats and minimumTable.seats>=requiredSeats:
                minimumTable = table
        end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
        reservations = Reservation.objects.filter(
            table=minimumTable,
            start__gte=datetime.datetime.now(),
            end__lte=end_of_day
        )
        reservedSlots = []
        for reservation in reservations:
            reservedSlots.append([reservation.start, reservation.end])
        reservedSlots = sorted(reservedSlots, key=lambda a: a[0])
        availableSlots = []
        if len(reservedSlots) == 0:
            availableSlots = [[datetime.datetime.now(), end_of_day]]
        else:
            if datetime.datetime.now() - reservedSlots[0][0] < 0:
                availableSlots = [[datetime.datetime.now(), reservedSlots[0][0]]]
            for i in range(len(reservedSlots)-1):
                if datetime.datetime.now() - reservedSlots[0][0] < 0:
                    availableSlots.append([reservedSlots[i][1], reservedSlots[i+1][0]])
            if datetime.datetime.now() - reservedSlots[0][0] < 0:
                availableSlots.append([reservedSlots[len(reservedSlots)-1][1], end_of_day])
        result = {'table': minimumTable.number, 'seats': minimumTable.seats, 'availableSlots': availableSlots}
        return JsonResponse(result)
    else:
        return HttpResponse("Invalid method")
@authorized
def reserveTimeSlot(request):
    if request.method == 'POST':
        content = request.POST
        tableNumber = content['table']
        start = content['start']
        end = content['end']
        start = datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S.%f')
        end = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M:%S.%f')
        end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
        if start<datetime.datetime.now() or end>end_of_day or start>=end:
            return HttpResponse("invalid time range")
        table = Table.objects.filter(number=tableNumber)[0]
        reservations = Reservation.objects.filter(
            table=table,
            start__gte=datetime.datetime.now(),
            end__lte=end_of_day
        )
        start = start.replace(tzinfo=datetime.timezone.utc)
        end = end.replace(tzinfo=datetime.timezone.utc)
        for reservation in reservations:
            if (start>=reservation.start and start<=reservation.end) or (end>=reservation.start and end<=reservation.start):
                return HttpResponse("table already reserved")
        reservation = Reservation(table=table,start=start,end=end)
        reservation.save()
        return HttpResponse("table reserved successfully")
    else: 
        return HttpResponse("Invalid method")
@authorized
def getTodaysReservations(request):
    if request.method == 'GET':
        params = request.GET
        start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(0,0,0,0))
        end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
        try:
            sortDirection = params['sort']
        except:
            sortDirection = None
        try:
            pagination = params['pagination']
            size = int(params['size'])
            page = int(params['page'])
        except:
            pagination = None
            size = None
            page = None
        reservations = Reservation.objects.filter(start__gte=start_of_day,end__lte=end_of_day)
        if sortDirection is not None:
            if sortDirection == 'asc':
                reservations = reservations.order_by('start')
            elif sortDirection == 'dsc':
                reservations = reservations.order_by('-start')
        reservations = reservations.values()
        if pagination is not None and page is not None and size is not None:
            start = size*(page-1)
            end = min(start+size,len(reservations))
            reservations = reservations[start:end]
        reservations = json.dumps(list(reservations),cls=DjangoJSONEncoder)
        return JsonResponse({'reservations':reservations})
    else:
        return HttpResponse("Invalid method")

@adminOnly
def getAllReservations(request):
    if request.method == 'GET':
        params = request.GET
        table = None
        try:
            tableNumber = params['table']
        except:
            tableNumber = None
        try:
            start = params['start']
            end = params['end']
        except:
            start = None
            end = None
        try:
            pagination = params['pagination']
            size = int(params['size'])
            page = int(params['page'])
        except:
            pagination = None
            size = None
            page = None
        if tableNumber is not None:
            table = Table.objects.filter(number=tableNumber)[0]
        if table is not None and start is not None and end is not None:
            reservations = Reservation.objects.filter(table=table,start__gte=start,end__lte=end).values()
        elif table is not None:
            reservations = Reservation.objects.filter(table=table).values()
        elif start is not None and end is not None:
            reservations = Reservation.objects.filter(start__gte=start,end__lte=end).values()
        else:
            reservations = Reservation.objects.all().values()
        if pagination is not None and page is not None and size is not None:
            start = size*(page-1)
            end = min(start+size,len(reservations))
            reservations = reservations[start:end]
        reservations = json.dumps(list(reservations),cls=DjangoJSONEncoder)
        return JsonResponse({'reservations':reservations})
            
    else:
        return HttpResponse("Invalid method")

@authorized
def deleteReservation(request):
    if request.method == 'DELETE':
        params = request.GET
        reservationId = params['id']
        try:
            reservation = Reservation.objects.filter(id=reservationId)[0]
        except:
            return HttpResponse("reservation id doesn't exist")
        if reservation.start>datetime.datetime.now().replace(tzinfo=datetime.timezone.utc):
            start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(0,0,0,0)).replace(tzinfo=datetime.timezone.utc)
            end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999)).replace(tzinfo=datetime.timezone.utc)
            if reservation.start>=start_of_day and reservation.end<=end_of_day:
                reservation.delete()
                return HttpResponse("reservation deleted successfully")
            else:
                return HttpResponse("reservation is not available today")
        else:
            return HttpResponse("reservation date already passed")
    else:
        return HttpResponse("Invalid method")