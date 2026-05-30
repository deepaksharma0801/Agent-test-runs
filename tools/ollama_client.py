"""Tiny Ollama client with graceful fallback when Ollama is unavailable."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class OllamaClient:
    model: str = "llama3.2:3b"
    host: str = "http://localhost:11434"
    timeout_seconds: int = 60

    def generate(self, prompt: str, system: str = "", schema: dict | None = None) -> str | None:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        if schema:
            payload["format"] = schema

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.host.rstrip('/')}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return None

        return body.get("response")
