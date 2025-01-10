import importlib

class LLMClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider.lower()  # Ensure provider name is lowercase
        self.api_key = api_key
        self.client = self._initialize_client()

    def _initialize_client(self):
        # Construct the module name based on the provider
        module_name = f"llexem.llm.providers.{self.provider}_client"
        
        # Standardized lowercase class name
        class_name = f"{self.provider}client"
        
        # Dynamically import the module
        module = importlib.import_module(module_name)
        
        # Dynamically get the class from the module
        client_class = getattr(module, class_name)
        
        # Instantiate the client class with the API key
        return client_class(api_key=self.api_key)

    def llm_call(self, prompt_text: str, operation_params: dict = None) -> str:
        return self.client.llm_call(prompt_text, operation_params)
