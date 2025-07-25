import requests
import json
from google import genai
from backend.src.ems_copilot.infrastructure.database.conversation_history import ConversationHistory
from google.genai import types
import os
from ems_copilot.infrastructure.utils.secret_utils import get_gemini_api_key


class BaseAgent:
    """
    BaseAgent class for interacting with the Gemini API.
    This class provides a foundation for other agents to inherit from.
    """

    def __init__(self, gemini_api_key=None, project_id=None, agent_name=None):
        """
        Initialize the BaseAgent with the API key.
        
        Args:
            gemini_api_key: Direct API key. If None, will be retrieved from Secret Manager.
            project_id: Google Cloud project ID for Secret Manager access.
        """
        # Initialize conversation history
        self.conversation_history = ConversationHistory()
                # Get API key from Secret Manager if not provided directly
        if gemini_api_key is None:
            print(f"Getting API key from Secret Manager for project: {project_id}")
            self.gemini_api_key = get_gemini_api_key(project_id)
            print(f"API key retrieved: {self.gemini_api_key[:10]}..." if self.gemini_api_key else "API key is None")
        else:
            self.gemini_api_key = gemini_api_key
            print(f"Using provided API key: {self.gemini_api_key[:10]}..." if self.gemini_api_key else "Provided API key is None")
            
        # Use a default model if GEMINI_MODEL is not set
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"
        
        self.agent_name = agent_name

        # Global System Prompt is the prompt that will be used by *every* single agent. 
        # This simply describes what's going on to each agent. 
        self.global_system_prompt = """
            You are an instantiation of a agent class. 
            You are part of a team of agents that accomplish EMS related functionalities.
            If the user refers to you as 'LUCAS' this is your name, they are refferring to you.
            You will be given a set of conversation history which may or may not be relevant to you.
            Use this conversation history at your own discretion.
        """

    def call_gemini(self, user_prompt=None, system_prompt=None, functions=None, return_text=False, vector_query=None):
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
        print('initializing client with api key: ', self.gemini_api_key)
        client = genai.Client(api_key=self.gemini_api_key)

        # Setup config and tools only if functions are provided
        config = None
        if functions:
            tools = types.Tool(function_declarations=functions)
            config = types.GenerateContentConfig(tools=[tools])

        # Build the contents
        contents = []

        # New functionality would be great if we called the hypbrid context calling here.
        # Query both the past 5 conversations and 5 relevant conversations from conversation history class.
        # Prepend this to the user or system prompt. 
        
        if(vector_query):
            relevant_conversations = self.conversation_history.search_conversations(vector_query)
            user_query = f"""A list of relevant conversations with the user are stored here: {relevant_conversations}. Here is the current user's query: {user_query}""" 


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
        # Does this work?
        # Simply prepend the given system prompt to the the global prompt.
        system_prompt = self.global_system_prompt + system_prompt

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
            print(f"Using Gemini model: {self.gemini_model}")
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


        # Possibly add functionality to store the conversation in conversation history.

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



















