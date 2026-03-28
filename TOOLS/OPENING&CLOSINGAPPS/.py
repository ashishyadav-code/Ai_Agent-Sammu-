APP_ALIASES = {
    "files": "explorer.exe",
    "file manager": "explorer.exe",
    "explorer": "explorer.exe",
    "browser": "chrome.exe",
    "chrome": "chrome.exe",
    "opera": "opera.exe",
    "notepad": "notepad.exe",
    "vs code": "Code.exe",
    "vscode": "Code.exe",
    "calculator": "calc.exe",
    "cmd": "cmd.exe",
    "brave": "brave.exe",
    "spotify": "spotify.exe",
    "vlc": "vlc.exe",
}

def normalize_name(name: str):
    name = name.lower().strip()
    if name in APP_ALIASES:
        return APP_ALIASES[name]
    if not name.endswith(".exe"):
        name += ".exe"
    return name

from ollama import chat
import json

MODEL = "qwen2.5:3b"

SYSTEM_PROMPT = """You are an app controller. Extract ONLY app open/close commands.

STRICT Rules:
- Return ONLY raw JSON. No markdown, no explanation, no extra text.
- "intent" must be ONLY "open_app" or "close_app". Nothing else.
- "app_name" must be ONLY the app name. No extra words.
- Ignore anything that is NOT opening or closing an app.
- Single app → single JSON object.
- Multiple apps → JSON array.
- Nothing to open/close → return {}

Examples:

Input: open chrome
Output: {"intent": "open_app", "app_name": "chrome"}

Input: close notepad
Output: {"intent": "close_app", "app_name": "notepad"}

Input: open chrome and notepad
Output: [{"intent": "open_app", "app_name": "chrome"}, {"intent": "open_app", "app_name": "notepad"}]

Input: open chrome and close notepad
Output: [{"intent": "open_app", "app_name": "chrome"}, {"intent": "close_app", "app_name": "notepad"}]

Input: open brave, explorer and close opera
Output: [{"intent": "open_app", "app_name": "brave"}, {"intent": "open_app", "app_name": "explorer"}, {"intent": "close_app", "app_name": "opera"}]

Input: play music and open chrome
Output: {"intent": "open_app", "app_name": "chrome"}

Input: hi
Output: {}

Input: play antigravity song
Output: {}
"""

def ask_model(user_input: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    res = chat(model=MODEL, messages=messages)
    content = res["message"]["content"].strip()

    # Clean markdown agar model ne wrap kar diya
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(content)

        # Normalize app names
        if isinstance(parsed, list):
            for item in parsed:
                if "app_name" in item:
                    item["app_name"] = normalize_name(item["app_name"])
        elif isinstance(parsed, dict) and "app_name" in parsed:
            parsed["app_name"] = normalize_name(parsed["app_name"])

        return parsed

    except Exception as e:
        print("Parse error:", content)
        return {}


# Test
tests = [
    "open brave",
    "close notepad",
    "open chrome and notepad",
    "brave, explorer khol do aur opera band kar do",
    "play antigravity and open chrome",
    "hi bhai kya haal",
]

for test in tests:
    result = ask_model(test)
    print(f"Input : {test}")
    print(f"Output: {result}\n")