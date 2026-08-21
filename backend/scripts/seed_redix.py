from app.db.session import SessionLocal
from app.models.client import Client
from app.models.server import Server
from app.models.application import Application
import secrets

db = SessionLocal()

client = Client(name="Redix", api_key=secrets.token_hex(32), is_active=True)
db.add(client)
db.flush()

server = Server(client_id=client.id, name="Redix Production Server", host="redix-server-01", environment="production", is_active=True)
db.add(server)
db.flush()

application = Application(
    server_id=server.id,
    name="Redix App",
    container_name="redix-app",
    provider="coolify",
    resource_uuid="pending-coolify-uuid",  # baad mein real UUID se update karenge
    is_active=True,
)
db.add(application)
db.commit()

print("API_KEY:", client.api_key)
print("HOST:", server.host)
print("CONTAINER_NAME:", application.container_name)