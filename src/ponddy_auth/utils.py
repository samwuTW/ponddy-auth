import typing

from django.conf import settings
from django.utils import timezone
from jose import jwt
from requests import Session

APP_NAME_SETTING_NAME = getattr(
    settings, "PONDDY_AUTH_APP_NAME_SETTING_NAME", "PONDDY_AUTH_APP_NAME"
)
API_CLIENT_ID_SETTING_NAME = getattr(
    settings, "PONDDY_AUTH_API_CLIENT_ID_SETTING_NAME", "PONDDY_AUTH_API_CLIENT_ID"
)
API_SECRET_SETTING_NAME = getattr(
    settings, "PONDDY_AUTH_API_SECRET_SETTING_NAME", "PONDDY_AUTH_API_SECRET"
)
API_TOKEN_PREFIX_SETTING_NAME = getattr(
    settings,
    "PONDDY_AUTH_API_TOKEN_PREFIX_SETTING_NAME",
    "PONDDY_AUTH_API_TOKEN_PREFIX",
)


setting_app_name = getattr(settings, APP_NAME_SETTING_NAME, None)
setting_api_client_id = getattr(settings, API_CLIENT_ID_SETTING_NAME, None)
setting_api_secret = getattr(settings, API_SECRET_SETTING_NAME, None)
setting_api_token_prefix = getattr(settings, API_TOKEN_PREFIX_SETTING_NAME, "SSO")


class APIClient(Session):
    def refresh_api_header(self) -> None:
        self.status = timezone.now().timestamp()
        self.payload = {
            "api": self.api_client_id,
            "app": self.app_name,
            "status": str(self.status),
        }
        self.payload.update(self.payload_patch)
        token = f"{self.api_token_prefix} ".encode("utf-8") + jwt.encode(
            self.payload, self.api_secret
        ).encode("utf-8")

        headers = {
            "API": self.api_client_id,
            "APP": self.app_name,
            "Authorization": token,
            "status": str(self.status),
        }

        self.headers.update(headers)

    def __init__(
        self,
        payload_patch: typing.Optional[typing.Dict[str, typing.Any]] = None,
        app_name: typing.Optional[str] = None,
        api_client_id: typing.Optional[str] = None,
        api_secret: typing.Optional[str] = None,
        api_token_prefix: typing.Optional[str] = None,
    ):
        super().__init__()
        self.app_name = app_name or setting_app_name
        self.api_client_id = api_client_id or setting_api_client_id
        self.api_secret = api_secret or setting_api_secret
        self.api_token_prefix = api_token_prefix or setting_api_token_prefix

        self.payload_patch = payload_patch or {}
        self.refresh_api_header()
