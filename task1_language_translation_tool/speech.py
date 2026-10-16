"""
Optional text-to-speech helper.

If `pyttsx3` is installed we use it (works offline). If it is missing we
silently fall back to the platform's built-in command so the app still
works. Speech is a bonus feature, never a hard dependency.
"""

import platform
import shutil
import subprocess


def speak(text):
    """Speak `text` aloud. Returns True on success, False otherwise."""
    text = (text or "").strip()
    if not text:
        return False

    # Preferred: pyttsx3 (offline, cross-platform).
    try:
        import pyttsx3

        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return True
    except Exception:
        pass

    # Fallbacks using the OS voice.
    system = platform.system()
    try:
        if system == "Darwin" and shutil.which("say"):
            subprocess.run(["say", text], check=True)
            return True
        if system == "Windows":
            subprocess.run(
                ["powershell", "-c",
                 f"Add-Type -AssemblyName System.Speech; "
                 f"(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"],
                check=True,
            )
            return True
        if shutil.which("espeak"):
            subprocess.run(["espeak", text], check=True)
            return True
    except Exception:
        pass
    return False
