#!/usr/bin/env python
"""Initialize the database with Alembic."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from skripsi_helper.db.session import engine, Base


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
