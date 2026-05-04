"""Initialize database tables on deployment."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.db.database import engine
from backend.db.models import Base

def init_db():
    """Create all database tables."""
    print("🗄️ Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialization complete!")

if __name__ == "__main__":
    init_db()
