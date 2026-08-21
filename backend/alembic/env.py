from logging.config import fileConfig
from alembic import context
from app.core.config import settings
from app.core.database import engine
from app.db.base import Base

# 1. Alembic Config object
config = context.config

# 2. Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 3. Escape '%' signs so configparser doesn't crash on encoded passwords
escaped_db_url = settings.DATABASE_URL.replace("%", "%%")
config.set_main_option("sqlalchemy.url", escaped_db_url)

# 4. Set target_metadata BEFORE running migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()