from ollama import chat
model = "qwen2.5:3b"

user_inpt = input("Enter query: ")

def queryDetector(user_inpt):
    prompt = f"""
Classify the user's intention.
user input: "{user_inpt}"
return only one word:
[General,Tool,Web search]

Do not explain anything.
"""
    res = chat(
        model=model,
        messages=[{"role":"user","content":prompt}]
    )
    intention = res['message']['content'].strip().lower()
    return intention


answer = queryDetector(user_inpt)
print(answer)