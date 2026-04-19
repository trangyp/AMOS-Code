"""AMOS Client SDK - For client repos to call AMOS-Consulting API Hub.

This SDK is used by:
- AMOS-Claws (agent frontend)
- Mailinhconect (product frontend)  
- AMOS-Invest (investor frontend)

Usage:
    from amos_client_sdk import AMOSClient
    
    client = AMOSClient(api_url="https://api.yourdomain.com")
    response = await client.chat("Hello", session_id="sess-123")
"""

from __future__ import annotations

import os
from typing import Any

try:
    import httpx
except ImportError:
    raise ImportError("httpx not installed. Run: pip install httpx")

from amos_brain.api_contracts import (
    ChatRequest,
    ChatResponse,
    ChatContext,
    BrainRunRequest,
    BrainRunResponse,
    RepoScanRequest,
    RepoScanResult,
    RepoFixRequest,
    RepoFixResult,
    ModelInfo,
    ModelRequest,
    ModelResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
)


class AMOSClientError(Exception):
    """Error from AMOS API Hub."""
    
    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class AMOSClient:
    """Client for AMOS API Hub.
    
    All client repos (AMOS-Claws, Mailinhconect, AMOS-Invest) use this
    to communicate with the AMOS-Consulting backend.
    """
    
    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize AMOS client.
        
        Args:
            api_url: AMOS API Hub URL (default: from AMOS_API_URL env var)
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url or os.getenv("AMOS_API_URL", "http://localhost:8000")
        self.api_key = api_key or os.getenv("AMOS_API_KEY")
        self.timeout = timeout
        
        # Ensure no trailing slash
        self.api_url = self.api_url.rstrip("/")
        
        self._client: httpx.AsyncClient | None = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers,
            )
        return self._client
    
    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _post(self, path: str, data: dict) -> dict:
        """Make POST request to API."""
        client = await self._get_client()
        url = f"{self.api_url}{path}"
        
        response = await client.post(url, json=data)
        
        if response.status_code >= 400:
            error_data = response.json().get("error", {})
            raise AMOSClientError(
                error_data.get("message", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                details=error_data.get("details"),
            )
        
        return response.json()
    
    async def _get(self, path: str) -> dict | list:
        """Make GET request to API."""
        client = await self._get_client()
        url = f"{self.api_url}{path}"
        
        response = await client.get(url)
        
        if response.status_code >= 400:
            error_data = response.json().get("error", {})
            raise AMOSClientError(
                error_data.get("message", f"HTTP {response.status_code}"),
                status_code=response.status_code,
            )
        
        return response.json()
    
    # ========================================================================
    # Health Check
    # ========================================================================
    
    async def health(self) -> dict:
        """Check API health."""
        return await self._get("/v1/health")
    
    # ========================================================================
    # Chat API
    # ========================================================================
    
    async def chat(
        self,
        message: str,
        session_id: str,
        conversation_id: str | None = None,
        workspace_id: str | None = None,
        model: str | None = None,
        history: list[dict] | None = None,
    ) -> ChatResponse:
        """Send chat message to AMOS.
        
        Args:
            message: User message
            session_id: Session identifier
            conversation_id: Optional conversation ID
            workspace_id: Optional workspace/tenant ID
            model: Optional specific model to use
            history: Optional conversation history
            
        Returns:
            ChatResponse with assistant's message
        """
        request = ChatRequest(
            message=message,
            context=ChatContext(
                session_id=session_id,
                conversation_id=conversation_id,
                workspace_id=workspace_id,
            ),
            history=history or [],
            model=model,
        )
        
        response_data = await self._post("/v1/chat", request.model_dump())
        return ChatResponse(**response_data)
    
    # ========================================================================
    # Brain API
    # ========================================================================
    
    async def brain_run(
        self,
        input_data: dict,
        session_id: str | None = None,
        max_branches: int = 5,
        collapse_strategy: str = "best",
    ) -> BrainRunResponse:
        """Execute AMOS brain cycle.
        
        Args:
            input_data: State graph input variables
            session_id: Optional session ID
            max_branches: Maximum branches to generate
            collapse_strategy: Branch selection strategy
            
        Returns:
            BrainRunResponse with execution results
        """
        from amos_brain.api_contracts.brain import StateGraphInput
        
        request = BrainRunRequest(
            input=StateGraphInput(variables=input_data),
            max_branches=max_branches,
            collapse_strategy=collapse_strategy,
            session_id=session_id,
        )
        
        response_data = await self._post("/v1/brain/run", request.model_dump())
        return BrainRunResponse(**response_data)
    
    # ========================================================================
    # Repo Doctor API
    # ========================================================================
    
    async def repo_scan(
        self,
        repo_path: str,
        scan_types: list[str] | None = None,
    ) -> RepoScanResult:
        """Scan repository for issues.
        
        Args:
            repo_path: Path to repository
            scan_types: Types of scans to run (style, security, performance)
            
        Returns:
            RepoScanResult with found issues
        """
        request = RepoScanRequest(
            repo_path=repo_path,
            scan_types=scan_types or ["style", "security"],
        )
        
        response_data = await self._post("/v1/repo/scan", request.model_dump())
        return RepoScanResult(**response_data)
    
    async def repo_fix(
        self,
        scan_id: str,
        issue_ids: list[str] | None = None,
        dry_run: bool = True,
    ) -> RepoFixResult:
        """Apply fixes to repository issues.
        
        Args:
            scan_id: Scan ID from repo_scan
            issue_ids: Specific issues to fix (None = all)
            dry_run: Preview changes without applying
            
        Returns:
            RepoFixResult with applied changes
        """
        request = RepoFixRequest(
            scan_id=scan_id,
            issue_ids=issue_ids,
            dry_run=dry_run,
        )
        
        response_data = await self._post("/v1/repo/fix", request.model_dump())
        return RepoFixResult(**response_data)
    
    # ========================================================================
    # Models API
    # ========================================================================
    
    async def list_models(self) -> list[ModelInfo]:
        """List available LLM models.
        
        Returns:
            List of available models
        """
        response_data = await self._get("/v1/models")
        return [ModelInfo(**m) for m in response_data]
    
    async def run_model(
        self,
        model_id: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ModelResponse:
        """Run inference on specific model.
        
        Args:
            model_id: Model identifier
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            ModelResponse with generated content
        """
        request = ModelRequest(
            model_id=model_id,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        response_data = await self._post("/v1/models/run", request.model_dump())
        return ModelResponse(**response_data)
    
    # ========================================================================
    # Workflow API
    # ========================================================================
    
    async def run_workflow(
        self,
        workflow_id: str,
        inputs: dict | None = None,
        synchronous: bool = True,
    ) -> WorkflowRunResponse:
        """Execute AMOS workflow.
        
        Args:
            workflow_id: Workflow identifier
            inputs: Workflow inputs
            synchronous: Wait for completion
            
        Returns:
            WorkflowRunResponse with results
        """
        request = WorkflowRunRequest(
            workflow_id=workflow_id,
            inputs=inputs or {},
            synchronous=synchronous,
        )
        
        response_data = await self._post("/v1/workflow/run", request.model_dump())
        return WorkflowRunResponse(**response_data)


# ============================================================================
# Convenience Functions
# ============================================================================

async def chat(message: str, session_id: str, **kwargs) -> ChatResponse:
    """Quick chat function using default client."""
    client = AMOSClient()
    try:
        return await client.chat(message, session_id, **kwargs)
    finally:
        await client.close()


async def brain_run(input_data: dict, **kwargs) -> BrainRunResponse:
    """Quick brain run function using default client."""
    client = AMOSClient()
    try:
        return await client.brain_run(input_data, **kwargs)
    finally:
        await client.close()
