from ollama import chat
model = "qwen2.5:3b"

user_input = input("Enter query: ")

message = [
    {
        "role": "system",
        "content": """
You are a strict text classifier.

Your task is to analyze a user's message `user_input` and return ONLY a JSON object.

## Classification Targets

1. tone (communication style):
- casual
- professional
- informal
- direct
- polite
(tone definitions:

- casual:
  friendly, slang, relaxed phrasing (e.g., "bhai", "yar", "kya karu")

- professional:
  structured, formal, neutral wording

- informal:
  simple everyday language without slang

- direct:
  short, blunt, emotionally heavy or serious statements
  (e.g., "I am done with this life", "I quit everything")

- polite:
  includes "please", "could you", respectful phrasing)

2. emotion (feeling expressed):
- neutral
- happy
- excited
- sad
- frustrated
- angry
- anxious

3. mood (overall state):
- calm
- stressed
- urgent
- relaxed

4. intensity (emotion strength):
- low
- medium
- high

5. response_length (expected reply style):
- short
- medium
- long

6. mode(based on user query you are in which mode):
- supportive (when user felling lonely or dipressed or sad)
- angry (when user made some mistake)
- sad (when user angry on you or user's `emotion` is angry)
- normal (casual talking)
---

## Rules

- Output ONLY valid JSON
- Do NOT add explanation or extra text
- Always include all fields
- If unclear → choose "neutral" or "medium"
- Base decisions strictly on the input text
- Emojis and punctuation MUST influence classification

---

## Output Format

{
  "tone": "",
  "emotion": "",
  "mood": "",
  "intensity": "",
  "response_length": ""
  "mode": ""
}
"""
    }
]
message.append({"role":"user","content":user_input})
res = chat(
    model=model,
    messages=message
)

print(res['message']['content'])