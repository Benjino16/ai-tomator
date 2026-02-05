from fastapi import Cookie, HTTPException
from jose import jwt, JWTError

from ai_tomator.manager.database import Database


class JWTAuthenticator:
    def __init__(
        self, secret_key: str, algorithm: str, db: Database, require_user_auth=True
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.db = db
        self.require_user_auth = require_user_auth

    def __call__(self, access_token: str | None = Cookie(default=None)):
        if not self.require_user_auth:
            return self.db.users.get_by_username("localhost")
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        try:
            payload = jwt.decode(
                access_token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            username = str(payload["sub"])
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = self.db.users.get_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
