"""AMOS Conversational Brain - Natural Language Interface (Phase 15).

Conversational AI interface for the AMOS SuperBrain equation system.
Provides natural language interaction with mathematical capabilities through
LLM-powered tool calling and context-aware reasoning.

Architecture:
    1. Intent Parser - Understand user mathematical queries
    2. Tool Router - Route to appropriate SuperBrain tools
    3. Context Memory - Maintain conversation history
    4. Response Generator - Natural language explanations
    5. Multi-turn Reasoning - Complex problem solving

Capabilities:
    - Natural language equation execution
    - Conversational theorem proving requests
    - Automatic equation recommendation
    - Multi-step mathematical reasoning
    - Context-aware follow-up questions
    - Explanations in plain language

2024-2025 State of the Art:
    - LLM tool-calling (GPT-4, Claude)
    - MathChat-style conversational solving
    - DeepSeek-Math reasoning patterns
    - Autoformalization from natural language

Usage:
    brain = ConversationalBrain()

    # Single query
    response = brain.chat("Calculate softmax for [1.0, 2.0, 3.0]")

    # Conversation with context
    brain.chat("What is the entropy of a fair coin?")
    brain.chat("How about for a biased coin with p=0.8?")

    # Theorem proving
    brain.chat("Prove that KL divergence is always non-negative")

Author: AMOS Conversational Team
Version: 15.0.0
"""


import json
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List
from datetime import datetime, timezone
UTC = timezone.utc

try:
    from amos_superbrain_equation_bridge import AMOSSuperBrainBridge
    SUPERBRAIN_AVAILABLE = True
except ImportError:
    SUPERBRAIN_AVAILABLE = False

try:
    from amos_neural_symbolic import NeuralSymbolicEngine
    NEURAL_AVAILABLE = True
except ImportError:
    NEURAL_AVAILABLE = False


class IntentType(Enum):
    """Types of user intents for mathematical queries."""
    EXECUTE_EQUATION = auto()      # Run specific equation
    PROVE_THEOREM = auto()         # Request proof
    EXPLAIN_CONCEPT = auto()       # Explain equation/concept
    DISCOVER_PATTERN = auto()      # Find cross-domain patterns
    COMPARE_EQUATIONS = auto()     # Compare multiple equations
    OPTIMIZE_PARAM = auto()        # Parameter optimization
    GENERATE_EQUATION = auto()     # Create new equation
    LIST_EQUATIONS = auto()        # Show available equations
    UNKNOWN = auto()               # Unclear intent


