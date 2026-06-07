from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from fastapi.security import HTTPBearer
from fastapi.security import HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.models.user import User

from app.core.security import decode_token


security = HTTPBearer()


def get_current_user(

    credentials: HTTPAuthorizationCredentials = Depends(security),

    db: Session = Depends(get_db)

):

    token = credentials.credentials

    payload = decode_token(token)

    if not payload:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    username = payload.get("sub")

    user = db.query(User).filter(
        User.username == username
    ).first()

    # if not user:

    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="User not found"
    #     )
    if not user.is_active:
        raise HTTPException(
        status_code=403,
        detail="User disabled"
    )

    return user

def require_role(allowed_roles: list):

    def checker(
            current_user=Depends(get_current_user)
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )

        return current_user

    return checker