import jwt
import time
import json
from django.http import JsonResponse


def authorized(func):
    def wrap(*args, **kwargs):
        request = args[0]
        headers = request.headers
        try:
            jwt_encoded = headers['jwt']
        except:
            return JsonResponse({"error":"jwt is missing"})
        try:
            jwt_decoded = jwt.decode(jwt_encoded,'secret',algorithms=['HS256'])
        except:
            return JsonResponse({"error":"token invalid"})
            
        if (time.time()-jwt_decoded['time'])/86400<=1:
            result = func(*args,**kwargs)
            return result
        else:
            return JsonResponse({"error":"token expired"})
    return wrap

def adminOnly(func):
    def wrap(*args, **kwargs):
        request = args[0]
        headers = request.headers
        try:
            jwt_encoded = headers['jwt']
        except:
            return JsonResponse({"error":"jwt is missing"})
        try:
            jwt_decoded = jwt.decode(jwt_encoded,'secret',algorithms=['HS256'])
        except:
            return JsonResponse({"error":"token invalid"})
        if jwt_decoded['role'] == 'admin':
            if (time.time()-jwt_decoded['time'])/86400<=1:
                result = func(*args,**kwargs)
                return result
            else:
                return JsonResponse({"error":"token expired"})
        else:
            return JsonResponse({"error":"only admins authorized"})
    return wrap

def processJson(func):
    def wrap(*args,**kwargs):
        request = args[0]
        try:
            body = json.loads(request.body.decode('utf-8'))
        except:
            return JsonResponse({"error":"Json body not found"})
        result = func(body)
        return result
    return wrap