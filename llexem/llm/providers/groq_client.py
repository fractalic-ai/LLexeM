from groq import Groq
from llexem.config import Config  # Import Config to access settings

class groqclient:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def llm_call(self, prompt_text: str) -> str:
        # Use settings from Config, with default fallbacks
        model = Config.MODEL or "llama-3.1-70b-versatile"
        temperature = Config.TEMPERATURE or 0.6
        max_tokens = Config.CONTEXT_SIZE or 4096
        top_p = Config.TOP_P or 1
        system_prompt = Config.SYSTEM_PROMPT or "You are a helpful assistant."

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=False,
            stop=None,
        )
        return response.choices[0].message.content
