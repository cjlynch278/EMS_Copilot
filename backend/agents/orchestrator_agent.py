import sys
import os
import json
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent
from agents.gps_agent import GPSAgent
from agents.vitals_agent import VitalsAgent


class OrchestratorAgent(BaseAgent):
    """
    OrchestratorAgent class for managing interactions between specialized agents.
    Inherits from BaseAgent to handle Gemini API calls.
    """

    def __init__(self, gemini_api_key):
        """
        Initialize the OrchestratorAgent with the API key and Gemini API URL.
        """
        super().__init__(gemini_api_key)  # Initialize BaseAgent
        self.name = "OrchestratorAgent"
        self.description = "An agent that orchestrates the interaction between other agents."
        self.gemini_api_key = gemini_api_key
        self.firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
        google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        # Initialize agents
        self.gps_agent = GPSAgent(gemini_api_key, google_maps_api_key)
        self.vitals_agent = VitalsAgent(gemini_api_key, self.firebase_credentials_path)

        self.system_prompt = "Don't worry too much about clarification. You are an orchestrator agent,simply route the user to the correct agent. " 
        self.memory = []
    def orchestrate(self, user_prompt):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
        # Define the system prompt

        self.memory.append(user_prompt)
        functions = [
            {
                "name": "gps_agent",
                "description": "Get directions and ETA to a location. Find locations that best match description to user query. This agent has access to current user locaiton.",
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
                "description": "Perform functionality based on user input. The vitals agent can look up patient data, write patient vitals and look up trending values.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "input": {
                            "type": "string",
                            "description": "What functionality needs to be performed"
                        }
                    },
                    "required": ["input"]
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
        try:
            response = self.call_gemini(user_prompt, self.system_prompt, functions=functions)

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return None
        # Handle the response
        response = self.get_agent_response(response)
        self.memory.append({"role": "agent", "content": response})

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
        if agent_name == "vitals_agent":
            input_data = parameters["input"]


            response = self.vitals_agent.call_vitals_agent(input_data)
            return response
        
    def run(self):
        """
        Run the orchestrator in a loop to handle multiple user inputs.
        """
        print("Orchestrator is running. Type 'exit' to stop.")
        while True:
            user_prompt = input("You: ")
            if user_prompt.lower() == "exit":
                print("Exiting orchestrator.")
                break

            response = self.orchestrate(user_prompt)
            print(f"Agent: {response}")