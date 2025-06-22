import os
import json
from ems_copilot.domain.services.base_agent import BaseAgent
from ems_copilot.domain.services.gps_agent import GPSAgent
from ems_copilot.domain.services.vitals_agent import VitalsAgent


class OrchestratorAgent(BaseAgent):
    """
    OrchestratorAgent class for managing interactions between specialized agents.
    Inherits from BaseAgent to handle Gemini API calls.
    """

    def __init__(self, gemini_api_key, firebase_credentials_path=None):
        """
        Initialize the OrchestratorAgent with the API key and Gemini API URL.
        """
        super().__init__(gemini_api_key)  # Initialize BaseAgent
        self.name = "OrchestratorAgent"
        self.description = "An agent that orchestrates the interaction between other agents."
        self.gemini_api_key = gemini_api_key
        
        # Use provided credentials path or fall back to environment variable
        if firebase_credentials_path is None:
            self.firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
        else:
            self.firebase_credentials_path = firebase_credentials_path
            
        google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        # Initialize agents
        self.gps_agent = GPSAgent(gemini_api_key, google_maps_api_key)
        self.vitals_agent = VitalsAgent(gemini_api_key, self.firebase_credentials_path)
        #update this system prompt to stop
        self.system_prompt = "You are an orchestrator agent for an EMS system. You MUST ALWAYS use a function call to route user queries to the appropriate agent. Never respond with text directly. Use gps_agent for location/direction queries, vitals_agent for patient vitals, weather_agent for weather queries, sql_agent for database queries, and triage_agent for patient symptoms. ALWAYS call one of these functions."
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
            # Combine system prompt with user prompt for better clarity
            combined_prompt = f"{self.system_prompt}\n\nUser query: {user_prompt}"
            response = self.call_gemini(combined_prompt, functions=functions)

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
        print("--------------------------------")
        print(response)
        print("--------------------------------")
        
        try:
            # Check if response has the expected structure and function call
            if (not response or 
                not response.candidates or 
                not response.candidates[0] or 
                not response.candidates[0].content or 
                not response.candidates[0].content.parts or 
                not response.candidates[0].content.parts[0] or 
                not response.candidates[0].content.parts[0].function_call):
                
                print("No function call found in response")
                return "I understand your query, but I need to route it to a specific agent. Please try asking about: patient vitals (e.g., 'record heart rate'), GPS directions (e.g., 'get directions to hospital'), weather (e.g., 'what's the weather'), database queries, or patient triage (e.g., 'patient has chest pain')."
            
            agent_name = response.candidates[0].content.parts[0].function_call.name
            parameters = response.candidates[0].content.parts[0].function_call.args
            
            if agent_name == "gps_agent":
                question = parameters["question"]
                # Call the GPS agent with the question
                response = self.gps_agent.call_gps(question)
                return response
            elif agent_name == "vitals_agent":
                input_data = parameters["input"]
                response = self.vitals_agent.call_vitals_agent(input_data)
                return response
            elif agent_name == "weather_agent":
                location = parameters["location"]
                return f"Weather agent would get weather for: {location}"
            elif agent_name == "sql_agent":
                query = parameters["query"]
                return f"SQL agent would execute: {query}"
            elif agent_name == "triage_agent":
                symptoms = parameters["symptoms"]
                return f"Triage agent would assess symptoms: {symptoms}"
            else:
                return f"Unknown agent: {agent_name}"
                
        except Exception as e:
            print(f"Error in get_agent_response: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"
    
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