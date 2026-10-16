# Task 1 — Language Translation Tool

A small desktop + terminal app that translates text between languages using a
translation API. Built for the CodeAlpha Artificial Intelligence internship.

## Features

- Enter text and pick a **source** and **target** language.
- Uses a translation API (`deep-translator` → Google Translate, no API key needed).
- Sends the text to the API and shows the translated text clearly.
- **Copy** button to copy the result.
- **Speak** button (optional text-to-speech).
- Works as a **Tkinter desktop GUI** and as a **terminal (CLI)** app.

## Requirements

- Python 3.8+
- See `requirements.txt`

## Setup (VS Code terminal)

```bash
# 1. Open this folder in VS Code
# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Run

Desktop GUI:

```bash
python main.py
```

Terminal mode (no window):

```bash
python main.py --cli
```

## Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point — launches the GUI or the terminal mode |
| `translator.py` | Core translation logic + supported languages |
| `speech.py` | Optional text-to-speech helper |
| `requirements.txt` | Dependencies |

## Using a different API

All translation calls live in `translator.py`. To use Microsoft Translator or
the official Google Cloud Translation API instead, replace the body of the
`translate()` function — nothing else in the project needs to change.

## Notes

- `Auto Detect` lets the API detect the source language for you.
- Internet access is required to reach the translation service.
