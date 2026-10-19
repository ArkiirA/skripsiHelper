from logging.config import fileConfig
import asyncio

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from alembic import context

from skripsi_helper.core.config import settings
from skripsi_helper.db.session import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable: AsyncEngine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async def go():
        async with connectable.connect() as connection:
            await connection.run_sync(Base.metadata.create_all)
        await connectable.dispose()

    asyncio.run(go())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
