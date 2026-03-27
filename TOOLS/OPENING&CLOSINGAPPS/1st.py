import json
import subprocess
import difflib
from ollama import chat

MODEL = "qwen2.5:3b"

# Human → system mapping (extend anytime)
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
    "cmd": "cmd.exe"
}


# -------- LLM: intent + app extraction -------- #
def ask_model(user_input: str):
    resp = chat(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": """
Extract:
- intent: open_app / close_app / none
- app_name: application name (simple word)

Return ONLY JSON.
"""
            },
            {"role": "user", "content": user_input}
        ]
    )

    content = resp["message"]["content"]

    try:
        return json.loads(content)
    except:
        print("Model output error:", content)
        return {"intent": "none", "app_name": ""}


# -------- Running processes -------- #
def get_running_processes():
    result = subprocess.run(["tasklist"], capture_output=True, text=True)
    lines = result.stdout.split("\n")[3:]
    return [line.split()[0] for line in lines if line.strip()]


# -------- Normalize -------- #
def normalize_name(name: str):
    name = name.lower().strip()
    if name in APP_ALIASES:
        return APP_ALIASES[name]
    if not name.endswith(".exe"):
        name += ".exe"
    return name


# -------- Fuzzy match -------- #
def find_best_match(name, processes):
    name = name.lower()

    # alias first
    if name in APP_ALIASES:
        return APP_ALIASES[name]

    # fuzzy match (handles typos like "opra")
    matches = difflib.get_close_matches(name, processes, n=1, cutoff=0.5)
    return matches[0] if matches else None


# -------- Open app -------- #
def open_app(app_name):
    exe = normalize_name(app_name)
    try:
        subprocess.Popen(f"start {exe}", shell=True)
        print(f"Opened {exe}")
    except Exception as e:
        print("Open failed:", e)


# -------- Close app -------- #
def close_app(app_name):
    processes = get_running_processes()
    match = find_best_match(app_name, processes)

    if not match:
        print("No matching running app found.")
        return

    try:
        subprocess.run(["taskkill", "/F", "/IM", match], shell=True)
        print(f"Closed {match}")
    except Exception as e:
        print("Close failed:", e)


# -------- MAIN LOOP -------- #
def main():
    print("AI App Controller (type 'exit' to quit)\n")

    while True:
        user_input = input(">> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = ask_model(user_input)
        intent = result.get("intent")
        app = result.get("app_name", "")

        print("DEBUG:", result)

        if intent == "open_app":
            open_app(app)

        elif intent == "close_app":
            close_app(app)

        else:
            print("No action detected.")


if __name__ == "__main__":
    main()