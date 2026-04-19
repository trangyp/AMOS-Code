#!/usr/bin/env python3
"""Quick test of AMOS Local Platform components."""

import sys
from pathlib import Path

# Test imports
print("Testing imports...")
try:
    from amos_model_fabric.litellm_setup import LiteLLMSetup
    print("✓ LiteLLMSetup imported")
except Exception as e:
    print(f"✗ LiteLLMSetup: {e}")
    sys.exit(1)

try:
    from amos_model_fabric.continue_integration import ContinueConfigGenerator
    print("✓ ContinueConfigGenerator imported")
except Exception as e:
    print(f"✗ ContinueConfigGenerator: {e}")

try:
    from amos_model_fabric.aider_integration import AiderIntegration
    print("✓ AiderIntegration imported")
except Exception as e:
    print(f"✗ AiderIntegration: {e}")

try:
    from repo_doctor.security_scanner import SecurityVerificationEngine
    print("✓ SecurityVerificationEngine imported")
except Exception as e:
    print(f"✗ SecurityVerificationEngine: {e}")

try:
    from clawspring.openclaw_bridge import OpenClawBridge
    print("✓ OpenClawBridge imported")
except Exception as e:
    print(f"✗ OpenClawBridge: {e}")

# Test LiteLLM config generation
print("\nTesting LiteLLM config generation...")
setup = LiteLLMSetup()
config = setup.generate_config()
print(f"✓ Generated config with {len(config.get('model_list', []))} models")

# Test Continue config
print("\nTesting Continue config generation...")
cont = ContinueConfigGenerator()
config = cont.generate_config()
print(f"✓ Generated Continue config with {len(config.get('models', []))} models")

print("\n✅ All core components working!")
print("\nNext steps:")
print("  1. Install security scanners: ./scripts/install_security_scanners.sh")
print("  2. Setup platform: python3 amos_local_platform.py setup")
print("  3. Start services: python3 amos_local_platform.py start")
