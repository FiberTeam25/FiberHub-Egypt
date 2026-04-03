"""Drop all tables and types so Alembic can start fresh."""
import sqlalchemy as sa
from app.config import get_settings

settings = get_settings()
# Use sync driver for this one-off script
url = settings.database_url.replace("+asyncpg", "")
engine = sa.create_engine(url)

with engine.connect() as conn:
    conn.execute(sa.text("DROP SCHEMA public CASCADE"))
    conn.execute(sa.text("CREATE SCHEMA public"))
    conn.execute(sa.text("GRANT ALL ON SCHEMA public TO CURRENT_USER"))
    conn.commit()

print("Database reset complete.")
