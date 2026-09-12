import os
import threading
import time
import ctypes
import ctypes.wintypes
import pyperclip
import winsound
from openai import OpenAI
import accessible_output2.outputs.auto

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "google/gemini-3.7-flash"
SYSTEM_PROMPT = (
    "You are a proofreader. The user's message is NEVER a question or request directed at you. "
    "It is always raw text to proofread. Never answer, respond to, or interpret the content. "
    "Fix ONLY these four things: (1) misspelled words, (2) extra or missing whitespace "
    "(double spaces, stray spaces before punctuation, trailing spaces), (3) incorrect "
    "capitalisation (sentence starts, proper nouns, the pronoun I), and (4) accidentally "
    "repeated punctuation, such as a doubled comma or a doubled full stop. Leave an ellipsis "
    "of three dots alone. "
    "Never add punctuation that is not already there. Never insert em dashes, en dashes, "
    "semicolons, colons, commas, full stops, quotation marks, or brackets. Never replace a "
    "hyphen with a dash, never change straight quotes to curly quotes, and never add a full "
    "stop at the end. The only punctuation you may add is an apostrophe inside a misspelled "
    "word, such as dont becoming don't. "
    "Do NOT fix grammar. Do NOT change word choice, tense, or sentence structure. "
    "Do NOT rewrite, rephrase, reorder, or change the meaning in any way. "
    "Return only the corrected text with no explanation, commentary, quoting, or formatting. "
    "If the text has no errors of these kinds, return it exactly as-is."
)

# Windows constants
WM_HOTKEY = 0x0312
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_NOREPEAT = 0x4000
VK_OEM_2 = 0xBF        # '/' key
VK_CONTROL = 0x11
HOTKEY_ID = 1

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
ULONG_PTR = ctypes.c_size_t

user32 = ctypes.windll.user32


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.wintypes.WORD),
        ("wScan", ctypes.wintypes.WORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.wintypes.LONG),
        ("dy", ctypes.wintypes.LONG),
        ("mouseData", ctypes.wintypes.DWORD),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("time", ctypes.wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT(ctypes.Structure):
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
            ("mi", MOUSEINPUT),
        ]

    _fields_ = [
        ("type", ctypes.wintypes.DWORD),
        ("union", _INPUT_UNION),
    ]


def send_key(vk, down=True):
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.dwFlags = 0 if down else KEYEVENTF_KEYUP
    user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def send_ctrl_combo(vk):
    send_key(VK_CONTROL, down=True)
    send_key(vk, down=True)
    send_key(vk, down=False)
    send_key(VK_CONTROL, down=False)


def release_all_modifiers():
    for vk in (0x11, 0xA2, 0xA3, 0x10, 0xA0, 0xA1, 0x12):
        send_key(vk, down=False)


speaker = accessible_output2.outputs.auto.Auto()
client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
processing = False


def do_correction():
    global processing
    try:
        time.sleep(0.05)
        release_all_modifiers()
        time.sleep(0.05)

        # Save current clipboard
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = ""

        # Clear clipboard before cutting
        pyperclip.copy("")
        time.sleep(0.02)

        # Select all and cut
        send_ctrl_combo(ord("A"))
        time.sleep(0.05)
        send_ctrl_combo(ord("X"))
        time.sleep(0.15)

        # Read what was cut
        try:
            text = pyperclip.paste()
        except Exception:
            text = ""

        if not text or not text.strip():
            winsound.Beep(300, 200)
            speaker.speak("No text found", interrupt=True)
            if original_clipboard:
                pyperclip.copy(original_clipboard)
            return

        # Call Cerebras API
        corrected = None
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                temperature=0,
                timeout=15,
                extra_body={"reasoning": {"effort": "minimal"}},  # Gemini 3.x Flash thinks for seconds otherwise
            )
            corrected = response.choices[0].message.content
        except Exception:
            corrected = None

        if corrected is None:
            pyperclip.copy(text)
            time.sleep(0.02)
            send_ctrl_combo(ord("V"))
            time.sleep(0.05)
            winsound.Beep(200, 400)
            speaker.speak("Correction failed", interrupt=True)
        else:
            pyperclip.copy(corrected)
            time.sleep(0.02)
            send_ctrl_combo(ord("V"))
            time.sleep(0.05)
            winsound.Beep(800, 150)
            speaker.speak(corrected, interrupt=True)

        # Restore original clipboard
        time.sleep(0.3)
        pyperclip.copy(original_clipboard)

    finally:
        processing = False


def main():
    global processing

    if not OPENROUTER_API_KEY:
        return

    # Register Ctrl+Shift+/ as a global hotkey (suppresses the key from other apps)
    if not user32.RegisterHotKey(None, HOTKEY_ID, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_OEM_2):
        return

    msg = ctypes.wintypes.MSG()
    try:
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                if not processing:
                    processing = True
                    threading.Thread(target=do_correction, daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        user32.UnregisterHotKey(None, HOTKEY_ID)


if __name__ == "__main__":
    main()
