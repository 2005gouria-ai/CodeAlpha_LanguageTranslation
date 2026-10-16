"""
Language Translation Tool
=========================

A user interface to translate text between languages.

Run from the VS Code terminal:

    python main.py            # launches the Tkinter desktop GUI
    python main.py --cli      # runs in the terminal (no window needed)

Requirements: see requirements.txt
"""

import argparse
import sys

from translator import LANGUAGES, translate, TranslationError


# --------------------------------------------------------------------------
# Terminal (CLI) mode
# --------------------------------------------------------------------------
def run_cli():
    print("=" * 60)
    print(" Language Translation Tool  (terminal mode)")
    print("=" * 60)
    names = list(LANGUAGES.keys())
    print("\nAvailable languages:")
    for i, name in enumerate(names, 1):
        print(f"  {i:>2}. {name}")

    def pick(prompt, default):
        raw = input(f"{prompt} [{default}]: ").strip()
        if not raw:
            return default
        if raw.isdigit() and 1 <= int(raw) <= len(names):
            return names[int(raw) - 1]
        return raw

    print("\nType 'quit' as the text to exit.\n")
    while True:
        text = input("Text to translate: ")
        if text.strip().lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        source = pick("Source language (name or number)", "Auto Detect")
        target = pick("Target language (name or number)", "Hindi")
        try:
            result = translate(text, target=target, source=source)
            print("\n--- Translation ---")
            print(result)
            print("-------------------\n")
        except TranslationError as exc:
            print(f"[error] {exc}\n")


# --------------------------------------------------------------------------
# Desktop (GUI) mode
# --------------------------------------------------------------------------
def run_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    from speech import speak

    root = tk.Tk()
    root.title("Language Translation Tool")
    root.geometry("760x560")
    root.minsize(640, 480)

    names = list(LANGUAGES.keys())

    # ---- Header --------------------------------------------------------
    header = tk.Label(root, text="Language Translation Tool",
                      font=("Segoe UI", 16, "bold"), pady=10)
    header.pack()

    # ---- Language selectors -------------------------------------------
    top = tk.Frame(root)
    top.pack(fill="x", padx=14, pady=4)

    tk.Label(top, text="From:").grid(row=0, column=0, sticky="w")
    src_var = tk.StringVar(value="Auto Detect")
    src_box = ttk.Combobox(top, textvariable=src_var, values=names,
                           state="readonly", width=24)
    src_box.grid(row=0, column=1, padx=(4, 20))

    tk.Label(top, text="To:").grid(row=0, column=2, sticky="w")
    tgt_var = tk.StringVar(value="Hindi")
    tgt_box = ttk.Combobox(top, textvariable=tgt_var, values=names,
                           state="readonly", width=24)
    tgt_box.grid(row=0, column=3, padx=4)

    def swap():
        s, t = src_var.get(), tgt_var.get()
        if s == "Auto Detect":
            messagebox.showinfo("Swap", "Cannot swap while source is 'Auto Detect'.")
            return
        src_var.set(t), tgt_var.set(s)

    ttk.Button(top, text="Swap", command=swap).grid(row=0, column=4, padx=8)

    # ---- Input ---------------------------------------------------------
    tk.Label(root, text="Enter text:").pack(anchor="w", padx=14, pady=(12, 0))
    input_box = tk.Text(root, height=7, wrap="word", font=("Segoe UI", 11))
    input_box.pack(fill="both", expand=False, padx=14)

    # ---- Output --------------------------------------------------------
    tk.Label(root, text="Translated text:").pack(anchor="w", padx=14, pady=(12, 0))
    output_box = tk.Text(root, height=7, wrap="word", font=("Segoe UI", 11),
                         bg="#f4f6f8")
    output_box.pack(fill="both", expand=False, padx=14)

    def set_output(value):
        output_box.delete("1.0", "end")
        output_box.insert("1.0", value)

    # ---- Actions -------------------------------------------------------
    def do_translate():
        try:
            result = translate(input_box.get("1.0", "end"), tgt_var.get(), src_var.get())
            set_output(result)
        except TranslationError as exc:
            set_output("")
            messagebox.showerror("Translation error", str(exc))

    def copy_output():
        text = output_box.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Copy", "There is nothing to copy yet.")
            return
        root.clipboard_clear()
        root.clipboard_append(text)
        status.config(text="Copied to clipboard.")

    def speak_output():
        text = output_box.get("1.0", "end").strip()
        if not text:
            return
        if not speak(text):
            messagebox.showinfo("Text-to-speech",
                                "Install 'pyttsx3' (pip install pyttsx3) for speech.")

    def clear_all():
        input_box.delete("1.0", "end")
        set_output("")
        status.config(text="")

    btns = tk.Frame(root)
    btns.pack(fill="x", padx=14, pady=12)
    ttk.Button(btns, text="Translate", command=do_translate).pack(side="left")
    ttk.Button(btns, text="Copy", command=copy_output).pack(side="left", padx=8)
    ttk.Button(btns, text="Speak", command=speak_output).pack(side="left")
    ttk.Button(btns, text="Clear", command=clear_all).pack(side="left", padx=8)

    status = tk.Label(root, text="", fg="#2b7a0b", anchor="w")
    status.pack(fill="x", padx=14, pady=(0, 8))

    input_box.focus_set()
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Language Translation Tool")
    parser.add_argument("--cli", action="store_true",
                        help="run in the terminal instead of the desktop GUI")
    args = parser.parse_args()

    if args.cli:
        run_cli()
        return
    try:
        run_gui()
    except Exception as exc:  # e.g. no display available
        print(f"[warning] Could not start the GUI ({exc}). Falling back to terminal mode.\n")
        run_cli()


if __name__ == "__main__":
    main()
