import json
import time

from pytube import request
from pytube.innertube import InnerTube, _client_id, _client_secret


class InnerTubeAuth(InnerTube):
    """
    InnerTubeAuth is a subclass of PyTube's InnerTube that handles OAuth authentication.

    By default InnerTube propts for user response to OAuth Requests, this breaks it up into two steps.
    """

    def __init__(self, use_oauth=True):
        super().__init__(use_oauth=use_oauth)
        self.access_token = None
        self.refresh_token = None
        self.expires = None

    def start_bearer_token_fetch(self):
        """Fetch an OAuth token."""
        data = {"client_id": _client_id, "scope": "https://www.googleapis.com/auth/youtube"}
        response = request._execute_request(
            "https://oauth2.googleapis.com/device/code", "POST", headers={"Content-Type": "application/json"}, data=data
        )
        response_data = json.loads(response.read())
        verification_url = response_data["verification_url"]
        user_code = response_data["user_code"]
        return response_data, verification_url, user_code

    def finish_bearer_token_fetch(self, response_data: str):
        data = {
            "client_id": _client_id,
            "client_secret": _client_secret,
            "device_code": response_data["device_code"],
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }
        response = request._execute_request(
            "https://oauth2.googleapis.com/token", "POST", headers={"Content-Type": "application/json"}, data=data
        )
        response_data = json.loads(response.read())

        self.access_token = response_data["access_token"]
        self.refresh_token = response_data["refresh_token"]
        self.expires = time.time() + response_data["expires_in"]
        self.cache_tokens()


def prompt_for_oauth():
    """
    Prompts the user for an OAuth token.
    """
    base_innertube = InnerTubeAuth()
    response_data, verification_url, user_code = base_innertube.start_bearer_token_fetch()
    return response_data, verification_url, user_code


def save_oauth_token(response_data: str):
    """
    Saves the OAuth token to the config file.
    """
    base_innertube = InnerTubeAuth()
    base_innertube.finish_bearer_token_fetch(response_data)
    return base_innertube.expires
