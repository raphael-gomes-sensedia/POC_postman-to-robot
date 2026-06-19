"""Wrapper para API de IA (OpenAI / OpenCode)."""


def call_ai(prompt, api_provider="opencode", model="opencode/oci"):
    """Chama a API de IA com o prompt fornecido."""
    return f"# TODO: {api_provider}/{model}"
