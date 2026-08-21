import asyncio

from app.db.session import SessionLocal

from app.services.monitoring_worker import (
    process_pending_logs,
)


PROCESS_INTERVAL = 5


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