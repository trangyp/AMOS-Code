#!/usr/bin/env python3
"""AMOS Interface Layer Kernel - 14_INTERFACE_LAYER Subsystem

Responsible for:
- CLI interface for command-line interaction
- API server for external integration
- Web dashboard for visualization
- Chat/conversational interface
- Input/output routing and formatting
- Session management
"""

import json
import logging
import queue
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
UTC = timezone.utc

UTC = UTC
from enum import Enum, auto
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.interfaces")


class InterfaceType(Enum):
    """Types of interfaces supported."""

    CLI = auto()  # Command-line interface
    API = auto()  # REST API server
    DASHBOARD = auto()  # Web dashboard
    CHAT = auto()  # Chat/conversational interface
    WEBSOCKET = auto()  # Real-time websocket


class CommandType(Enum):
    """Types of CLI commands."""

    QUERY = auto()  # Ask a question
    ACTION = auto()  # Execute an action
    STATUS = auto()  # Get status
    CONFIG = auto()  # Configure settings
    HELP = auto()  # Get help
    EXIT = auto()  # Exit/quit


@dataclass
class Command:
    """A parsed command from user input."""

    command_type: CommandType
    raw_input: str
    args: list[str] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    session_id: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


@dataclass
class Response:
    """A response to a command or query."""

    success: bool
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    response_type: str = "text"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
            "response_type": self.response_type,
        }


@dataclass
class Session:
    """A user session."""

    session_id: str
    user_id: str
    interface_type: InterfaceType
    context: dict[str, Any] = field(default_factory=dict)
    message_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    last_active: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()
        if not self.last_active:
            self.last_active = self.created_at


