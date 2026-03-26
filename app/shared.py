"""
Shared resources loaded once at startup and imported by all routers.
"""
import os
import json

from fastapi.templating import Jinja2Templates

SUPPORTED_LANGS = ["it", "en"]

translations: dict = {}
_locales_dir = os.path.join(os.path.dirname(__file__), "locales")

for _lang in SUPPORTED_LANGS:
    _file_path = os.path.join(_locales_dir, f"{_lang}.json")
    try:
        with open(_file_path, "r", encoding="utf-8") as _f:
            translations[_lang] = json.load(_f)
    except FileNotFoundError:
        print(f"ATTENZIONE: File di traduzione non trovato per la lingua: {_lang}")
        translations[_lang] = {}

templates = Jinja2Templates(directory="app/templates")
