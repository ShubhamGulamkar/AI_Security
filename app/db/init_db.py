from app.db.database import engine
from app.db.database import Base

from app.models.user import User
from app.models.document import Document
from app.models.audit_log import AuditLog


def init_db():

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":

    init_db()

    print("Database Created")