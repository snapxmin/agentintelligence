"""Aliyun Bailian GLM chat client."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Callable
from urllib import request


DEFAULT_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "glm-4.5"


@dataclass(frozen=True)
class BailianConfig:
    """Configuration for the OpenAI-compatible Bailian endpoint."""

    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout: int = 60

    @classmethod
    def from_env(cls) -> "BailianConfig":
        api_key = os.getenv("BAILIAN_API_KEY") or os.getenv("DASHSCOPE_API_KEY") or ""
        model = os.getenv("BAILIAN_MODEL", DEFAULT_MODEL)
        base_url = os.getenv("BAILIAN_BASE_URL", DEFAULT_BASE_URL)
        timeout = int(os.getenv("BAILIAN_TIMEOUT", "60"))
        return cls(api_key=api_key, model=model, base_url=base_url, timeout=timeout)


class BailianGLMClient:
    """Small client for Bailian's OpenAI-compatible chat completions API."""

    def __init__(
        self,
        config: BailianConfig,
        urlopen: Callable[..., object] = request.urlopen,
    ) -> None:
        self._config = config
        self._urlopen = urlopen

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        payload = {
            "model": self._config.model,
            "messages": messages,
            "temperature": temperature,
        }
        data = json.dumps(payload).encode("utf-8")
        endpoint = self._config.base_url.rstrip("/") + "/chat/completions"
        req = request.Request(
            endpoint,
            data=data,
            headers={
                "Authorization": "Bearer " + self._config.api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with self._urlopen(req, timeout=self._config.timeout) as response:
            body = response.read().decode("utf-8")

        decoded = json.loads(body)
        return decoded["choices"][0]["message"]["content"]
