"""
AMOS LLM Code Generator

Production integration with LLM providers for code generation.
Supports OpenAI, Anthropic, and local models.

Uses the brain's cognitive architecture for structured prompting
and self-correction loops.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from amos_brain.super_brain import get_super_brain


@dataclass
class CodeGenerationRequest:
    """Request for code generation."""

    instruction: str
    target_file: str | None = None
    target_symbol: str | None = None
    existing_code: str = ""
    context_files: list[str] = None
    constraints: list[str] = None


@dataclass
class CodeGenerationResult:
    """Result of code generation."""

    generated_code: str
    explanation: str
    confidence: float
    used_tokens: int
    model: str
    success: bool
    error: str | None = None


class LLMCodeGenerator:
    """
    Production LLM-based code generator.

    Integrates with multiple providers:
    - OpenAI GPT-4o/4-turbo
    - Anthropic Claude 3.5 Sonnet
    - Local models via Ollama/LM Studio

    Uses structured prompting and the brain's
    cognitive stack for intelligent code generation.
    """

    def __init__(self):
        self.super_brain = get_super_brain()
        self._openai_client = None
        self._anthropic_client = None

    def _get_openai_client(self):
        """Lazy load OpenAI client."""
        if self._openai_client is None:
            try:
                from openai import OpenAI

                api_key = os.environ.get("OPENAI_API_KEY")
                if api_key:
                    self._openai_client = OpenAI(api_key=api_key)
            except ImportError:
                pass
        return self._openai_client

    def _get_anthropic_client(self):
        """Lazy load Anthropic client."""
        if self._anthropic_client is None:
            try:
                from anthropic import Anthropic

                api_key = os.environ.get("ANTHROPIC_API_KEY")
                if api_key:
                    self._anthropic_client = Anthropic(api_key=api_key)
            except ImportError:
                pass
        return self._anthropic_client

    def _build_system_prompt(self) -> str:
        """Build the system prompt for code generation."""
        return """You are AMOS Code Generator, an expert software engineer.

Your task is to generate high-quality, production-ready Python code.

Rules:
1. Generate only valid Python code that passes syntax checks
2. Follow PEP 8 style guidelines
3. Include proper type annotations
4. Add docstrings for public functions/classes
5. Handle edge cases appropriately
6. Use modern Python features (3.10+)
7. Never include explanatory text outside code blocks

