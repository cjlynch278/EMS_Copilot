import os
import json
import chromadb
from datetime import datetime
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer


class ConversationHistory:
    """
    Simple conversation history using ChromaDB for vector storage and semantic search.
    """
    
    def __init__(self, persist_directory: str = "./conversation_history"):
        """
        Initialize the conversation history service.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="conversation_history",
            metadata={"description": "EMS Copilot conversation history"}
        )
        
        # Initialize sentence transformer for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def add_conversation(self, 
                        user_query: str, 
                        agent_response: str) -> str:
        """
        Add a conversation exchange to the history.
        
        Args:
            user_query: The user's query
            agent_response: The agent's response
            
        Returns:
            The ID of the added conversation
        """
        # Create a combined text for embedding
        combined_text = f"User: {user_query}\nAgent: {agent_response}"
        
        # Generate embedding
        embedding = self.embedding_model.encode(combined_text).tolist()
        
        # Prepare simple metadata
        conversation_metadata = {
            "timestamp": datetime.now().isoformat(),
            "user_query": str(user_query),
            "agent_response": str(agent_response)
        }
        
        # Add to collection
        conversation_id = f"conv_{datetime.now().timestamp()}"
        self.collection.add(
            embeddings=[embedding],
            documents=[combined_text],
            metadatas=[conversation_metadata],
            ids=[conversation_id]
        )
        
        return conversation_id
    
    def search_conversations(self, 
                           query: str, 
                           n_results: int = 5) -> List[Dict]:
        """
        Search for relevant conversations based on semantic similarity.
        
        Args:
            query: The search query
            n_results: Number of results to return
            
        Returns:
            List of relevant conversations with metadata
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        relevant_conversations = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                conversation = {
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                }
                relevant_conversations.append(conversation)
        
        return relevant_conversations
    
    def clear_history(self):
        """
        Clear all conversation history.
        """
        self.collection.delete() 