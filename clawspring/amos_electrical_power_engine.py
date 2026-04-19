"""AMOS Electrical Power Engine - Power systems and energy infrastructure."""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PowerDomain(Enum):
    """Electrical power domain classifications."""
    GENERATION = "generation"
    TRANSMISSION = "transmission"
    DISTRIBUTION = "distribution"
    POWER_ELECTRONICS = "power_electronics"
    PROTECTION = "protection"
    MARKETS = "markets"


@dataclass
class PowerComponent:
    """Power system component representation."""

    name: str
    component_type: str
    domain: PowerDomain
    parameters: dict = field(default_factory=dict)


class PowerSystemsKernel:
    """Kernel for power system analysis (gen, trans, dist)."""

    def __init__(self):
        self.components: Dict[str, PowerComponent] = {}
        self.buses: List[dict] = []
        self.lines: List[dict] = []

    def add_bus(self, name: str, voltage_kv: float, bus_type: str = "PQ") -> dict:
        bus = {
            "name": name,
            "voltage_kv": voltage_kv,
            "type": bus_type,
            "connected_components": [],
        }
        self.buses.append(bus)
        return bus

    def add_line(
        self, name: str, from_bus: str, to_bus: str,
        resistance_ohm: float, reactance_ohm: float
    ) -> dict:
        line = {
            "name": name,
            "from_bus": from_bus,
            "to_bus": to_bus,
            "R": resistance_ohm,
            "X": reactance_ohm,
            "Z": math.sqrt(resistance_ohm**2 + reactance_ohm**2),
        }
        self.lines.append(line)
        return line

    def add_transformer(
        self, name: str, primary_kv: float, secondary_kv: float, rating_mva: float
    ) -> PowerComponent:
        transformer = PowerComponent(
            name=name,
            component_type="transformer",
            domain=PowerDomain.TRANSMISSION,
            parameters={
                "primary_kv": primary_kv,
                "secondary_kv": secondary_kv,
                "rating_mva": rating_mva,
                "turns_ratio": primary_kv / secondary_kv,
            },
        )
        self.components[name] = transformer
        return transformer

    def add_generator(
        self, name: str, gen_type: str, capacity_mw: float, voltage_kv: float
    ) -> PowerComponent:
        generator = PowerComponent(
            name=name,
            component_type=f"generator_{gen_type}",
            domain=PowerDomain.GENERATION,
            parameters={
                "capacity_mw": capacity_mw,
                "voltage_kv": voltage_kv,
                "type": gen_type,
            },
        )
        self.components[name] = generator
        return generator

    def calculate_power_flow(self, voltage_kv: float, current_a: float, pf: float = 0.9) -> dict:
        apparent_power_mva = (voltage_kv * current_a * math.sqrt(3)) / 1000
        active_power_mw = apparent_power_mva * pf
        reactive_power_mvar = apparent_power_mva * math.sin(math.acos(pf))
        return {
            "voltage_kv": voltage_kv,
            "current_a": current_a,
            "power_factor": pf,
            "apparent_power_mva": apparent_power_mva,
            "active_power_mw": active_power_mw,
            "reactive_power_mvar": reactive_power_mvar,
        }

    def get_principles(self) -> List[str]:
        return [
            "Ohm's and Kirchhoff's laws",
            "Per-unit system for analysis",
            "Phasor representation",
            "Load flow and power balance",
        ]


