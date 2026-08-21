from app.integrations.coolify_client import CoolifyClient


class ResourceResolver:

    def __init__(self):

        self.client = CoolifyClient()

    # ----------------------------------------
    # Resolve Application by Name
    # ----------------------------------------

    def resolve_application(
        self,
        application_name: str,
    ):

        applications = self.client.get_applications()

        for application in applications:

            if (
                application["name"].strip().lower()
                == application_name.strip().lower()
            ):

                return application

        raise ValueError(
            f"Application '{application_name}' not found."
        )

    # ----------------------------------------
    # Get UUID
    # ----------------------------------------

    def get_application_uuid(
        self,
        application_name: str,
    ) -> str:

        application = self.resolve_application(
            application_name,
        )

        return application["uuid"]