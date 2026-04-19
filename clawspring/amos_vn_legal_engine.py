"""AMOS VN Legal Engine - Vietnam-specialised legal reasoning."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class LegalDomain(Enum):
    """Vietnam legal domains."""
    CORPORATE = "corporate"
    FINANCE = "finance"
    DISPUTES = "disputes"
    REGULATORY = "regulatory"
    IP_DATA = "ip_data"
    ESG = "esg"


@dataclass
class LegalFinding:
    """Legal analysis finding."""

    domain: str
    concept: str
    application: str
    risk_level: str


class CorporateLawKernel:
    """Kernel for Vietnam corporate law analysis."""

    PRINCIPLES = [
        "enterprise_law",
        "investment_law",
        "company_structuring",
        "shareholder_rights",
        "board_governance",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze corporate law aspects."""
        findings = []
        scenario_lower = scenario.lower()
        corporate_indicators = [
            ("incorporation", "enterprise_registration", "Company formation"),
            ("company", "corporate_structure", "Entity structuring"),
            ("shareholder", "shareholder_agreement", "Equity arrangements"),
            ("board", "board_governance", "Director duties"),
            ("merger", "mna_vietnam", "M&A regulations"),
            ("acquisition", "business_acquisition", "Takeover rules"),
            ("joint venture", "jv_structure", "Foreign investment"),
            ("wfoe", "wholly_foreign_owned", "100% foreign ownership"),
            ("representative office", "rep_office", "Liaison office"),
            ("branch", "branch_registration", "Branch establishment"),
        ]
        for indicator, concept, application in corporate_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="corporate",
                        concept=concept,
                        application=application,
                        risk_level="moderate",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class FinanceLawKernel:
    """Kernel for Vietnam finance/banking law analysis."""

    PRINCIPLES = [
        "state_bank_regulations",
        "securities_law",
        "insurance_regulations",
        "foreign_exchange",
        "payment_systems",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze finance law aspects."""
        findings = []
        scenario_lower = scenario.lower()
        finance_indicators = [
            ("banking", "banking_license", "Credit institutions"),
            ("securities", "securities_offering", "Stock market"),
            ("ipo", "public_listing", "HoSE/HNX listing"),
            ("bond", "bond_issuance", "Corporate bonds"),
            ("foreign exchange", "fx_regulations", "Forex controls"),
            ("loan", "lending_regulations", "Credit agreements"),
            ("collateral", "security_interest", "Mortgage/Pledge"),
            ("insurance", "insurance_license", "Insurance business"),
            ("fintech", "digital_payment", "Payment services"),
            ("crypto", "virtual_asset", "Cryptocurrency ban"),
        ]
        for indicator, concept, application in finance_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="finance",
                        concept=concept,
                        application=application,
                        risk_level="high" if "crypto" in indicator else "moderate",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class DisputesLawKernel:
    """Kernel for Vietnam dispute resolution analysis."""

    PRINCIPLES = [
        "civil_procedure_code",
        "commercial_arbitration",
        "enforcement_rules",
        "appeal_process",
        "alternative_dispute",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze dispute resolution aspects."""
        findings = []
        scenario_lower = scenario.lower()
        dispute_indicators = [
            ("litigation", "court_proceeding", "People's Court"),
            ("arbitration", "viac_arbitration", "VIAC/VIAC-DN"),
            ("mediation", "commercial_mediation", "Conciliation"),
            ("enforcement", "judgment_enforcement", "Civil judgment"),
            ("appeal", "appellate_process", "Higher court"),
            ("contract dispute", "breach_contract", "Civil Code remedies"),
            ("tort", "tious_liability", "Damages claim"),
            ("injunction", "preliminary_relief", "Emergency measures"),
            ("evidence", "evidence_preservation", "Notarization"),
            ("statute", "limitation_period", "Time limits"),
        ]
        for indicator, concept, application in dispute_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="disputes",
                        concept=concept,
                        application=application,
                        risk_level="high",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class RegulatoryLawKernel:
    """Kernel for Vietnam regulatory compliance analysis."""

    PRINCIPLES = [
        "licensing_requirements",
        "sector_regulations",
        "competition_law",
        "consumer_protection",
        "labor_compliance",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze regulatory compliance aspects."""
        findings = []
        scenario_lower = scenario.lower()
        regulatory_indicators = [
            ("license", "business_license", "Investment registration"),
            ("permit", "operational_permit", "Sector approvals"),
            ("compliance", "regulatory_compliance", "Ongoing duties"),
            ("competition", "competition_law", "Vietnam Competition Law"),
            ("antitrust", "monopoly_control", "Dominant position"),
            ("consumer", "consumer_protection", "Product liability"),
            ("labor", "labor_law", "Employment contracts"),
            ("environment", "environmental_permit", "EIA requirements"),
            ("tax", "tax_compliance", "GDT regulations"),
            ("customs", "import_export", "Customs procedures"),
        ]
        for indicator, concept, application in regulatory_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="regulatory",
                        concept=concept,
                        application=application,
                        risk_level="high" if "compliance" in indicator else "moderate",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class IPDataLawKernel:
    """Kernel for Vietnam IP and data protection analysis."""

    PRINCIPLES = [
        "intellectual_property",
        "data_privacy",
        "cybersecurity",
        "technology_transfer",
        "licensing",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze IP and data protection aspects."""
        findings = []
        scenario_lower = scenario.lower()
        ip_indicators = [
            ("patent", "patent_protection", "NOIP registration"),
            ("trademark", "trademark_registration", "Brand protection"),
            ("copyright", "copyright_vietnam", "Author rights"),
            ("trade secret", "confidentiality", "Undisclosed info"),
            ("data", "data_protection", "PDPD compliance"),
            ("privacy", "personal_data", "Consent requirements"),
            ("cybersecurity", "cybersecurity_law", "Network security"),
            ("cross-border", "data_transfer", "Overseas transfer"),
            ("technology", "tech_transfer", "Licensing agreement"),
            ("software", "software_copyright", "Program protection"),
        ]
        for indicator, concept, application in ip_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="ip_data",
                        concept=concept,
                        application=application,
                        risk_level="high" if "data" in indicator else "moderate",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class ESGLawKernel:
    """Kernel for Vietnam ESG (Environmental, Social, Governance) analysis."""

    PRINCIPLES = [
        "environmental_law",
        "social_compliance",
        "corporate_governance",
        "sustainability_reporting",
        "ethical_standards",
    ]

    def __init__(self):
        self.findings: List[LegalFinding] = []

    def analyze(self, scenario: str) -> List[LegalFinding]:
        """Analyze ESG aspects."""
        findings = []
        scenario_lower = scenario.lower()
        esg_indicators = [
            ("environment", "environmental_protection", "EIA/EPR"),
            ("carbon", "carbon_regulations", "Emission controls"),
            ("sustainability", "esg_reporting", "Disclosure"),
            ("social", "labor_standards", "Working conditions"),
            ("governance", "board_ethics", "Director duties"),
            ("ethics", "anti_corruption", "Bribery prevention"),
            ("human rights", "rights_compliance", "Due diligence"),
            ("supply chain", "supply_compliance", "Vendor standards"),
            ("community", "community_engagement", "Social license"),
            ("disclosure", "transparency", "Public reporting"),
        ]
        for indicator, concept, application in esg_indicators:
            if indicator in scenario_lower:
                findings.append(
                    LegalFinding(
                        domain="esg",
                        concept=concept,
                        application=application,
                        risk_level="moderate",
                    )
                )
        self.findings = findings
        return findings

    def get_principles(self) -> List[str]:
        return self.PRINCIPLES


class VNLegalEngine:
    """AMOS VN Legal Engine - Vietnam-specialised legal reasoning."""

    VERSION = "vInfinity_Legal_1.0.0"
    NAME = "AMOS_VN_Legal_OMEGA"

    def __init__(self):
        self.corporate_kernel = CorporateLawKernel()
        self.finance_kernel = FinanceLawKernel()
        self.disputes_kernel = DisputesLawKernel()
        self.regulatory_kernel = RegulatoryLawKernel()
        self.ip_data_kernel = IPDataLawKernel()
        self.esg_kernel = ESGLawKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run Vietnam legal analysis."""
        domains = domains or [
            "corporate",
            "finance",
            "disputes",
            "regulatory",
            "ip_data",
            "esg",
        ]
        results: Dict[str, Any] = {}
        if "corporate" in domains:
            results["corporate"] = self._analyze_corporate(description)
        if "finance" in domains:
            results["finance"] = self._analyze_finance(description)
        if "disputes" in domains:
            results["disputes"] = self._analyze_disputes(description)
        if "regulatory" in domains:
            results["regulatory"] = self._analyze_regulatory(description)
        if "ip_data" in domains:
            results["ip_data"] = self._analyze_ip_data(description)
        if "esg" in domains:
            results["esg"] = self._analyze_esg(description)
        return results

    def _analyze_corporate(self, description: str) -> dict:
        findings = self.corporate_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.corporate_kernel.get_principles(),
        }

    def _analyze_finance(self, description: str) -> dict:
        findings = self.finance_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.finance_kernel.get_principles(),
        }

    def _analyze_disputes(self, description: str) -> dict:
        findings = self.disputes_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.disputes_kernel.get_principles(),
        }

    def _analyze_regulatory(self, description: str) -> dict:
        findings = self.regulatory_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.regulatory_kernel.get_principles(),
        }

    def _analyze_ip_data(self, description: str) -> dict:
        findings = self.ip_data_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.ip_data_kernel.get_principles(),
        }

    def _analyze_esg(self, description: str) -> dict:
        findings = self.esg_kernel.analyze(description)
        return {
            "query": description[:100],
            "findings_count": len(findings),
            "findings": [
                {"concept": f.concept, "application": f.application, "risk": f.risk_level}
                for f in findings[:3]
            ],
            "principles": self.esg_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with safety disclaimer."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "Jurisdiction: Vietnam (Socialist Republic of Vietnam)",
            "",
            "## Legal Domain Coverage",
        ]
        domain_names = {
            "corporate": "Corporate Law (Enterprise Law, Investment Law)",
            "finance": "Finance & Banking (State Bank, Securities, Insurance)",
            "disputes": "Dispute Resolution (Courts, Arbitration, Enforcement)",
            "regulatory": "Regulatory Compliance (Licensing, Competition, Labor)",
            "ip_data": "IP & Data Protection (NOIP, PDPD, Cybersecurity)",
            "esg": "ESG (Environmental, Social, Governance)",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                findings_count = data.get("findings_count", 0)
                lines.append(f"- **Findings**: {findings_count}")
                if data.get("findings"):
                    lines.append("- **Key Issues**:")
                    for finding in data["findings"]:
                        lines.append(
                            f"  - {finding['concept']}: {finding['application']} (Risk: {finding['risk']})"
                        )
                if "principles" in data:
                    lines.append(f"- **Legal Principles**: {', '.join(data['principles'][:3])}...")
        lines.extend([
            "",
            "## Vietnam Legal Framework",
            "- **Civil Law System**: Based on French civil law tradition",
            "- **Key Codes**: Civil Code 2015, Criminal Code 2015, Labor Code 2019",
            "- **Courts**: People's Courts (4-tier system)",
            "- **Arbitration**: VIAC (Vietnam International Arbitration Centre)",
            "- **Foreign Investment**: Law on Investment 2020, Law on Enterprises 2020",
            "- **Data Protection**: PDPD (Personal Data Protection Decree) 2023",
            "",
            "## Critical Safety Disclaimer",
            "⚠️ **THIS IS INFORMATIONAL ONLY - NOT LEGAL ADVICE**",
            "",
            "- Analysis is for educational and preliminary guidance purposes",
            "- Vietnamese law changes frequently - verify with current regulations",
            "- Always consult licensed Vietnamese attorneys for specific matters",
            "- Government procedures vary by province and interpretation",
            "- This engine does not establish attorney-client relationship",
            "- Not suitable for emergency legal situations",
            "",
            "## 24-Dimensional Legal Analysis Axes",
            "1. Matter Type (advisory/transactional/contentious/regulatory)",
            "2. Jurisdiction Scope (local/cross-border/global)",
            "3. Client Type (individual/SME/corporate/state)",
            "4. Industry Context (tech/finance/energy/healthcare)",
            "5. Risk Level (low/moderate/high/critical)",
            "6. Materiality (under 1m / 1-10m / 10-100m / over 100m)",
            "7. Time Pressure (normal/expedited/urgent/emergency)",
            "8. Regulatory Intensity (light/medium/heavy/special)",
            "9. Dispute Stage (pre-dispute/filed/trial/appeal/enforcement)",
            "10. Contract Stage (structuring/drafting/negotiation/signing)",
            "11. Evidence State (incomplete/partial/strong/forensic)",
            "12. Counterparty Profile (cooperative/neutral/aggressive)",
            "13. Document Type (MOU/term sheet/main agreement/policy)",
            "14. Enforcement Forum (court/arbitration/mediator/regulator)",
            "15. Standard Level (local/regional/global/internal)",
            "16. Legal Function Role (external/in-house/regulator/board)",
            "17. Time Horizon (short/medium/long/legacy)",
            "18. Outcome Priority (risk/speed/value/relationship)",
            "19. Evidence Risk Tolerance",
            "20. Documentation Style (lean/standard/comprehensive)",
            "21. Discovery/Disclosure Exposure",
            "22. Public Sensitivity",
            "23. Governance Layer (ops/management/board/regulator)",
            "24. Output Mode (memo/opinion/markup/playbook)",
        ])
        return "\n".join(lines)


# Singleton instance
_vn_legal_engine: Optional[VNLegalEngine] = None


def get_vn_legal_engine() -> VNLegalEngine:
    """Get or create the VN Legal Engine singleton."""
    global _vn_legal_engine
    if _vn_legal_engine is None:
        _vn_legal_engine = VNLegalEngine()
    return _vn_legal_engine
