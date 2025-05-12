from IPython.display import display, Markdown
from logging_config import setup_logger
from class_Gemini import Gemini  # Assuming this is the Gemini client class

# Set up the logger for this module
logger = setup_logger(__name__)

logger.info("This is an info log from the GeminiAgent module.")


class GeminiAgent:
    def __init__(self, name, gemini_config=None):
        """
        Initialize the GeminiAgent with configuration details.
        """
        self.name = name or "default_name"

        # Initialize the Gemini client if configuration is provided
        if gemini_config:
            self.gemini_client = Gemini(**gemini_config)
        else:
            self.gemini_client = None
            print("\nWarning: Gemini client is not initialized. Check your configurations.")
            display(Markdown("**Warning:** Gemini client is not initialized."))

    def call_gemini(self, user_prompt, system_prompt):
        """
        Call the Gemini API with the provided user and system prompts.
        """
        if not self.gemini_client:
            error_message = "Gemini client is not initialized. Please provide a valid client."
            print(error_message)
            display(Markdown(f"**Error:** {error_message}"))
            raise ValueError(error_message)

        messages = {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
        }

        try:
            # Call the Gemini API
            response = self.gemini_client.process_prompt(messages["user_prompt"])
            return response

        except Exception as e:
            error_message = f"Error while calling Gemini: {e}"
            print(error_message)
            display(Markdown(f"**Error:** {error_message}"))
            raise