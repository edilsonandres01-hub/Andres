"""Rate Limiting Middleware"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client = request.client.host if request.client else "unknown"
        now = time.time()
        self.requests.setdefault(client, [])
        self.requests[client] = [t for t in self.requests[client] if t > now - self.window]
        if len(self.requests[client]) >= self.max_requests:
            raise HTTPException(429, "Too many requests")
        self.requests[client].append(now)
        return await call_next(request)
