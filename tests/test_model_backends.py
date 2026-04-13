"""Tests for AMOS model backend abstraction.

Tests cover:
- Backend initialization and configuration
- Health check responses
- Retry logic behavior
- Error handling and message quality
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Ensure amos_brain is in path  # noqa: E402
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))  # noqa: E402

import requests  # noqa: E402

from amos_brain.model_backend import (  # noqa: E402
    OllamaBackend,
    OpenAICompatibleLocalBackend,
    LLMResult,
    with_retry,
)


class TestWithRetry(unittest.TestCase):
    """Tests for the retry decorator."""

    def test_success_no_retry(self):
        """Function that succeeds should not retry."""
        mock_func = Mock(return_value="success")
        decorated = with_retry(max_retries=3)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_then_success(self):
        """Function that fails then succeeds should retry."""
        mock_func = Mock(side_effect=[
            requests.ConnectionError("fail"), "success"
        ])
        decorated = with_retry(max_retries=3, base_delay=0.01)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)

    def test_max_retries_exceeded(self):
        """Function that always fails should raise after max retries."""
        mock_func = Mock(side_effect=requests.ConnectionError("always fails"))
        decorated = with_retry(max_retries=2, base_delay=0.01)(mock_func)

        with self.assertRaises(requests.ConnectionError) as ctx:
            decorated()

        self.assertIn("always fails", str(ctx.exception))
        self.assertEqual(mock_func.call_count, 3)  # Initial + 2 retries


class TestOllamaBackend(unittest.TestCase):
    """Tests for OllamaBackend."""

    def setUp(self):
        """Set up test fixtures."""
        self.backend = OllamaBackend(
            model="llama3.2:latest",
            base_url="http://127.0.0.1:11434"
        )

    @patch('amos_brain.model_backend.requests.Session')
    def test_generate_success(self, mock_session_class):
        """Test successful generation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello!"}
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        backend = OllamaBackend(model="test-model")
        result = backend.generate(
            system_prompt="You are helpful",
            user_prompt="Hi"
        )

        self.assertIsInstance(result, LLMResult)
        self.assertEqual(result.text, "Hello!")
        mock_session.post.assert_called_once()

    @patch('amos_brain.model_backend.requests.Session')
    def test_health_check_healthy(self, mock_session_class):
        """Test health check when server is healthy."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [{"name": "llama3.2:latest"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        backend = OllamaBackend(model="llama3.2:latest")
        health = backend.health_check()

        self.assertEqual(health["status"], "healthy")
        self.assertEqual(health["backend"], "ollama")
        self.assertEqual(health["model"], "llama3.2:latest")

    @patch('amos_brain.model_backend.requests.Session')
    def test_health_check_model_not_found(self, mock_session_class):
        """Test health check when model is not available."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "models": [{"name": "other-model"}]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        backend = OllamaBackend(model="missing-model")
        health = backend.health_check()

        self.assertEqual(health["status"], "error")
        self.assertIn("missing-model", health["error"])
        self.assertIn("help", health)
        self.assertIn("ollama pull", health["help"])

    @patch('amos_brain.model_backend.requests.Session')
    def test_health_check_connection_error(self, mock_session_class):
        """Test health check when server is not running."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.ConnectionError(
            "Connection refused"
        )
        mock_session_class.return_value = mock_session

        backend = OllamaBackend(model="test-model")
        health = backend.health_check()

        self.assertEqual(health["status"], "error")
        self.assertIn("help", health)
        self.assertIn("ollama serve", health["help"])


class TestOpenAICompatibleBackend(unittest.TestCase):
    """Tests for OpenAICompatibleLocalBackend."""

    def setUp(self):
        """Set up test fixtures."""
        self.backend = OpenAICompatibleLocalBackend(
            model="local-model",
            base_url="http://127.0.0.1:1234/v1",
            api_key="local"
        )

    @patch('amos_brain.model_backend.requests.Session')
    def test_generate_success(self, mock_session_class):
        """Test successful generation."""
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Response text"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_session.post.return_value = mock_response
        mock_session_class.return_value = mock_session

        backend = OpenAICompatibleLocalBackend(
            model="test-model",
            base_url="http://localhost:1234/v1"
        )
        result = backend.generate(
            system_prompt="You are helpful",
            user_prompt="Hi"
        )

        self.assertIsInstance(result, LLMResult)
        self.assertEqual(result.text, "Response text")

    @patch('amos_brain.model_backend.requests.Session')
    def test_health_check_lmstudio_port(self, mock_session_class):
        """Test health check provides LM Studio specific help."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.ConnectionError()
        mock_session_class.return_value = mock_session

        backend = OpenAICompatibleLocalBackend(
            model="test",
            base_url="http://127.0.0.1:1234/v1"
        )
        health = backend.health_check()

        self.assertEqual(health["status"], "error")
        self.assertIn("help", health)
        self.assertIn("LM Studio", health["help"])

    @patch('amos_brain.model_backend.requests.Session')
    def test_health_check_vllm_port(self, mock_session_class):
        """Test health check provides vLLM specific help."""
        import requests

        mock_session = MagicMock()
        mock_session.get.side_effect = requests.ConnectionError()
        mock_session_class.return_value = mock_session

        backend = OpenAICompatibleLocalBackend(
            model="test",
            base_url="http://127.0.0.1:8000/v1"
        )
        health = backend.health_check()

        self.assertEqual(health["status"], "error")
        self.assertIn("vLLM", health["help"])


class TestBackendConfiguration(unittest.TestCase):
    """Tests for backend configuration validation."""

    def test_ollama_default_url(self):
        """Test Ollama backend uses correct default URL."""
        backend = OllamaBackend(model="test")
        self.assertEqual(backend.base_url, "http://127.0.0.1:11434")

    def test_ollama_custom_url(self):
        """Test Ollama backend accepts custom URL."""
        backend = OllamaBackend(
            model="test",
            base_url="http://192.168.1.100:11434"
        )
        self.assertEqual(backend.base_url, "http://192.168.1.100:11434")

    def test_openai_backend_trailing_slash(self):
        """Test OpenAI backend strips trailing slash."""
        backend = OpenAICompatibleLocalBackend(
            model="test",
            base_url="http://localhost:1234/v1/"
        )
        self.assertEqual(backend.base_url, "http://localhost:1234/v1")


if __name__ == "__main__":
    unittest.main()
