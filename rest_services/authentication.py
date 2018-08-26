import requests
from jose import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

class ApiAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.META.get('HTTP_AUTHORIZATION')
        if not auth:
            return None
        
        parts = auth.split()
        if parts[0].lower() == 'bearer':
            access_token = parts[1]
        else:
            access_token = auth

        try:
            payload = jwt.decode(access_token, settings.USER_AUTH_SECRET_KEY, algorithms=['HS256'], audience=settings.USER_AUTH_JWT_AUD)
            user_id = payload['userId']
        
            url = settings.USERS_END_POINT + '/' + user_id
            req = requests.get(url, headers={'x-api-key': settings.USER_AUTH_X_API_KEY})
            if req.status_code == requests.codes.ok:
                user = req.json()
            else:
                raise exceptions.AuthenticationFailed('No such user')
        except jwt.JWTError:
            raise exceptions.AuthenticationFailed('Invalid JWT')

        return (user, None)
