from logging.config import fileConfig

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from alembic import context
from alembic import op
from database import DATABASE_URL  # Убедитесь, что DATABASE_URL правильный

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None  # Убедитесь, что у вас есть метаданные моделей

# Define the async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Define sessionmaker for async sessions
AsyncSession = sessionmaker(
    engine, class_="AsyncSession", expire_on_commit=False
)

# Function to run migrations in 'offline' mode
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Function to run migrations in 'online' mode
async def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Create the async engine for migration
    connectable = create_async_engine(DATABASE_URL, echo=True)

    # Use `async with` for connecting to the database and running migrations
    async with connectable.connect() as connection:
        # Use the connection in the migration context
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        # Run migrations asynchronously
        async with connection.begin():
            await context.run_migrations()

# Check if we are running in offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())
