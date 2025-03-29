import contextlib
import openai


class OpenAIClient:
    def __init__(self, api_key, api_base=None):
        self.api_key = api_key
        self.api_base = api_base

    def set_api_key(self, new_api_key):
        """
        Update the API key for this client.
        :param new_api_key: The new API key to set.
        :return: None
        """
        self.api_key = new_api_key

    @contextlib.contextmanager
    def use_config(self):
        """
        Context manager to temporarily set OpenAI API key and base URL.
        We use this to make a client for OpenAI API calls and for DeepSeek.
        """
        # Save current configuration
        old_api_key = openai.api_key
        old_api_base = getattr(openai, "api_base", None)
        # Set new configuration
        openai.api_key = self.api_key
        if self.api_base:
            openai.api_base = self.api_base
        try:
            yield
        finally:
            # Restore previous configuration
            openai.api_key = old_api_key
            if old_api_base is not None:
                openai.api_base = old_api_base

    def chat_completion(self, **kwargs):
        """
        Wrapper for OpenAI's ChatCompletion API.
        :param kwargs: Additional parameters for the API call.
        :return: API response.
        """
        with self.use_config():
            return openai.ChatCompletion.create(**kwargs)
