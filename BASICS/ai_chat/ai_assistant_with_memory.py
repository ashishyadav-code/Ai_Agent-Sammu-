import whisper
import torch
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import json
from ollama import chat

# ------------------ DEVICE ------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on {device}")

# ------------------ LOAD WHISPER ------------------
stt_model = whisper.load_model("medium").to(device)

# ------------------ AUDIO RECORD ------------------
def record_audio(duration=5, fs=16000):
    print("\n🎤 Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    print(" Recording done")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(temp_file.name, fs, recording)
    return temp_file.name

# ------------------ MEMORY ------------------
MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"name": None}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

memory = load_memory()

# ------------------ TOOLS ------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "remember_name",
            "description": "Save the user's name when clearly provided",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "User's name"
                    }
                },
                "required": ["name"]
            }
        }
    }
]

# ------------------ SYSTEM PROMPT ------------------
messages = [
    {
        "role": "system",
        "content": f"""
You are Sammu, an AI assistant.

Call the function `remember_name` ONLY if the user clearly provides their name.

Otherwise respond normally.

If name is already known, use it naturally in responses.

Current known name: {memory.get("name")}
"""
    }
]

# ------------------ TOOL HANDLER ------------------
def handle_tool_call(name):
    memory["name"] = name
    save_memory(memory)
    print(f"✅ Name saved: {name}")

# ------------------ JSON FALLBACK PARSER ------------------
def try_parse_tool_call(text):
    try:
        data = json.loads(text)
        if isinstance(data, dict) and data.get("name") == "remember_name":
            return data
    except:
        return None
    return None

# ------------------ MAIN LOOP ------------------
while True:
    try:
        audio_file = record_audio(duration=5)

        with torch.no_grad():
            result = stt_model.transcribe(audio_file)

        user_text = result["text"].strip()

        if user_text == "":
            print("No speech detected")
            continue

        print("👤 You:", user_text)

        messages.append({"role": "user", "content": user_text})

        # 🔥 FIRST LLM CALL
        res = chat(
            model='gpt-oss:120b-cloud',
            messages=messages,
            tools=tools
        )

        message = res['message']
        content = message.get("content", "")

        tool_called = False
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                if tool_call["function"]["name"] == "remember_name":
                    name = tool_call["function"]["arguments"]["name"]
                    handle_tool_call(name)
                    tool_called = True
        parsed = try_parse_tool_call(content)
        if parsed:
            name = parsed["arguments"]["name"]
            handle_tool_call(name)
            tool_called = True
        if tool_called:
            messages.append({
                "role": "assistant",
                "content": "Name saved."
            })

            res = chat(
                model='gpt-oss:120b-cloud',
                messages=messages
            )

            final_reply = res['message']['content']

        else:
            final_reply = content

        # ------------------ NAME INJECTION ------------------
        if memory.get("name"):
            final_reply = f"{memory['name']}, {final_reply}"

        messages.append({"role": "assistant", "content": final_reply})

        print("🤖 Sammu:", final_reply)

    except KeyboardInterrupt:
        print("\n🛑 Exiting...")
        break

    except Exception as e:
        print("❌ Error:", e)