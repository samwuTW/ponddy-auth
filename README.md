# Ponddy Auth Library
Provide the class for the Django restful framework authentication, accept the `Auth` token and check the name of <API_AGENT_PREFIX>_<API_ID> in django.contrib.auth.models.Group or not.
If the group exists then append the API_AGENT_PROPERTY_NAME into `request.user` let you can check either API or user permissions.

Provide the Django model permission class compatible with the restful framework, let it can support valid the permission what in this request contains the API's permission validation.

## Usage
### Install package
```shell-script
pip install -U ponddy-auth
```

### Install into restful framework authentication setting
```python
REST_FRAMEWORK = {
    # ...
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'ponddy_auth.authentication.SSOAuthentication',  # Add this line
    ),
}
```

## Settings
### `AUTH_TOKEN_VALID_URL`
The real Auth server URL
 - None default
### `API_AGENT_PREFIX`
The prefix of API name of group
 - Default: `api_agent_`
### `API_AGENT_PROPERTY_NAME`
The property name what injects into the `request.user` object
 - Default: `_api_agent`
### `PONDDY_AUTH_APP_NAME`
Your APP name
### `PONDDY_AUTH_API_CLIENT_ID`
Your client ID
### `PONDDY_AUTH_API_SECRET`
Your client secret
### `PONDDY_AUTH_API_TOKEN_PREFIX`
The token prefix, default is `SSO`

#### Alias
If you are already set some variables as another setting variable, you can change those to specify the settled variable name
### `PONDDY_AUTH_APP_NAME_SETTING_NAME`
Setting alias of `PONDDY_AUTH_APP_NAME`
### `PONDDY_AUTH_API_CLIENT_ID_SETTING_NAME`
Setting alias of `PONDDY_AUTH_API_CLIENT_ID`
### `PONDDY_AUTH_API_SECRET_SETTING_NAME`
Setting alias of `PONDDY_AUTH_API_SECRET`
### `PONDDY_AUTH_API_TOKEN_PREFIX_SETTING_NAME`
Setting alias of `PONDDY_AUTH_API_TOKEN_PREFIX`

## Permission
### Check permission manually
```python
# project/app/views.py
from rest_framework.decorators import api_view


@api_view(['GET'])
def my_view(request):
   if request.user._api_agent.has_perm('auth.view_users') or \
      request.user._api_agent.has_perms(['app.perm', 'app.perm']):
       # do something
       pass
```

### Use Permission class
```python
# project/app/views.py
from django.contrib.auth.models import User
from rest_framework import viewsets

from ponddy_auth.permissions import SSODjangoModelPermissions

from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [SSODjangoModelPermissions, ]
 ```
