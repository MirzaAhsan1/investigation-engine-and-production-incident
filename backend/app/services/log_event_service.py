from sqlalchemy.orm import Session

from app.enums.log_status import LogStatusEnum

from app.models.log_event import LogEvent


def get_pending_logs(
    db: Session,
    limit: int = 50,
):

    return (

        db.query(LogEvent)

        .filter(
            LogEvent.status == LogStatusEnum.PENDING
        )

        .order_by(
            LogEvent.created_at.asc()
        )

        .limit(limit)

        .all()

    )


def mark_processing(
    db: Session,
    log: LogEvent,
):

    log.status = LogStatusEnum.PROCESSING

    db.commit()

    db.refresh(log)

    return log


def mark_completed(
    db: Session,
    log: LogEvent,
):

    log.status = LogStatusEnum.COMPLETED

    db.commit()

    db.refresh(log)

    return log


def mark_failed(
    db: Session,
    log: LogEvent,
):

    log.status = LogStatusEnum.FAILED

    db.commit()

    db.refresh(log)

    return log


def mark_ignored(
    db: Session,
    log: LogEvent,
):

    log.status = LogStatusEnum.IGNORED

    db.commit()

    db.refresh(log)

    return log