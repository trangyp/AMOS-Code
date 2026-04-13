"""
Protocol Handler — Protocol Compliance & Message Handling

Handles protocol definitions, message formats, and conversions
between different communication protocols.

Owner: Trang
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ProtocolType(Enum):
    """Types of protocols."""
    HTTP = "http"
    HTTPS = "https"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    MQTT = "mqtt"
    AMQP = "amqp"
    CUSTOM = "custom"


class MessageFormat(Enum):
    """Message format types."""
    JSON = "json"
    XML = "xml"
    PROTOBUF = "protobuf"
    YAML = "yaml"
    CSV = "csv"
    BINARY = "binary"


@dataclass
class Protocol:
    """Protocol definition."""
    id: str
    name: str
    protocol_type: ProtocolType
    version: str
    message_format: MessageFormat
    schema: Dict[str, Any]
    required_headers: List[str]
    enabled: bool = True


@dataclass
class Message:
    """A protocol message."""
    protocol_id: str
    timestamp: datetime
    headers: Dict[str, str]
    payload: Dict[str, Any]
    format: MessageFormat
    valid: bool = True


class ProtocolHandler:
    """
    Handles protocol definitions and message processing.
    
    Manages protocol configurations, validates messages,
    and handles format conversions.
    """
    
    def __init__(self):
        self.protocols: Dict[str, Protocol] = {}
        self.messages: List[Message] = []
        self._load_default_protocols()
    
    def _load_default_protocols(self):
        """Load default protocol definitions."""
        default_protocols = [
            Protocol(
                id="PROTO-001",
                name="AMOS API",
                protocol_type=ProtocolType.HTTPS,
                version="1.0",
                message_format=MessageFormat.JSON,
                schema={"type": "object", "required": ["action"]},
                required_headers=["Content-Type", "Authorization"],
            ),
            Protocol(
                id="PROTO-002",
                name="AMOS Internal",
                protocol_type=ProtocolType.CUSTOM,
                version="1.0",
                message_format=MessageFormat.JSON,
                schema={"type": "object"},
                required_headers=["X-AMOS-Source"],
            ),
        ]
        
        for protocol in default_protocols:
            self.protocols[protocol.id] = protocol
    
    def register_protocol(self, protocol: Protocol) -> bool:
        """Register a new protocol."""
        if protocol.id in self.protocols:
            return False
        self.protocols[protocol.id] = protocol
        return True
    
    def validate_message(self, protocol_id: str, 
                         headers: Dict[str, str],
                         payload: Dict[str, Any]) -> bool:
        """Validate a message against protocol schema."""
        if protocol_id not in self.protocols:
            return False
        
        protocol = self.protocols[protocol_id]
        
        # Check required headers
        for header in protocol.required_headers:
            if header not in headers:
                return False
        
        # Check message format compatibility
        content_type = headers.get("Content-Type", "")
        if protocol.message_format == MessageFormat.JSON:
            if "json" not in content_type.lower():
                return False
        
        return True
    
    def create_message(self, protocol_id: str,
                       headers: Dict[str, str],
                       payload: Dict[str, Any]) -> Optional[Message]:
        """Create a validated message."""
        valid = self.validate_message(protocol_id, headers, payload)
        
        if not valid:
            return None
        
        protocol = self.protocols[protocol_id]
        
        message = Message(
            protocol_id=protocol_id,
            timestamp=datetime.utcnow(),
            headers=headers,
            payload=payload,
            format=protocol.message_format,
            valid=valid,
        )
        
        self.messages.append(message)
        return message
    
    def convert_format(self, data: Dict[str, Any],
                       from_format: MessageFormat,
                       to_format: MessageFormat) -> Optional[str]:
        """Convert data between formats."""
        if from_format == to_format:
            return str(data)
        
        if from_format == MessageFormat.JSON:
            if to_format == MessageFormat.XML:
                # Simple XML conversion
                xml_parts = ["<root>"]
                for key, value in data.items():
                    xml_parts.append(f"  <{key}>{value}</{key}>")
                xml_parts.append("</root>")
                return "\n".join(xml_parts)
            elif to_format == MessageFormat.YAML:
                # Simple YAML conversion
                yaml_parts = []
                for key, value in data.items():
                    yaml_parts.append(f"{key}: {value}")
                return "\n".join(yaml_parts)
        
        return None
    
    def get_protocol(self, protocol_id: str) -> Optional[Protocol]:
        """Get a protocol definition."""
        return self.protocols.get(protocol_id)
    
    def list_protocols(self, 
                       protocol_type: Optional[ProtocolType] = None) -> List[Protocol]:
        """List all protocols, optionally filtered by type."""
        protocols = list(self.protocols.values())
        if protocol_type:
            protocols = [p for p in protocols if p.protocol_type == protocol_type]
        return protocols
    
    def get_messages(self, 
                     protocol_id: Optional[str] = None,
                     valid_only: bool = True) -> List[Message]:
        """Get messages, optionally filtered."""
        messages = self.messages
        
        if protocol_id:
            messages = [m for m in messages if m.protocol_id == protocol_id]
        
        if valid_only:
            messages = [m for m in messages if m.valid]
        
        return messages


if __name__ == "__main__":
    print("Protocol Handler Module")
    print("=" * 50)
    
    handler = ProtocolHandler()
    print(f"Loaded {len(handler.protocols)} protocols")
    
    # Example message
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer token123",
    }
    
    payload = {"action": "test", "data": "example"}
    
    message = handler.create_message("PROTO-001", headers, payload)
    if message:
        print(f"Created valid message: {message.protocol_id}")
    else:
        print("Failed to create message")
    
    print("Protocol Handler ready")
