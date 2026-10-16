"""
Core translation logic for the Language Translation Tool.

Engines, tried in order:
  1. Google Translate public endpoint  (stdlib only, no API key)
  2. deep-translator -> GoogleTranslator  (if installed)
  3. deep-translator -> MyMemory          (if installed)

To use Microsoft Translator or the official Google Cloud Translation API
instead, replace only the body of `translate()` below.
"""

import json
import time
import urllib.parse
import urllib.request

try:
    from deep_translator import GoogleTranslator
except Exception:  # pragma: no cover
    GoogleTranslator = None

try:
    from deep_translator import MyMemoryTranslator
except Exception:  # pragma: no cover
    MyMemoryTranslator = None


# A practical, curated set of languages. `code` is the ISO code used by the
# translation engine; `name` is what we show in the UI / CLI.
LANGUAGES = {
    "Auto Detect": "auto",
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Punjabi": "pa",
    "Tamil": "ta",
    "Telugu": "te",
    "Urdu": "ur",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese (Simplified)": "zh-CN",
    "Arabic": "ar",
}

# MyMemory uses region-tagged codes. Only needed for that fallback engine.
_MYMEMORY_CODES = {
    "en": "en-GB", "hi": "hi-IN", "bn": "bn-IN", "gu": "gu-IN",
    "kn": "kn-IN", "ml": "ml-IN", "mr": "mr-IN", "pa": "pa-IN",
    "ta": "ta-IN", "te": "te-IN", "ur": "ur-PK", "fr": "fr-FR",
    "de": "de-DE", "es": "es-ES", "it": "it-IT", "pt": "pt-PT",
    "ru": "ru-RU", "ja": "ja-JP", "ko": "ko-KR", "zh-CN": "zh-CN",
    "ar": "ar-SA",
}

_UA = "Mozilla/5.0 (compatible; LanguageTranslationTool/1.0)"


class TranslationError(Exception):
    """Raised when translation fails for any reason."""


def get_supported_languages():
    """Return the {display name: ISO code} mapping used across the app."""
    return dict(LANGUAGES)


def code_for(name):
    """Map a display name to its ISO code (accepts codes as-is)."""
    if name in LANGUAGES:
        return LANGUAGES[name]
    if name in LANGUAGES.values():
        return name
    raise TranslationError(f"Unknown language: {name!r}")


# --------------------------------------------------------------------------
# Engine 1: public Google Translate endpoint (no key, stdlib only)
# --------------------------------------------------------------------------
def _translate_public_google(text, source_code, target_code):
    params = {
        "client": "gtx",
        "sl": "auto" if source_code == "auto" else source_code,
        "tl": target_code,
        "dt": "t",
        "q": text,
    }
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    # Response shape: [[[translated, original, ...], ...], ...]
    return "".join(segment[0] for segment in data[0] if segment and segment[0])


# --------------------------------------------------------------------------
# Engines 2 & 3: deep-translator backends
# --------------------------------------------------------------------------
def _translate_deep_google(text, source_code, target_code):
    if GoogleTranslator is None:
        raise TranslationError("deep-translator (Google) is not installed.")
    src = "auto" if source_code == "auto" else source_code
    return GoogleTranslator(source=src, target=target_code).translate(text)


def _translate_mymemory(text, source_code, target_code):
    if MyMemoryTranslator is None:
        raise TranslationError("deep-translator (MyMemory) is not installed.")
    if source_code == "auto":
        source_code = "en"  # MyMemory has no auto-detect; assume English.
    src = _MYMEMORY_CODES.get(source_code, source_code)
    tgt = _MYMEMORY_CODES.get(target_code, target_code)
    return MyMemoryTranslator(source=src, target=tgt).translate(text)


def translate(text, target, source="Auto Detect"):
    """
    Translate `text` from `source` to `target`.

    `source` and `target` may be display names ("English") or ISO codes ("en").
    Tries each engine in turn and returns the first non-empty result.
    """
    text = (text or "").strip()
    if not text:
        raise TranslationError("Please enter some text to translate.")

    source_code = code_for(source)
    target_code = code_for(target)

    if source_code != "auto" and source_code == target_code:
        raise TranslationError("Source and target languages are the same.")

    engines = [
        ("Google", _translate_public_google),
        ("Google(deep-translator)", _translate_deep_google),
        ("MyMemory", _translate_mymemory),
    ]

    errors = []
    for name, engine in engines:
        for attempt in range(2):
            try:
                result = engine(text, source_code, target_code)
                if result:
                    return result
            except Exception as exc:
                errors.append(f"{name}: {exc}")
                if attempt == 0:
                    time.sleep(1.0)
                else:
                    break

    raise TranslationError("Translation failed. " + " | ".join(errors))
