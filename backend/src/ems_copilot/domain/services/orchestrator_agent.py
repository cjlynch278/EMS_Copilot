import os
import json
from ems_copilot.domain.services.base_agent import BaseAgent
from ems_copilot.domain.services.gps_agent import GPSAgent
from ems_copilot.domain.services.vitals_agent import VitalsAgent
from ems_copilot.domain.services.triage_agent import TriageAgent
from ems_copilot.infrastructure.database.conversation_history import ConversationHistory


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
        self.triage_agent = TriageAgent(gemini_api_key, self.firebase_credentials_path)
        #update this system prompt to stop
        self.system_prompt = "You are an orchestrator agent for an EMS system. You MUST ALWAYS use a function call to route user queries to the appropriate agent. Never respond with text directly. Use gps_agent for location/direction queries, vitals_agent for patient vitals, weather_agent for weather queries, sql_agent for database queries, and triage_agent for patient symptoms or contextual assessments (like 'what's wrong', 'assess patient', etc.). ALWAYS call one of these functions."
        self.memory = []
        self.conversation_history = ConversationHistory()

        # Initalize task Queue, responsible for managing which agents need to be executed
        self.task_queue = []
        


    def run(self):
        """
        Run the orchestrator in a loop to handle tasks from the task queue.
        """
        print("Orchestrator is running. Type 'exit' to stop.")
        while True:
            if self.task_queue:
                task = self.task_queue.pop(0)
                if task.get("type") == "conversation":
                    # Handle conversation task
                    print(f"Conversation active for: {task['original_input']}")
                    # The conversation will be handled in the next user input
                else:
                    self.orchestrate(task)
            else:
                print("No tasks in the queue. Waiting for user input...")
                user_prompt = input("You: ")
                if user_prompt.lower() == "exit":
                    print("Exiting orchestrator.")
                    break
                self.orchestrate(user_prompt)

    def orchestrate(self, user_prompt):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
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
                "description": """Record patient information and vitals. Use this agent when the user wants to RECORD or WRITE DOWN patient information.
                Examples: 'record patient vitals', 'write down patient allergies', 'note that patient has a laceration', 'patient has O2 of 95'.
                This agent writes data to the database but does not provide medical assessments or recommendations.""",
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
                "description": "Provide medical assessments and recommendations. Use this agent when the user wants an ASSESSMENT, DIAGNOSIS, or MEDICAL OPINION about a patient's condition. Examples: 'assess this patient', 'what's wrong with the patient', 'should I be concerned about these symptoms', 'what priority level is this patient'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_query": {
                            "type": "string",
                            "description": "The user query to be processed by the triage agent. This should simply be exactly what the user asked."
                        }
                    },
                    "required": ["user_query"]
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
        agent_response = self.get_agent_response(response)
        
        # Store response in memory and conversation history
        if hasattr(agent_response, 'text'):
            response_text = agent_response.text
        else:
            response_text = str(agent_response)
            
        self.memory.append({"role": "agent", "content": response_text})
        self.conversation_history.add_conversation(
            user_query=user_prompt,
            agent_response=response_text
        )

        return response_text
    
    def get_agent_response(self, response):
        """
        Get the response from the specified agent with the given parameters.
        Response should always follow the agent_response model.
        """

        
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
                # Call the GPS agent - now returns AgentResponse
                agent_response = self.gps_agent.call_gps(question)
                if agent_response.is_success():
                    return agent_response.text
                else:
                    return f"GPS Error: {agent_response.text}"
            elif agent_name == "vitals_agent":
                input_data = parameters["input"]
                # Call the Vitals agent - now returns AgentResponse
                return self.vitals_agent.call_vitals_agent(input_data)
            elif agent_name == "weather_agent":
                location = parameters["location"]
                return f"Weather agent would get weather for: {location}"
            elif agent_name == "sql_agent":
                query = parameters["query"]
                return f"SQL agent would execute: {query}"
            elif agent_name == "triage_agent":
                user_query = parameters["user_query"]
                # Call the Triage agent - now returns AgentResponse
                return self.triage_agent.call_triage_agent(user_query)
            else:
                return f"Unknown agent: {agent_name}"
                
        except Exception as e:
            print(f"Error in get_agent_response: {e}")
            return f"Sorry, I encountered an error processing your request: {str(e)}"
    

   
