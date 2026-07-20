"""Ollama LLM integration with graceful fallback.

Wraps the Ollama REST API for local Llama 3 inference.
If Ollama is not running, assessment falls back to rules-based mode
rather than failing.
"""

import json
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OllamaService:
    """Client for the local Ollama LLM server."""

    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def is_available(self) -> bool:
        """Check if Ollama is running and responsive."""
        if not settings.use_ollama:
            return False
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def generate(self, prompt: str, system: str | None = None) -> str | None:
        """Send a prompt to Ollama and return the generated text.

        Args:
            prompt: The user prompt with context.
            system: Optional system prompt to guide the model's behavior.

        Returns:
            Generated text string, or None if the call fails.
        """
        payload: dict = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": 2048,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.HTTPError as exc:
            logger.error("Ollama generate failed: %s", exc)
            return None

    @staticmethod
    def extract_json(text: str) -> dict | None:
        """Extract JSON object from LLM response text.

        The LLM may wrap JSON in markdown code blocks or add prose around it.
        This method extracts the first valid JSON object found.
        """
        if not text:
            return None

        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON object boundaries
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        logger.warning("Could not extract JSON from LLM response")
        return None
