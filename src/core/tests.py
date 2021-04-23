import json
from unittest.mock import patch
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.http import HttpRequest
from django.shortcuts import reverse
from django.test import TestCase
from jose import jwt
from ponddy_api_test_client import SSOClient

from ponddy_auth.authentication import SSOAuthentication

from .mocks import MockAuthHTTPResponse

SSO_AUTH_HEADER_PREFIX = getattr(settings, "SSO_AUTH_HEADER_PREFIX", "SSO")
API_AGENT_PREFIX = getattr(settings, "API_AGENT_PREFIX", "api_agent")


class TestAPIMixin:
    EMAIL = "abc@abc.xyz"
    APP = "APP"
    API = str(uuid4())
    SECRET = "SECRET"

    def get_payload(self):
        return {"email": self.EMAIL, "api": self.API}

    def set_up_api(self):
        self.api, _ = Group.objects.get_or_create(
            name="{prefix}_{api_agent}".format(prefix=API_AGENT_PREFIX, api_agent=self.API)
        )
        self._permission = "auth.view_user"
        self._perm_app_label, self._perm_codename = "auth.view_user".split(".")
        self.permission = Permission.objects.get(
            codename=self._perm_codename,
            content_type__app_label=self._perm_app_label,
        )
        self.api.permissions.add(self.permission)
        self.token = jwt.encode(self.get_payload(), self.SECRET)
        self.sso_client = SSOClient(
            token="{prefix} {token}".format(prefix=SSO_AUTH_HEADER_PREFIX, token=self.token)
        )


class APIClientTest(TestAPIMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.set_up_api()

    @patch("ponddy_auth.authentication.requests.get")
    def test_api_client_request_authenticated(self, mock_auth):
        from ponddy_auth.utils import APIClient

        client = APIClient(
            app_name=self.APP,
            api_client_id=self.API,
            api_secret=self.SECRET,
        )
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(
            content=json.dumps(client.payload)
        )
        request = HttpRequest()
        request.META = {f"HTTP_{key.upper()}": val for key, val in client.headers.items()}
        user, payload = SSOAuthentication().authenticate(request)
        assert user.is_anonymous is True
        assert hasattr(user, "_api_agent")
        api_agent = getattr(user, "_api_agent")
        assert isinstance(api_agent, Group)

        assert hasattr(api_agent, "has_perm")
        assert hasattr(api_agent, "has_perms")

        assert api_agent.has_perm(self._permission)
        assert api_agent.has_perms(
            [
                self._permission,
            ]
        )


class SSOAuthenticationTest(TestAPIMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.set_up_api()

    @patch("ponddy_auth.authentication.requests.get")
    def test_sso_auth_will_return_user_if_auth_valid_token(self, mock_auth):
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(
            content=json.dumps(self.get_payload())
        )
        request = HttpRequest()
        request.META = self.sso_client.get(reverse("user-list")).request
        user, payload = SSOAuthentication().authenticate(request)

        assert user.is_anonymous is False
        self.assertEqual(payload, self.get_payload())

        assert hasattr(user, "_api_agent")
        api_agent = getattr(user, "_api_agent")
        assert isinstance(api_agent, Group)

        assert hasattr(api_agent, "has_perm")
        assert hasattr(api_agent, "has_perms")

        assert api_agent.has_perm(self._permission)
        assert api_agent.has_perms(
            [
                self._permission,
            ]
        )

    @patch("ponddy_auth.authentication.requests.get")
    def test_valid_sso_can_list_users(self, mock_auth):
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(
            content=json.dumps(self.get_payload())
        )
        resp = self.sso_client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, 200)

    @patch("ponddy_auth.authentication.requests.get")
    def test_valid_sso_cannot_create_user(self, mock_auth):
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(
            content=json.dumps(self.get_payload())
        )
        resp = self.sso_client.post(
            reverse("user-list"),
            json.dumps({"username": "newuser", "password": "TheA11newPWD"}),
        )
        self.assertEqual(resp.status_code, 403)
        self.assertNotEqual(resp.status_code, 200)

    @patch("ponddy_auth.authentication.requests.get")
    def test_invalid_sso_cannot_do_anything(self, mock_auth):
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(ok=False, content=b"")
        resp = self.sso_client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, 401)

    @patch("ponddy_auth.authentication.requests.get")
    def test_empty_authentication_token_will_not_raise_error(self, mock_auth):
        mock_auth.side_effect = lambda *arg, **kwarg: MockAuthHTTPResponse(ok=False, content=b"")
        resp = self.client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, 401)

    @patch("ponddy_auth.authentication.requests.get")
    def test_token_group_not_exists(self, mock_auth):
        payload = self.get_payload()
        payload.update({"api": str(uuid4())})
        mock_auth.side_effect = lambda *arg, **kwargs: MockAuthHTTPResponse(
            content=json.dumps(payload)
        )
        resp = self.sso_client.get(reverse("user-list"))
        self.assertEqual(resp.status_code, 401)
