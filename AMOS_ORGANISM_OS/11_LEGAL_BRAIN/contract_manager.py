"""Contract Manager — Contract tracking and management

Manages contracts, agreements, and legal obligations
for the AMOS organism.
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

UTC = UTC
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ContractStatus(Enum):
    """Status of a contract."""

    DRAFT = "draft"
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRING = "expiring"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class ContractType(Enum):
    """Type of contract."""

    SERVICE = "service"
    LICENSE = "license"
    PARTNERSHIP = "partnership"
    NDA = "nda"
    EMPLOYMENT = "employment"
    VENDOR = "vendor"
    CUSTOM = "custom"


@dataclass
class Contract:
    """A contract or agreement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    contract_type: ContractType = ContractType.CUSTOM
    status: ContractStatus = ContractStatus.DRAFT
    parties: list[str] = field(default_factory=list)
    start_date: str = ""
    end_date: str = None
    renewal_date: str = None
    value: float = 0.0
    currency: str = "USD"
    key_terms: list[str] = field(default_factory=list)
    obligations: list[str] = field(default_factory=list)
    notes: str = ""
    document_path: str = None
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            **asdict(self),
            "contract_type": self.contract_type.value,
            "status": self.status.value,
        }


@dataclass
class ContractAlert:
    """Alert for contract events."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    contract_id: str = ""
    alert_type: str = ""  # renewal, expiry, payment, etc.
    message: str = ""
    due_date: str = ""
    acknowledged: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ContractManager:
    """Manages contracts and legal agreements.

    Tracks contract lifecycle, renewals, obligations,
    and generates alerts for important dates.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.contracts: list[Contract] = []
        self.alerts: list[ContractAlert] = []

        self._load_data()

    def _load_data(self):
        """Load contract data from disk."""
        data_file = self.data_dir / "contracts.json"
        if data_file.exists():
            try:
                data = json.loads(data_file.read_text())
                for c_data in data.get("contracts", []):
                    contract = Contract(
                        id=c_data["id"],
                        title=c_data["title"],
                        contract_type=ContractType(c_data["contract_type"]),
                        status=ContractStatus(c_data["status"]),
                        parties=c_data.get("parties", []),
                        start_date=c_data.get("start_date", ""),
                        end_date=c_data.get("end_date"),
                        renewal_date=c_data.get("renewal_date"),
                        value=c_data.get("value", 0.0),
                        currency=c_data.get("currency", "USD"),
                        key_terms=c_data.get("key_terms", []),
                        obligations=c_data.get("obligations", []),
                        notes=c_data.get("notes", ""),
                        document_path=c_data.get("document_path"),
                        created_at=c_data["created_at"],
                        updated_at=c_data["updated_at"],
                    )
                    self.contracts.append(contract)

                for a_data in data.get("alerts", []):
                    alert = ContractAlert(**a_data)
                    self.alerts.append(alert)
            except Exception as e:
                print(f"[CONTRACT] Error loading data: {e}")

    def save(self):
        """Save contract data to disk."""
        data_file = self.data_dir / "contracts.json"
        data = {
            "saved_at": datetime.now(UTC).isoformat(),
            "contracts": [c.to_dict() for c in self.contracts],
            "alerts": [a.to_dict() for a in self.alerts],
        }
        data_file.write_text(json.dumps(data, indent=2))

    def create_contract(
        self,
        title: str,
        contract_type: ContractType,
        parties: list[str],
        start_date: str,
        end_date: str = None,
    ) -> Contract:
        """Create a new contract."""
        contract = Contract(
            title=title,
            contract_type=contract_type,
            parties=parties,
            start_date=start_date,
            end_date=end_date,
            status=ContractStatus.DRAFT,
        )
        self.contracts.append(contract)
        self.save()
        return contract

    def get_contract(self, contract_id: str) -> Optional[Contract]:
        """Get a contract by ID."""
        for contract in self.contracts:
            if contract.id == contract_id:
                return contract
        return None

    def update_status(self, contract_id: str, status: ContractStatus) -> bool:
        """Update contract status."""
        contract = self.get_contract(contract_id)
        if contract:
            contract.status = status
            contract.updated_at = datetime.now(UTC).isoformat()
            self.save()
            return True
        return False

    def check_expirations(self) -> list[ContractAlert]:
        """Check for upcoming expirations and generate alerts."""
        new_alerts = []
        today = datetime.now(UTC)
        warning_days = 30

        for contract in self.contracts:
            if contract.status not in [ContractStatus.EXPIRED, ContractStatus.TERMINATED]:
                # Check end date
                if contract.end_date:
                    end = datetime.fromisoformat(contract.end_date)
                    days_until = (end - today).days

                    if days_until <= 0:
                        contract.status = ContractStatus.EXPIRED
                        alert = ContractAlert(
                            contract_id=contract.id,
                            alert_type="expired",
                            message=f"Contract '{contract.title}' has expired",
                            due_date=contract.end_date,
                        )
                        new_alerts.append(alert)
                    elif days_until <= warning_days:
                        contract.status = ContractStatus.EXPIRING
                        alert = ContractAlert(
                            contract_id=contract.id,
                            alert_type="expiring_soon",
                            message=f"Contract '{contract.title}' expires in {days_until} days",
                            due_date=contract.end_date,
                        )
                        new_alerts.append(alert)

                # Check renewal date
                if contract.renewal_date:
                    renewal = datetime.fromisoformat(contract.renewal_date)
                    days_until = (renewal - today).days

                    if 0 < days_until <= warning_days:
                        alert = ContractAlert(
                            contract_id=contract.id,
                            alert_type="renewal_due",
                            message=f"Contract '{contract.title}' renewal due in {days_until} days",
                            due_date=contract.renewal_date,
                        )
                        new_alerts.append(alert)

        self.alerts.extend(new_alerts)
        self.save()
        return new_alerts

    def get_active_contracts(self) -> list[dict[str, Any]]:
        """Get all active contracts."""
        active = [
            c
            for c in self.contracts
            if c.status in [ContractStatus.ACTIVE, ContractStatus.EXPIRING]
        ]
        return [c.to_dict() for c in active]

    def get_pending_alerts(self) -> list[dict[str, Any]]:
        """Get pending (unacknowledged) alerts."""
        pending = [a for a in self.alerts if not a.acknowledged]
        return sorted(
            [a.to_dict() for a in pending],
            key=lambda x: x["due_date"],
        )

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                self.save()
                return True
        return False

    def get_contract_summary(self) -> dict[str, Any]:
        """Get summary of contract portfolio."""
        by_status = {}
        for c in self.contracts:
            s = c.status.value
            by_status[s] = by_status.get(s, 0) + 1

        total_value = sum(c.value for c in self.contracts if c.status == ContractStatus.ACTIVE)

        return {
            "total_contracts": len(self.contracts),
            "by_status": by_status,
            "active_contracts": len(
                [c for c in self.contracts if c.status == ContractStatus.ACTIVE]
            ),
            "total_portfolio_value": total_value,
            "currency": "USD",
            "pending_alerts": len([a for a in self.alerts if not a.acknowledged]),
        }


# Global instance
_MANAGER: Optional[ContractManager] = None


def get_contract_manager(data_dir: Optional[Path] = None) -> ContractManager:
    """Get or create global contract manager."""
    global _MANAGER
    if _MANAGER is None:
        _MANAGER = ContractManager(data_dir)
    return _MANAGER


if __name__ == "__main__":
    print("Contract Manager (11_LEGAL_BRAIN)")
    print("=" * 40)

    manager = get_contract_manager()

    # Create sample contract
    contract = manager.create_contract(
        title="Cloud Service Agreement",
        contract_type=ContractType.SERVICE,
        parties=["AMOS", "AWS"],
        start_date=datetime.now(UTC).isoformat(),
    )
    print(f"\nCreated contract: {contract.title}")

    print("\nContract Summary:")
    summary = manager.get_contract_summary()
    print(f"  Total contracts: {summary['total_contracts']}")
    print(f"  Portfolio value: ${summary['total_portfolio_value']:.2f}")
