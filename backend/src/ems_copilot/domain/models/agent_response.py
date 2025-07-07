class AgentResponse:
    def __init__(
        self,
        status: str,
        text: str = "",
        reason: str = "",
        data: dict = None,
        metadata: dict = None
    ):
        """
        Args:
            status (str): 'success' or 'fail'
            text (str): A message intended for the user
            reason (str): Reason for failure (e.g., 'missing_patient_name')
            data (dict): Collected or required data (e.g., partial input)
            metadata (dict): Anything extra (e.g., timestamp, follow-up prompts)
        """
        self.status = status
        self.text = text
        self.reason = reason
        self.data = data or {}
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "status": self.status,
            "text": self.text,
            "reason": self.reason,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def is_success(self) -> bool:
        """Check if the response indicates success."""
        return self.status == "success"
    
    def is_failure(self) -> bool:
        """Check if the response indicates failure."""
        return self.status == "fail"
    
    def __str__(self) -> str:
        """String representation for easy logging."""
        return f"AgentResponse(status='{self.status}', text='{self.text}', reason='{self.reason}')"