class InterfaceLayerKernel:
    """The Interface Layer Kernel provides all external interfaces
    for interacting with the AMOS organism.
    """

    def __init__(self, organism_root: Path, organism_instance=None):
        self.root = organism_root
        self.interfaces_path = organism_root / "14_INTERFACES"
        self.config_path = self.interfaces_path / "config"
        self.logs_path = self.interfaces_path / "logs"

        # Ensure directories
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

        # Reference to organism
        self.organism = organism_instance

        # Active sessions
        self.sessions: dict[str, Session] = {}

        # Command handlers
        self.command_handlers: dict[CommandType, Callable] = {}

        # Message queues for async communication
        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()

        # API server
        self.api_server: HTTPServer = None
        self.api_thread: threading.Thread = None

        # Statistics
        self.stats = {
            "commands_processed": 0,
            "sessions_created": 0,
            "api_requests": 0,
            "messages_exchanged": 0,
        }

        # Default configuration
        self.config = {
            "cli_enabled": True,
            "api_enabled": True,
            "api_port": 7777,
            "dashboard_enabled": True,
            "dashboard_port": 7778,
            "chat_enabled": True,
            "session_timeout_minutes": 30,
            "max_message_history": 100,
        }

        # Register default command handlers
        self._register_default_handlers()

        logger.info(f"InterfaceLayerKernel initialized at {self.interfaces_path}")

    def _register_default_handlers(self):
        """Register default command handlers."""
        self.command_handlers[CommandType.STATUS] = self._handle_status
        self.command_handlers[CommandType.HELP] = self._handle_help
        self.command_handlers[CommandType.QUERY] = self._handle_query
        self.command_handlers[CommandType.ACTION] = self._handle_action

    def _handle_status(self, cmd: Command) -> Response:
        """Handle status command."""
        if self.organism:
            state = self.organism.get_state_summary()
            return Response(
                success=True,
                message="AMOS Organism Status",
                data={
                    "active_subsystems": state.get("active_subsystems", []),
                    "uptime": state.get("uptime", "unknown"),
                    "cycle_count": state.get("cycle_count", 0),
                },
            )
        return Response(success=True, message="Interface layer active", data={"status": "ready"})

    def _handle_help(self, cmd: Command) -> Response:
        """Handle help command."""
        help_text = """
AMOS 7-System Organism - Available Commands:

  status              - Get organism status
  query <text>        - Ask a question or query
  action <name>       - Execute an action
  think <topic>       - Start a thinking thread
  perceive            - Run perception cycle
  learn <topic>       - Learn about a topic
  config <key> <val>  - Configure settings
  help                - Show this help
  exit                - Exit the interface

Examples:
  query "What is the weather?"
  action "scan_environment"
  think "optimize_performance"
        """
        return Response(success=True, message=help_text.strip())

    def _handle_query(self, cmd: Command) -> Response:
        """Handle query command."""
        query_text = " ".join(cmd.args) if cmd.args else "No query provided"

        if self.organism and hasattr(self.organism, "_brain") and self.organism._brain:
            try:
                result = self.organism.think({"query": query_text}, mode="exploratory")
                return Response(
                    success=True, message=f"Query processed: {query_text}", data={"result": result}
                )
            except Exception as e:
                return Response(success=False, message=f"Error processing query: {e}")

        return Response(success=True, message=f"Received query: {query_text}")

    def _handle_action(self, cmd: Command) -> Response:
        """Handle action command."""
        action_name = cmd.args[0] if cmd.args else "unknown"

        if self.organism and hasattr(self.organism, "act"):
            try:
                result = self.organism.act({"action": action_name, "args": cmd.args[1:]})
                return Response(
                    success=True, message=f"Action executed: {action_name}", data={"result": result}
                )
            except Exception as e:
                return Response(success=False, message=f"Error executing action: {e}")

        return Response(success=True, message=f"Action requested: {action_name}")

    def parse_command(self, raw_input: str, session_id: str = "default") -> Command:
        """Parse raw input into a command."""
        parts = raw_input.strip().split()
        if not parts:
            return Command(CommandType.HELP, raw_input, session_id=session_id)

        cmd_str = parts[0].lower()
        args = parts[1:]

        # Map command strings to types
        cmd_map = {
            "status": CommandType.STATUS,
            "help": CommandType.HELP,
            "?": CommandType.HELP,
            "query": CommandType.QUERY,
            "ask": CommandType.QUERY,
            "action": CommandType.ACTION,
            "do": CommandType.ACTION,
            "config": CommandType.CONFIG,
            "exit": CommandType.EXIT,
            "quit": CommandType.EXIT,
        }

        cmd_type = cmd_map.get(cmd_str, CommandType.QUERY)  # Default to query

        return Command(command_type=cmd_type, raw_input=raw_input, args=args, session_id=session_id)

    def execute_command(self, cmd: Command) -> Response:
        """Execute a parsed command."""
        handler = self.command_handlers.get(cmd.command_type)

        if handler:
            try:
                response = handler(cmd)
                self.stats["commands_processed"] += 1
                return response
            except Exception as e:
                logger.error(f"Error executing command {cmd.command_type}: {e}")
                return Response(success=False, message=f"Error: {e}")

        return Response(success=False, message=f"Unknown command type: {cmd.command_type}")

    def create_session(self, user_id: str, interface_type: InterfaceType) -> Session:
        """Create a new user session."""
        session_id = (
            f"sess_{interface_type.name.lower()}_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        )

        session = Session(session_id=session_id, user_id=user_id, interface_type=interface_type)

        self.sessions[session_id] = session
        self.stats["sessions_created"] += 1

        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Session:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def process_message(self, message: str, session_id: str = "default") -> str:
        """Process a message and return formatted response."""
        # Parse command
        cmd = self.parse_command(message, session_id)

        # Execute
        response = self.execute_command(cmd)

        # Log to session history
        if session_id in self.sessions:
            self.sessions[session_id].message_history.append(
                {
                    "input": message,
                    "output": response.message,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )

        self.stats["messages_exchanged"] += 1

        # Format response
        if response.success:
            return f"✓ {response.message}"
        else:
            return f"✗ {response.message}"

    def run_cli(self):
        """Run the interactive CLI."""
        print("\n" + "=" * 60)
        print("AMOS 7-System Organism - Command Line Interface")
        print("=" * 60)
        print("Type 'help' for available commands or 'exit' to quit.")
        print("=" * 60 + "\n")

        session = self.create_session("cli_user", InterfaceType.CLI)

        while True:
            try:
                user_input = input("AMOS> ").strip()

                if not user_input:
                    continue

                cmd = self.parse_command(user_input, session.session_id)

                if cmd.command_type == CommandType.EXIT:
                    print("Goodbye!")
                    break

                response = self.execute_command(cmd)

                # Log to session
                session.message_history.append(
                    {
                        "input": user_input,
                        "output": response.message,
                        "timestamp": datetime.now(UTC).isoformat(),
                    }
                )

                # Display response
                if response.success:
                    print(f"✓ {response.message}")
                    if response.data:
                        print(json.dumps(response.data, indent=2))
                else:
                    print(f"✗ {response.message}")

                # Update session activity
                session.last_active = datetime.now(UTC).isoformat()

            except KeyboardInterrupt:
                print("\nInterrupted. Goodbye!")
                break
            except EOFError:
                print("\nEOF received. Exiting.")
                break
            except Exception as e:
                print(f"Error: {e}")

    def start_api_server(self, port: int = None):
        """Start the REST API server."""
        port = port or self.config["api_port"]

        class AMOSRequestHandler(BaseHTTPRequestHandler):
            """HTTP request handler for AMOS API."""

            def log_message(self, format, *args):
                logger.info(f"API {self.address_string()} - {format % args}")

            def do_GET(self):
                """Handle GET requests."""
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()

                response = {
                    "status": "AMOS API Server",
                    "version": "1.0",
                    "endpoints": ["/status", "/query", "/action", "/help"],
                }

                self.wfile.write(json.dumps(response).encode())

            def do_POST(self):
                """Handle POST requests."""
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length)

                try:
                    data = json.loads(post_data.decode())

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()

                    # Process via interface layer
                    if self.server.interface_layer:
                        message = data.get("message", "")
                        session_id = data.get("session_id", "api_default")

                        result = self.server.interface_layer.process_message(message, session_id)

                        response = {
                            "success": True,
                            "response": result,
                            "timestamp": datetime.now(UTC).isoformat(),
                        }
                    else:
                        response = {"success": False, "error": "Interface layer not initialized"}

                    self.wfile.write(json.dumps(response).encode())

                except json.JSONDecodeError:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())

        class AMOSServer(HTTPServer):
            """Custom HTTP server with interface layer reference."""

            def __init__(self, server_address, handler_class, interface_layer):
                super().__init__(server_address, handler_class)
                self.interface_layer = interface_layer

        try:
            self.api_server = AMOSServer(("localhost", port), AMOSRequestHandler, self)

            self.api_thread = threading.Thread(target=self.api_server.serve_forever, daemon=True)
            self.api_thread.start()

            logger.info(f"API server started on port {port}")
            return True

        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False

    def stop_api_server(self):
        """Stop the API server."""
        if self.api_server:
            self.api_server.shutdown()
            logger.info("API server stopped")

    def get_state(self) -> dict[str, Any]:
        """Get current interface layer state."""
        return {
            "active_sessions": len(self.sessions),
            "commands_processed": self.stats["commands_processed"],
            "sessions_created": self.stats["sessions_created"],
            "api_enabled": self.config["api_enabled"],
            "cli_enabled": self.config["cli_enabled"],
            "chat_enabled": self.config["chat_enabled"],
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def shutdown(self):
        """Shutdown the interface layer."""
        self.stop_api_server()
        logger.info("InterfaceLayerKernel shutdown complete")


if __name__ == "__main__":
    # Test the interface layer kernel
    root = Path(__file__).parent.parent
    interfaces = InterfaceLayerKernel(root)

    print("Interface Layer State (initial):")
    print(json.dumps(interfaces.get_state(), indent=2))

    print("\n=== Test 1: Command Parsing ===")

    test_inputs = ["status", "help", "query what is the weather", "action scan_environment", "exit"]

    for inp in test_inputs:
        cmd = interfaces.parse_command(inp)
        print(f"'{inp}' -> {cmd.command_type.name}")

    print("\n=== Test 2: Command Execution ===")

    # Test status command
    cmd = interfaces.parse_command("status")
    response = interfaces.execute_command(cmd)
    print(f"status: {response.success} - {response.message}")

    # Test help command
    cmd = interfaces.parse_command("help")
    response = interfaces.execute_command(cmd)
    print(f"help: {response.success} - {response.message[:50]}...")

    # Test query command
    cmd = interfaces.parse_command("query test question")
    response = interfaces.execute_command(cmd)
    print(f"query: {response.success} - {response.message}")

    print("\n=== Test 3: Session Management ===")

    session = interfaces.create_session("test_user", InterfaceType.CLI)
    print(f"Created session: {session.session_id}")
    print(f"Sessions active: {len(interfaces.sessions)}")

    print("\n=== Test 4: Message Processing ===")

    result = interfaces.process_message("status", session.session_id)
    print(f"Processed 'status': {result[:50]}...")

    result = interfaces.process_message("help", session.session_id)
    print(f"Processed 'help': {result[:50]}...")

    print("\n=== Test 5: Session History ===")

    print(f"Session has {len(session.message_history)} messages")
    for msg in session.message_history:
        print(f"  - {msg['input']} -> {msg['output'][:30]}...")

    print("\nFinal State:")
    print(json.dumps(interfaces.get_state(), indent=2))

    interfaces.shutdown()
    print("\nInterface Layer Kernel test complete!")
