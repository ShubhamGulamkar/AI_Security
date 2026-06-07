from sqlalchemy.orm import Session

from app.models.user import User

from app.core.security import hash_password
from app.core.security import verify_password
from app.utils.password_validator import validate_password


def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        role: str
):

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        role=role
    )

    validate_password(password)

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def get_user_by_username(
        db: Session,
        username: str
):

    return db.query(User).filter(
        User.username == username
    ).first()


def authenticate_user(
        db: Session,
        username: str,
        password: str
):

    user = get_user_by_username(
        db,
        username
    )

    if not user:
        return None

    if not verify_password(
            password,
            user.hashed_password
    ):
        return None

    return user