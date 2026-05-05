from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.user import User
from app.modules.auth.schemas import TokenResponse, UserLogin, UserRegister


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveUserError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, data: UserRegister) -> TokenResponse:
        existing = self.db.scalars(select(User).where(User.email == data.email)).first()
        if existing is not None:
            raise EmailAlreadyRegisteredError

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return TokenResponse(access_token=create_access_token(user.id), user=user)

    def login_user(self, data: UserLogin) -> TokenResponse:
        user = self.db.scalars(select(User).where(User.email == data.email)).first()
        if user is None or not verify_password(data.password, user.password_hash):
            raise InvalidCredentialsError
        if not user.is_active:
            raise InactiveUserError
        return TokenResponse(access_token=create_access_token(user.id), user=user)
