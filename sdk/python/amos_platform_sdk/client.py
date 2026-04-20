"""AMOS Platform SDK Client.

Synchronous and asynchronous clients for AMOS Platform API.
"""

from __future__ import annotations

from typing import Any

import httpx

from amos_platform_sdk.exceptions import (
    AMOSAPIError,
    AMOSAuthenticationError,
    AMOSNotFoundError,
    AMOSRateLimitError,
    AMOSValidationError,
)

DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_TIMEOUT = 30.0


class AMOSClient:
    """Synchronous client for AMOS Platform API.

    Usage:
        client = AMOSClient(api_key="your_key")
        response = client.chat("Hello!")
        print(response.content)
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
        )

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses."""
        if response.status_code == 401:
            raise AMOSAuthenticationError("Authentication failed")
        elif response.status_code == 404:
            raise AMOSNotFoundError("Resource not found")
        elif response.status_code == 422:
            raise AMOSValidationError(f"Validation error: {response.text}")
        elif response.status_code == 429:
            raise AMOSRateLimitError("Rate limit exceeded")
        elif response.status_code >= 500:
            raise AMOSAPIError(f"Server error: {response.status_code}")
        response.raise_for_status()

    def health(self) -> dict[str, Any]:
        """Check API health."""
        response = self._client.get("/v1/health")
        self._handle_error(response)
        return response.json()

    def status(self) -> dict[str, Any]:
        """Get system status."""
        response = self._client.get("/v1/status")
        self._handle_error(response)
        return response.json()

    def chat(
        self,
        message: str,
        context: dict[str, Any] = None,
        model: str = "ollama/llama3.2",
    ) -> dict[str, Any]:
        """Send chat request."""
        payload = {
            "message": message,
            "context": context or {},
            "model": model,
        }
        response = self._client.post("/v1/chat", json=payload)
        self._handle_error(response)
        return response.json()

    def list_models(self) -> list[dict[str, Any]]:
        """List available models."""
        response = self._client.get("/v1/models")
        self._handle_error(response)
        return response.json()

    def run_model(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Run model inference."""
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
        }
        response = self._client.post("/v1/models/run", json=payload)
        self._handle_error(response)
        return response.json()

    def scan_repo(
        self,
        repo_path: str,
        auto_fix: bool = False,
    ) -> dict[str, Any]:
        """Scan repository for issues."""
        payload = {
            "repo_path": repo_path,
            "auto_fix": auto_fix,
        }
        response = self._client.post("/v1/repo/scan", json=payload)
        self._handle_error(response)
        return response.json()

    def fix_repo(
        self,
        repo_path: str,
        issues: list[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Apply fixes to repository."""
        payload = {"repo_path": repo_path}
        if issues:
            payload["issues"] = issues
        response = self._client.post("/v1/repo/fix", json=payload)
        self._handle_error(response)
        return response.json()

    def run_workflow(
        self,
        workflow_id: str,
        inputs: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Run workflow."""
        payload = {
            "workflow_id": workflow_id,
            "inputs": inputs or {},
        }
        response = self._client.post("/v1/workflow/run", json=payload)
        self._handle_error(response)
        return response.json()

    def run_brain(
        self,
        state: dict[str, Any],
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Execute brain cycle."""
        payload = {
            "state": state,
            "context": context or {},
        }
        response = self._client.post("/v1/brain/run", json=payload)
        self._handle_error(response)
        return response.json()

    def close(self) -> None:
        """Close HTTP client."""
        self._client.close()

    def __enter__(self) -> AMOSClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class AsyncAMOSClient:
    """Asynchronous client for AMOS Platform API.

    Usage:
        async with AsyncAMOSClient(api_key="your_key") as client:
            response = await client.chat("Hello!")
            print(response.content)
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        self._client: httpx.Optional[AsyncClient] = None
        self._headers = headers

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._headers,
            )
        return self._client

    async def _handle_error(self, response: httpx.Response) -> None:
        """Handle API error responses."""
        if response.status_code == 401:
            raise AMOSAuthenticationError("Authentication failed")
        elif response.status_code == 404:
            raise AMOSNotFoundError("Resource not found")
        elif response.status_code == 422:
            raise AMOSValidationError(f"Validation error: {response.text}")
        elif response.status_code == 429:
            raise AMOSRateLimitError("Rate limit exceeded")
        elif response.status_code >= 500:
            raise AMOSAPIError(f"Server error: {response.status_code}")
        response.raise_for_status()

    async def health(self) -> dict[str, Any]:
        """Check API health."""
        client = await self._get_client()
        response = await client.get("/v1/health")
        await self._handle_error(response)
        return response.json()

    async def status(self) -> dict[str, Any]:
        """Get system status."""
        client = await self._get_client()
        response = await client.get("/v1/status")
        await self._handle_error(response)
        return response.json()

    async def chat(
        self,
        message: str,
        context: dict[str, Any] = None,
        model: str = "ollama/llama3.2",
    ) -> dict[str, Any]:
        """Send chat request."""
        client = await self._get_client()
        payload = {
            "message": message,
            "context": context or {},
            "model": model,
        }
        response = await client.post("/v1/chat", json=payload)
        await self._handle_error(response)
        return response.json()

    async def list_models(self) -> list[dict[str, Any]]:
        """List available models."""
        client = await self._get_client()
        response = await client.get("/v1/models")
        await self._handle_error(response)
        return response.json()

    async def run_model(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Run model inference."""
        client = await self._get_client()
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
        }
        response = await client.post("/v1/models/run", json=payload)
        await self._handle_error(response)
        return response.json()

    async def scan_repo(
        self,
        repo_path: str,
        auto_fix: bool = False,
    ) -> dict[str, Any]:
        """Scan repository for issues."""
        client = await self._get_client()
        payload = {
            "repo_path": repo_path,
            "auto_fix": auto_fix,
        }
        response = await client.post("/v1/repo/scan", json=payload)
        await self._handle_error(response)
        return response.json()

    async def fix_repo(
        self,
        repo_path: str,
        issues: list[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Apply fixes to repository."""
        client = await self._get_client()
        payload = {"repo_path": repo_path}
        if issues:
            payload["issues"] = issues
        response = await client.post("/v1/repo/fix", json=payload)
        await self._handle_error(response)
        return response.json()

    async def run_workflow(
        self,
        workflow_id: str,
        inputs: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Run workflow."""
        client = await self._get_client()
        payload = {
            "workflow_id": workflow_id,
            "inputs": inputs or {},
        }
        response = await client.post("/v1/workflow/run", json=payload)
        await self._handle_error(response)
        return response.json()

    async def run_brain(
        self,
        state: dict[str, Any],
        context: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Execute brain cycle."""
        client = await self._get_client()
        payload = {
            "state": state,
            "context": context or {},
        }
        response = await client.post("/v1/brain/run", json=payload)
        await self._handle_error(response)
        return response.json()

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> AsyncAMOSClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
