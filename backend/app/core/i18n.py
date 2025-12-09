
import json
import os
from contextvars import ContextVar
from typing import Dict, Optional

from app.core.config import settings

# Thread-safe context variable to store the current request's locale
_request_locale: ContextVar[str] = ContextVar("request_locale", default="zh")

class I18n:
    def __init__(self):
        self._locales: Dict[str, Dict[str, str]] = {}
        self.default_locale = "zh"
        self.supported_locales = ["zh", "en", "ja"]
        self.load_locales()

    def load_locales(self):
        """Load JSON files from app/locales directory."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        locales_dir = os.path.join(base_dir, "locales")
        
        for lang in self.supported_locales:
            file_path = os.path.join(locales_dir, f"{lang}.json")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    self._locales[lang] = json.load(f)
            else:
                print(f"Warning: Locale file not found: {file_path}")
                self._locales[lang] = {}

    def get_locale(self) -> str:
        """Get current locale from context."""
        return _request_locale.get()

    def set_locale(self, locale: str):
        """Set current locale in context."""
        if locale in self.supported_locales:
            _request_locale.set(locale)
        else:
            _request_locale.set(self.default_locale)

    def t(self, key: str, **kwargs) -> str:
        """
        Translate key to current locale.
        If key not found, return key (or English fallback).
        Support string formatting via kwargs.
        Support nested keys with dot notation (e.g., "menu.invalid_parent").
        """
        locale = self.get_locale()
        translations = self._locales.get(locale, {})
        
        # Support nested keys with dot notation
        keys = key.split(".")
        text = translations
        for k in keys:
            if isinstance(text, dict):
                text = text.get(k)
            else:
                text = None
                break
        
        # Fallback to default locale if not found
        if text is None:
            default_translations = self._locales.get(self.default_locale, {})
            text = default_translations
            for k in keys:
                if isinstance(text, dict):
                    text = text.get(k)
                else:
                    text = None
                    break
        
        # Final fallback to key itself
        if text is None:
            text = key
            
        if kwargs and isinstance(text, str):
            try:
                return text.format(**kwargs)
            except Exception:
                pass
                
        return text if isinstance(text, str) else key

# Global instance
i18n = I18n()
