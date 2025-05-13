import sys
import os
import json
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent


class OrchestratorAgent(BaseAgent):
    """
    OrchestratorAgent class for managing interactions between specialized agents.
    Inherits from BaseAgent to handle Gemini API calls.
    """

    def __init__(self, gemini_api_key, gemini_model):
        """
        Initialize the OrchestratorAgent with the API key and Gemini API URL.
        """
        super().__init__(gemini_api_key, gemini_model=gemini_model)  # Initialize BaseAgent
        self.name = "OrchestratorAgent"
        self.gemini_model = gemini_model
        self.description = "An agent that orchestrates the interaction between other agents."
        self.gemini_api_key = gemini_api_key

        self.system_prompt = ""
    def orchestrate(self, user_prompt):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
        # Define the system prompt

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
        response = self.call_gemini(user_prompt, self.system_prompt, functions=functions)
        return response