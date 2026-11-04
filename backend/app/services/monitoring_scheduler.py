import asyncio

from app.db.session import SessionLocal

from app.services.monitoring_worker import (
    process_pending_logs,
)

from app.services.coolify_status_service import (
    poll_all_applications,
)


PROCESS_INTERVAL = 5

# Coolify status/deployment polling runs on its own, slower
# cadence — separate from the Fluent Bit log/metric loop above
# — since it hits the Coolify API directly and shouldn't be
# tied to how fast pending logs happen to be arriving.
COOLIFY_POLL_INTERVAL = 30


async def monitoring_loop():

    print(
        "[MONITORING WORKER] "
        "Automatic monitoring worker started."
    )

    while True:

        db = SessionLocal()

        try:

            result = process_pending_logs(
                db=db,
            )

            if result["processed"] > 0:

                print(
                    "[MONITORING WORKER] "
                    f"Processed: {result['processed']} "
                    f"| Failed: {result['failed']}"
                )

        except Exception as exc:

            print(
                "[MONITORING WORKER] "
                f"Worker error: {exc}"
            )

        finally:

            db.close()

        await asyncio.sleep(
            PROCESS_INTERVAL
        )


async def coolify_polling_loop():

    print(
        "[COOLIFY STATUS] "
        "Coolify status polling worker started."
    )

    while True:

        db = SessionLocal()

        try:

            result = poll_all_applications(
                db=db,
            )

            if result["polled"] > 0 or result["failed"] > 0:

                print(
                    "[COOLIFY STATUS] "
                    f"Polled: {result['polled']} "
                    f"| Failed: {result['failed']}"
                )

        except Exception as exc:

            print(
                "[COOLIFY STATUS] "
                f"Worker error: {exc}"
            )

        finally:

            db.close()

        await asyncio.sleep(
            COOLIFY_POLL_INTERVAL
        )