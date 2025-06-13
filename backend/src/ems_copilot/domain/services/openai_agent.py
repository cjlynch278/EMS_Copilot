import openai

class OpenAIAgent:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    def classify_query(self, query: str) -> str:
        """
        Use OpenAI to classify the query type.
        """
        messages = [
            {
                "role": "system",
                "content": "You are an EMS Copilot AI. Your job is to classify the following query into one of these categories: protocol, database, triage, vitals, or route."
            },
            {
                "role": "user", 
                "content": f"Query: {query}\nRespond with only the category name (protocol, database, triage, vitals, or route)."
            }
        ]
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Use the appropriate model
                messages=messages,
                max_tokens=10,
                temperature=0
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return "unknown"

