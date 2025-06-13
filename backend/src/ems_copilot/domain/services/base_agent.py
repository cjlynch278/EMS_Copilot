import requests
import json
from google import genai
from google.genai import types
import os


class BaseAgent:
    """
    BaseAgent class for interacting with the Gemini API.
    This class provides a foundation for other agents to inherit from.
    """

    def __init__(self, gemini_api_key):
        """
        Initialize the BaseAgent with the API key.
        """
        self.gemini_api_key = gemini_api_key
        self.gemini_model = os.getenv("GEMINI_MODEL")
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"

    def call_gemini(self, user_prompt=None, system_prompt=None, functions=None):
        """
        Call the Gemini API with optional user prompt, system prompt, and functions.

        Args:
            user_prompt (str): The user prompt to include in the API call.
            system_prompt (str): The system prompt to include in the API call.
            functions (list): A list of function declarations to include in the API call.

        Returns:
            dict: The response from the Gemini API.
        """
        # Initialize the client
        client = genai.Client(api_key=self.gemini_api_key)

        # Setup config and tools only if functions are provided
        config = None
        if functions:
            tools = types.Tool(function_declarations=functions)
            config = types.GenerateContentConfig(tools=[tools])

        # Build the contents
        contents = []

        # Add user prompt
        if user_prompt:
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text=user_prompt
                        )
                    ]
                )
            )

        # Add system prompt
        if system_prompt:
            contents.append(
                types.Content(
                    role="model",
                    parts=[
                        types.Part(
                            text=system_prompt
                        )
                    ]
                )
            )

        # Make the API call
        try:
            if config:
                response = client.models.generate_content(
                    model=self.gemini_model,
                    config=config,
                    contents=contents
                )
            else:
                response = client.models.generate_content(
                    model=self.gemini_model,
                    contents=contents
                )

            print("Response received from Gemini API.")
            # Print the response
            print(response)
            
            return response

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return str(e)



















