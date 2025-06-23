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
5. When to escalate care

Use the provided patient history and vital signs data to inform your assessment."""
    
    def extract_patient_name(self, symptoms: str) -> Optional[str]:
        """
        Extract patient name from symptoms text.
        
        Args:
            symptoms: The symptoms text
            
        Returns:
            Extracted patient name or None
        """
        # Common patterns for patient names
        patterns = [
            r'patient\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "patient John Smith"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+has',      # "John Smith has"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+is',       # "John Smith is"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+complaining', # "John Smith complaining"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, symptoms, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def get_patient_context(self, patient_name: str) -> Dict[str, Any]:
        """
        Get comprehensive patient context from Firestore.
        
        Args:
            patient_name: Name of the patient
            
        Returns:
            Dictionary containing patient context
        """
        context = {
            "patient_name": patient_name,
            "vitals": [],
            "recent_conversations": [],
            "summary": ""
        }
        
        try:
            # Get recent vitals
            vitals_data = self.firestore_db.get_vitals_by_patient_name("vitals", patient_name)
            if vitals_data:
                context["vitals"] = vitals_data
            
            # Get relevant conversation history
            relevant_conversations = self.conversation_history.search_relevant_conversations(
                query=f"patient symptoms vitals triage assessment",
                n_results=10
            )
            context["recent_conversations"] = relevant_conversations
            
            # Create summary
            if context["vitals"]:
                latest_vitals = context["vitals"][0] if context["vitals"] else {}
                context["summary"] = f"Patient {patient_name} has recent vitals: {latest_vitals}"
            
        except Exception as e:
            print(f"Error getting patient context: {e}")
            context["summary"] = f"Unable to retrieve patient data: {str(e)}"
        
        return context
    
    def perform_triage(self, symptoms: str) -> str:
        """
        Perform triage assessment.
        
        Args:
            symptoms: Patient symptoms description
            
        Returns:
            Triage assessment and recommendations
        """
        try:
            # Build simple prompt
            prompt = f"SYMPTOMS: {symptoms}\n\nTRIAGE GUIDELINES:\nIMMEDIATE (Red) - Life-threatening conditions\nURGENT (Orange) - Serious but stable\nDELAYED (Yellow) - Stable conditions\nMINOR (Green) - Non-urgent"
            
            # Call Gemini for triage assessment
            response = self.call_gemini(
                user_prompt=prompt,
                system_prompt=self.system_prompt,
                return_text=True
            )
            
            # Store conversation in history
            self.conversation_history.add_conversation(
                user_query=symptoms,
                agent_response=response
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error performing triage: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_triage_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent triage assessments.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of triage assessments
        """
        try:
            return self.conversation_history.search_conversations("triage assessment", limit)
        except Exception as e:
            print(f"Error getting triage history: {e}")
            return []
    
    def search_triage_context(self, query: str) -> List[Dict]:
        """
        Search for relevant triage context.
        
        Args:
            query: Search query
            
        Returns:
            List of relevant conversations
        """
        try:
            return self.conversation_history.search_conversations(query, 5)
        except Exception as e:
            print(f"Error searching triage context: {e}")
            return []
    
    def perform_contextual_triage(self, query: str = None) -> str:
        """
        Perform triage assessment based on recent conversation history.
        
        Args:
            query: Optional query to help focus the search (e.g., "what's wrong", "assess patient")
            
        Returns:
            Triage assessment and recommendations
        """
        try:
            # Search for recent relevant conversations
            search_query = query or "patient symptoms vitals triage assessment"
            recent_conversations = self.conversation_history.search_conversations(
                query=search_query,
                n_results=10
            )
            
            if not recent_conversations:
                return "No recent patient interactions found. Please provide specific symptoms or patient information for triage assessment."
            
            # Build simple context from conversations
            conversation_context = []
            for conv in recent_conversations[:5]:
                conversation_context.append({
                    'query': conv['metadata'].get('user_query', ''),
                    'response': conv['metadata'].get('agent_response', ''),
                    'timestamp': conv['metadata'].get('timestamp', '')
                })
            
            # Build assessment prompt
            prompt_parts = ["CONTEXTUAL TRIAGE ASSESSMENT"]
            
            if query:
                prompt_parts.append(f"User Query: {query}")
            
            prompt_parts.append(f"\nRECENT CONVERSATION HISTORY:")
            for i, conv in enumerate(conversation_context, 1):
                prompt_parts.append(f"{i}. Query: {conv['query']}")
                prompt_parts.append(f"   Response: {conv['response'][:200]}...")
                prompt_parts.append("")
            
            prompt_parts.append(f"\nTRIAGE GUIDELINES:")
            prompt_parts.append("""
Based on the conversation history above, provide:

1. TRIAGE PRIORITY LEVEL:
   - IMMEDIATE (Red): Life-threatening conditions requiring immediate intervention
   - URGENT (Orange): Serious conditions requiring treatment within 10-60 minutes  
   - DELAYED (Yellow): Stable conditions that can wait 1-2 hours
   - MINOR (Green): Non-urgent conditions that can wait 2+ hours

2. ASSESSMENT SUMMARY:
   - Key concerns identified
   - Patient status overview
   - Recommended actions
""")
            
            full_prompt = "\n".join(prompt_parts)
            
            # Call Gemini for contextual triage assessment
            response = self.call_gemini(
                user_prompt=full_prompt,
                system_prompt=self.system_prompt,
                return_text=True
            )
            
            # Store this assessment in conversation history
            self.conversation_history.add_conversation(
                user_query=query or "Contextual triage assessment",
                agent_response=response
            )
            
            return response
            
        except Exception as e:
            error_msg = f"Error performing contextual triage: {str(e)}"
            print(error_msg)
            return error_msg
    
    def call_triage_agent(self, symptoms: str = None) -> str:
        """
        Main method to call the triage agent (for compatibility with orchestrator).
        Now supports both explicit symptoms and contextual assessment.
        
        Args:
            symptoms: Optional patient symptoms (if None, performs contextual assessment)
            
        Returns:
            Triage assessment
        """
        if symptoms:
            # If explicit symptoms provided, use traditional triage
            return self.perform_triage(symptoms)
        else:
            # If no symptoms, perform contextual assessment
            return self.perform_contextual_triage()