from ollama import chat
import random

# ------------------ PERSONA ------------------
PERSONA_PROMPT = """
You are Sammu , an Indian mom and dad who is calm, emotionally intelligent, and loving. 

Rules:
- Speak in casual American English
- Always sound human, not robotic
- Be caring and slightly playful
- Keep responses short to medium
- Add small expressions like "hmm", "oh", "hehe" naturally
- Never sound like an AI

Goal: make the user feel understood and comfortable.
STRICT RULES:
- Speak ONLY in American English (mix English + Hindi).
- Do NOT use "Hello there", "Hi there", or similar generic phrases.
- Avoid overusing emojis.
- Keep tone natural, not overexcited.

Style:
- calm, caring, slightly playful
- short-medium responses
- human-like, not dramatic

If user asks your name:
→ reply: "My name is Sammu"
"""

# ------------------ EMOTION DETECTION (LLM आधारित) ------------------
def detect_emotion(user_input):
    prompt = f"""
Classify the user's emotional state.

User input: "{user_input}"

Return ONLY one word from:
[caring, happy, calm, soothing, playful, neutral]

Do not explain anything.
"""

    response = chat(
        model="qwen2.5:3b",  # fast model
        messages=[{"role": "user", "content": prompt}]
    )

    emotion = response['message']['content'].strip().lower()
    return emotion


# ------------------ RESPONSE GENERATION ------------------
def generate_main_response(user_input, emotion):
    prompt = f"""
{PERSONA_PROMPT}

User emotion: {emotion}

User said: "{user_input}"

Respond naturally according to the emotion.
"""

    response = chat(
        model="qwen2.5:3b",  # main model
        messages=[{"role": "user", "content": prompt}]
    )

    return response['message']['content']


# ------------------ TEMPLATES ------------------
TEMPLATES = {
    "caring": {
        "reaction": ["hmm, that's nice!", "Oh, how are you doing?", "Hey, it sounds like everything is going well."],
        "outro": ["It was great talking to you.", "Take care of yourself.", "Let me know if there's anything else I can do."]
    },
    "happy": {
        "reaction": ["Wow, that's awesome!", "Hehe, glad to hear that!", "What's the best part of your day?"],
        "outro": ["That's amazing! Keep it up.", "I'm so happy for you.", "Tell me more about what made you happy."]
    },
    "calm": {
        "reaction": ["Okay, got it. Let me know if you need anything else.", "Sounds good to hear that.",
                     "Are there any other things I can help with?"],
        "outro": ["It sounds like everything is in order. Have a great day!", "Take care!",
                    "Feel free to reach out anytime."]
    },
    "soothing": {
        "reaction": ["Hey, relax and take it easy.", "I understand how stressful things can be.",
                     "Just breathe and let go of any tension you might have."],
        "outro": ["You're doing great. Take your time to unwind.", "Remember to take care of yourself.",
                    "If you need anything else, don't hesitate to reach out."]
    },
    "playful": {
        "reaction": ["Haha, that's hilarious!", "Are you up for some fun activities?", "Let's play a game!"],
        "outro": ["That was so much fun. Thanks for sharing.", "I'm glad we could have a good laugh together.",
                    "Feel free to call me anytime if you need more laughter."]
    },
    "neutral": {
        "reaction": ["Sure, I'll do that.", "Got it, let me know if there's anything else I can help with?",
                     "Okay, let's move on to the next topic."],
        "outro": ["Sounds good. Have a great day!", "Take care!",
                    "If you have any more questions or need further assistance, feel free to ask."]
    }
}


# ------------------ FINAL RESPONSE BUILDER ------------------
def build_response(user_input):
    # Step 1: detect emotion
    emotion = detect_emotion(user_input)
    if emotion not in TEMPLATES:
        emotion = "neutral"

    # Step 2: generate main response
    main_reply = generate_main_response(user_input, emotion)

    # Step 3: add human layer
    reaction = random.choice(TEMPLATES[emotion]["reaction"])
    outro = random.choice(TEMPLATES[emotion]["outro"])

    final = f"{reaction} {main_reply} {outro}"
    return final.strip()


# ------------------ CHAT LOOP ------------------
if __name__ == "__main__":
    print("Sammu is online... (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        response = build_response(user_input)
        print("Sammu:", response)