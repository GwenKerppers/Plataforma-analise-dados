from fastapi import APIRouter

from app.modules.authentication.dependencies import CurrentUser
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def read_me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
