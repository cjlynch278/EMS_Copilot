import sys
import os
import json
import requests
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent


class VitalsAgent(BaseAgent):
    """
    Vitals_Agent class for managing all vitals. These vitals will be stored in a SQL database.
    This agent will be used to track trending patient vitals and provide information about them.
    """

    def __init__(self, gemini_api_key, gemini_model, firebase_credentials_path, firebase_collection_name="vitals"):

        """
        Initialize the Vitals_Agent with the API key and Gemini API URL.
        This agent will be used to track trending patient vitals and provide information about them.
        """

        super().__init__(gemini_api_key, gemini_model=gemini_model)  # Initialize BaseAgent
        self.name = "Vitals_Agent"
        self.gemini_model = gemini_model
        self.description = "An agent that provides vitals related functionalities."

        self.gemini_api_key = gemini_api_key
        self.system_prompt = "You are a Vitals agent. You can provide vitals related functionalities." \
        "You will be given a question, you will need to answer it given the info you are given in the prompt." \
        "Be concise with your answer. No need to remind this user that you are a non emergency agent."
    
    def call_vitals_agent(self, question):
        """
        Call the Vitals agent with the given question.
        This method will be used to call the Vitals agent with the given question.
        """
        functions = [
        {
            "name": "write_vitals",
            "description": "Write vitals data to Firestore.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The ID of the patient."
                    },
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
                        "description": "The timestamp of the vitals data in ISO 8601 format. The timestamp should be now if not specified."
                    }
                },
                "required": ["patient_id", "vitals_name", "vitals_value", "timestamp"]
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


        try:
            response = self.call_gemini(self.system_prompt, question, functions = functions)
            return response
        except Exception as e:
            print(f"Error calling Vitals agent: {e}")
            return None
    def write_vitals(self, json_vitals_data):
        """
        Write vitals data to Firestore.
        """
        try:
            self.firestore_db.write_vitals("vitals", json_vitals_data)
        except Exception as e:
            print(f"Error writing vitals: {e}")

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