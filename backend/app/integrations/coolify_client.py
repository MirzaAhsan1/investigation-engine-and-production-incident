import requests

from app.core.config import settings


class CoolifyClient:

    def __init__(self):

        self.base_url = settings.coolify_base_url.rstrip("/")

        self.headers = {
            "Authorization": f"Bearer {settings.coolify_api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        self.timeout = settings.coolify_timeout

        self.verify_ssl = settings.coolify_verify_ssl

    # ---------------------------------------
    # Internal Request
    # ---------------------------------------

    def _request(
        self,
        method: str,
        endpoint: str,
        json: dict | None = None,
    ):

        response = requests.request(

            method=method,

            url=f"{self.base_url}{endpoint}",

            headers=self.headers,

            json=json,

            timeout=self.timeout,

            verify=self.verify_ssl,

        )

        response.raise_for_status()

        if response.text:

            return response.json()

        return None

    # ---------------------------------------
    # Applications
    # ---------------------------------------

    def get_applications(self):

        return self._request(

            "GET",

            "/applications",

        )

    # ---------------------------------------
    # Find Application by Name
    # ---------------------------------------

    def find_application(
        self,
        application_name: str,
    ):

        applications = self.get_applications()

        for app in applications:

            if app["name"].lower() == application_name.lower():

                return app

        return None

    # ---------------------------------------
    # UUID Resolver
    # ---------------------------------------

    def get_application_uuid(
        self,
        application_name: str,
    ):

        app = self.find_application(
            application_name,
        )

        if app is None:

            raise ValueError(

                f"Application '{application_name}' not found."

            )

        return app["uuid"]

    # ---------------------------------------
    # Operations
    # ---------------------------------------

    def restart_application(self,application_name: str,):

        uuid = self.get_application_uuid(
            application_name,
        )

        return self._request(

            "GET",

            f"/applications/{uuid}/restart",

        )

    def start_application(self,application_name: str,):

        uuid = self.get_application_uuid(
            application_name,
        )

        return self._request(

            "GET",

            f"/applications/{uuid}/start",

        )

    def stop_application(self,application_name: str,):

        uuid = self.get_application_uuid(
            application_name,
        )

        return self._request(

            "GET",

            f"/applications/{uuid}/stop",

        )

    def deploy_application(self,application_name: str,):

        uuid = self.get_application_uuid(
            application_name,
        )

        return self._request(

            "GET",

            f"/applications/{uuid}/deploy",

        )




