#!/usr/bin/env python3
"""
Simple test to verify conversation functionality is working.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent

def test_simple_conversation():
    """Test the simple conversation flow."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(gemini_api_key)
    
    print("=== Testing Simple Conversation Flow ===\n")
    
    # Test 1: Record vitals without patient name
    print("Test 1: Recording vitals without patient name")
    print("Input: 'record BP vitals'")
    response1 = orchestrator.orchestrate("record BP vitals")
    print(f"Response: {response1}")
    print(f"Conversation state: {orchestrator.conversation_state}")
    print()
    
    # Test 2: Provide missing patient name
    print("Test 2: Providing missing patient name")
    print("Input: 'patient name is John Smith'")
    response2 = orchestrator.orchestrate("patient name is John Smith")
    print(f"Response: {response2}")
    print(f"Conversation state: {orchestrator.conversation_state}")
    print()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_simple_conversation() 