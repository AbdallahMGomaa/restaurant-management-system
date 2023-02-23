from django.http import JsonResponse
from TableManagement.models import Table
from ReservationManagement.models import Reservation
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import authorized, adminOnly
from django.views.decorators.http import require_GET, require_POST, require_http_methods

@authorized
@require_GET
def checkAvailableTimeSlots(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({"error":"Json body not found"})
    try:
        requiredSeats = int(body['seats'])
    except:
        return JsonResponse({"error":"seats number is required"})
    minimumTable = Table.objects.filter(seats__gte=requiredSeats).order_by('seats').first()
    if not minimumTable:
        return JsonResponse({"error":"no tables available"})
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
    timeNow = datetime.datetime.now().astimezone()

    if len(reservedSlots) == 0:
        availableSlots = [[timeNow, end_of_day]]
    else:
        if  timeNow < reservedSlots[0][0]:
            availableSlots = [[timeNow, reservedSlots[0][0]]]
        for i in range(len(reservedSlots)-1):
            if timeNow < reservedSlots[0][0]:
                availableSlots.append([reservedSlots[i][1], reservedSlots[i+1][0]])
        if timeNow < reservedSlots[0][0]:
            availableSlots.append([reservedSlots[len(reservedSlots)-1][1], end_of_day])
    result = {'table': minimumTable.number, 'seats': minimumTable.seats, 'availableSlots': availableSlots}
    return JsonResponse(result)


@authorized
@require_POST
def reserveTimeSlot(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({"error":"Json body not found"})
    try:
        tableNumber = body['table']
        start = body['start']
        end = body['end']
    except:
        return JsonResponse({"error":"missing inputs"})
    start = datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S.%f')
    end = datetime.datetime.strptime(end,'%Y-%m-%d %H:%M:%S.%f')
    end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
    if start<datetime.datetime.now() or end>end_of_day or start>=end:
        return JsonResponse({"error":"invalid time range"})
    table = Table.objects.filter(number=tableNumber)[0]
    reservations = Reservation.objects.filter(
        table=table,
        start__gte=datetime.datetime.now(),
        end__lte=end_of_day
    )
    start = start.replace(tzinfo=datetime.timezone.utc)
    end = end.replace(tzinfo=datetime.timezone.utc)
    for reservation in reservations:
        if (start>=reservation.start and start<=reservation.end) or (end>=reservation.start and end<=reservation.end):
            return JsonResponse({"error":"table already reserved"})
    reservation = Reservation(table=table,start=start,end=end)
    reservation.save()
    return JsonResponse({"message":"table reserved successfully"})

@authorized
@require_GET
def getTodaysReservations(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({"error":"Json body not found"})
    start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(0,0,0,0))
    end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999))
    try:
        sortDirection = body['sort']
    except:
        sortDirection = None
    try:
        pagination = body['pagination']
        size = int(body['size'])
        page = int(body['page'])
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


@adminOnly
@require_GET
def getAllReservations(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({"error":"Json body not found"})
    table = None
    try:
        tableNumber = body['table']
    except:
        tableNumber = None
    try:
        start = body['start']
        end = body['end']
    except:
        start = None
        end = None
    try:
        pagination = body['pagination']
        size = int(body['size'])
        page = int(body['page'])
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


@authorized
@require_http_methods(['DELETE'])
def deleteReservation(request):
    try:
        body = json.loads(request.body.decode('utf-8'))
    except:
        return JsonResponse({"error":"Json body not found"})
    try:
        reservationId = body['id']
    except:
        return JsonResponse({"error":"reservation ID is required"})
    try:
        reservation = Reservation.objects.filter(id=reservationId)[0]
    except:
        return JsonResponse({"error":"reservation id doesn't exist"})
    if reservation.start>datetime.datetime.now().replace(tzinfo=datetime.timezone.utc):
        start_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(0,0,0,0)).replace(tzinfo=datetime.timezone.utc)
        end_of_day = datetime.datetime.combine(datetime.datetime.now(), datetime.time(23,59,59,999999)).replace(tzinfo=datetime.timezone.utc)
        if reservation.start>=start_of_day and reservation.end<=end_of_day:
            reservation.delete()
            return JsonResponse({"message":"reservation deleted successfully"})
        else:
            return JsonResponse({"error":"reservation is not available today"})
    else:
        return JsonResponse({"error":"reservation date already passed"})
