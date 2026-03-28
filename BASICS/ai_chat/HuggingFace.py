import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

from huggingface_hub import InferenceClient

# Use provider="auto" — HF picks the best available free provider
client = InferenceClient(
    provider="auto",   # NOT "hf-inference"
    api_key=HF_TOKEN
)

# Use chat_completion (not text_generation) for modern LLMs
response = client.chat_completion(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[
        {"role": "user", "content": "What is artificial intelligence?"}
    ],
    max_tokens=200
)

print(response.choices[0].message.content)