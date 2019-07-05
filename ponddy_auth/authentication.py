import json
import requests
from functools import partial

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, AnonymousUser

from rest_framework.authentication import get_authorization_header


User = get_user_model()
API_AGENT_PREFIX = getattr(settings, 'API_AGENT_PREFIX', 'api_agent')
API_AGENT_PROPERTY_NAME = getattr(
    settings,
    'API_AGENT_PROPERTY_NAME',
    '_api_agent'
)


def has_perm(self, perm):
    perm_cache_name = "_perm_cache"
    if not hasattr(self, perm_cache_name):
        setattr(self, perm_cache_name, {
            "%s.%s" % (ct, name)
            for ct, name
            in self.permissions.all().values_list(
                'content_type__app_label',
                'codename').order_by()
        })
    return perm in getattr(self, perm_cache_name)


def has_perms(self, perm_list):
    return all(self.has_perm(perm) for perm in perm_list)


def attach_permission_functions(obj):
    for function in [has_perm, has_perms]:
        setattr(obj, function.__name__, partial(function, obj))


class SSOAuthentication():
    def authenticate(self, request):
        token = get_authorization_header(request)
        check_token = requests.get(
            settings.AUTH_TOKEN_VALID_URL,
            headers={
                'authorization': token,
                'app': request.META.get('HTTP_APP', None),
                'api': request.META.get('HTTP_API', None),
                'status': str(request.META.get('HTTP_STATUS', None))
            }
        )
        if check_token.ok:
            payload = json.loads(check_token.content)
            user = AnonymousUser()
            if payload.get('email', False):
                user, _ = User.objects.get_or_create(
                    username=payload['email'],
                    email=payload['email']
                )
            api_agent = Group.objects.get(
                name="{prefix}_{api_agent}".format(
                    prefix=API_AGENT_PREFIX, api_agent=payload['api']
                )
            )
            attach_permission_functions(api_agent)
            setattr(user, API_AGENT_PROPERTY_NAME, api_agent)
            return (user, payload)
        return (None, None)
