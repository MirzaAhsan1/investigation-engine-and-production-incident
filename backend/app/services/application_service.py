from uuid import UUID

from sqlalchemy.orm import Session

from app.models.application import Application


def create_application(
    db: Session,
    payload,
):
    application = Application(
        server_id=payload.server_id,
        name=payload.name,
        container_name=payload.container_name,
        provider=payload.provider,
        resource_uuid=payload.resource_uuid,
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def get_applications(
    db: Session,
):
    return (
        db.query(Application)
        .order_by(Application.created_at.asc())
        .all()
    )


def get_application(
    db: Session,
    application_id: UUID,
):
    return db.get(
        Application,
        application_id,
    )


def get_applications_by_server(
    db: Session,
    server_id: UUID,
):
    return (
        db.query(Application)
        .filter(
            Application.server_id == server_id,
            Application.is_active == True,
        )
        .all()
    )


def get_application_by_container(
    db: Session,
    server_id: UUID,
    container_name: str,
):
    return (
        db.query(Application)
        .filter(
            Application.server_id == server_id,
            Application.container_name == container_name,
            Application.is_active == True,
        )
        .first()
    )