#!/usr/bin/env python3
"""
Test the simplified conversation approach.
The orchestrator just routes requests and returns responses.
If an agent needs more info, the user can provide it in their next request.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent

def test_simplified_conversation():
    """Test the simplified conversation flow."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(gemini_api_key)
    
    print("=== Testing Simplified Conversation Flow ===\n")
    
    # Test 1: Record vitals without patient name (should return error)
    print("Test 1: Recording vitals without patient name")
    print("Input: 'record BP vitals'")
    response1 = orchestrator.orchestrate("record BP vitals")
    print(f"Response: {response1}")
    print()
    
    # Test 2: Record vitals with patient name (should work)
    print("Test 2: Recording vitals with patient name")
    print("Input: 'record BP vitals for patient John Smith'")
    response2 = orchestrator.orchestrate("record BP vitals for patient John Smith")
    print(f"Response: {response2}")
    print()
    
    # Test 3: Another request with missing info
    print("Test 3: Triage request without patient info")
    print("Input: 'assess patient symptoms'")
    response3 = orchestrator.orchestrate("assess patient symptoms")
    print(f"Response: {response3}")
    print()
    
    # Test 4: Triage request with patient info
    print("Test 4: Triage request with patient info")
    print("Input: 'assess patient John Smith who has chest pain'")
    response4 = orchestrator.orchestrate("assess patient John Smith who has chest pain")
    print(f"Response: {response4}")
    print()
    
    print("=== Simplified Conversation Test Complete ===")
    print("\nKey insight: The orchestrator is now much simpler!")
    print("- It just routes requests to agents")
    print("- Agents handle their own missing info detection")
    print("- Users can provide missing info in their next request")
    print("- No complex conversation state management needed")

if __name__ == "__main__":
    test_simplified_conversation() 