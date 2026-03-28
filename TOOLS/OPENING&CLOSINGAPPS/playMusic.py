import subprocess
import urllib.parse
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from ollama import chat
import json

MODEL = 'qwen2.5:3b'
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def play_music_on_youtube(song_name: str):
    query = urllib.parse.quote(song_name)
    url = f"https://www.youtube.com/results?search_query={query}"

    subprocess.call("taskkill /f /im brave.exe", shell=True)
    time.sleep(2)

    subprocess.Popen([
        BRAVE_PATH,
        "--remote-debugging-port=9222",
        "--user-data-dir=C:\\brave-debug",
        url
    ])
    time.sleep(6)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    service = Service(ChromeDriverManager(driver_version="146.0.7680.0").install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 20)

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "ytd-app")))

        first_video = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title"))
        )
        title = first_video.get_attribute("title")
        first_video.click()
        print(f"🎵 Ab chal raha hai: {title}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")


SYSTEM_PROMPT = """You are a music player assistant. Extract song/video title from user input.
Return ONLY valid JSON, no explanation, no extra text.

Examples:
Input: play shape of you song
Output: {"command": "play", "song": "Shape of You"}

Input: kishore kumar old songs
Output: {"command": "play", "song": "Kishore Kumar old songs"}

Input: headlights slowed
Output: {"command": "play", "song": "Headlights slowed"}
"""

def ask_model(user_input: str):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    resp = chat(model=MODEL, messages=messages)

    content = resp["message"]["content"].strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print("Parse error:", content)
        return {}


def main():
    print("Music player ready!")

    while True:
        user_input = input("\nSong name: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            break

        result = ask_model(user_input)

        if "song" in result:
            play_music_on_youtube(result["song"])
        else:
            print("Can't understand song, try again")

if __name__ == "__main__":
    main()