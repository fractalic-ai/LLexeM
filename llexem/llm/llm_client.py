# LLM Client
# - llm_call

from openai import OpenAI


def llm_call(prompt_text: str) -> str:
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are an agent and your instructions are to analyze the task you've received and perform it"
            },
            {
                "role": "user",
                "content": prompt_text
            }
        ],
        temperature=0.6,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].message.content