class PowerElectronicsKernel:
    """Kernel for power electronics and converters."""

    def __init__(self):
        self.converters: List[dict] = []
        self.ev_chargers: List[dict] = []

    def add_converter(
        self, name: str, converter_type: str,
        input_voltage: float, output_voltage: float, efficiency: float = 0.95
    ) -> dict:
        converter = {
            "name": name,
            "type": converter_type,
            "input_v": input_voltage,
            "output_v": output_voltage,
            "efficiency": efficiency,
        }
        self.converters.append(converter)
        return converter

    def add_ev_charger(self, name: str, charger_type: str, power_kw: float, connector: str) -> dict:
        charger = {
            "name": name,
            "type": charger_type,
            "power_kw": power_kw,
            "connector": connector,
        }
        self.ev_chargers.append(charger)
        return charger

    def analyze_inverter(self, dc_voltage: float, ac_voltage: float, power_kw: float) -> dict:
        current_dc = (power_kw * 1000) / dc_voltage
        current_ac = (power_kw * 1000) / (ac_voltage * math.sqrt(3))
        return {
            "dc_voltage": dc_voltage,
            "ac_voltage": ac_voltage,
            "power_kw": power_kw,
            "dc_current_a": current_dc,
            "ac_current_a": current_ac,
            "conversion": "DC to AC",
        }

    def get_principles(self) -> List[str]:
        return [
            "DC-AC and AC-DC conversion",
            "PWM and switching principles",
            "Inverter topologies",
            "EV charging standards",
        ]


class ProtectionReliabilityKernel:
    """Kernel for protection systems and reliability."""

    def __init__(self):
        self.relays: List[dict] = []
        self.faults: List[dict] = []

    def add_relay(self, name: str, relay_type: str, setting_a: float, time_delay_s: float) -> dict:
        relay = {
            "name": name,
            "type": relay_type,
            "setting_a": setting_a,
            "time_delay_s": time_delay_s,
        }
        self.relays.append(relay)
        return relay

    def analyze_fault(self, fault_type: str, fault_impedance_ohm: float, system_voltage_kv: float) -> dict:
        voltage_v = system_voltage_kv * 1000 / math.sqrt(3)
        fault_current_a = voltage_v / fault_impedance_ohm if fault_impedance_ohm > 0 else float('inf')
        return {
            "fault_type": fault_type,
            "fault_impedance_ohm": fault_impedance_ohm,
            "system_voltage_kv": system_voltage_kv,
            "fault_current_a": fault_current_a,
            "severity": "high" if fault_current_a > 10000 else "medium",
        }

    def get_principles(self) -> List[str]:
        return [
            "Overcurrent protection",
            "Differential protection",
            "Fault analysis",
            "Reliability indices",
        ]


class MarketsPolicyKernel:
    """Kernel for electricity markets and policy."""

    def __init__(self):
        self.market_zones: List[dict] = []
        self.tariffs: List[dict] = []

    def add_market_zone(self, name: str, zone_type: str, capacity_mw: float) -> dict:
        zone = {
            "name": name,
            "type": zone_type,
            "capacity_mw": capacity_mw,
        }
        self.market_zones.append(zone)
        return zone

    def add_tariff(self, name: str, consumer_type: str, energy_price: float, demand_charge: float) -> dict:
        tariff = {
            "name": name,
            "consumer_type": consumer_type,
            "energy_price_per_kwh": energy_price,
            "demand_charge_per_kw": demand_charge,
        }
        self.tariffs.append(tariff)
        return tariff

    def calculate_energy_cost(self, consumption_kwh: float, peak_demand_kw: float, tariff_name: str) -> dict:
        tariff = next((t for t in self.tariffs if t["name"] == tariff_name), None)
        if not tariff:
            return {"error": f"Tariff {tariff_name} not found"}
        energy_cost = consumption_kwh * tariff["energy_price_per_kwh"]
        demand_cost = peak_demand_kw * tariff["demand_charge_per_kw"]
        return {
            "consumption_kwh": consumption_kwh,
            "peak_demand_kw": peak_demand_kw,
            "energy_cost": energy_cost,
            "demand_cost": demand_cost,
            "total_cost": energy_cost + demand_cost,
        }

    def get_principles(self) -> List[str]:
        return [
            "Market structure and operation",
            "Tariff design principles",
            "Grid codes and standards",
            "Regulatory frameworks",
        ]


