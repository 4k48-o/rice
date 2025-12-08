
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.i18n import i18n

class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Check Query Param ?lang=
        lang = request.query_params.get("lang")
        
        # 2. Check Accept-Language Header if not found
        if not lang:
            accept_language = request.headers.get("Accept-Language")
            if accept_language:
                # Simple parser: take the first preferred language
                # e.g., "en-US,en;q=0.9,ja;q=0.8" -> "en"
                # For simplicity, we just look for exact substring match or first part
                # In production, a proper parser is better.
                for supported in i18n.supported_locales:
                    if supported in accept_language:
                         lang = supported
                         break
        
        # 3. Set Locale (defaults to 'zh' inside set_locale if lang is None)
        i18n.set_locale(lang if lang else "zh")
        
        response = await call_next(request)
        return response
