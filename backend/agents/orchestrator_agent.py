import sys
import os
import json
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent
import json


class OrchestratorAgent(BaseAgent):
    """
    OrchestratorAgent class for managing interactions between specialized agents.
    Inherits from BaseAgent to handle Gemini API calls.
    """

    def __init__(self, gemini_api_key, gemini_url):
        """
        Initialize the OrchestratorAgent with the API key and Gemini API URL.
        """
        super().__init__(gemini_api_key, gemini_url)  # Initialize BaseAgent
        self.name = "OrchestratorAgent"
        self.description = "An agent that orchestrates the interaction between other agents."
        print(f"OrchestratorAgent initialized with API key: {self.gemini_api_key} and URL: {self.gemini_url}")
        print(f"OrchestratorAgent initialized with name: {self.name} and description: {self.description}")
    def orchestrate(self, user_prompt):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
        # Define the system prompt
        system_prompt = """You are an AI orchestrator agent embedded in an ambulance's digital copilot system. 
            Your role is to interpret natural language from EMTs and route the request to the appropriate specialized agent. 
            You do not answer questions directly. Instead, you must always return a function name and parameters to call the correct agent.

            If the user prompt is unclear, make a best guess based on the available agents and their descriptions. Always return a function name and parameters.
            """
        functions = [
            {
                "name": "gps_agent",
                "description": "Get directions and ETA to a location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "The destination to navigate to."
                        }
                    },
                    "required": ["destination"]
                }
            },
            {
                "name": "weather_agent",
                "description": "Get current weather for a location.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get weather for."
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "sql_agent",
                "description": "Search hospital databases with SQL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to run."
                        }
                    },
                    "required": ["query"]
                }
            },
            # Add more agents similarly...
        ]

        # Call the Gemini API with functions
        response = self.call_gemini(user_prompt, system_prompt, functions=functions)
        if response:
            print("Response from Gemini API:", json.dumps(response, indent=2))