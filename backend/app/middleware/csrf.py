"""CSRF Protection Middleware"""
import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException


class CSRFMiddleware(BaseHTTPMiddleware):
    SAFE = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        if request.method not in self.SAFE:
            cookie_token = request.cookies.get("csrf_token")
            header_token = request.headers.get("X-CSRF-Token")
            if (
                not cookie_token
                or not header_token
                or not secrets.compare_digest(cookie_token, header_token)
            ):
                raise HTTPException(403, "CSRF token missing or invalid")
        response = await call_next(request)
        if "csrf_token" not in request.cookies:
            response.set_cookie(
                "csrf_token",
                secrets.token_hex(32),
                httponly=False,
                samesite="strict",
                secure=True,
            )
        return response
