def get_time():
    """
    Get the current time in ISO 8601 format.
    """
    from datetime import datetime
    return datetime.now().isoformat()