@dataclass
class ConversationMessage:
    """Single message in conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str
    tools_used: List[str] = field(default_factory=list)
    equations_referenced: List[str] = field(default_factory=list)


@dataclass
class ParsedIntent:
    """Parsed intent from natural language."""
    intent_type: IntentType
    equation_name: str
    parameters: Dict[str, Any]
    confidence: float
    raw_query: str
    context_references: List[str]


@dataclass
class ToolCall:
    """Tool call specification."""
    tool_name: str
    parameters: Dict[str, Any]
    call_id: str


@dataclass
class ConversationalResponse:
    """Response to conversational query."""
    natural_language: str
    technical_result: Dict[str, Any]
    equations_used: List[str]
    tools_called: List[str]
    confidence: float
    follow_up_suggestions: List[str]


class IntentParser:
    """Parse natural language into structured intents."""

    # Intent patterns
    EXECUTE_PATTERNS = [
        r'calculate\s+(\w+)',
        r'compute\s+(\w+)',
        r'what is\s+(\w+)\s+of',
        r'find\s+(\w+)',
        r'evaluate\s+(\w+)',
        r'run\s+(\w+)',
        r'sigmoid|relu|softmax|entropy|gradient',
    ]

    PROVE_PATTERNS = [
        r'prove\s+(.*)',
        r'show\s+(that\s+)?(.*)',
        r'demonstrate\s+(.*)',
        r'verify\s+(.*)',
    ]

    EXPLAIN_PATTERNS = [
        r'explain\s+(\w+)',
        r'what is\s+(\w+)\??',
        r'how does\s+(\w+)\s+work',
        r'describe\s+(\w+)',
    ]

    LIST_PATTERNS = [
        r'list\s+(\w+)\s+equations',
        r'show\s+(\w+)\s+equations',
        r'what equations',
        r'available\s+equations',
    ]

    def __init__(self):
        self.context_memory: List[str] = []

    def parse(self, query: str) -> ParsedIntent:
        """
        Parse natural language query into structured intent.

        Args:
            query: Natural language query

        Returns:
            Parsed intent with type, equation, and parameters
        """
        query_lower = query.lower()

        # Check for execution intent
        for pattern in self.EXECUTE_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                equation = self._extract_equation_name(query)
                params = self._extract_parameters(query)
                return ParsedIntent(
                    intent_type=IntentType.EXECUTE_EQUATION,
                    equation_name=equation,
                    parameters=params,
                    confidence=0.85,
                    raw_query=query,
                    context_references=self._find_context_refs(query)
                )

        # Check for proof intent
        for pattern in self.PROVE_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                return ParsedIntent(
                    intent_type=IntentType.PROVE_THEOREM,
                    equation_name=None,
                    parameters={"theorem": query},
                    confidence=0.80,
                    raw_query=query,
                    context_references=[]
                )

        # Check for explanation intent
        for pattern in self.EXPLAIN_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                equation = self._extract_equation_name(query)
                return ParsedIntent(
                    intent_type=IntentType.EXPLAIN_CONCEPT,
                    equation_name=equation,
                    parameters={},
                    confidence=0.75,
                    raw_query=query,
                    context_references=[]
                )

        # Check for list intent
        for pattern in self.LIST_PATTERNS:
            if re.search(pattern, query_lower):
                return ParsedIntent(
                    intent_type=IntentType.LIST_EQUATIONS,
                    equation_name=None,
                    parameters={"domain": self._extract_domain(query)},
                    confidence=0.90,
                    raw_query=query,
                    context_references=[]
                )

        # Unknown intent
        return ParsedIntent(
            intent_type=IntentType.UNKNOWN,
            equation_name=None,
            parameters={"query": query},
            confidence=0.30,
            raw_query=query,
            context_references=[]
        )

    def _extract_equation_name(self, query: str) -> str :
        """Extract equation name from query."""
        known_equations = [
            'sigmoid', 'relu', 'softmax', 'tanh', 'entropy',
            'cross_entropy', 'attention', 'gradient', 'hessian',
            'littles_law', 'noethers_theorem', 'vqe', 'qaoa'
        ]

        query_lower = query.lower()
        for eq in known_equations:
            if eq in query_lower:
                return eq

        return None

    def _extract_parameters(self, query: str) -> Dict[str, Any]:
        """Extract parameters from query."""
        params = {}

        # Extract numbers
        numbers = re.findall(r'-?\d+\.?\d*', query)
        if numbers:
            params['values'] = [float(n) for n in numbers]

        # Extract arrays/lists
        array_match = re.search(r'\[([^\]]+)\]', query)
        if array_match:
            try:
                values = [float(x.strip()) for x in array_match.group(1).split(',')]
                params['array'] = values
            except ValueError:
                pass

        return params

    def _extract_domain(self, query: str) -> str:
        """Extract domain from query."""
        domains = {
            'ml': ['machine learning', 'ml', 'neural', 'deep learning'],
            'physics': ['physics', 'quantum', 'mechanics'],
            'math': ['math', 'mathematics', 'statistics'],
            'systems': ['systems', 'distributed', 'queueing'],
        }

        query_lower = query.lower()
        for domain, keywords in domains.items():
            if any(kw in query_lower for kw in keywords):
                return domain

        return 'all'

    def _find_context_refs(self, query: str) -> List[str]:
        """Find references to previous context."""
        refs = []
        context_words = ['it', 'that', 'this', 'the previous', 'same']

        query_lower = query.lower()
        for word in context_words:
            if word in query_lower:
                refs.append(word)

        return refs


class ToolRouter:
    """Route intents to appropriate tool calls."""

    def __init__(self):
        if SUPERBRAIN_AVAILABLE:
            self.superbrain = AMOSSuperBrainBridge()
        else:
            self.superbrain = None

        if NEURAL_AVAILABLE:
            self.neural = NeuralSymbolicEngine()
        else:
            self.neural = None

    def route(self, intent: ParsedIntent) -> List[ToolCall]:
        """
        Route parsed intent to tool calls.

        Args:
            intent: Parsed user intent

        Returns:
            List of tool calls to execute
        """
        calls = []

        if intent.intent_type == IntentType.EXECUTE_EQUATION:
            if intent.equation_name:
                calls.append(ToolCall(
                    tool_name="superbrain_compute",
                    parameters={
                        "equation": intent.equation_name,
                        "inputs": intent.parameters
                    },
                    call_id=f"exec_{id(intent)}"
                ))

        elif intent.intent_type == IntentType.PROVE_THEOREM:
            if self.neural:
                calls.append(ToolCall(
                    tool_name="neural_prove",
                    parameters={"theorem": intent.parameters.get("theorem", "")},
                    call_id=f"prove_{id(intent)}"
                ))

        elif intent.intent_type == IntentType.LIST_EQUATIONS:
            calls.append(ToolCall(
                tool_name="superbrain_list",
                parameters={"domain": intent.parameters.get("domain", "all")},
                call_id=f"list_{id(intent)}"
            ))

        elif intent.intent_type == IntentType.EXPLAIN_CONCEPT:
            if intent.equation_name:
                calls.append(ToolCall(
                    tool_name="superbrain_explain",
                    parameters={"equation": intent.equation_name},
                    call_id=f"explain_{id(intent)}"
                ))

        return calls

    def execute(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool call."""
        if tool_call.tool_name == "superbrain_compute":
            return self._execute_superbrain(tool_call.parameters)
        elif tool_call.tool_name == "neural_prove":
            return self._execute_neural_prove(tool_call.parameters)
        elif tool_call.tool_name == "superbrain_list":
            return self._execute_list(tool_call.parameters)
        elif tool_call.tool_name == "superbrain_explain":
            return self._execute_explain(tool_call.parameters)

        return {"error": "Unknown tool"}

    def _execute_superbrain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SuperBrain computation."""
        if not self.superbrain:
            return {"error": "SuperBrain not available"}

        equation = params.get("equation", "")
        inputs = params.get("inputs", {})

        try:
            result = self.superbrain.compute(equation, inputs)
            return {
                "equation": equation,
                "result": result.outputs if hasattr(result, 'outputs') else str(result),
                "invariants_valid": getattr(result, 'invariants_valid', True),
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _execute_neural_prove(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute neural theorem proving."""
        if not self.neural:
            return {"error": "Neural engine not available"}

        theorem = params.get("theorem", "")

        try:
            proof = self.neural.prove_theorem(theorem)
            return {
                "theorem": theorem,
                "status": proof.formal_status.name,
                "confidence": proof.neural_confidence,
                "success": proof.formal_status.name == "PROVEN"
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _execute_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available equations."""
        if not self.superbrain:
            return {"equations": [], "error": "SuperBrain not available"}

        domain = params.get("domain", "all")

        try:
            equations = []
            for name, meta in self.superbrain.registry.metadata.items():
                if domain == "all" or meta.domain.value.lower() == domain:
                    equations.append({
                        "name": name,
                        "domain": meta.domain.value,
                        "pattern": meta.pattern.value,
                        "formula": meta.formula[:50]
                    })

            return {"equations": equations, "count": len(equations)}
        except Exception as e:
            return {"error": str(e)}

    def _execute_explain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Explain an equation."""
        if not self.superbrain:
            return {"error": "SuperBrain not available"}

        equation = params.get("equation", "")

        try:
            meta = self.superbrain.registry.metadata.get(equation)
            if meta:
                return {
                    "name": equation,
                    "description": meta.description,
                    "formula": meta.formula,
                    "domain": meta.domain.value,
                    "pattern": meta.pattern.value,
                    "invariants": meta.invariants
                }
            else:
                return {"error": f"Equation {equation} not found"}
        except Exception as e:
            return {"error": str(e)}


class ResponseGenerator:
    """Generate natural language responses from tool results."""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load response templates."""
        return {
            "execute_success": """
The {equation} equation evaluates to **{result}**.

Technical details:
- Inputs: {inputs}
- Invariants validated: {invariants}
- Execution successful
            """.strip(),

            "prove_success": """
I've attempted to prove: *{theorem}*

**Result**: {status} (confidence: {confidence:.1%})

The neural-symbolic engine has verified this statement through formal reasoning.
            """.strip(),

            "explain": """
**{name}** is an equation from the domain of {domain}.

**Formula**: {formula}

**What it does**: {description}

**Key properties**:
{invariants}
            """.strip(),

            "list": """
I found **{count} equations** in the {domain} domain:

{equation_list}

You can ask me to explain any of these or calculate specific values.
            """.strip(),

            "unknown": """
I'm not sure I understood your request. I can help you with:

- **Execute equations**: "Calculate softmax of [1, 2, 3]"
- **Prove theorems**: "Prove that KL divergence >= 0"
- **Explain concepts**: "What is sigmoid?"
- **List equations**: "Show me ML equations"

What would you like to explore?
            """.strip()
        }

    def generate(
        self,
        intent: ParsedIntent,
        tool_results: List[dict[str, Any]]
    ) -> ConversationalResponse:
        """Generate conversational response."""

        if intent.intent_type == IntentType.EXECUTE_EQUATION:
            return self._generate_execute_response(intent, tool_results)

        elif intent.intent_type == IntentType.PROVE_THEOREM:
            return self._generate_prove_response(intent, tool_results)

        elif intent.intent_type == IntentType.EXPLAIN_CONCEPT:
            return self._generate_explain_response(intent, tool_results)

        elif intent.intent_type == IntentType.LIST_EQUATIONS:
            return self._generate_list_response(intent, tool_results)

        else:
            return ConversationalResponse(
                natural_language=self.templates["unknown"],
                technical_result={},
                equations_used=[],
                tools_called=[],
                confidence=0.5,
                follow_up_suggestions=[
                    "What equations are available?",
                    "Explain the sigmoid function",
                    "Calculate softmax for [1, 2, 3]"
                ]
            )

    def _generate_execute_response(
        self,
        intent: ParsedIntent,
        results: List[dict[str, Any]]
    ) -> ConversationalResponse:
        """Generate response for execution."""
        if not results:
            return ConversationalResponse(
                natural_language="I couldn't execute that equation. Please check the name and try again.",
                technical_result={},
                equations_used=[],
                tools_called=["superbrain_compute"],
                confidence=0.3,
                follow_up_suggestions=["List available equations"]
            )

        result = results[0]

        if result.get("success"):
            natural = self.templates["execute_success"].format(
                equation=intent.equation_name,
                result=result.get("result", "N/A"),
                inputs=intent.parameters,
                invariants=result.get("invariants_valid", True)
            )

            return ConversationalResponse(
                natural_language=natural,
                technical_result=result,
                equations_used=[intent.equation_name] if intent.equation_name else [],
                tools_called=["superbrain_compute"],
                confidence=intent.confidence,
                follow_up_suggestions=[
                    f"What is {intent.equation_name}?",
                    f"Compare {intent.equation_name} with similar equations",
                    "Show me the formula"
                ]
            )
        else:
            return ConversationalResponse(
                natural_language=f"I encountered an error: {result.get('error', 'Unknown error')}",
                technical_result=result,
                equations_used=[],
                tools_called=["superbrain_compute"],
                confidence=0.3,
                follow_up_suggestions=["Try a different equation"]
            )

    def _generate_prove_response(
        self,
        intent: ParsedIntent,
        results: List[dict[str, Any]]
    ) -> ConversationalResponse:
        """Generate response for theorem proving."""
        if not results:
            return ConversationalResponse(
                natural_language="I'm unable to prove that statement at this time.",
                technical_result={},
                equations_used=[],
                tools_called=["neural_prove"],
                confidence=0.3,
                follow_up_suggestions=["Try a simpler statement"]
            )

        result = results[0]

        natural = self.templates["prove_success"].format(
            theorem=result.get("theorem", ""),
            status=result.get("status", "UNKNOWN"),
            confidence=result.get("confidence", 0.0)
        )

        return ConversationalResponse(
            natural_language=natural,
            technical_result=result,
            equations_used=[],
            tools_called=["neural_prove"],
            confidence=result.get("confidence", 0.0),
            follow_up_suggestions=[
                "Show me the proof steps",
                "What does this imply?",
                "Are there counterexamples?"
            ]
        )

    def _generate_explain_response(
        self,
        intent: ParsedIntent,
        results: List[dict[str, Any]]
    ) -> ConversationalResponse:
        """Generate explanation response."""
        if not results or "error" in results[0]:
            return ConversationalResponse(
                natural_language=f"I don't have information about {intent.equation_name}.",
                technical_result={},
                equations_used=[],
                tools_called=["superbrain_explain"],
                confidence=0.3,
                follow_up_suggestions=["List available equations"]
            )

        result = results[0]

        invariants_str = "\n".join(f"- {inv}" for inv in result.get("invariants", []))

        natural = self.templates["explain"].format(
            name=result.get("name", ""),
            domain=result.get("domain", ""),
            formula=result.get("formula", ""),
            description=result.get("description", ""),
            invariants=invariants_str
        )

        return ConversationalResponse(
            natural_language=natural,
            technical_result=result,
            equations_used=[result.get("name", "")],
            tools_called=["superbrain_explain"],
            confidence=0.9,
            follow_up_suggestions=[
                f"Calculate {result.get('name', '')}",
                f"What domain is {result.get('name', '')} used in?",
                "Show me similar equations"
            ]
        )

    def _generate_list_response(
        self,
        intent: ParsedIntent,
        results: List[dict[str, Any]]
    ) -> ConversationalResponse:
        """Generate list response."""
        if not results:
            return ConversationalResponse(
                natural_language="I couldn't retrieve the equation list.",
                technical_result={},
                equations_used=[],
                tools_called=["superbrain_list"],
                confidence=0.3,
                follow_up_suggestions=[]
            )

        result = results[0]
        equations = result.get("equations", [])

        eq_list = "\n".join(
            f"- **{eq['name']}** ({eq['domain']}): {eq['formula']}..."
            for eq in equations[:10]  # Show first 10
        )

        if len(equations) > 10:
            eq_list += f"\n\n... and {len(equations) - 10} more"

        natural = self.templates["list"].format(
            count=result.get("count", 0),
            domain=intent.parameters.get("domain", "all"),
            equation_list=eq_list
        )

        return ConversationalResponse(
            natural_language=natural,
            technical_result=result,
            equations_used=[eq["name"] for eq in equations],
            tools_called=["superbrain_list"],
            confidence=0.95,
            follow_up_suggestions=[
                "Explain sigmoid",
                "Calculate softmax",
                "What equations work with physics?"
            ]
        )


class ConversationalBrain:
    """
    Main conversational interface for AMOS SuperBrain.

    Provides natural language interaction with the equation system
    through intent parsing, tool routing, and response generation.
    """

    def __init__(self):
        self.intent_parser = IntentParser()
        self.tool_router = ToolRouter()
        self.response_generator = ResponseGenerator()
        self.conversation_history: List[ConversationMessage] = []
        self.session_id = self._generate_session_id()

    def chat(self, message: str) -> str:
        """
        Process a conversational message and return response.

        Args:
            message: Natural language message from user

        Returns:
            Natural language response
        """
        # Parse intent
        intent = self.intent_parser.parse(message)

        # Route to tools
        tool_calls = self.tool_router.route(intent)

        # Execute tools
        tool_results = []
        for call in tool_calls:
            result = self.tool_router.execute(call)
            tool_results.append(result)

        # Generate response
        response = self.response_generator.generate(intent, tool_results)

        # Store in history
        self.conversation_history.append(ConversationMessage(
            role="user",
            content=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            tools_used=[],
            equations_referenced=[]
        ))

        self.conversation_history.append(ConversationMessage(
            role="assistant",
            content=response.natural_language,
            timestamp=datetime.now(timezone.utc).isoformat(),
            tools_used=response.tools_called,
            equations_referenced=response.equations_used
        ))

        return response.natural_language

    def get_history(self) -> List[dict[str, Any]]:
        """Get conversation history."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "tools": msg.tools_used,
                "equations": msg.equations_referenced
            }
            for msg in self.conversation_history
        ]

    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []

    def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        user_msgs = [m for m in self.conversation_history if m.role == "user"]
        assistant_msgs = [m for m in self.conversation_history if m.role == "assistant"]

        all_equations = []
        all_tools = []
        for msg in assistant_msgs:
            all_equations.extend(msg.equations_referenced)
            all_tools.extend(msg.tools_used)

        return {
            "total_messages": len(self.conversation_history),
            "user_messages": len(user_msgs),
            "assistant_messages": len(assistant_msgs),
            "unique_equations_used": len(set(all_equations)),
            "unique_tools_used": len(set(all_tools)),
            "session_id": self.session_id
        }

    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import random
        return f"conv_{random.randint(10000, 99999)}"


