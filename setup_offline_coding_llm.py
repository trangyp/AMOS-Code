#!/usr/bin/env python3

"""Setup script for the strongest offline LLM coding model for AMOS Brain.

This script:
1. Checks if Ollama is installed
2. Installs Ollama if needed
3. Downloads the best coding model (Qwen 2.5 Coder 32B)
4. Configures AMOS to use the offline model
5. Tests the integration

Creator: Trang Phan
Version: 1.0.0
"""

import os
import platform
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def print_step(step: int, total: int, text: str) -> None:
    """Print a step indicator."""
    print(f"[{step}/{total}] {text}")


def check_ollama_installed() -> bool:
    """Check if Ollama is already installed."""
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_ollama() -> bool:
    """Install Ollama based on the operating system."""
    system = platform.system()

    print(f"Detected OS: {system}")

    if system == "Darwin":  # macOS
        # Check if Homebrew is available
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            print("Installing Ollama via Homebrew...")
            result = subprocess.run(["brew", "install", "ollama"], capture_output=True, text=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Download from official website
            print("Please download and install Ollama from: https://ollama.com/download")
            print("After installation, run this script again.")
            return False

    elif system == "Linux":
        print("Installing Ollama via official installer...")
        install_script = "/tmp/install_ollama.sh"
        try:
            urllib.request.urlretrieve("https://ollama.com/install.sh", install_script)
            os.chmod(install_script, 0o755)
            result = subprocess.run(["sh", install_script], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Installation failed: {e}")
            return False

    elif system == "Windows":
        print("Please download and install Ollama from: https://ollama.com/download")
        print("After installation, run this script again.")
        return False


def start_ollama_service() -> bool:
    """Start the Ollama service."""
    try:
        # Check if already running
        result = subprocess.run(
            ["curl", "-s", "http://localhost:11434/api/tags"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            print("✓ Ollama service is already running")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    print("Starting Ollama service...")
    try:
        # Start ollama in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        # Wait for service to start
        for _ in range(30):
            time.sleep(1)
            try:
                result = subprocess.run(
                    ["curl", "-s", "http://localhost:11434/api/tags"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if result.returncode == 0:
                    print("✓ Ollama service started successfully")
                    return True
            except Exception:
                continue

        print("✗ Failed to start Ollama service")
        return False

    except Exception as e:
        print(f"✗ Error starting Ollama: {e}")
        return False


def get_available_models() -> list[str]:
    """Get list of models already downloaded in Ollama."""
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = []
            for line in result.stdout.strip().split("\n")[1:]:  # Skip header
                if line:
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
    except Exception:
        pass
    return []


def download_model(model_name: str) -> bool:
    """Download a model using Ollama."""
    print(f"\nDownloading {model_name}...")
    print("This may take several minutes depending on your connection.\n")

    try:
        process = subprocess.Popen(
            ["ollama", "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Show progress
        for line in process.stdout:
            line = line.strip()
            if line:
                print(f"  {line}")

        process.wait()

        if process.returncode == 0:
            print(f"\n✓ {model_name} downloaded successfully")
            return True
        else:
            print(f"\n✗ Failed to download {model_name}")
            return False

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        return False
    except Exception as e:
        print(f"\n✗ Error downloading model: {e}")
        return False


def configure_amos(model_name: str) -> None:
    """Configure AMOS to use the offline model."""
    print("\nConfiguring AMOS Brain...")

    env_file = Path(".env")
    env_content = []

    # Read existing .env if it exists
    if env_file.exists():
        env_content = env_file.read_text().split("\n")

    # Remove existing OLLAMA_MODEL line if present
    env_content = [line for line in env_content if not line.startswith("OLLAMA_MODEL=")]

    # Add new configuration
    env_content.append(f"OLLAMA_MODEL={model_name}")
    env_content.append("OLLAMA_HOST=http://localhost:11434")
    env_content.append("")
    env_content.append("# Offline LLM Configuration")
    env_content.append(f"# Primary model: {model_name}")
    env_content.append("# Fallback: cloud providers (if API keys set)")

    # Write back
    env_file.write_text("\n".join(env_content))

    print(f"✓ Updated .env with OLLAMA_MODEL={model_name}")


def test_integration(model_name: str) -> bool:
    """Test the AMOS + Ollama integration."""
    print("\nTesting AMOS Brain + Offline LLM integration...")

    test_script = f"""
    import asyncio
sys.path.insert(0, ".")

    from backend.llm_providers import LLMRouter, LLMRequest, Message

async def test():
    router = LLMRouter()

    # Check available providers
    providers = router.get_available_providers()
    print(f"\\nAvailable providers: {{[p['name'] for p in providers]}}")

    if "ollama" not in [p["name"] for p in providers]:
        print("✗ Ollama provider not available")
        return False

    # Test coding task
    request = LLMRequest(
        messages=[
            Message(role="system", content="You are an expert coding assistant."),
            Message(role="user", content="Write a Python function to calculate fibonacci numbers using memoization.")
        ],
        model="{model_name}",
        temperature=0.7
    )

    print(f"\\nSending test request to {{request.model}}...")
    print("This may take a moment for first inference...\\n")

    try:
        response = await router.route_request(request, preference="ollama")

        print(f"✓ Response received!")
        print(f"  Model: {{response.model}}")
        print(f"  Provider: {{response.provider}}")
        print(f"  Latency: {{response.latency_ms:.0f}}ms")
        print(f"  Tokens: {{response.usage}}")
        print(f"\\nPreview: {{response.content[:200]}}...")

        return True

    except Exception as e:
        print(f"✗ Test failed: {{e}}")
        return False
    finally:
        await router.close_all()

if __name__ == "__main__":
    success = asyncio.run(test())
    sys.exit(0 if success else 1)
"""

    test_file = Path("/tmp/test_amos_ollama.py")
    test_file.write_text(test_script)

    try:
        result = subprocess.run(
            [sys.executable, str(test_file)], capture_output=True, text=True, timeout=120
        )
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("✗ Test timed out (120s)")
        return False
    except Exception as e:
        print(f"✗ Test error: {e}")
        return False


def main():
    """Main setup process."""
    print_header("AMOS Brain - Offline LLM Setup")
    print("Setting up the strongest offline coding model for AMOS.\n")

    total_steps = 6
    current_step = 0

    # Step 1: Check Ollama
    current_step += 1
    print_step(current_step, total_steps, "Checking Ollama installation...")

    if check_ollama_installed():
        print("✓ Ollama is already installed")
    else:
        print("✗ Ollama not found")
        print_step(current_step, total_steps, "Installing Ollama...")

        if not install_ollama():
            print("\n✗ Failed to install Ollama automatically.")
            print("Please install manually from: https://ollama.com")
            sys.exit(1)

    # Step 2: Start Ollama service
    current_step += 1
    print_step(current_step, total_steps, "Starting Ollama service...")

    if not start_ollama_service():
        print("\n✗ Failed to start Ollama service.")
        print("Please start it manually: ollama serve")
        sys.exit(1)

    # Step 3: Check available models
    current_step += 1
    print_step(current_step, total_steps, "Checking available models...")

    available_models = get_available_models()
    print(f"Currently available models: {available_models or 'None'}")

    # Step 4: Download best coding model
    current_step += 1
    print_step(current_step, total_steps, "Downloading strongest coding model...")

    # Coding model recommendations (best to good)
    coding_models = [
        ("qwen2.5-coder:32b", "Qwen 2.5 Coder 32B - State-of-the-art coding model"),
        ("qwen2.5-coder:14b", "Qwen 2.5 Coder 14B - Excellent coding, smaller size"),
        ("deepseek-coder-v2:16b", "DeepSeek Coder V2 16B - Great for code completion"),
        ("codellama:70b", "CodeLlama 70B - Meta's largest coding model"),
        ("codellama:34b", "CodeLlama 34B - Balanced performance"),
        ("llama3.3:70b", "Llama 3.3 70B - General purpose, good at coding"),
        ("phi4:14b", "Phi-4 14B - Microsoft's latest, efficient"),
    ]

    selected_model = None

    # Check if any good coding model is already available
    for model_name, _ in coding_models:
        base_name = model_name.split(":")[0]
        for available in available_models:
            if base_name in available.lower():
                selected_model = available
                print(f"✓ Found existing coding model: {selected_model}")
                break
        if selected_model:
            break

    # If no good model found, download the best one
    if not selected_model:
        print("\nRecommended coding models (best to good):")
        for i, (model, desc) in enumerate(coding_models, 1):
            print(f"  {i}. {model} - {desc}")

        print("\nDefault: Downloading Qwen 2.5 Coder 14B (best balance of power and size)")
        print("Press Ctrl+C to cancel and download a different model manually\n")

        # Try downloading in order of preference
        for model_name, desc in coding_models:
            if download_model(model_name):
                selected_model = model_name
                break

        if not selected_model:
            print("\n✗ Failed to download any model.")
            print("Please download manually: ollama pull qwen2.5-coder:14b")
            sys.exit(1)

    # Step 5: Configure AMOS
    current_step += 1
    print_step(current_step, total_steps, "Configuring AMOS Brain...")
    configure_amos(selected_model)

    # Step 6: Test integration
    current_step += 1
    print_step(current_step, total_steps, "Testing integration...")

    if test_integration(selected_model):
        print("\n" + "=" * 60)
        print("  ✓ SETUP COMPLETE!")
        print("=" * 60)
        print("\nYour AMOS Brain is now configured to use:")
        print(f"  Model: {selected_model}")
        print("  Provider: Ollama (offline/local)")
        print("\nYou can now use the brain with:")
        print("  python amos_cli.py brain 'Your coding question'")
        print("  python -c \"import amos_brain; b = amos_brain.activate(); b.think('code')\"")
        print("\nTo use in Python:")
        print("  from backend.llm_providers import llm_router")
        print("  # The router will automatically prefer Ollama when available")
        print(f"\n{'=' * 60}\n")
    else:
        print("\n⚠ Setup completed but test failed.")
        print("The model is downloaded but there may be an integration issue.")
        print("Check that Ollama is running: ollama serve")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user.")
        sys.exit(1)
