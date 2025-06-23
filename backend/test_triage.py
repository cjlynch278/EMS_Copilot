#!/usr/bin/env python3
"""
Test script for the TriageAgent functionality.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
curr_dir = Path(os.getcwd())
src_dir = curr_dir / "src"
sys.path.append(str(src_dir))

from ems_copilot.domain.services.triage_agent import TriageAgent
from ems_copilot.infrastructure.database.conversation_history import ConversationHistory

def test_triage_agent():
    """Test the triage agent functionality."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
    
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return
    
    print("🚑 Testing TriageAgent...")
    
    # Initialize triage agent
    triage_agent = TriageAgent(gemini_api_key, firebase_credentials_path)
    
    # Test cases
    test_cases = [
        {
            "symptoms": "Patient John Smith has chest pain and shortness of breath",
            "description": "Cardiac symptoms - should be IMMEDIATE priority"
        },
        {
            "symptoms": "Patient Sarah Johnson has a fever of 101 and sore throat",
            "description": "Minor illness - should be MINOR priority"
        },
        {
            "symptoms": "Patient Mike Davis has severe bleeding from a cut on his arm",
            "description": "Bleeding - should be URGENT priority"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['description']}")
        print(f"Symptoms: {test_case['symptoms']}")
        print(f"{'='*60}")
        
        try:
            # Perform triage
            result = triage_agent.perform_triage(test_case['symptoms'])
            print(f"Triage Result:\n{result}")
            
        except Exception as e:
            print(f"Error in test case {i}: {e}")
    
    # Test conversation history
    print(f"\n{'='*60}")
    print("Testing Conversation History")
    print(f"{'='*60}")
    
    try:
        # Get recent conversations
        recent_conversations = triage_agent.get_triage_history(limit=5)
        print(f"Recent conversations: {len(recent_conversations)} found")
        
        # Search for relevant context
        search_results = triage_agent.search_triage_context("chest pain")
        print(f"Search results for 'chest pain': {len(search_results)} found")
        
    except Exception as e:
        print(f"Error testing conversation history: {e}")

def test_contextual_triage():
    """Test the contextual triage functionality."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
    
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return
    
    print("🚑 Testing Contextual TriageAgent...")
    
    # Initialize triage agent
    triage_agent = TriageAgent(gemini_api_key, firebase_credentials_path)
    
    # First, let's add some conversation history to simulate a patient interaction
    print("\n📝 Adding conversation history...")
    
    # Simulate a conversation about a patient with low O2
    triage_agent.conversation_history.add_conversation(
        user_query="Record patient Hank Smith having a o2 of 93 and sugar of 120",
        agent_response="Vitals recorded: O2 93%, Glucose 120 mg/dL",
        patient_name="Hank Smith",
        metadata={"type": "vitals_recording"}
    )
    
    triage_agent.conversation_history.add_conversation(
        user_query="Patient Hank Smith is complaining of shortness of breath",
        agent_response="Shortness of breath noted for Hank Smith",
        patient_name="Hank Smith",
        metadata={"type": "symptom_report"}
    )
    
    triage_agent.conversation_history.add_conversation(
        user_query="Hank Smith's O2 dropped to 89",
        agent_response="O2 89% recorded for Hank Smith - concerning drop",
        patient_name="Hank Smith",
        metadata={"type": "vitals_update"}
    )
    
    # Test contextual triage queries
    contextual_queries = [
        {
            "query": "what's wrong",
            "description": "General assessment query"
        },
        {
            "query": "assess the patient",
            "description": "Direct assessment request"
        },
        {
            "query": "how is Hank Smith doing",
            "description": "Patient-specific status check"
        },
        {
            "query": "should I be concerned",
            "description": "Concern assessment"
        }
    ]
    
    print(f"\n{'='*60}")
    print("Testing Contextual Triage Queries")
    print(f"{'='*60}")
    
    for i, test_case in enumerate(contextual_queries, 1):
        print(f"\n--- Test Case {i}: {test_case['description']} ---")
        print(f"Query: '{test_case['query']}'")
        print("-" * 50)
        
        try:
            # Perform contextual triage
            result = triage_agent.perform_contextual_triage(test_case['query'])
            print(f"Assessment:\n{result}")
            
        except Exception as e:
            print(f"Error in contextual test case {i}: {e}")
    
    # Test conversation history search
    print(f"\n{'='*60}")
    print("Testing Conversation History Search")
    print(f"{'='*60}")
    
    try:
        # Search for relevant conversations
        search_results = triage_agent.search_triage_context("oxygen shortness breath")
        print(f"Search results for 'oxygen shortness breath': {len(search_results)} found")
        
        for i, result in enumerate(search_results[:3], 1):
            print(f"\nResult {i}:")
            print(f"  Patient: {result['metadata'].get('patient_name', 'unknown')}")
            print(f"  Query: {result['metadata'].get('user_query', '')}")
            print(f"  Relevance: {result.get('distance', 0):.3f}")
        
    except Exception as e:
        print(f"Error testing conversation search: {e}")

if __name__ == "__main__":
    test_contextual_triage() 