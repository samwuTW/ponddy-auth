from django.conf import settings
from rest_framework.permissions import DjangoModelPermissions


API_AGENT_PROPERTY_NAME = getattr(
    settings,
    'API_AGENT_PROPERTY_NAME',
    '_api_agent'
)


class SSODjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_permission(self, request, view):
        api_agent = getattr(request.user, API_AGENT_PROPERTY_NAME, None)
        queryset = self._queryset(view)
        perms = self.get_required_permissions(request.method, queryset.model)
        return (super().has_permission(request, view) or
                (api_agent and api_agent.has_perms(perms)))
