"""AMOSL Parser.

Parses AMOSL source code into AST.
Grammar based on 9-tuple: (O, S, D, C, E, M, U, V, A, R)
"""

from __future__ import annotations

from .ast_nodes import (
    ActionDecl,
    AdaptDecl,
    BioEntityDecl,
    BioState,
    ConstraintDecl,
    DynamicsDecl,
    EffectDecl,
    EntityDecl,
    Evolution,
    Expr,
    Field,
    HybridEntityDecl,
    HybridState,
    Location,
    MeasureDecl,
    OntologyDecl,
    Program,
    QuantumEntityDecl,
    QuantumState,
    RealizeDecl,
    StateDecl,
    StateVar,
    Transition,
    UncertaintyDecl,
    VerifyDecl,
)


class ParseError(Exception):
    """Parser error."""

    pass


class Token:
    """Lexer token."""

    def __init__(self, type_: str, value: str, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col


class Lexer:
    """Simple AMOSL lexer."""

    KEYWORDS = {
        "ontology",
        "state",
        "dynamics",
        "constraint",
        "effect",
        "measure",
        "uncertainty",
        "verify",
        "adapt",
        "realize",
        "classical",
        "quantum",
        "biological",
        "hybrid",
        "entity",
        "qubit",
        "gene",
        "protein",
        "bridge",
        "action",
        "transition",
        "evolve",
        "invariant",
        "true",
        "false",
        "unknown",
        "probable",
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []

    def error(self, msg: str) -> None:
        raise ParseError(f"Line {self.line}, Col {self.col}: {msg}")

    def advance(self) -> None:
        if self.pos < len(self.source) and self.source[self.pos] == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.pos += 1

    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.source):
            return "\0"
        return self.source[pos]

    def skip_whitespace(self) -> None:
        while self.peek() in " \t\r":
            self.advance()

    def skip_comment(self) -> None:
        if self.peek() == "/" and self.peek(1) == "/":
            while self.peek() not in "\n\0":
                self.advance()

    def read_string(self) -> str:
        quote = self.peek()
        self.advance()  # consume opening quote
        result = []
        while self.peek() not in "\n\0":
            if self.peek() == quote:
                self.advance()
                return "".join(result)
            if self.peek() == "\\":
                self.advance()
            result.append(self.peek())
            self.advance()
        self.error("Unterminated string")
        return ""  # unreachable

    def read_number(self) -> str:
        result = []
        while self.peek().isdigit() or self.peek() == ".":
            result.append(self.peek())
            self.advance()
        return "".join(result)

    def read_identifier(self) -> str:
        result = []
        while self.peek().isalnum() or self.peek() in "_-":
            result.append(self.peek())
            self.advance()
        return "".join(result)

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            self.skip_comment()

            if self.pos >= len(self.source):
                break

            char = self.peek()
            line, col = self.line, self.col

            # String
            if char in "\"'":
                self.tokens.append(Token("STRING", self.read_string(), line, col))
                continue

            # Number
            if char.isdigit():
                self.tokens.append(Token("NUMBER", self.read_number(), line, col))
                continue

            # Identifier or keyword
            if char.isalpha() or char == "_":
                ident = self.read_identifier()
                token_type = ident.upper() if ident in self.KEYWORDS else "IDENT"
                self.tokens.append(Token(token_type, ident, line, col))
                continue

            # Single-character tokens
            self.advance()
            if char in "{}[]()" or char in ":;,.":
                self.tokens.append(Token(char, char, line, col))
            elif char in "=+-*/<>!":
                # Check for two-character operators
                if self.peek() == "=":
                    self.advance()
                    self.tokens.append(Token(char + "=", char + "=", line, col))
                else:
                    self.tokens.append(Token(char, char, line, col))
            elif char == "\n":
                pass  # skip newlines
            elif char == "\0":
                break

        self.tokens.append(Token("EOF", "", self.line, self.col))
        return self.tokens


class Parser:
    """AMOSL recursive descent parser."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 0) -> Token:
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]

    def advance(self) -> Token:
        token = self.current()
        self.pos += 1
        return token

    def expect(self, type_: str) -> Token:
        if self.current().type != type_:
            raise ParseError(
                f"Expected {type_}, got {self.current().type} at line {self.current().line}"
            )
        return self.advance()

    def match(self, *types: str) -> bool:
        return self.current().type in types

    def location(self) -> Location:
        """Get current location."""
        tok = self.current()
        return Location(tok.line, tok.col)

    def parse(self) -> Program:
        """Parse full program."""
        ontology = OntologyDecl()
        state = StateDecl()
        dynamics = DynamicsDecl()
        constraints = []
        effects = []
        measures = []
        uncertainties = []
        verifies = []
        adapts = []
        realizes = RealizeDecl()

        while not self.match("EOF"):
            if self.match("ONTOLOGY"):
                ontology = self.parse_ontology()
            elif self.match("STATE"):
                state = self.parse_state()
            elif self.match("DYNAMICS"):
                dynamics = self.parse_dynamics()
            elif self.match("CONSTRAINT"):
                constraints.append(self.parse_constraint())
            elif self.match("EFFECT"):
                effects.append(self.parse_effect())
            elif self.match("MEASURE"):
                measures.append(self.parse_measure())
            elif self.match("UNCERTAINTY"):
                uncertainties.append(self.parse_uncertainty())
            elif self.match("VERIFY"):
                verifies.append(self.parse_verify())
            elif self.match("ADAPT"):
                adapts.append(self.parse_adapt())
            elif self.match("REALIZE"):
                realizes = self.parse_realize()
            else:
                self.advance()  # skip unknown

        return Program(
            ontology=ontology,
            state=state,
            dynamics=dynamics,
            constraints=constraints,
            effects=effects,
            measures=measures,
            uncertainties=uncertainties,
            verifies=verifies,
            adapts=adapts,
            realizes=realizes,
        )

    def parse_ontology(self) -> OntologyDecl:
        """Parse ontology declaration."""
        self.expect("ONTOLOGY")
        self.expect("{")

        decl = OntologyDecl()

        while not self.match("}"):
            if self.match("CLASSICAL"):
                decl.classical = self.parse_classical_entities()
            elif self.match("QUANTUM"):
                decl.quantum = self.parse_quantum_entities()
            elif self.match("BIOLOGICAL"):
                decl.biological = self.parse_bio_entities()
            elif self.match("HYBRID"):
                decl.hybrid = self.parse_hybrid_entities()
            else:
                self.advance()

        self.expect("}")
        return decl

    def parse_classical_entities(self) -> list[EntityDecl]:
        """Parse classical entity declarations."""
        self.expect("CLASSICAL")
        self.expect("{")
        entities = []

        while not self.match("}"):
            if self.match("ENTITY"):
                self.advance()
                name = self.expect("IDENT").value
                entity = EntityDecl(name=name, loc=self.location())

                if self.match("{"):
                    self.advance()
                    while not self.match("}"):
                        if self.match("IDENT"):
                            field_name = self.advance().value
                            self.expect(":")
                            field_type = self.expect("IDENT").value
                            entity.fields.append(Field(field_name, field_type, loc=self.location()))
                        else:
                            self.advance()
                    self.expect("}")

                entities.append(entity)
            else:
                self.advance()

        self.expect("}")
        return entities

    def parse_quantum_entities(self) -> list[QuantumEntityDecl]:
        """Parse quantum entity declarations."""
        self.expect("QUANTUM")
        self.expect("{")
        entities = []

        while not self.match("}"):
            if self.match("QUBIT"):
                self.advance()
                name = self.expect("IDENT").value
                size = 1
                if self.match("["):
                    self.advance()
                    size = int(self.expect("NUMBER").value)
                    self.expect("]")
                entities.append(QuantumEntityDecl(name, size, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return entities

    def parse_bio_entities(self) -> list[BioEntityDecl]:
        """Parse biological entity declarations."""
        self.expect("BIOLOGICAL")
        self.expect("{")
        entities = []

        while not self.match("}"):
            if self.match("GENE", "PROTEIN"):
                token = self.advance()
                name = self.expect("IDENT").value
                entities.append(
                    BioEntityDecl(name, type_name=token.value.lower(), loc=self.location())
                )
            else:
                self.advance()

        self.expect("}")
        return entities

    def parse_hybrid_entities(self) -> list[HybridEntityDecl]:
        """Parse hybrid entity declarations."""
        self.expect("HYBRID")
        self.expect("{")
        entities = []

        while not self.match("}"):
            if self.match("BRIDGE"):
                self.advance()
                name = self.expect("IDENT").value
                entities.append(HybridEntityDecl(name, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return entities

    def parse_state(self) -> StateDecl:
        """Parse state declaration."""
        self.expect("STATE")
        self.expect("{")

        decl = StateDecl()

        while not self.match("}"):
            if self.match("CLASSICAL"):
                decl.classical = self.parse_classical_state()
            elif self.match("QUANTUM"):
                decl.quantum = self.parse_quantum_state()
            elif self.match("BIOLOGICAL"):
                decl.biological = self.parse_bio_state()
            elif self.match("HYBRID"):
                decl.hybrid = self.parse_hybrid_state()
            else:
                self.advance()

        self.expect("}")
        return decl

    def parse_classical_state(self) -> list[StateVar]:
        """Parse classical state variables."""
        self.expect("CLASSICAL")
        self.expect("{")
        vars_list = []

        while not self.match("}"):
            if self.match("IDENT"):
                name = self.advance().value
                type_name = "Any"
                if self.match(":"):
                    self.advance()
                    type_name = self.expect("IDENT").value
                vars_list.append(StateVar(name, type_name, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return vars_list

    def parse_quantum_state(self) -> list[QuantumState]:
        """Parse quantum state variables."""
        self.expect("QUANTUM")
        self.expect("{")
        vars_list = []

        while not self.match("}"):
            if self.match("IDENT"):
                name = self.advance().value
                vars_list.append(QuantumState(name, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return vars_list

    def parse_bio_state(self) -> list[BioState]:
        """Parse biological state variables."""
        self.expect("BIOLOGICAL")
        self.expect("{")
        vars_list = []

        while not self.match("}"):
            if self.match("IDENT"):
                name = self.advance().value
                vars_list.append(BioState(name, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return vars_list

    def parse_hybrid_state(self) -> list[HybridState]:
        """Parse hybrid state variables."""
        self.expect("HYBRID")
        self.expect("{")
        vars_list = []

        while not self.match("}"):
            if self.match("IDENT"):
                name = self.advance().value
                vars_list.append(HybridState(name, loc=self.location()))
            else:
                self.advance()

        self.expect("}")
        return vars_list

    def parse_dynamics(self) -> DynamicsDecl:
        """Parse dynamics declaration."""
        self.expect("DYNAMICS")
        self.expect("{")

        decl = DynamicsDecl()

        while not self.match("}"):
            if self.match("ACTION"):
                decl.actions.append(self.parse_action())
            elif self.match("TRANSITION"):
                decl.transitions.append(self.parse_transition())
            elif self.match("EVOLVE"):
                decl.evolutions.append(self.parse_evolution())
            else:
                self.advance()

        self.expect("}")
        return decl

    def parse_action(self) -> ActionDecl:
        """Parse action declaration."""
        self.expect("ACTION")
        name = self.expect("IDENT").value
        self.expect("{")

        action = ActionDecl(name, loc=self.location())

        while not self.match("}"):
            if self.match("PRE"):
                self.advance()
                self.expect(":")
                action.pre = Expr(self.expect("IDENT").value)
            elif self.match("POST"):
                self.advance()
                self.expect(":")
                action.post = Expr(self.expect("IDENT").value)
            else:
                self.advance()

        self.expect("}")
        return action

    def parse_transition(self) -> Transition:
        """Parse transition."""
        self.expect("TRANSITION")
        from_state = self.expect("IDENT").value
        self.expect("->")
        to_state = self.expect("IDENT").value
        return Transition(from_state, to_state, loc=self.location())

    def parse_evolution(self) -> Evolution:
        """Parse evolution rule."""
        self.expect("EVOLVE")
        target = self.expect("IDENT").value
        return Evolution(target, loc=self.location())

    def parse_constraint(self) -> ConstraintDecl:
        """Parse constraint declaration."""
        self.expect("CONSTRAINT")
        name = self.expect("IDENT").value
        return ConstraintDecl(name, loc=self.location())

    def parse_effect(self) -> EffectDecl:
        """Parse effect declaration."""
        self.expect("EFFECT")
        name = self.expect("IDENT").value
        return EffectDecl(name, loc=self.location())

    def parse_measure(self) -> MeasureDecl:
        """Parse measure declaration."""
        self.expect("MEASURE")
        target = self.expect("IDENT").value
        return MeasureDecl(target, loc=self.location())

    def parse_uncertainty(self) -> UncertaintyDecl:
        """Parse uncertainty declaration."""
        self.expect("UNCERTAINTY")
        return UncertaintyDecl(loc=self.location())

    def parse_verify(self) -> VerifyDecl:
        """Parse verify declaration."""
        self.expect("VERIFY")
        return VerifyDecl(loc=self.location())

    def parse_adapt(self) -> AdaptDecl:
        """Parse adapt declaration."""
        self.expect("ADAPT")
        target = self.expect("IDENT").value
        return AdaptDecl(target, loc=self.location())

    def parse_realize(self) -> RealizeDecl:
        """Parse realize declaration."""
        self.expect("REALIZE")
        self.expect("{")

        decl = RealizeDecl()

        while not self.match("}"):
            if self.match("TARGET"):
                self.advance()
                self.expect(":")
                decl.target = self.expect("IDENT").value
            elif self.match("TRACE"):
                self.advance()
                self.expect(":")
                decl.trace = self.expect("TRUE", "FALSE").value == "true"
            else:
                self.advance()

        self.expect("}")
        return decl


def parse(source: str) -> Program:
    """Parse AMOSL source code."""
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()
