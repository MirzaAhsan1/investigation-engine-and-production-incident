from app.db.session import SessionLocal
from app.models.client import Client
from app.models.server import Server
from app.models.application import Application
import secrets

db = SessionLocal()

client = Client(
    name="CoolifyRealTest",
    api_key=secrets.token_hex(32),
    is_active=True,
)
db.add(client)
db.flush()

server = Server(
    client_id=client.id,
    name="Coolify Prod Server",
    host="coolify-prod-01",          # Fluent Bit config mein isi naam se use hoga
    environment="production",
    is_active=True,
)
db.add(server)
db.flush()

application = Application(
    server_id=server.id,
    name="Backend App",
    container_name="backend-wisyd1twjmlq7sryv2efq6e1-133932457197",
    provider="coolify",
    resource_uuid="pending",          # Coolify token milne pe update karenge
    is_active=True,
)
db.add(application)
db.commit()

print("API_KEY:", client.api_key)
print("HOST:", server.host)
print("CONTAINER_NAME:", application.container_name)
print("PUBLIC_DOMAIN (testing ke liye, DB mein save nahi):",
      "https://qpvtaeq6x67di8fwani5igls.s0226.digitalsofts.com")