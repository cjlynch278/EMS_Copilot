#!/usr/bin/env python3
"""
Test script to verify that the conversation functionality has been restored.
This tests the multi-turn conversation flow where missing information triggers follow-up questions.
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ems_copilot.domain.services.orchestrator_agent import OrchestratorAgent

def test_conversation_flow():
    """Test the conversation flow with missing information."""
    
    # Get API key from environment
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        return
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(gemini_api_key)
    
    print("=== Testing Conversation Flow with Missing Information ===\n")
    
    # Test 1: Record vitals without patient name (should trigger follow-up)
    print("Test 1: Recording vitals without patient name")
    print("Input: 'record BP vitals'")
    response1 = orchestrator.orchestrate("record BP vitals")
    print(f"Response: {response1}")
    print(f"Conversation state: {orchestrator.conversation_state}")
    print(f"Task queue: {orchestrator.task_queue}")
    print()
    
    # Test 2: Provide missing patient name (should complete the original request)
    print("Test 2: Providing missing patient name")
    print("Input: 'patient name is John Smith'")
    response2 = orchestrator.orchestrate("patient name is John Smith")
    print(f"Response: {response2}")
    print(f"Conversation state: {orchestrator.conversation_state}")
    print(f"Task queue: {orchestrator.task_queue}")
    print()
    
    # Test 3: New request (should work normally)
    print("Test 3: New request after conversation")
    print("Input: 'record heart rate 80'")
    response3 = orchestrator.orchestrate("record heart rate 80")
    print(f"Response: {response3}")
    print(f"Conversation state: {orchestrator.conversation_state}")
    print(f"Task queue: {orchestrator.task_queue}")
    print()
    
    print("=== Conversation Flow Test Complete ===")

if __name__ == "__main__":
    test_conversation_flow() 