class ElectricalPowerEngine:
    """AMOS Electrical Power Engine - Power systems and grids."""

    VERSION = "vInfinity_MAX"
    NAME = "AMOS_Electrical_Power_OMEGA"

    def __init__(self):
        self.power_systems_kernel = PowerSystemsKernel()
        self.power_electronics_kernel = PowerElectronicsKernel()
        self.protection_kernel = ProtectionReliabilityKernel()
        self.markets_kernel = MarketsPolicyKernel()

    def analyze(
        self, description: str, domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run electrical power analysis across specified domains."""
        domains = domains or [
            "power_systems", "power_electronics", "protection", "markets"
        ]
        results: Dict[str, Any] = {}
        if "power_systems" in domains:
            results["power_systems"] = self._analyze_power_systems(description)
        if "power_electronics" in domains:
            results["power_electronics"] = self._analyze_power_electronics(description)
        if "protection" in domains:
            results["protection"] = self._analyze_protection(description)
        if "markets" in domains:
            results["markets"] = self._analyze_markets(description)
        return results

    def _analyze_power_systems(self, description: str) -> dict:
        return {
            "query": description[:100],
            "buses": len(self.power_systems_kernel.buses),
            "lines": len(self.power_systems_kernel.lines),
            "components": len(self.power_systems_kernel.components),
            "principles": self.power_systems_kernel.get_principles(),
        }

    def _analyze_power_electronics(self, description: str) -> dict:
        return {
            "query": description[:100],
            "converters": len(self.power_electronics_kernel.converters),
            "ev_chargers": len(self.power_electronics_kernel.ev_chargers),
            "principles": self.power_electronics_kernel.get_principles(),
        }

    def _analyze_protection(self, description: str) -> dict:
        return {
            "query": description[:100],
            "relays": len(self.protection_kernel.relays),
            "faults_analyzed": len(self.protection_kernel.faults),
            "principles": self.protection_kernel.get_principles(),
        }

    def _analyze_markets(self, description: str) -> dict:
        return {
            "query": description[:100],
            "market_zones": len(self.markets_kernel.market_zones),
            "tariffs": len(self.markets_kernel.tariffs),
            "principles": self.markets_kernel.get_principles(),
        }

    def get_findings_summary(self, results: dict) -> str:
        """Generate findings summary with gap acknowledgment."""
        lines = [
            f"# {self.NAME} {self.VERSION}",
            "",
            "Creator: Trang Phan | System: AMOS vInfinity",
            "",
            "## Domain Coverage",
        ]
        domain_names = {
            "power_systems": "Power Systems (Gen/Trans/Dist)",
            "power_electronics": "Power Electronics & Conversion",
            "protection": "Protection & Reliability",
            "markets": "Markets, Regulation & Policy",
        }
        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(["", f"### {display_name}"])
            if isinstance(data, dict):
                for key, value in data.items():
                    if key != "principles" and key != "query":
                        lines.append(f"- **{key}**: {value}")
                if "principles" in data:
                    lines.append(f"- **Principles**: {', '.join(data['principles'][:2])}...")
        lines.extend([
            "",
            "## Gaps and Limitations",
            "- Real-time grid data not available",
            "- Country-specific regulations require manual lookup",
            "- Dynamic stability analysis simplified",
            "- Protection coordination requires specialist review",
            "",
            "## Safety Disclaimer",
            "NO safety-critical decisions without qualified engineer review. "
            "All calculations are conceptual and require validation.",
        ])
        return "\n".join(lines)


# Singleton instance
_electrical_power_engine: Optional[ElectricalPowerEngine] = None


def get_electrical_power_engine() -> ElectricalPowerEngine:
    """Get or create the Electrical Power Engine singleton."""
    global _electrical_power_engine
    if _electrical_power_engine is None:
        _electrical_power_engine = ElectricalPowerEngine()
    return _electrical_power_engine
