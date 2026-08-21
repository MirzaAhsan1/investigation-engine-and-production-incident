from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate


def create_client(
    db: Session,
    payload: ClientCreate,
):

    client = Client(

        name=payload.name,

        api_key=payload.api_key,

    )

    db.add(client)

    db.commit()

    db.refresh(client)

    return client


def get_clients(
    db: Session,
):

    return (

        db.query(Client)

        .order_by(Client.name)

        .all()

    )


def get_client(
    db: Session,
    client_id,
):

    return db.get(
        Client,
        client_id,
    )


def get_client_by_api_key(
    db: Session,
    api_key: str,
):

    return (

        db.query(Client)

        .filter(
            Client.api_key == api_key,
            Client.is_active == True,
        )

        .first()

    )