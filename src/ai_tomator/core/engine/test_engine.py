from ai_tomator.core.engine.base import BaseEngine


class TestEngine(BaseEngine):
    """
    TestEngine is a mock implementation of BaseEngine.

    It allows users to validate their AI-Tomator setup without needing
    a real API endpoint. All calls are simulated locally and always use
    the predefined test domain (https://test.ai-tomator.local) and token.

    This engine ensures that the system’s routing, configuration, and
    engine management logic work correctly before connecting to real APIs.
    """

    def __init__(self, api_token: str = None, base_url: str = None):
        self.url = base_url or "https://test.ai-tomator.local"
        self.api_token = api_token or "test_api_token"

        if self.url != "https://test.ai-tomator.local":
            raise ValueError(f"Could not make a connection to {self.url}")

    def run(
        self,
        model: str,
        prompt: str,
        temperature: float,
        file_path: str = None,
        content: str = None,
    ) -> str:

        if not file_path and not content:
            raise ValueError("Either file_path or content must be specified")

        if file_path:
            return (
                f"[TEST ENGINE] Processed file '{file_path}' "
                f"using model '{model}' at {self.url} "
                f"with token '{self.api_token}'."
            )

        return (
            f"[TEST ENGINE] Processed content '{content}' "
            f"using model '{model}' at {self.url} "
            f"with token '{self.api_token}'."
        )
