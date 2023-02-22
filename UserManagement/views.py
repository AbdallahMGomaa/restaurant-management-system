from django.http import JsonResponse, HttpResponse
from UserManagement.models import User
import jwt, time, json
from django.core.serializers.json import DjangoJSONEncoder
from RMS.auth import adminOnly

# Create your views here.
@adminOnly
def createUser(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        try:
            name = body['name']
            number = body['number']
            role = body['role']
            password = body['password']
        except:
            return HttpResponse("missing inputs")
        if len(password)>=6:
            if name != None and password != None and number != None and role != None:
                if role not in ['admin','employee']:
                    return HttpResponse("invalid role")
                elif User.objects.filter(number=number).exists():
                    return HttpResponse("user already exists")                
                user = User(name=name, password=password,number=number, role=role)
                user.save()
                encoded_jwt = jwt.encode({'number':user.number,'name': user.name,'role':user.role,'time':time.time()},"secret",'HS256')
                return JsonResponse({"jwt":encoded_jwt})
            else:
                return HttpResponse("attributes can't be None")
        else:
            return HttpResponse("password too short")
    else:
        return HttpResponse("invalid method")


def login(request):
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        try:
            number = body['number']
            password = body['password']
        except:
            return HttpResponse("missing login info")
        try:
            user = User.objects.filter(number=number)[0]
        except:
            return HttpResponse("user not found")
        if user.password != password:
            return HttpResponse("invlid password")
        encoded_jwt = jwt.encode({'number':user.number,'name': user.name,'role':user.role,'time':time.time()},"secret",'HS256')
        return JsonResponse({'jwt':encoded_jwt})
    else:
        return HttpResponse("Invalid method")

@adminOnly 
def deleteUser(request):
    if request.method == 'DELETE':
        body = json.loads(request.body.decode('utf-8'))
        try:
            number = body['number']   
        except:
            return HttpResponse("user number required") 
        try:
            user = User.objects.filter(number=number)[0]
            user.delete()
            return HttpResponse("User deleted successfully")
        except:
            return HttpResponse("user doesn't exist")
    else:
        return HttpResponse("Invalid method")

@adminOnly
def getUsers(request):
    if request.method == "GET":        
        users = User.objects.all().values()
        users = json.dumps(list(users),cls=DjangoJSONEncoder)
        return JsonResponse({'users': users})        
    else:
        return HttpResponse("invalid method")