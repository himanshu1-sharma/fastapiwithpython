import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# -----------------------------
# ✅ Step 1: Add project root to sys.path
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# -----------------------------
# ✅ Step 2: Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# ✅ Step 3: Import settings, Base, and models
# -----------------------------
from app.core.config import settings
from app.db.base_class import Base
from app.db.models.user_model import User  # ensure models are imported so Alembic can detect them

# -----------------------------
# ✅ Step 4: Alembic Configuration
# -----------------------------
config = context.config

# Use database URL from settings.py (loaded via .env)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# -----------------------------
# ✅ Step 5: Migration Runners
# -----------------------------
def run_migrations_offline():
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


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# -----------------------------
# ✅ Step 6: Choose Mode
# -----------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
