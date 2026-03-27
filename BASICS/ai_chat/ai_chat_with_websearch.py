from ollama import chat
import json
from tavily import TavilyClient

tavily_client = TavilyClient(api_key="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")

# ------------------ TOOL ------------------
tools = [
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_weather",
    #         "description": "Get weather for a given city",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "city": {
    #                     "type": "string",
    #                     "description": "City name"
    #                 }
    #             },
    #             "required": ["city"]
    #         }
    #     }
    # },
    {
        "type": "function",
        "function": {
            "name": "get_webOuput",
            "description": "Get webOutput for a given topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to get output for"
                    }
                },
                "required": ["topic"]
            }
        }
    }
]

# ------------------ DATA ------------------
# Weatherdict = {
#     "mathura": 10,
#     "lucknow": 30
# }

# ------------------ HANDLER ------------------
# def handler(city):
#     city = city.lower()
#     weather = Weatherdict.get(city, None)

#     if weather is None:
#         return f"No data for {city}"
    
#     return f"Weather in {city} is {weather}°C"

# ------------------ SYSTEM ------------------
messages = [
    {
        "role": "system",
        "content": """
You are Sammu(a girl assistant).

If a tool is needed, call it.

Give the putput in json formate:
if a tool is being called respond like:
{
    "action": "tool calling`",
    "response": "<your answer>"
}
otherwise respond like:
{
    "action": "normal`",
    "response": "<your answer>"
}
"""
    }
]

# ------------------ INPUT ------------------
user = input("You: ")
messages.append({"role": "user", "content": user})

# ------------------ LLM CALL ------------------
res = chat(
    model="gpt-oss:120b-cloud",   # stable use this
    messages=messages,
    tools=tools
)

message = res["message"]

# ------------------ TOOL OR NORMAL ------------------
if message.get("tool_calls"):
    print("⚡ Tool Called")

    for tc in message["tool_calls"]:
        # if tc["function"]["name"] == "get_weather":

        #     args = tc["function"]["arguments"]
        #     print(args)

        #     # handle string/dict case
        #     if isinstance(args, str):
        #         args = json.loads(args)

        #     city = args["city"]

        #     print("City:", city)

        #     result = handler(city)

        #     messages.append({
        #         "role": "tool",
        #         "name": "get_weather",
        #         "content": result
        #     })

        if tc in message["tool_calls"]:
            if tc["function"]["name"] == "get_webOuput":

                args = tc["function"]["arguments"]
                # print(args)

                # handle string/dict case
                if isinstance(args, str):
                    args = json.loads(args)

                topic = args["topic"]

                # print("Topic:", topic)

                # result = handler(city)
                
                result = tavily_client.search(topic, include_answer=True)['answer']
                
                
                messages.append({
                    "role": "tool",
                    "name": "get_webOuput",
                    "content": result
                })

        res = chat(
            model="gpt-oss:120b-cloud",
            messages=messages
        )
        final_reply = res["message"]["content"]

else:
    final_reply = message.get("content", "")

# ------------------ OUTPUT ------------------
print("AI:", final_reply)