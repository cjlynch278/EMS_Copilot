import requests
import json
import google.generativeai as genai

class BaseAgent:
    """
    BaseAgent class for interacting with the Gemini API.
    This class provides a foundation for other agents to inherit from.
    """

    def __init__(self, gemini_api_key, gemini_url, model):
        """
        Initialize the BaseAgent with the API key and Gemini API URL.
        """
        self.gemini_api_key = gemini_api_key
        self.gemini_url = gemini_url
        genai.configure(api_key=self.gemini_api_key)
        self.client = genai.GenerativeModel(model)


    def call_gemini(self, user_prompt, system_prompt=None, functions=None):
        """
        Make a call to the Gemini API using the provided user prompt, system prompt, and optional functions.
        """
    

        headers = {
            "Content-Type": "application/json",
        }

        # Base payload with user and system prompts
        payload = {
            "contents": []
        }
        prompt = ""
        if system_prompt:
            prompt += f"{system_prompt}\n"
        
        if user_prompt:
            prompt += f"{user_prompt}\n"

        # Add prompts to the payload
        payload["contents"].append({
            "parts": [{"text": f"{prompt}" }]
        })


        # Add functions to the payload if provided
        if functions:
            payload["tools"] = [
                {
                    "functionDeclarations": functions
                }
            ]

        # Debugging: Print the payload
        print(f"Payload: {json.dumps(payload, indent=2)}")

        try:
            # Make the POST request
            response = requests.post(
                f"{self.gemini_url}?key={self.gemini_api_key}",
                headers=headers,
                data=json.dumps(payload),
            )

            # Raise an exception for HTTP errors
            response.raise_for_status()

            # Parse and return the response
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error while calling Gemini API: {e}")
            return None