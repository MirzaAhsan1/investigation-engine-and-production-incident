from app.integrations.coolify_client import CoolifyClient


coolify = CoolifyClient()


def execute_action(action):

    provider = action.provider.lower()

    operation = action.action_type.upper()

    target = action.target

    # ----------------------------------
    # Coolify Provider
    # ----------------------------------

    if provider == "coolify":

        if operation == "RESTART_APPLICATION":

            return coolify.restart_application(
                target,
            )

        elif operation == "START_APPLICATION":

            return coolify.start_application(
                target,
            )

        elif operation == "STOP_APPLICATION":

            return coolify.stop_application(
                target,
            )

        elif operation == "DEPLOY_APPLICATION":

            return coolify.deploy_application(
                target,
            )

        else:

            raise Exception(
                f"Unsupported Coolify Operation: {operation}"
            )

    raise Exception(
        f"Unsupported Provider: {provider}"
    )