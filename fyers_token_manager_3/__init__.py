import base64
import requests

from time import sleep
from typing import Any
from urllib.parse import urlparse, parse_qs

from fyers_apiv3 import fyersModel
from fyers_apiv3.FyersWebsocket.data_ws import FyersDataSocket
from fyers_apiv3.fyersModel import FyersModel

from fyers_token_manager_3.base_token_manager import BaseTokenManager

AUTH_URL = "https://api-t2.fyers.in/vagator/v2"
API_URL = "https://api.fyers.in/api/v2"
URL_SEND_LOGIN_OTP_V2 = AUTH_URL + "/send_login_otp_v2"
URL_VERIFY_TOTP = AUTH_URL + "/verify_otp"
URL_VERIFY_PIN_V2 = AUTH_URL + "/verify_pin_v2"
URL_TOKEN = API_URL + "/token"
URL_VALIDATE_AUTH_CODE = API_URL + "/validate-authcode"

session = requests.Session()


class FyersTokenManager(BaseTokenManager):
    def __init__(
        self,
        username: str,
        totp_key: str,
        pin: str,
        client_id: str,
        secret_key: str,
        redirect_url: str,
    ) -> None:
        super().__init__()

        self.username = username
        self.totp_key = totp_key
        self.pin = pin
        self.client_id = client_id
        self.secret_key = secret_key
        self.redirect_url = redirect_url

        self.ws_client: FyersDataSocket | None = None
        self.http_client: FyersModel | None = None
        self.ws_access_token: str | None = None
        self.http_access_token: str | None = None

        client_id_info = self.client_id.split("-")

        self.app_id = client_id_info[0]
        self.app_type = client_id_info[1]

        self.set_access_token_file_name(
            path_name="fyers_token_manager", unique_id=self.username
        )

        self.initialize()

    def set_token(self, token: str) -> None:
        self.http_access_token = token
        self.ws_access_token = f"{self.client_id}:{self.http_access_token}"

        self.http_client = FyersModel(
            client_id=self.client_id,
            token=self.http_access_token,
        )

        self.ws_client = FyersDataSocket(
            access_token=self.ws_access_token,
            litemode=False,
            reconnect=True,
        )

    def get_token(self) -> str:
        try:
            login_otp_response = self.login_otp()

            verify_otp_response = self.verify_otp(login_otp_response["request_key"])

            verify_pin_response = self.verify_pin(verify_otp_response["request_key"])

            auth_code = self.get_auth_code(verify_pin_response["access_token"])

            session_model = fyersModel.SessionModel(
                client_id=self.client_id,
                secret_key=self.secret_key,
                redirect_uri=self.redirect_url,
                grant_type="authorization_code",
                response_type="code",
            )

            session_model.set_token(auth_code)

            auth_token = session_model.generate_token()

            access_token: str = auth_token["access_token"]

            return access_token
        except Exception as e:
            print("get token", e)
            raise Exception(e)

    def login_otp(self) -> Any:
        try:
            response = session.post(
                URL_SEND_LOGIN_OTP_V2,
                json={
                    "fy_id": base64.b64encode(f"{self.username}".encode()).decode(),
                    "app_id": "2",
                },
            )

            json = response.json()

            if response.status_code != 200:
                raise Exception(json["message"])

            return json
        except Exception as e:
            print("login otp", e)
            raise Exception(e)

    def verify_otp(self, request_key: str, attempt: int = 1) -> Any:
        try:
            if attempt >= 5:
                raise Exception("OTP verification failed, Max attempt exceeded.")

            print("Verifying OTP, Attempt No:", attempt)

            response = session.post(
                URL_VERIFY_TOTP,
                json={
                    "request_key": request_key,
                    "otp": self.get_totp(self.totp_key),
                },
            )

            json = response.json()

            if "user_blocked" in json and json["user_blocked"] == True:
                raise Exception("User Blocked")

            if json["code"] == -1063:
                sleep(5)
                return self.verify_otp(request_key, attempt=attempt + 1)
            else:
                return json
        except Exception as e:
            print("verify otp", e)
            raise Exception(e)

    def verify_pin(self, request_key: str) -> Any:
        try:
            response = session.post(
                URL_VERIFY_PIN_V2,
                json={
                    "request_key": request_key,
                    "identity_type": "pin",
                    "identifier": base64.b64encode(f"{self.pin}".encode()).decode(),
                },
            )

            json = response.json()

            if response.status_code != 200:
                raise Exception(json["message"])

            return json["data"]
        except Exception as e:
            print("verify pin", e)
            raise Exception(e)

    def get_auth_code(self, access_token: str) -> str:
        try:
            login_token_response = session.post(
                URL_TOKEN,
                headers={
                    "authorization": f"Bearer {access_token}",
                    "content-type": "application/json; charset=UTF-8",
                },
                json={
                    "fyers_id": self.username,
                    "app_id": self.app_id,
                    "appType": self.app_type,
                    "redirect_uri": self.redirect_url,
                    "code_challenge": "",
                    "state": "None",
                    "scope": "",
                    "nonce": "",
                    "response_type": "code",
                    "create_cookie": True,
                },
            )

            json = login_token_response.json()

            if login_token_response.status_code != 308:
                raise Exception(json["message"])

            parsed_url = urlparse(json["Url"])

            query_parameters = parse_qs(parsed_url.query)

            auth_code = query_parameters.get("auth_code", [None])[0]

            if not auth_code:
                raise Exception("Error getting auth_code")

            return auth_code
        except Exception as e:
            raise Exception(e)