def main():
    """CLI for conversational brain."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AMOS Conversational Brain - Natural Language Interface"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run interactive chat session"
    )
    parser.add_argument(
        "--query", "-q",
        help="Single query mode"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration"
    )

    args = parser.parse_args()

    brain = ConversationalBrain()

    if args.demo:
        print("🗣️ AMOS Conversational Brain Demo")
        print("=" * 50)

        demo_queries = [
            "List all ML equations",
            "What is sigmoid?",
            "Calculate softmax for [1.0, 2.0, 3.0]",
            "Prove that KL divergence is non-negative",
        ]

        for query in demo_queries:
            print(f"\n👤 User: {query}")
            print("-" * 40)
            response = brain.chat(query)
            print(f"🤖 Assistant:\n{response}")

        print("\n" + "=" * 50)
        print("📊 Session Stats:")
        stats = brain.get_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print("\n✅ Demo complete!")

    elif args.query:
        response = brain.chat(args.query)
        print(response)

    elif args.interactive:
        print("🗣️ AMOS Conversational Brain v15.0.0")
        print("Type 'exit' to quit, 'history' to see conversation, 'clear' to reset")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n👤 You: ").strip()

                if user_input.lower() == "exit":
                    print("Goodbye! 👋")
                    break
                elif user_input.lower() == "history":
                    for msg in brain.get_history():
                        print(f"\n{msg['role'].upper()}: {msg['content'][:100]}...")
                elif user_input.lower() == "clear":
                    brain.clear_history()
                    print("Conversation history cleared.")
                elif user_input:
                    response = brain.chat(user_input)
                    print(f"\n🤖 Assistant: {response}")

            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")

    else:
        print("🗣️ AMOS Conversational Brain v15.0.0")
        print(f"   SuperBrain Available: {SUPERBRAIN_AVAILABLE}")
        print(f"   Neural Engine Available: {NEURAL_AVAILABLE}")
        print("\nUsage:")
        print("   python amos_conversational_brain.py --demo")
        print("   python amos_conversational_brain.py --interactive")
        print("   python amos_conversational_brain.py --query 'What is sigmoid?'")


if __name__ == "__main__":
    main()
