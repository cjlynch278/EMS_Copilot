from google.cloud import secretmanager
import os


def get_gemini_api_key(project_id: str = None) -> str:
    """
    Get the Gemini API key from Google Cloud Secret Manager.
    
    Args:
        project_id: Google Cloud project ID. If None, will try to get from GOOGLE_CLOUD_PROJECT env var.
        
    Returns:
        The Gemini API key as a string
        
    Raises:
        ValueError: If project_id is not provided and GOOGLE_CLOUD_PROJECT is not set
        Exception: If secret retrieval fails
    """
    # Get project ID
    if project_id is None:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        if not project_id:
            raise ValueError("Project ID must be provided or set in GOOGLE_CLOUD_PROJECT environment variable")
    
    try:
        # Initialize Secret Manager client
        client = secretmanager.SecretManagerServiceClient()
        
        # Build the secret name
        name = f"projects/{project_id}/secrets/gemini_api_key/versions/latest"
        
        # Access the secret
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
        
    except Exception as e:
        raise Exception(f"Failed to retrieve Gemini API key from Secret Manager: {str(e)}") 