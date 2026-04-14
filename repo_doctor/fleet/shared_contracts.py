"""
Shared Contract Analysis Across Fleet

Detects contract violations that repeat across repositories.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ContractViolationCluster:
    """A cluster of similar contract violations across repos."""
    
    violation_type: str
    pattern: str
    affected_repos: list[str]
    common_cause: str | None = None
    suggested_fix: str | None = None


class SharedContractAnalyzer:
    """
    Analyze contract consistency across fleet.
    
    Detects shared API schemas, packaging policies, entrypoint policies,
    shell/runtime policies, and security policies.
    """
    
    def __init__(self):
        self.contracts: dict[str, dict[str, Any]] = {}
    
    def register_repo_contracts(
        self,
        repo_id: str,
        api_schema: dict[str, Any],
        packaging_policy: dict[str, Any],
        entrypoint_policy: dict[str, Any],
        runtime_policy: dict[str, Any],
        security_policy: dict[str, Any],
    ) -> None:
        """Register a repo's contract surface."""
        self.contracts[repo_id] = {
            "api_schema": api_schema,
            "packaging": packaging_policy,
            "entrypoints": entrypoint_policy,
            "runtime": runtime_policy,
            "security": security_policy,
        }
    
    def find_api_schema_divergence(self) -> list[ContractViolationCluster]:
        """
        Find API schema inconsistencies across repos.
        
        Returns clusters of repos with divergent API contracts.
        """
        clusters = []
        
        # Group repos by API schema hash
        schema_groups: dict[str, list[str]] = {}
        for repo_id, contracts in self.contracts.items():
            schema = contracts.get("api_schema", {})
            # Simple hash of schema structure
            schema_key = self._hash_schema(schema)
            
            if schema_key not in schema_groups:
                schema_groups[schema_key] = []
            schema_groups[schema_key].append(repo_id)
        
        # If multiple schema versions exist, report divergence
        if len(schema_groups) > 1:
            for schema_key, repos in schema_groups.items():
                clusters.append(ContractViolationCluster(
                    violation_type="api_schema_divergence",
                    pattern=f"schema_variant_{schema_key[:8]}",
                    affected_repos=repos,
                    common_cause="Different API schema versions across fleet",
                    suggested_fix="Standardize on common API schema",
                ))
        
        return clusters
    
    def find_packaging_policy_violations(self) -> list[ContractViolationCluster]:
        """Find repos violating shared packaging policies."""
        clusters = []
        
        # Check for version format consistency
        version_formats: dict[str, list[str]] = {}
        for repo_id, contracts in self.contracts.items():
            policy = contracts.get("packaging", {})
            version_format = policy.get("version_format", "unknown")
            
            if version_format not in version_formats:
                version_formats[version_format] = []
            version_formats[version_format].append(repo_id)
        
        # Report if multiple version formats exist
        if len(version_formats) > 1:
            for fmt, repos in version_formats.items():
                clusters.append(ContractViolationCluster(
                    violation_type="packaging_policy_divergence",
                    pattern=f"version_format_{fmt}",
                    affected_repos=repos,
                    common_cause="Inconsistent versioning schemes",
                    suggested_fix="Standardize on semantic versioning",
                ))
        
        return clusters
    
    def find_shared_security_violations(self) -> list[ContractViolationCluster]:
        """Find security violations common across repos."""
        clusters = []
        
        # Aggregate forbidden flows
        flow_violations: dict[str, list[str]] = {}
        for repo_id, contracts in self.contracts.items():
            security = contracts.get("security", {})
            flows = security.get("forbidden_flows", [])
            
            for flow in flows:
                if flow not in flow_violations:
                    flow_violations[flow] = []
                flow_violations[flow].append(repo_id)
        
        # Report flows that appear in multiple repos
        for flow, repos in flow_violations.items():
            if len(repos) > 1:
                clusters.append(ContractViolationCluster(
                    violation_type="shared_security_violation",
                    pattern=flow,
                    affected_repos=repos,
                    common_cause="Shared vulnerable pattern",
                    suggested_fix="Apply fleet-wide security patch",
                ))
        
        return clusters
    
    def _hash_schema(self, schema: dict[str, Any]) -> str:
        """Create simple hash of schema structure."""
        import hashlib
        import json
        
        # Normalize and hash
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()[:16]
