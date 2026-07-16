from fastapi import Response

from app.tokens import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_HOURS

ACCESS_COOKIE = "photo_server_access"
REFRESH_COOKIE = "photo_server_refresh"

# SameSite=Strict, not buzzkit's Lax: photos.reuterborg.se is the only
# origin in play (TODO.md 1.9), no cross-site redirect needs Lax's leeway.
_COMMON = dict(httponly=True, secure=True, samesite="strict", path="/")


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COMMON,
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_HOURS * 3600,
        **_COMMON,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")
