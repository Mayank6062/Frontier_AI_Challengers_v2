import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AzureOpenAI, OpenAIError


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _create_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=_get_required_env("AZURE_OPENAI_API_KEY"),
        azure_endpoint=_get_required_env("AZURE_OPENAI_ENDPOINT"),
        api_version=_get_required_env("AZURE_OPENAI_API_VERSION"),
    )


def ask_llm(prompt: str) -> str:
    """Send one prompt to Azure OpenAI and return the generated text."""
    try:
        client = _create_client()
        response = client.chat.completions.create(
            model=_get_required_env("AZURE_OPENAI_DEPLOYMENT"),
            messages=[{"role": "user", "content": prompt}],
        )
    except OpenAIError as exc:
        raise RuntimeError(f"Azure OpenAI request failed: {exc}") from exc

    message = response.choices[0].message.content
    if not message:
        raise RuntimeError("Azure OpenAI returned an empty response.")

    return message
