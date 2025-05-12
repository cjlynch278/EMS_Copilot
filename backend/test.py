import openai

openai.api_key = "your-openai-api-key"

messages = [
    {
        "role": "system",
        "content": "You are an EMS Copilot AI. Your job is to classify the following query into one of these categories: protocol, database, triage, vitals, or route."
    },
    {
        "role": "user", 
        "content": "Query: What is the stroke protocol?\nRespond with only the category name (protocol, database, triage, vitals, or route)."
    }
]

try:
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=10,
        temperature=0
    )
    print(response['choices'][0]['message']['content'].strip())
except openai.error.OpenAIError as e:
    print(f"OpenAI Error: {e}")
