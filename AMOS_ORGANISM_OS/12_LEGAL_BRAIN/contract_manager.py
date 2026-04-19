"""Contract Manager — Contract & IP Management

Manages contracts, intellectual property protection,
and legal agreements for the organism.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class ContractStatus(Enum):
    """Status of a contract."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class IPType(Enum):
    """Type of intellectual property."""

    COPYRIGHT = "copyright"
    PATENT = "patent"
    TRADEMARK = "trademark"
    TRADE_SECRET = "trade_secret"
    LICENSE = "license"


@dataclass
class Contract:
    """A legal contract."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    contract_type: str = ""  # service, license, nda, etc.
    parties: list[str] = field(default_factory=list)
    terms: Dict[str, Any] = field(default_factory=dict)
    status: ContractStatus = ContractStatus.DRAFT
    start_date: str = None
    end_date: str = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "status": self.status.value,
        }


@dataclass
class IPProtection:
    """Intellectual property protection record."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    ip_type: IPType = IPType.COPYRIGHT
    owner: str = ""
    description: str = ""
    registration_date: str = None
    protections: list[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "ip_type": self.ip_type.value,
        }


class ContractManager:
    """Manages contracts and intellectual property.

    Tracks contract lifecycle, IP protection, and legal agreements.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

        self.contracts: Dict[str, Contract] = {}
        self.ip_registry: Dict[str, IPProtection] = {}

        self._load_data()

    def create_contract(
        self,
        name: str,
        contract_type: str,
        parties: list[str],
        terms: dict[str, Any] = None,
    ) -> Contract:
        """Create a new contract."""
        contract = Contract(
            name=name,
            contract_type=contract_type,
            parties=parties,
            terms=terms or {},
        )
        self.contracts[contract.id] = contract
        self._save_data()
        return contract

    def activate_contract(self, contract_id: str) -> bool:
        """Activate a contract."""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        contract.status = ContractStatus.ACTIVE
        contract.start_date = datetime.now(UTC).isoformat()
        self._save_data()
        return True

    def terminate_contract(self, contract_id: str, reason: str = "") -> bool:
        """Terminate a contract."""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False

        contract.status = ContractStatus.TERMINATED
        self._save_data()
        return True

    def register_ip(
        self,
        name: str,
        ip_type: IPType,
        owner: str,
        description: str = "",
        protections: list[str] = None,
    ) -> IPProtection:
        """Register intellectual property."""
        ip = IPProtection(
            name=name,
            ip_type=ip_type,
            owner=owner,
            description=description,
            protections=protections or [],
        )
        self.ip_registry[ip.id] = ip
        self._save_data()
        return ip

    def get_active_contracts(self) -> list[Contract]:
        """Get all active contracts."""
        return [c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE]

    def check_ip_protection(self, content: str) -> list[str]:
        """Check if content matches registered IP."""
        violations = []
        for ip in self.ip_registry.values():
            if ip.name.lower() in content.lower():
                violations.append(f"Potential use of protected IP: {ip.name}")
        return violations

    def _load_data(self):
        """Load contracts and IP from disk."""
        contracts_file = self.data_dir / "contracts.json"
        if contracts_file.exists():
            try:
                data = json.loads(contracts_file.read_text())
                for c_data in data.get("contracts", []):
                    contract = Contract(
                        id=c_data["id"],
                        name=c_data["name"],
                        contract_type=c_data.get("contract_type", ""),
                        parties=c_data.get("parties", []),
                        terms=c_data.get("terms", {}),
                        status=ContractStatus(c_data["status"]),
                        start_date=c_data.get("start_date"),
                        end_date=c_data.get("end_date"),
                    )
                    self.contracts[contract.id] = contract

                for ip_data in data.get("ip_registry", []):
                    ip = IPProtection(
                        id=ip_data["id"],
                        name=ip_data["name"],
                        ip_type=IPType(ip_data["ip_type"]),
                        owner=ip_data["owner"],
                        description=ip_data.get("description", ""),
                        protections=ip_data.get("protections", []),
                    )
                    self.ip_registry[ip.id] = ip
            except Exception as e:
                print(f"[CONTRACT] Error loading data: {e}")

    def _save_data(self):
        """Save contracts and IP to disk."""
        contracts_file = self.data_dir / "contracts.json"
        data = {
            "contracts": [c.to_dict() for c in self.contracts.values()],
            "ip_registry": [ip.to_dict() for ip in self.ip_registry.values()],
            "saved_at": datetime.now(UTC).isoformat(),
        }
        contracts_file.write_text(json.dumps(data, indent=2))

    def list_contracts(self) -> list[dict[str, Any]]:
        """List all contracts."""
        return [c.to_dict() for c in self.contracts.values()]

    def list_ip(self) -> list[dict[str, Any]]:
        """List all registered IP."""
        return [ip.to_dict() for ip in self.ip_registry.values()]

    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        active = len(self.get_active_contracts())
        return {
            "total_contracts": len(self.contracts),
            "active_contracts": active,
            "total_ip_registered": len(self.ip_registry),
            "contract_types": ["service", "license", "nda", "partnership"],
            "ip_types": [t.value for t in IPType],
        }


_MANAGER: Optional[ContractManager] = None


def get_contract_manager(data_dir: Optional[Path] = None) -> ContractManager:
    """Get or create global contract manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = ContractManager(data_dir)
    return _MANAGER
