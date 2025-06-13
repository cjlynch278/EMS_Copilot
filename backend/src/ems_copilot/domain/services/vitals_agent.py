import os
import json
import requests
from pathlib import Path
from ems_copilot.infrastructure.database.firestore_db import FirestoreDB
from ems_copilot.infrastructure.utils.general_utils import *
from ems_copilot.domain.services.base_agent import BaseAgent


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
        self.firestore_db = FirestoreDB(os.getenv("FIRESTORE_CREDENTIALS_PATH"))


        self.gemini_api_key = gemini_api_key
        self.system_prompt  = (
            "You are a Vitals agent. Your role is to manage patient vitals. "
            "When given a input or statement, determine the appropriate action and invoke the corresponding function. "
            "Do not generate any natural language responses. "
            "If the input contains vitals data, invoke the 'write_vitals' function with the provided data. "
            "Only return the function call and its arguments. Do not include any text."
        )
    
    def call_vitals_agent(self, input):
        """
        Call the Vitals agent with the given input.
        This method will be used to call the Vitals agent with the given input.
        """
        functions = [
        {
            "name": "write_vitals",
            "description": "Write vitals data to Firestore.",
            "parameters": {
                "type": "object",
                "properties": {

                    "vitals_name": {
                        "type": "string",
                        "description": "The type of vital being recorded (heart rate, bp, o2)."
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
            "description": "Retrieve vitals data for a specific patient by their name from Firestore.",
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
            response = self.call_gemini( system_prompt=self.system_prompt, user_prompt=user_prompt, functions=functions)
            handle_response = self.handle_response(response=response)
            return response
        except Exception as e:
            print(f"Error calling Vitals agent: {e}")
            return None
    def write_vitals(self, json_vitals_data):
        """
        Write vitals data to Firestore.
        """
        try:
            # Write the vitals data to the Firestore 'vitals' collection
            self.firestore_db.write_vitals("vitals", json_vitals_data)

            # Construct the response
            response = {
                "status": "success",
                "entry": {
                    "type": json_vitals_data.get("vitals_name"),
                    "value": json_vitals_data.get("vitals_value"),
                    "timestamp": json_vitals_data.get("timestamp")
                },
                "message": f"{json_vitals_data.get('vitals_name').capitalize()} recorded successfully."
            }

            return response
        except Exception as e:
            print(f"Error writing vitals: {e}")
            return {
                "status": "error",
                "message": f"Failed to record {json_vitals_data.get('vitals_name')}. Error: {str(e)}"
            }

    def get_vitals(self, patient_id):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            return self.firestore_db.get_vitals("vitals", patient_id)
        except Exception as e:
            print(f"Error retrieving vitals: {e}")
            return None
        
    def get_vitals_by_patient_name(self, patient_name):
        """
        Retrieve vitals data for a specific patient from Firestore.
        """
        try:
            return self.firestore_db.get_vitals_by_patient_name("vitals", patient_name)
        except Exception as e:
            print(f"Error retrieving vitals: {e}")
            return None
        


    def handle_response(self, response):
        """
        Handle the response from the Gemini API and execute the appropriate function.
        """
        try:
            # Extract the function call from the response
            function_call = response.candidates[0].content.parts[0].function_call

            if function_call and function_call.name == "write_vitals":
                # Extract arguments for the write_vitals function
                vitals_data = function_call.args

                # Execute the write_vitals function
                response = self.write_vitals(vitals_data)
                print(f"Vitals data written successfully: {vitals_data}")
                return response
            else:
                print("No valid function call detected in the response.")
                return None
        except Exception as e:
            print(f"Error handling response: {e}")
            return None