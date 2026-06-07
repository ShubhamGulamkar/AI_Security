from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.auth import get_current_user
from app.dependencies.auth import require_role


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me")
def my_profile(
        current_user=Depends(get_current_user)
):

    return {
        "username": current_user.username,
        "role": current_user.role
    }


@router.get("/admin")
def admin_endpoint(

    current_user=Depends(
        require_role(["Admin"])
    )

):

    return {
        "message": "Admin Access Granted"
    }


@router.get("/doctor")
def doctor_endpoint(

    current_user=Depends(
        require_role(
            ["Doctor", "Admin"]
        )
    )

):

    return {
        "message": "Doctor Access Granted"
    }


@router.get("/nurse")
def nurse_endpoint(

    current_user=Depends(
        require_role(
            ["Nurse", "Admin"]
        )
    )

):

    return {
        "message": "Nurse Access Granted"
    }