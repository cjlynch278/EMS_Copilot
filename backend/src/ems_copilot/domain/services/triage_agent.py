import os
import json
import re
from typing import Dict, List, Optional, Any
from ems_copilot.domain.services.base_agent import BaseAgent
from ems_copilot.infrastructure.database.firestore_db import FirestoreDB
from ems_copilot.infrastructure.database.conversation_history import ConversationHistory


class TriageAgent(BaseAgent):
    """
    TriageAgent class for performing patient triage with context from conversation history
    and patient data from Firestore.
    """
    
    def __init__(self, gemini_api_key: str, firebase_credentials_path: str = None):
        """
        Initialize the TriageAgent.
        
        Args:
            gemini_api_key: API key for Gemini
            firebase_credentials_path: Path to Firebase credentials
        """
        super().__init__(gemini_api_key)
        self.name = "TriageAgent"
        self.description = "An agent that performs patient triage with context from history and patient data."
        
        # Initialize Firestore connection
        if firebase_credentials_path is None:
            firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
        self.firestore_db = FirestoreDB(firebase_credentials_path)
        
        # Initialize conversation history
        self.conversation_history = ConversationHistory()
        
        # Triage system prompt
        self.system_prompt = """You are an expert EMS triage agent. Your role is to:
`
1. Analyze patient symptoms and vital signs
2. Assess triage priority (Immediate, Urgent, Delayed, Minor)
3. Provide evidence-based recommendations
4. Consider patient history and context

TRIAGE PRIORITY LEVELS:
- IMMEDIATE (Red): Life-threatening conditions requiring immediate intervention
- URGENT (Orange): Serious conditions requiring treatment within 10-60 minutes
- DELAYED (Yellow): Stable conditions that can wait 1-2 hours
- MINOR (Green): Non-urgent conditions that can wait 2+ hours

Always provide:
1. Triage priority level
2. Rationale for the assessment
3. Recommended immediate actions
4. Key symptoms to monitor
5. When to escalate care`

Use the provided patient history and vital signs data to inform your assessment.

You will be given a result from a vector database. This will be relevant conversation history.

Try to be relatively concise in your response. If you notice something severe, you should escalate care."""
    
    
    def perform_triage(self, user_query: str) -> str:
        """
        Perform triage assessment.
        
        Args:
            user_query: the user query to be processed by the triage agent. This should simply be exactly what the user asked.
            
        Returns:
            Triage assessment and recommendations
        """
        try:
            # Get relevant patient history
            self.conversation_history.search_conversations(user_query)

            # Build simple prompt
            prompt = f"""Here is the relevant conversation history: {self.conversation_history.search_conversations(user_query)}.
            please ferform a triage of the patient.
            Here is the user query: {user_query}"""
            
            # Call Gemini for triage assessment
            response = self.call_gemini(
                user_prompt=prompt,
                system_prompt=self.system_prompt,
                return_text=True
            )
            
            # Store conversation in history
            self.conversation_history.add_conversation(
                user_query=user_query,
                agent_response=response
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error performing triage: {str(e)}"
            print(error_msg)
            return error_msg
    
    
    
   
    
    def call_triage_agent(self, user_query: str = None) -> str:
        """
        Main method to call the triage agent (for compatibility with orchestrator).
        Now supports both explicit symptoms and contextual assessment.
        
        Args:
            user_query: Optional patient symptoms (if None, performs contextual assessment)
            
        Returns:
            Triage assessment
        """
        return self.perform_triage(user_query)
