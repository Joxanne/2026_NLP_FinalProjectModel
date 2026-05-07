import os
import openai

_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("TWCC_API_KEY")
        base_url = os.environ.get("TWCC_API_URL", "https://api-ams.twcc.ai/api") + "/models"
        timeout = float(os.environ.get("TWCC_TIMEOUT", "60"))
        max_retries = int(os.environ.get("TWCC_MAX_RETRY", "2"))
        if not api_key:
            raise RuntimeError("TWCC_API_KEY 未設定，請在 .env 中填入 API key。")
        _client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
    return _client


def ask(question: str, system_prompt: str, max_tokens: int = 300) -> str:
    model = os.environ.get("TWCC_MODEL", "llama3.3-ffm-70b-16k-chat")
    response = _get_client().chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content
