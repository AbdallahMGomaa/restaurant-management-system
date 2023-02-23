from django.http import JsonResponse
from UserManagement.models import User
import jwt, time, json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import adminOnly, processJson
from django.views.decorators.http import require_GET, require_POST, require_http_methods

# Create your views here.
@adminOnly
@require_POST
@processJson
def createUser(body):
    try:
        name = body['name']
        number = body['number']
        role = body['role']
        password = body['password']
    except:
        return JsonResponse({"error":"missing inputs"})
    if len(password)>=6:
        if name != None and password != None and number != None and role != None:
            if role not in ['admin','employee']:
                return JsonResponse({"error":"invalid role"})
            elif User.objects.filter(number=number).exists():
                return JsonResponse({"error":"user already exists"})                
            user = User(name=name, password=password,number=number, role=role)
            user.save()
            encoded_jwt = jwt.encode({'number':user.number,'name': user.name,'role':user.role,'time':time.time()},"secret",'HS256')
            return JsonResponse({"jwt":encoded_jwt})
        else:
            return JsonResponse({"error":"attributes can't be None"})
    else:
        return JsonResponse({"error":"password too short"})


@require_POST
@processJson
def login(body):
    try:
        number = body['number']
        password = body['password']
    except:
        return JsonResponse({"error":"missing login info"})
    try:
        user = User.objects.filter(number=number)[0]
    except:
        return JsonResponse({"error":"user not found"})
    if user.password != password:
        return JsonResponse({"error":"invlid password"})
    encoded_jwt = jwt.encode({'number':user.number,'name': user.name,'role':user.role,'time':time.time()},"secret",'HS256')
    return JsonResponse({'jwt':encoded_jwt})


@adminOnly 
@require_http_methods(['DELETE'])
@processJson
def deleteUser(body):
    try:
        number = body['number']   
    except:
        return JsonResponse({"error":"user number required"}) 
    try:
        user = User.objects.filter(number=number)[0]
        user.delete()
        return JsonResponse({"message":"User deleted successfully"})
    except:
        return JsonResponse({"message":"user doesn't exist"})


@adminOnly
@require_GET
def getUsers(request):
    users = User.objects.all().values()
    users = json.dumps(list(users),cls=DjangoJSONEncoder)
    return JsonResponse({'users': users})        
