import sys
import os
import json
import requests
from pathlib import Path
curr_dir = Path(os.getcwd())
root_dir = Path(curr_dir.parents[0])
sys.path.append(str(root_dir))

from agents.base_agent import BaseAgent


class GPSAgent(BaseAgent):
    """
    GPSAgent class for managing GPS-related functionalities.
    Inherits from BaseAgent to handle Gemini API calls.
    """

    def __init__(self, gemini_api_key, google_maps_api_key):
        """
        Initialize the GPSAgent with the API key and Gemini API URL.
        """
        super().__init__(gemini_api_key)  # Initialize BaseAgent
        self.name = "GPSAgent"
        self.description = "An agent that provides GPS-related functionalities."
        self.gemini_api_key = gemini_api_key
        self.google_maps_api_key = google_maps_api_key
        self.system_prompt = "You are a GPS agent. You can provide directions, ETA, and address" \
        "You will be given a question, you will need to answer it given the info you are given in the prompt." \
        "Be concise with your answer. No need to remind this user that you are a non emergency agent."
    def call_gps(self, question):
        """
        Orchestrate the interaction by analyzing the user prompt and routing it to the appropriate agent.
        """
        # Define the system prompt

        current_location = self.get_current_location()
        # Call the Gemini API with functions
        gps_user_prompt = f"Current location: {current_location}. Question: {question}"
        print(f"GPS User Prompt: {gps_user_prompt}")
        response = self.call_gemini(user_prompt=gps_user_prompt, system_prompt=self.system_prompt, functions=None)
        return response

    def get_current_location(self):
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.google_maps_api_key}"
        response = requests.post(url)
        
        if response.status_code == 200:

            location = response.json()['location']
            lat = location['lat']
            lng = location['lng']
            response_str = f"Latitude: {lat}, Longitude: {lng}"
            return response_str
        else:
            raise Exception(f"Error: {response.text}")

    