from app.models import application
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

    
    def get_application_by_uuid(self, resource_uuid: str):
        """Fetch application directly by Coolify UUID."""
        return self._request("GET", f"/applications/{resource_uuid}")

    def get_application_status(self, resource_uuid: str) -> str | None:
        """Returns raw status string e.g. 'running:healthy'."""
        application = self.get_application_by_uuid(resource_uuid)
        if application is None:
            return None
        return application.get("status")

    def get_deployments(self, resource_uuid: str):
        """List deployments, filtered client-side by application_uuid."""
        deployments = self._request("GET", "/deployments")
        if not deployments:
            return []
        return [d for d in deployments if d.get("application_uuid") == resource_uuid]

    def get_latest_deployment(self, resource_uuid: str):
        """Most recent deployment by created_at, or None."""
        deployments = self.get_deployments(resource_uuid)
        if not deployments:
            return None
        return max(deployments, key=lambda d: d.get("created_at") or "")




