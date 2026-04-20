"""AMOS Biology & Cognition Engine - Biological and neurological systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BiologicalLevel(Enum):
    """Biological organization levels."""

    MOLECULAR = "molecular"
    CELLULAR = "cellular"
    TISSUE = "tissue"
    ORGAN = "organ"
    SYSTEM = "system"
    ORGANISM = "organism"


@dataclass
class BiologicalEntity:
    """Biological entity representation."""

    name: str
    entity_type: str
    level: BiologicalLevel
    properties: dict[str, Any] = field(default_factory=dict)


class MolecularGeneticKernel:
    """Kernel for molecular and genetic biology."""

    ENTITIES = [
        "DNA",
        "RNA",
        "Proteins",
        "Lipids",
        "Carbohydrates",
        "Ions",
        "Signalling_Molecules",
        "Hormones",
        "Neurotransmitters",
    ]

    MECHANISMS = [
        "Gene_Expression",
        "Epigenetic_Modification",
        "Transcription",
        "Translation",
        "Protein_Folding",
        "Post_Translational_Modification",
        "DNA_Repair",
        "Cell_Cycle_Regulation",
    ]

    def __init__(self):
        self.entities: dict[str, BiologicalEntity] = {}
        self.pathways: list[dict] = []

    def define_entity(
        self,
        name: str,
        entity_type: str,
        **properties,
    ) -> BiologicalEntity:
        """Define a molecular entity."""
        entity = BiologicalEntity(
            name=name,
            entity_type=entity_type,
            level=BiologicalLevel.MOLECULAR,
            properties=properties,
        )
        self.entities[name] = entity
        return entity

    def add_pathway(
        self,
        name: str,
        steps: list[str],
        inputs: list[str],
        outputs: list[str],
    ) -> dict:
        """Add a biological pathway."""
        pathway = {
            "name": name,
            "steps": steps,
            "inputs": inputs,
            "outputs": outputs,
        }
        self.pathways.append(pathway)
        return pathway

    def analyze_gene_expression(self, gene_name: str) -> dict:
        """Analyze gene expression patterns."""
        return {
            "gene": gene_name,
            "transcription": "DNA → mRNA",
            "translation": "mRNA → Protein",
            "regulation": "Transcription factors, epigenetic marks",
            "note": "Conceptual analysis only - not wet lab",
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Central dogma: DNA → RNA → Protein",
            "Gene expression regulation",
            "Epigenetic modifications",
            "Signal transduction cascades",
        ]


class CellularTissueKernel:
    """Kernel for cellular and tissue biology."""

    CELL_TYPES = [
        "Neurons",
        "Astrocytes",
        "Oligodendrocytes",
        "Microglia",
        "Muscle_Cells",
        "Endocrine_Cells",
        "Immune_Cells",
    ]

    PROCESSES = [
        "Membrane_Potential_Dynamics",
        "Ion_Channel_Regulation",
        "Synaptic_Transmission",
        "Myelination",
        "Neuroinflammation",
        "Metabolic_Support",
        "Cellular_Stress_Response",
    ]

    def __init__(self):
        self.cells: dict[str, BiologicalEntity] = {}
        self.tissues: list[dict] = []

    def define_cell(
        self,
        name: str,
        cell_type: str,
        **properties,
    ) -> BiologicalEntity:
        """Define a cell type."""
        cell = BiologicalEntity(
            name=name,
            entity_type=cell_type,
            level=BiologicalLevel.CELLULAR,
            properties=properties,
        )
        self.cells[name] = cell
        return cell

    def define_tissue(
        self,
        name: str,
        tissue_type: str,
        cell_types: list[str],
    ) -> dict:
        """Define a tissue."""
        tissue = {
            "name": name,
            "type": tissue_type,
            "cell_types": cell_types,
        }
        self.tissues.append(tissue)
        return tissue

    def analyze_neural_transmission(self) -> dict:
        """Analyze neural transmission."""
        return {
            "mechanism": "Action potential → Neurotransmitter release",
            "synapse_types": ["Excitatory", "Inhibitory", "Modulatory"],
            "key_neurotransmitters": ["Glutamate", "GABA", "Dopamine", "Serotonin"],
            "note": "Simplified conceptual model",
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Cell structure and function",
            "Membrane transport and signaling",
            "Synaptic transmission basics",
            "Tissue organization",
        ]


class OrganSystemKernel:
    """Kernel for organ and system-level biology."""

    ORGANS = [
        "Brain",
        "Spinal_Cord",
        "Heart",
        "Lungs",
        "Liver",
        "Kidneys",
        "Gut",
        "Endocrine_Glands",
        "Skin",
    ]

    BRAIN_SUBSYSTEMS = [
        "Cortex",
        "Hippocampus",
        "Amygdala",
        "Basal_Ganglia",
        "Thalamus",
        "Hypothalamus",
        "Cerebellum",
        "Brainstem",
    ]

    def __init__(self):
        self.organs: dict[str, BiologicalEntity] = {}
        self.systems: list[dict] = []

    def define_organ(
        self,
        name: str,
        organ_type: str,
        **properties,
    ) -> BiologicalEntity:
        """Define an organ."""
        organ = BiologicalEntity(
            name=name,
            entity_type=organ_type,
            level=BiologicalLevel.ORGAN,
            properties=properties,
        )
        self.organs[name] = organ
        return organ

    def define_system(
        self,
        name: str,
        organs: list[str],
        function: str,
    ) -> dict:
        """Define a biological system."""
        system = {
            "name": name,
            "organs": organs,
            "function": function,
        }
        self.systems.append(system)
        return system

    def analyze_brain_function(self, region: str) -> dict:
        """Analyze brain region function."""
        functions = {
            "Cortex": "Higher cognition, sensory processing",
            "Hippocampus": "Memory formation, spatial navigation",
            "Amygdala": "Emotion processing, fear response",
            "Basal_Ganglia": "Motor control, habit formation",
            "Thalamus": "Sensory relay, consciousness",
            "Hypothalamus": "Homeostasis, hormone regulation",
            "Cerebellum": "Motor coordination, timing",
            "Brainstem": "Vital functions, arousal",
        }
        return {
            "region": region,
            "function": functions.get(region, "Unknown"),
            "note": "Oversimplified functional mapping",
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Organ structure and function",
            "System integration",
            "Brain functional anatomy",
            "Homeostatic regulation",
        ]


class CognitionBehaviorKernel:
    """Kernel for cognition and behavior analysis."""

    def __init__(self):
        self.cognitive_processes: list[dict] = []
        self.behaviors: list[dict] = []

    def define_cognitive_process(
        self,
        name: str,
        process_type: str,
        brain_regions: list[str],
    ) -> dict:
        """Define a cognitive process."""
        process = {
            "name": name,
            "type": process_type,
            "brain_regions": brain_regions,
        }
        self.cognitive_processes.append(process)
        return process

    def define_behavior(
        self,
        name: str,
        behavior_type: str,
        triggers: list[str],
    ) -> dict:
        """Define a behavior pattern."""
        behavior = {
            "name": name,
            "type": behavior_type,
            "triggers": triggers,
        }
        self.behaviors.append(behavior)
        return behavior

    def analyze_learning(self, learning_type: str) -> dict:
        """Analyze learning mechanisms."""
        types = {
            "declarative": "Explicit memory, facts and events",
            "procedural": "Skill learning, habits",
            "associative": "Classical/operant conditioning",
            "observational": "Social learning, imitation",
        }
        return {
            "type": learning_type,
            "mechanism": types.get(learning_type, "Unknown"),
            "brain_regions": ["Hippocampus", "Cortex", "Basal_Ganglia"],
            "note": "Learning requires plasticity at synapses",
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Neural basis of cognition",
            "Learning and plasticity",
            "Behavioral neuroscience",
            "Cognitive architecture",
        ]


class PathologyRecoveryKernel:
    """Kernel for pathology and recovery analysis."""

    def __init__(self):
        self.pathologies: list[dict] = []
        self.recovery_processes: list[dict] = []

    def define_pathology(
        self,
        name: str,
        pathology_type: str,
        affected_systems: list[str],
    ) -> dict:
        """Define a pathology."""
        pathology = {
            "name": name,
            "type": pathology_type,
            "affected_systems": affected_systems,
        }
        self.pathologies.append(pathology)
        return pathology

    def analyze_recovery(
        self,
        condition: str,
        recovery_type: str,
    ) -> dict:
        """Analyze recovery mechanisms."""
        return {
            "condition": condition,
            "recovery_type": recovery_type,
            "mechanisms": [
                "Neural plasticity",
                "Compensatory strategies",
                "Cellular repair",
            ],
            "note": "Recovery analysis - not medical advice",
        }

    def _get_principles(self) -> list[str]:
        """Return kernel principles."""
        return [
            "Pathology mechanisms",
            "Recovery and adaptation",
            "Neuroplasticity",
            "NOT medical advice - informational only",
        ]


class BiologyCognitionEngine:
    """AMOS Biology & Cognition Engine - Unified biological analysis."""

    VERSION = "vInfinity_MAX"
    NAME = "Biology_and_Cognition_OMEGA"

    def __init__(self):
        self.molecular_kernel = MolecularGeneticKernel()
        self.cellular_kernel = CellularTissueKernel()
        self.organ_kernel = OrganSystemKernel()
        self.cognition_kernel = CognitionBehaviorKernel()
        self.pathology_kernel = PathologyRecoveryKernel()

    def analyze(
        self,
        description: str,
        domains: list[str | None] = None,
    ) -> dict[str, Any]:
        """Run biology/cognition analysis across specified domains."""
        domains = domains or ["molecular", "cellular", "organ", "cognition", "pathology"]
        results: dict[str, Any] = {}

        if "molecular" in domains:
            results["molecular"] = self._analyze_molecular(description)

        if "cellular" in domains:
            results["cellular"] = self._analyze_cellular(description)

        if "organ" in domains:
            results["organ"] = self._analyze_organ(description)

        if "cognition" in domains:
            results["cognition"] = self._analyze_cognition(description)

        if "pathology" in domains:
            results["pathology"] = self._analyze_pathology(description)

        return results

    def _analyze_molecular(self, description: str) -> dict:
        """Analyze molecular aspects."""
        return {
            "query": description[:100],
            "entities_defined": len(self.molecular_kernel.entities),
            "pathways": len(self.molecular_kernel.pathways),
            "principles": self.molecular_kernel._get_principles(),
        }

    def _analyze_cellular(self, description: str) -> dict:
        """Analyze cellular aspects."""
        return {
            "query": description[:100],
            "cells_defined": len(self.cellular_kernel.cells),
            "tissues": len(self.cellular_kernel.tissues),
            "principles": self.cellular_kernel._get_principles(),
        }

    def _analyze_organ(self, description: str) -> dict:
        """Analyze organ aspects."""
        return {
            "query": description[:100],
            "organs_defined": len(self.organ_kernel.organs),
            "systems": len(self.organ_kernel.systems),
            "principles": self.organ_kernel._get_principles(),
        }

    def _analyze_cognition(self, description: str) -> dict:
        """Analyze cognition aspects."""
        return {
            "query": description[:100],
            "cognitive_processes": len(self.cognition_kernel.cognitive_processes),
            "behaviors": len(self.cognition_kernel.behaviors),
            "principles": self.cognition_kernel._get_principles(),
        }

    def _analyze_pathology(self, description: str) -> dict:
        """Analyze pathology aspects."""
        return {
            "query": description[:100],
            "pathologies": len(self.pathology_kernel.pathologies),
            "principles": self.pathology_kernel._get_principles(),
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
            "molecular": "Molecular & Genetic",
            "cellular": "Cellular & Tissue",
            "organ": "Organ & System",
            "cognition": "Cognition & Behavior",
            "pathology": "Pathology & Recovery",
        }

        for domain, data in results.items():
            display_name = domain_names.get(domain, domain.title())
            lines.extend(
                [
                    "",
                    f"### {display_name}",
                ]
            )
            if isinstance(data, dict):
                for key, value in data.items():
                    if key not in ["principles", "query"]:
                        lines.append(f"- {key}: {value}")

        lines.extend(
            [
                "",
                "## Safety & Compliance",
                "",
                "### Safety Constraints",
                "- NOT medical advice - informational only",
                "- NO diagnostic or treatment recommendations",
                "- NO medical decisions based on these outputs",
                "- ALWAYS consult qualified healthcare professionals",
                "",
                "### Global Law Compliance",
                "- L1 (Structural): Biological hierarchy preserved",
                "- L2 (Temporal): Development and aging considered",
                "- L3 (Semantic): Clear biological reasoning",
                "- L4 (Cognitive): Multi-level integration",
                "- L5 (Safety): No harmful medical guidance",
                "- L6 (Humility): GAP acknowledgment below",
                "",
                "## Gap Acknowledgment",
                "",
                "**CRITICAL GAP:** This is NOT a biological simulator. "
                "All outputs are CONCEPTUAL and SIMPLIFIED only.",
                "",
                "Specific Gaps:",
                "- No biochemical pathway simulation",
                "- No genetic sequence analysis",
                "- No clinical data processing",
                "- No medical imaging analysis",
                "- No wet lab experimental design",
                "- Pattern-based analysis only, not computational biology",
                "",
                "### Biology-First Modelling",
                "Nervous system anchored.",
                "Layered from molecule → organism.",
                "",
                "### Creator Attribution",
                "This engine was architected by Trang Phan as part of AMOS vInfinity.",
            ]
        )

        return "\n".join(lines)


# Singleton
_biology_cognition_engine: BiologyCognitionEngine | None = None


def get_biology_cognition_engine() -> BiologyCognitionEngine:
    """Get singleton biology/cognition engine instance."""
    global _biology_cognition_engine
    if _biology_cognition_engine is None:
        _biology_cognition_engine = BiologyCognitionEngine()
    return _biology_cognition_engine


if __name__ == "__main__":
    print("=" * 60)
    print("AMOS BIOLOGY & COGNITION ENGINE")
    print("=" * 60)
    print()

    engine = get_biology_cognition_engine()

    # Add sample biological entities
    engine.molecular_kernel.define_entity(
        "dopamine",
        "Neurotransmitter",
        synthesis="Tyrosine → L-DOPA → Dopamine",
        receptors=["D1", "D2", "D3", "D4", "D5"],
    )

    engine.cellular_kernel.define_cell(
        "pyramidal_neuron",
        "Neurons",
        location="Cortex",
        neurotransmitter="Glutamate",
    )

    engine.organ_kernel.define_organ(
        "brain",
        "Brain",
        weight="1.4kg",
        neurons="86 billion",
    )

    engine.cognition_kernel.define_cognitive_process(
        "working_memory",
        "Executive Function",
        brain_regions=["Prefrontal Cortex", "Parietal Cortex"],
    )

    # Run analysis
    results = engine.analyze(
        "Analyze biological and cognitive systems",
        domains=["molecular", "cellular", "organ", "cognition"],
    )

    # Print findings
    print(engine.get_findings_summary(results))

    print()
    print("=" * 60)
    print("Engine: OPERATIONAL")
    print("=" * 60)
    print("\nCapabilities:")
    print("  - Molecular & Genetic (DNA, RNA, proteins, pathways)")
    print("  - Cellular & Tissue (cell types, neural transmission)")
    print("  - Organ & System (brain regions, body systems)")
    print("  - Cognition & Behavior (learning, memory, processing)")
    print("  - Pathology & Recovery (disease, plasticity, healing)")
    print()
    print("Safety: NOT medical advice - informational only.")
