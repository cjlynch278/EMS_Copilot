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

    def call_gemini(self, user_prompt=None, system_prompt=None, functions=None, return_text=False):
        """
        Call the Gemini API with optional user prompt, system prompt, and functions.

        Args:
            user_prompt (str): The user prompt to include in the API call.
            system_prompt (str): The system prompt to include in the API call.
            functions (list): A list of function declarations to include in the API call.
            return_text (bool): If True, return parsed text content instead of raw response.

        Returns:
            dict or str: The response from the Gemini API or parsed text content.
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

        # Add system prompt (if provided separately)
        if system_prompt:
            contents.append(
                types.Content(
                    role="user",
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
            
            # Return parsed text if requested, otherwise return raw response
            if return_text:
                return self.parse_gemini_response(response)
            else:
                return response

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return str(e)

    def parse_gemini_response(self, response):
        """
        Parse a Gemini response object and extract the text content.
        
        Args:
            response: The raw response object from Gemini API
            
        Returns:
            str: The extracted text content or error message
        """
        try:
            if not response or not response.candidates:
                return "No response received from the agent."
            
            candidate = response.candidates[0]
            if not candidate.content or not candidate.content.parts:
                return "Invalid response structure from the agent."
            
            # Extract text from all parts
            text_parts = []
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            
            if text_parts:
                return " ".join(text_parts)
            else:
                return "No text content found in the response."
                
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return f"Error parsing response: {str(e)}"



















