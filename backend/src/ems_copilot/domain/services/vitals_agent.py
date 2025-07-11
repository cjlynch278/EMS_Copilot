import os
import json
import requests
from pathlib import Path
from ems_copilot.infrastructure.database.firestore_db import FirestoreDB
from ems_copilot.infrastructure.database.conversation_history import ConversationHistory
from ems_copilot.infrastructure.utils.general_utils import *
from ems_copilot.domain.services.base_agent import BaseAgent
from ems_copilot.domain.models.agent_response import AgentResponse


class VitalsAgent(BaseAgent):
    """
    Vitals_Agent class for managing all vitals. These vitals will be stored in a SQL database.
    This agent will be used to track trending patient vitals and provide information about them.
    """

    def __init__(self, gemini_api_key, firebase_credentials_path, firebase_collection_name="vitals"):

        """
        Initialize the Vitals_Agent with the API key and Gemini API URL.
        This agent will be used to track trending patient vitals and provide information about them.
        """

        super().__init__(gemini_api_key)  # Initialize BaseAgent
        self.name = "Vitals_Agent"
        self.description = "An agent that provides vitals related functionalities."
        self.firestore_db = FirestoreDB(firebase_credentials_path)
        self.conversation_history = ConversationHistory()

        self.gemini_api_key = gemini_api_key
        self.system_prompt = (
            "You are a Vitals agent. Your role is to manage patient vitals and notes. "
            "When given an input or statement, analyze it for ALL vital signs mentioned and invoke the 'write_multiple_vitals' function for each vital sign found. "
            "For example, if the input says 'patient John Smith has O2 of 93 and sugar of 120', you should call write_multiple_vitals twice - once for O2 and once for glucose. "
            "Additionally, if the input contains important patient information that is not a vital sign (like injuries, symptoms, observations, etc.), invoke the 'write_multiple_vitals' function with vitals_name='note' and vitals_value set to the note content. "
            "For example, if the input says 'patient sustained head trauma to the back of the head', you should call write_multiple_vitals with vitals_name='note' and vitals_value='head trauma to the back of the head'. "
            "Do not generate any natural language responses. "
            "Only return the function calls and their arguments. Do not include any text."
            "However, if you detect missing required information (like patient name, vital sign type, or vital sign value), use the 'error' function to return an error message. "
        )
    
    def call_vitals_agent(self, input):
        """
        Call the Vitals agent with the given input.
        This method will be used to call the Vitals agent with the given input.
        """
        functions = [
        {
            "name": "write_multiple_vitals",
            "description": "Write a single vital sign data to Firestore. Call this function once for each vital sign found in the input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vitals_name": {
                        "type": "string",
                        "description": "The type of vital being recorded (heart rate, bp, o2, glucose, sugar, blood pressure, temperature, etc.)."
                    },
                    "vitals_value": {
                        "type": "string",
                        "description": "The value of the vital being recorded."
                    },
                    "patient_name": {
                        "type": "string",
                        "description": "The name of the patient."
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "The timestamp of the vitals data in ISO 8601 format. The timestamp should be the current time if not specified."
                    }
                },
                "required": [ "vitals_name", "vitals_value", "timestamp"]
            }
        },
        {
            "name": "error",
            "description": """
                Return an error message back to the orchestrator agent. If you think the user is asking 
                for something that is not a vital sign, return an error message. Or you have missing 
                information, return an error message. This can be used at your discretion
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "error_message": {
                        "type": "string",
                        "description": "The error message to return to the orchestrator agent."
                    }
                },
                "required": ["error_message"]
            }
        },
        {
            "name": "get_vitals",
            "description": "Retrieve vitals data for a specific patient from Firestore.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The ID of the patient whose vitals data is to be retrieved."
                    }
                },
                "required": ["patient_id"]
            }
        },
        {
            "name": "get_vitals_by_patient_name",
            "description": "Retrieve vitals data for a specific patient from Firestore.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {
                        "type": "string",
                        "description": "The name of the patient whose vitals data is to be retrieved."
                    }
                },
                "required": ["patient_name"]
            }
        }
    ]

        # Get current time: 
        try:
            current_time = get_time()
        except Exception as e:
            print(f"Error getting current time: {e}")

        try:
            user_prompt = f"Perform the following action: {input}. \n The current time is {current_time}."
            # First get the raw response to handle function calls
            raw_response = self.call_gemini( system_prompt=self.system_prompt, user_prompt=user_prompt, functions=functions)
            handle_response = self.handle_response(response=raw_response)
            
            # If we have a structured response from handle_response, return it
            if handle_response:
                # Store conversation in history - convert response to string
                response_str = str(handle_response) if handle_response else "No response"
                self.conversation_history.add_conversation(
                    user_query=input,
                    agent_response=response_str
                )
                
                return handle_response
            
            # Otherwise, return the parsed text response as an AgentResponse
            parsed_response = self.parse_gemini_response(raw_response)
            
            # Store conversation in history
            self.conversation_history.add_conversation(
                user_query=input,
                agent_response=parsed_response
            )
            
            # Convert text response to AgentResponse
            return AgentResponse(
                status="success",
                text=parsed_response,
                reason="",
                data={"parsed_response": parsed_response},
                metadata={
                    "agent": "vitals_agent",
                    "operation": "call_vitals_agent"
                }
            )
        except Exception as e:
            print(f"Error calling Vitals agent: {e}")
            return AgentResponse(
                status="fail",
                text=f"Sorry, I encountered an error processing your request: {str(e)}",
                reason=str(e),
                data={"error": str(e)},
                metadata={
                    "agent": "vitals_agent",
                    "operation": "call_vitals_agent"
                }
            )
    
    def write_vitals(self, json_vitals_data):
        """
        Write vitals data to Firestore.
        """
        try:
            # Write the vitals data to the Firestore 'vitals' collection
            self.firestore_db.write_vitals("vitals", json_vitals_data)

            # Return success response
            return AgentResponse(
                status="success",
                text=f"{json_vitals_data.get('vitals_name').capitalize()} recorded successfully.",
                reason="",
                data={
                    "entry": {
                        "type": json_vitals_data.get("vitals_name"),
                        "value": json_vitals_data.get("vitals_value"),
                        "timestamp": json_vitals_data.get("timestamp")
                    }
                },
                metadata={
                    "agent": "vitals_agent",
                    "operation": "write_vitals"
                }
            )
        except Exception as e:
            print(f"Error writing vitals: {e}")
            return AgentResponse(
                status="fail",
                text=f"Failed to record {json_vitals_data.get('vitals_name')}. Error: {str(e)}",
                reason=str(e),
                data={"error": str(e)},
                metadata={
                    "agent": "vitals_agent",
                    "operation": "write_vitals"
                }
            )
    
    def return_error(self, error_message):
        """
        Return an error message to the orchestrator.
        This function is called by the LLM when it detects an error or missing information.
        """
        return AgentResponse(
            status="fail",
            text=error_message,
            reason="user_error",
            data={"error_message": error_message},
            metadata={
                "agent": "vitals_agent",
                "operation": "return_error"
            }
        )

    def get_vitals(self, patient_id):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            vitals_data = self.firestore_db.get_vitals("vitals", patient_id)
            if vitals_data:
                return AgentResponse(
                    status="success",
                    text=f"Retrieved vitals data for patient {patient_id}",
                    reason="",
                    data={"vitals": vitals_data},
                    metadata={
                        "agent": "vitals_agent",
                        "operation": "get_vitals",
                        "patient_id": patient_id
                    }
                )
            else:
                return AgentResponse(
                    status="fail",
                    text=f"No vitals data found for patient {patient_id}",
                    reason=f"No vitals data found for patient {patient_id}",
                    data={"patient_id": patient_id},
                    metadata={
                        "agent": "vitals_agent",
                        "operation": "get_vitals"
                    }
                )
        except Exception as e:
            print(f"Error retrieving vitals: {e}")
            return AgentResponse(
                status="fail",
                text=f"Error retrieving vitals for patient {patient_id}: {str(e)}",
                reason=str(e),
                data={"error": str(e), "patient_id": patient_id},
                metadata={
                    "agent": "vitals_agent",
                    "operation": "get_vitals"
                }
            )
        
    def get_vitals_by_patient_name(self, patient_name):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            vitals_data = self.firestore_db.get_vitals_by_patient_name("vitals", patient_name)
            if vitals_data:
                return AgentResponse(
                    status="success",
                    text=f"Retrieved vitals data for patient {patient_name}",
                    reason="",
                    data={"vitals": vitals_data},
                    metadata={
                        "agent": "vitals_agent",
                        "operation": "get_vitals_by_patient_name",
                        "patient_name": patient_name
                    }
                )
            else:
                return AgentResponse(
                    status="fail",
                    text=f"No vitals data found for patient {patient_name}",
                    reason=f"No vitals data found for patient {patient_name}",
                    data={"patient_name": patient_name},
                    metadata={
                        "agent": "vitals_agent",
                        "operation": "get_vitals_by_patient_name"
                    }
                )
        except Exception as e:
            print(f"Error retrieving vitals: {e}")
            return AgentResponse(
                status="fail",
                text=f"Error retrieving vitals for patient {patient_name}: {str(e)}",
                reason=str(e),
                data={"error": str(e), "patient_name": patient_name},
                metadata={
                    "agent": "vitals_agent",
                    "operation": "get_vitals_by_patient_name"
                }
            )
        


    def handle_response(self, response):
        """
        Handle the response from the Gemini API and execute the appropriate function.
        """
        try:
            # Check if there are multiple function calls
            if not response.candidates or not response.candidates[0].content.parts:
                return None
            
            function_calls = []
            # Extract all function calls from the response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    function_calls.append(part.function_call)
            
            if not function_calls:
                print("No function calls detected in the response.")
                return None
            
            # Process all function calls
            results = []
            for function_call in function_calls:
                if function_call.name == "write_multiple_vitals":
                    # Extract arguments for the write_multiple_vitals function
                    vitals_data = function_call.args
                    
                    # Execute the write_vitals function
                    result = self.write_vitals(vitals_data)
                    results.append(result)
                    print(f"Vitals data written successfully: {vitals_data}")
                elif function_call.name == "error":
                    # Extract arguments for the error function
                    error_message = function_call.args.get("error_message")
                    
                    # Execute the error function
                    result = self.return_error(error_message)
                    results.append(result)
                    print(f"Error returned: {error_message}")
            
            # Return comprehensive response
            if len(results) == 1:
                return results[0]  # This is already an AgentResponse from write_vitals
            else:
                # Multiple vitals recorded
                successful_results = [result for result in results if result.is_success()]
                return AgentResponse(
                    status="success",
                    text=f"Successfully recorded {len(successful_results)} vital signs.",
                    reason="",
                    data={
                        "entries": [result.data.get("entry", {}) for result in successful_results],
                        "total_recorded": len(successful_results)
                    },
                    metadata={
                        "agent": "vitals_agent",
                        "operation": "write_multiple_vitals"
                    }
                )
                
        except Exception as e:
            print(f"Error handling response: {e}")
            return None