"""AMOSL Compiler.

Compiles AMOSL AST to the 4 IRs (CIR, QIR, BIR, HIR).
"""

from .ast_nodes import (
    BioEntityDecl,
    DynamicsDecl,
    EntityDecl,
    HybridEntityDecl,
    OntologyDecl,
    Program,
    QuantumEntityDecl,
    StateDecl,
)
from .ir import (
    BIR,
    CIR,
    HIR,
    QIR,
    BIRReaction,
    BIRSequence,
    BIRSpecies,
    CIRBlock,
    CIROp,
    HIRBridge,
    HIRSchedule,
    QIRGate,
    QIRRegister,
)


class CompileError(Exception):
    """Compilation error."""

    pass


class IRGenerator:
    """Generate IR from AST nodes."""

    def __init__(self):
        self.cir = CIR()
        self.qir = QIR()
        self.bir = BIR()
        self.hir = HIR()
        self.symbol_table: dict[str, str] = {}

    def generate(self, program: Program) -> tuple[CIR, QIR, BIR, HIR]:
        """Generate all IRs from program."""
        self.process_ontology(program.ontology)
        self.process_state(program.state)
        self.process_dynamics(program.dynamics)
        return self.cir, self.qir, self.bir, self.hir

    def process_ontology(self, ontology: OntologyDecl) -> None:
        """Process ontology declarations."""
        # Classical entities -> CIR blocks
        for entity in ontology.classical:
            self.process_classical_entity(entity)

        # Quantum entities -> QIR registers
        for entity in ontology.quantum:
            self.process_quantum_entity(entity)

        # Bio entities -> BIR species
        for entity in ontology.biological:
            self.process_bio_entity(entity)

        # Hybrid entities -> HIR bridges
        for entity in ontology.hybrid:
            self.process_hybrid_entity(entity)

    def process_classical_entity(self, entity: EntityDecl) -> None:
        """Process classical entity."""
        block = CIRBlock(name=f"entity_{entity.name}")

        # Add field initializations as operations
        for field in entity.fields:
            block.ops.append(CIROp(opcode="declare", operands=[field.name], result=field.type_name))

        self.cir.blocks.append(block)
        self.symbol_table[entity.name] = "classical"

    def process_quantum_entity(self, entity: QuantumEntityDecl) -> None:
        """Process quantum entity."""
        reg = QIRRegister(name=entity.name, size=entity.qubits, initial_state="|0⟩")
        self.qir.registers.append(reg)

        # Add default gates if circuit defined
        if entity.circuit:
            for gate_name in entity.circuit.gates:
                self.qir.gates.append(QIRGate(name=gate_name, targets=list(range(entity.qubits))))

        self.symbol_table[entity.name] = "quantum"

    def process_bio_entity(self, entity: BioEntityDecl) -> None:
        """Process biological entity."""
        species = BIRSpecies(name=entity.name, type_name=entity.protein or "gene")
        self.bir.species.append(species)

        # Add sequence if DNA/RNA defined
        if entity.dna:
            self.bir.sequences.append(
                BIRSequence(name=f"{entity.name}_dna", seq_type="dna", sequence=entity.dna)
            )

        self.symbol_table[entity.name] = "biological"

    def process_hybrid_entity(self, entity: HybridEntityDecl) -> None:
        """Process hybrid entity."""
        # Create bridges for each bridge definition
        for bridge_def in entity.bridges:
            bridge = HIRBridge(
                name=f"{entity.name}_{bridge_def.name}",
                source_substrate=self.symbol_table.get(bridge_def.source, "unknown"),
                target_substrate=self.symbol_table.get(bridge_def.target, "unknown"),
                source_var=bridge_def.source,
                target_var=bridge_def.target,
                transform=bridge_def.signal,
            )
            self.hir.bridges.append(bridge)

        self.symbol_table[entity.name] = "hybrid"

    def process_state(self, state: StateDecl) -> None:
        """Process state declarations."""
        # Classical state -> CIR declarations
        for var in state.classical:
            self.cir.blocks.append(
                CIRBlock(
                    name=f"state_{var.name}",
                    ops=[CIROp(opcode="init", operands=[var.type_name], result=var.name)],
                )
            )

        # Quantum state -> QIR registers
        for var in state.quantum:
            self.qir.registers.append(
                QIRRegister(
                    name=var.name,
                    size=1,
                    initial_state=var.amplitude.text if var.amplitude else "|0⟩",
                )
            )

        # Bio state -> BIR species
        for var in state.biological:
            self.bir.species.append(
                BIRSpecies(
                    name=var.name, initial_conc=var.concentration.text if var.concentration else 0.0
                )
            )

        # Hybrid state -> HIR bridges
        for var in state.hybrid:
            self.hir.bridges.append(
                HIRBridge(name=var.name, source_var=var.source, target_var=var.target)
            )

    def process_dynamics(self, dynamics: DynamicsDecl) -> None:
        """Process dynamics declarations."""
        # Actions -> CIR operations
        for action in dynamics.actions:
            block = CIRBlock(name=f"action_{action.name}")

            if action.pre:
                block.guard.condition = action.pre.text

            block.ops.append(CIROp(opcode="action", operands=[action.name], result="void"))

            self.cir.blocks.append(block)

        # Transitions -> CIR guards
        for trans in dynamics.transitions:
            self.cir.blocks.append(
                CIRBlock(
                    name=f"trans_{trans.from_state}_to_{trans.to_state}",
                    guard=CIRGuard(
                        condition=trans.condition.text if trans.condition else "true",
                        target=trans.to_state,
                    ),
                )
            )

        # Evolutions -> BIR reactions or HIR schedules
        for evo in dynamics.evolutions:
            if evo.rule == "mutate":
                # Biological evolution
                self.bir.reactions.append(
                    BIRReaction(reactants=[evo.target], products=[f"{evo.target}_mutated"])
                )
            else:
                # General evolution schedule
                self.hir.schedules.append(
                    HIRSchedule(name=f"evolve_{evo.target}", order=[evo.rule])
                )


def compile_program(program: Program) -> tuple[CIR, QIR, BIR, HIR]:
    """Compile AMOSL program to 4 IRs.

    Returns (CIR, QIR, BIR, HIR) tuple.
    """
    generator = IRGenerator()
    return generator.generate(program)
