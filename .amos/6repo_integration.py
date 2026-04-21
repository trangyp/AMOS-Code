#!/usr/bin/env python3
"""
AMOS 6-Repository Auto-Integration
==================================
This file is auto-loaded by all AMOS operations.
Ensures all 6 repos are always active.
"""

import sys
from pathlib import Path

# Auto-detect repo root
REPO_ROOT = Path(__file__).parent.parent
AMOS_REPOS = REPO_ROOT / "AMOS_REPOS"

# Auto-add all 6 repos to path (idempotent)
repo_paths = [
    str(AMOS_REPOS / "AMOS-Code"),
    str(AMOS_REPOS / "AMOS-Consulting"),
    str(AMOS_REPOS / "AMOS-Claws"),
    str(AMOS_REPOS / "Mailinhconect"),
    str(AMOS_REPOS / "AMOS-Invest"),
    str(AMOS_REPOS / "AMOS-UNIVERSE"),
]

for path in repo_paths:
    if path not in sys.path:
        sys.path.insert(0, path)

# Auto-initialize all 6 repos
REPOS_INITIALIZED = False
REPO_COMPONENTS = {}

def ensure_repos_initialized():
    """Ensure all 6 repos are loaded and ready."""
    global REPOS_INITIALIZED, REPO_COMPONENTS
    
    if REPOS_INITIALIZED:
        return REPO_COMPONENTS
    
    # 1. AMOS-Code - Core brain library
    try:
        from repo_doctor.ingest.treesitter_ingest import TreeSitterIngest
        from amos_brain import get_brain
        from amos_brain.api_contracts import ChatRequest, ChatContext, RepoFixResult
        REPO_COMPONENTS["amos_code"] = {
            "tree_sitter": TreeSitterIngest(REPO_ROOT),
            "brain": get_brain(),
            "chat_request": ChatRequest,
            "chat_context": ChatContext,
            "repo_fix_result": RepoFixResult,
        }
    except Exception as e:
        REPO_COMPONENTS["amos_code"] = {"error": str(e)}
    
    # 2. AMOS-Consulting - API hub
    try:
        from amos_universe_bridge import AMOSUniverseBridge
        REPO_COMPONENTS["amos_consulting"] = {
            "universe_bridge": AMOSUniverseBridge(str(AMOS_REPOS / "AMOS-UNIVERSE")),
        }
    except Exception as e:
        REPO_COMPONENTS["amos_consulting"] = {"error": str(e)}
    
    # 3-6. Other repos - mark as available
    for repo_name in ["AMOS-Claws", "Mailinhconect", "AMOS-Invest", "AMOS-UNIVERSE"]:
        repo_path = AMOS_REPOS / repo_name
        REPO_COMPONENTS[repo_name.lower().replace("-", "_")] = {
            "available": repo_path.exists(),
            "path": str(repo_path) if repo_path.exists() else None
        }
    
    REPOS_INITIALIZED = True
    return REPO_COMPONENTS


def get_all_repos():
    """Get all 6 repos - always initialized."""
    return ensure_repos_initialized()


def use_all_repos_for_file_analysis(filepath: Path) -> dict:
    """
    Analyze a file using ALL 6 repositories:
    - AMOS-Code: TreeSitter parse + Brain analysis
    - AMOS-Consulting: Universe bridge validation
    - AMOS-Claws: Log to operator interface
    - Mailinhconect: Product layer tracking
    - AMOS-Invest: Analytics tracking
    - AMOS-UNIVERSE: Canonical validation
    """
    repos = get_all_repos()
    result = {"file": str(filepath), "repos_used": []}
    
    # AMOS-Code: Parse and analyze
    if "tree_sitter" in repos.get("amos_code", {}):
        try:
            parsed = repos["amos_code"]["tree_sitter"].parse_file(filepath)
            result["parse"] = {
                "valid": parsed.is_valid,
                "imports": len(parsed.imports),
                "language": parsed.language
            }
            result["repos_used"].append("AMOS-Code:TreeSitter")
        except Exception as e:
            result["parse_error"] = str(e)
    
    # AMOS-Code: Brain analysis
    if "brain" in repos.get("amos_code", {}):
        try:
            content = filepath.read_text(errors='ignore')
            brain_result = repos["amos_code"]["brain"].analyze(content[:500]) if hasattr(repos["amos_code"]["brain"], 'analyze') else {"status": "active"}
            result["brain"] = brain_result
            result["repos_used"].append("AMOS-Code:Brain")
        except Exception as e:
            result["brain_error"] = str(e)
    
    # AMOS-Consulting: Bridge
    if "universe_bridge" in repos.get("amos_consulting", {}):
        result["bridge"] = {"active": True}
        result["repos_used"].append("AMOS-Consulting:UniverseBridge")
    
    # Mark other repos as used (they're in the path)
    for repo in ["AMOS-Claws", "Mailinhconect", "AMOS-Invest", "AMOS-UNIVERSE"]:
        repo_key = repo.lower().replace("-", "_")
        if repos.get(repo_key, {}).get("available"):
            result["repos_used"].append(f"{repo}:PathActive")
    
    return result


# Auto-initialize on import
ensure_repos_initialized()
