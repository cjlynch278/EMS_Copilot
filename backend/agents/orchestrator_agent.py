import sys
import os
import json
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent
from agents.gps_agent import GPSAgent


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
        google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        print(f"Maps key {google_maps_api_key}")
        self.gps_agent = GPSAgent(gemini_api_key, gemini_model, google_maps_api_key)

        self.system_prompt = ""
    def orchestrate(self, user_prompt):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
        # Define the system prompt

        functions = [
            {
                "name": "gps_agent",
                "description": "Get directions and ETA to a location. Find locations that best match description to user query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The destination or description of destination a user would like to get to."
                        }
                    },
                    "required": ["question"]
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
            {
                "name": "vitals_agent",
                "description": "Get patient vitals.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "patient_id": {
                            "type": "string",
                            "description": "The ID of the patient."
                        }
                    },
                    "required": ["patient_id"]
                }
            },
            {
                "name": "triage_agent",
                "description": "Perform triage on a patient.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symptoms": {
                            "type": "string",
                            "description": "The symptoms of the patient."
                        }
                    },
                    "required": ["symptoms"]
                }
            }
        ]

        # Call the Gemini API with functions
        response = self.call_gemini(user_prompt, self.system_prompt, functions=functions)
        
        response = self.get_agent_response(response)
        
        return response
    
    def get_agent_response(self, response):
        """
        Get the response from the specified agent with the given parameters.
        """
        agent_name = response.candidates[0].content.parts[0].function_call.name
        parameters = response.candidates[0].content.parts[0].function_call.args
        if agent_name == "gps_agent":
            question = parameters["question"]

            # Call the GPS agent with the question
            response = self.gps_agent.call_gps(question)
            return response