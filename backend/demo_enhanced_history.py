#!/usr/bin/env python3
"""
Demo script for the enhanced conversation history system.
Shows how different types of interactions are tracked and can be retrieved.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
curr_dir = Path(os.getcwd())
src_dir = curr_dir / "src"
sys.path.append(str(src_dir))

from ems_copilot.domain.services.triage_agent import TriageAgent
from ems_copilot.domain.services.vitals_agent import VitalsAgent
from ems_copilot.infrastructure.database.conversation_history import ConversationHistory

def demo_enhanced_conversation_history():
    """Demonstrate the enhanced conversation history system."""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    firebase_credentials_path = os.getenv("FIRESTORE_CREDENTIALS_PATH")
    
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in environment variables")
        return
    
    print("🚑 Enhanced Conversation History Demo")
    print("=" * 60)
    
    # Initialize conversation history
    conversation_history = ConversationHistory()
    
    # Initialize agents
    triage_agent = TriageAgent(gemini_api_key, firebase_credentials_path)
    vitals_agent = VitalsAgent(gemini_api_key, firebase_credentials_path)
    
    # Simulate a complete patient interaction scenario
    print("\n📝 Simulating Patient Interaction Scenario...")
    print("-" * 50)
    
    patient_name = "Hank Smith"
    
    # 1. Record initial vitals
    print(f"\n1. Recording initial vitals for {patient_name}...")
    vitals_response = vitals_agent.call_vitals_agent(f"Record patient {patient_name} having a o2 of 93 and sugar of 120")
    print(f"Response: {vitals_response}")
    
    # 2. Record additional vitals
    print(f"\n2. Recording additional vitals...")
    vitals_response2 = vitals_agent.call_vitals_agent(f"{patient_name} heart rate is 110 and blood pressure is 140/90")
    print(f"Response: {vitals_response2}")
    
    # 3. Report symptoms
    print(f"\n3. Reporting symptoms...")
    triage_response = triage_agent.call_triage_agent(f"Patient {patient_name} is complaining of chest pain and shortness of breath")
    print(f"Response: {triage_response}")
    
    # 4. Update vitals (worsening)
    print(f"\n4. Updating vitals (worsening condition)...")
    vitals_response3 = vitals_agent.call_vitals_agent(f"{patient_name} o2 dropped to 89 and heart rate increased to 125")
    print(f"Response: {vitals_response3}")
    
    # 5. Contextual assessment
    print(f"\n5. Performing contextual assessment...")
    contextual_response = triage_agent.perform_contextual_triage("what's wrong with the patient")
    print(f"Response: {contextual_response}")
    
    # 6. Add some action logs
    print(f"\n6. Adding action logs...")
    conversation_history.add_action_log(
        action="medication_administered",
        details={"medication": "Aspirin", "dose": "325mg", "route": "oral"},
        patient_name=patient_name,
        agent="vitals_agent"
    )
    
    conversation_history.add_action_log(
        action="oxygen_therapy_started",
        details={"flow_rate": "2L/min", "delivery_method": "nasal_cannula"},
        patient_name=patient_name,
        agent="triage_agent"
    )
    
    # Now demonstrate the enhanced retrieval capabilities
    print(f"\n{'='*60}")
    print("ENHANCED RETRIEVAL CAPABILITIES")
    print(f"{'='*60}")
    
    # 1. Get patient timeline
    print(f"\n1. Patient Timeline for {patient_name}:")
    print("-" * 40)
    timeline = conversation_history.get_patient_timeline(patient_name, limit=10)
    for i, entry in enumerate(timeline, 1):
        metadata = entry['metadata']
        print(f"{i}. [{metadata['conversation_type']}] {metadata['timestamp']}")
        if metadata['conversation_type'] == 'vitals_recording':
            print(f"   Vitals: {metadata.get('vitals_data', 'N/A')}")
        elif metadata['conversation_type'] == 'triage_assessment':
            print(f"   Priority: {metadata.get('priority_level', 'N/A')}")
        elif metadata['conversation_type'] == 'action_log':
            print(f"   Action: {metadata.get('action', 'N/A')}")
    
    # 2. Search for relevant context by type
    print(f"\n2. Relevant Vitals Context:")
    print("-" * 40)
    vitals_context = conversation_history.get_relevant_context(
        query="oxygen saturation heart rate",
        patient_name=patient_name,
        conversation_types=["vitals_recording", "vitals"],
        n_results=5
    )
    for i, context in enumerate(vitals_context, 1):
        print(f"{i}. {context['metadata']['conversation_type']}: {context['metadata'].get('user_query', 'N/A')}")
    
    # 3. Search for triage context
    print(f"\n3. Relevant Triage Context:")
    print("-" * 40)
    triage_context = conversation_history.get_relevant_context(
        query="chest pain shortness breath",
        patient_name=patient_name,
        conversation_types=["triage_assessment", "triage"],
        n_results=5
    )
    for i, context in enumerate(triage_context, 1):
        print(f"{i}. {context['metadata']['conversation_type']}: {context['metadata'].get('symptoms', 'N/A')}")
    
    # 4. Search for actions taken
    print(f"\n4. Actions Taken:")
    print("-" * 40)
    actions_context = conversation_history.get_relevant_context(
        query="medication oxygen therapy",
        patient_name=patient_name,
        conversation_types=["action_log"],
        n_results=5
    )
    for i, context in enumerate(actions_context, 1):
        print(f"{i}. {context['metadata']['action']}: {context['metadata'].get('details', 'N/A')}")
    
    # 5. Comprehensive patient assessment
    print(f"\n5. Comprehensive Patient Assessment:")
    print("-" * 40)
    all_context = conversation_history.get_relevant_context(
        query=f"patient {patient_name} status condition",
        patient_name=patient_name,
        n_results=15
    )
    
    print(f"Found {len(all_context)} relevant interactions:")
    for i, context in enumerate(all_context[:5], 1):
        metadata = context['metadata']
        print(f"{i}. [{metadata['conversation_type']}] {metadata['timestamp']}")
        print(f"   Relevance: {context.get('distance', 0):.3f}")
        if metadata['conversation_type'] == 'vitals_recording':
            print(f"   Vitals: {metadata.get('vitals_data', 'N/A')}")
        elif metadata['conversation_type'] == 'triage_assessment':
            print(f"   Symptoms: {metadata.get('symptoms', 'N/A')}")
    
    print(f"\n{'='*60}")
    print("Demo Complete! The conversation history system now tracks:")
    print("✅ Regular conversations")
    print("✅ Vitals recordings with structured data")
    print("✅ Triage assessments with priority levels")
    print("✅ Action logs for interventions")
    print("✅ Semantic search across all interaction types")
    print("✅ Patient-specific timelines")
    print("✅ Context-aware retrieval for LLMs")

if __name__ == "__main__":
    demo_enhanced_conversation_history() 