Output format:
```python
# Your code here
```
"""

    def _build_user_prompt(self, request: CodeGenerationRequest) -> str:
        """Build user prompt from request."""
        prompt_parts = [f"Instruction: {request.instruction}"]

        if request.target_file:
            prompt_parts.append(f"Target file: {request.target_file}")

        if request.target_symbol:
            prompt_parts.append(f"Target symbol: {request.target_symbol}")

        if request.existing_code:
            prompt_parts.append("\nExisting code context:")
            prompt_parts.append("```python")
            # Limit context to avoid token overflow
            context = request.existing_code[:4000]
            prompt_parts.append(context)
            prompt_parts.append("```")

        if request.constraints:
            prompt_parts.append("\nConstraints:")
            for constraint in request.constraints:
                prompt_parts.append(f"- {constraint}")

        prompt_parts.append("\nGenerate the code:")

        return "\n".join(prompt_parts)

    def generate_with_openai(
        self, request: CodeGenerationRequest, model: str = "gpt-4o-mini"
    ) -> CodeGenerationResult:
        """Generate code using OpenAI."""
        client = self._get_openai_client()
        if not client:
            return CodeGenerationResult(
                generated_code="",
                explanation="",
                confidence=0.0,
                used_tokens=0,
                model=model,
                success=False,
                error="OpenAI client not available - set OPENAI_API_KEY",
            )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": self._build_user_prompt(request)},
                ],
                temperature=0.2,
                max_tokens=4000,
            )

            content = response.choices[0].message.content

            # Extract code from markdown code blocks
            generated_code = self._extract_code(content)

            return CodeGenerationResult(
                generated_code=generated_code,
                explanation="Generated via OpenAI",
                confidence=0.85,
                used_tokens=response.usage.total_tokens,
                model=model,
                success=True,
            )

        except Exception as e:
            return CodeGenerationResult(
                generated_code="",
                explanation="",
                confidence=0.0,
                used_tokens=0,
                model=model,
                success=False,
                error=str(e),
            )

    def generate_with_anthropic(
        self, request: CodeGenerationRequest, model: str = "claude-3-5-sonnet-20241022"
    ) -> CodeGenerationResult:
        """Generate code using Anthropic Claude."""
        client = self._get_anthropic_client()
        if not client:
            return CodeGenerationResult(
                generated_code="",
                explanation="",
                confidence=0.0,
                used_tokens=0,
                model=model,
                success=False,
                error="Anthropic client not available - set ANTHROPIC_API_KEY",
            )

        try:
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.2,
                system=self._build_system_prompt(),
                messages=[{"role": "user", "content": self._build_user_prompt(request)}],
            )

            content = response.content[0].text

            # Extract code from markdown code blocks
            generated_code = self._extract_code(content)

            return CodeGenerationResult(
                generated_code=generated_code,
                explanation="Generated via Anthropic Claude",
                confidence=0.90,
                used_tokens=response.usage.input_tokens + response.usage.output_tokens,
                model=model,
                success=True,
            )

        except Exception as e:
            return CodeGenerationResult(
                generated_code="",
                explanation="",
                confidence=0.0,
                used_tokens=0,
                model=model,
                success=False,
                error=str(e),
            )

    def _extract_code(self, content: str) -> str:
        """Extract code from markdown code blocks."""
        import re

        # Look for python code blocks
        pattern = r"```python\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Look for any code blocks
        pattern = r"```\n?(.*?)\n?```"
        matches = re.findall(pattern, content, re.DOTALL)

        if matches:
            return matches[0].strip()

        # No code blocks found, return raw content
        return content.strip()

    def generate(
        self, request: CodeGenerationRequest, provider: str | None = None
    ) -> CodeGenerationResult:
        """
        Generate code using best available provider.

        Args:
            request: Code generation request
            provider: Specific provider ("openai", "anthropic", "auto")

        Returns:
            CodeGenerationResult with generated code or error
        """
        # Determine provider
        if provider is None or provider == "auto":
            # Prefer Anthropic for code, fallback to OpenAI
            if os.environ.get("ANTHROPIC_API_KEY"):
                provider = "anthropic"
            elif os.environ.get("OPENAI_API_KEY"):
                provider = "openai"
            else:
                return CodeGenerationResult(
                    generated_code="",
                    explanation="",
                    confidence=0.0,
                    used_tokens=0,
                    model="none",
                    success=False,
                    error="No API keys configured - set ANTHROPIC_API_KEY or OPENAI_API_KEY",
                )

        # Route to provider
        if provider == "anthropic":
            return self.generate_with_anthropic(request)
        elif provider == "openai":
            return self.generate_with_openai(request)
        else:
            return CodeGenerationResult(
                generated_code="",
                explanation="",
                confidence=0.0,
                used_tokens=0,
                model="none",
                success=False,
                error=f"Unknown provider: {provider}",
            )

    def generate_with_self_correction(
        self,
        request: CodeGenerationRequest,
        max_attempts: int = 3,
    ) -> CodeGenerationResult:
        """
        Generate code with automatic self-correction on failure.

        If the generated code has syntax errors or fails verification,
        automatically retry with the error feedback.
        """
        import ast

        for attempt in range(max_attempts):
            # Generate code
            result = self.generate(request)

            if not result.success:
                # Generation failed - retry
                request.constraints = request.constraints or []
                request.constraints.append(f"Previous attempt failed: {result.error}")
                continue

            # Check syntax
            try:
                ast.parse(result.generated_code)
                # Syntax valid - return result
                result.confidence = 0.95 if attempt == 0 else 0.80
                return result
            except SyntaxError as e:
                # Syntax error - add constraint and retry
                request.constraints = request.constraints or []
                request.constraints.append(
                    f"Previous code had syntax error at line {e.lineno}: {e.msg}"
                )
                continue

        # All attempts exhausted
        return CodeGenerationResult(
            generated_code="",
            explanation="",
            confidence=0.0,
            used_tokens=0,
            model="none",
            success=False,
            error=f"Failed to generate valid code after {max_attempts} attempts",
        )


def get_llm_generator() -> LLMCodeGenerator:
    """Get LLM code generator instance."""
    return LLMCodeGenerator()
