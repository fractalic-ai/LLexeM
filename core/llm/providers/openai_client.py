from openai import OpenAI
from core.config import Config  # Import Config to access settings

class openaiclient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def llm_call(self, prompt_text: str, operation_params: dict) -> str:
        # Use settings from Config, with default fallbacks
        model = Config.MODEL or "gpt-4o"
        temperature = Config.TEMPERATURE or 0.6
        max_tokens = Config.CONTEXT_SIZE  # Use Config.CONTEXT_SIZE if provided
        top_p = Config.TOP_P or 1

        system_prompt = Config.SYSTEM_PROMPT or "You are a helpful assistant."

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            temperature=temperature,
            max_tokens=max_tokens if max_tokens else None,
            top_p=top_p,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content
