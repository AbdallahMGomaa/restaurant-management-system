import jwt
import time
from django.http import HttpResponse


def authorized(func):
    def wrap(*args, **kwargs):
        request = args[0]
        headers = request.headers
        jwt_encoded = headers['jwt']
        jwt_decoded = jwt.decode(jwt_encoded,'secret',algorithms=['HS256'])
        if (time.time()-jwt_decoded['time'])/86400<=1:
            result = func(*args,**kwargs)
            return result
        else:
            return HttpResponse("token expired")
    return wrap

def adminOnly(func):
    def wrap(*args, **kwargs):
        request = args[0]
        headers = request.headers
        try:
            jwt_encoded = headers['jwt']
            jwt_decoded = jwt.decode(jwt_encoded,'secret',algorithms=['HS256'])
        except:
            return HttpResponse("token invalid")
        if jwt_decoded['role'] == 'admin':
            if (time.time()-jwt_decoded['time'])/86400<=1:
                result = func(*args,**kwargs)
                return result
            else:
                return HttpResponse("token expired")
        else:
            return HttpResponse("only admins authorized")
    return wrap