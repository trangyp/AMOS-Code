"""AMOS NATS Client - Unified messaging for 6-repo architecture."""

import asyncio
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
UTC = timezone.utc
from typing import Any, Callable, Dict, List, Optional
from contextlib import asynccontextmanager

import nats
from nats.aio.client import Client as NATSClient
from nats.aio.subscription import Subscription
from nats.js.client import JetStreamContext

logger = logging.getLogger(__name__)


@dataclass
class NATSMessage:
    """Standard message envelope for all AMOS NATS communications."""
    
    topic: str
    payload: Dict[str, Any]
    source: str  # Repo name that sent the message
    timestamp: str
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        topic: str,
        payload: Dict[str, Any],
        source: str,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None
    ) -> "NATSMessage":
        return cls(
            topic=topic,
            payload=payload,
            source=source,
            timestamp=datetime.now(timezone.utc).isoformat(),
            correlation_id=correlation_id,
            reply_to=reply_to
        )
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
    
    @classmethod
    def from_json(cls, data: str) -> "NATSMessage":
        return cls(**json.loads(data))


class AMOSNATSClient:
    """Unified NATS client for AMOS platform inter-repo communication."""
    
    def __init__(
        self,
        server_url: str = "nats://localhost:4222",
        repo_name: str = "unknown",
        jetstream_enabled: bool = True
    ):
        self.server_url = server_url
        self.repo_name = repo_name
        self.jetstream_enabled = jetstream_enabled
        
        self._nc: Optional[NATSClient] = None
        self._js: Optional[JetStreamContext] = None
        self._subscriptions: List[Subscription] = []
        
    async def connect(self) -> None:
        """Connect to NATS server."""
        self._nc = await nats.connect(
            self.server_url,
            name=f"amos-{self.repo_name}",
            reconnect_time_wait=2,
            max_reconnect_attempts=10
        )
        
        if self.jetstream_enabled:
            self._js = self._nc.jetstream()
            
        logger.info(f"NATS connected for repo: {self.repo_name}")
        
    async def disconnect(self) -> None:
        """Disconnect from NATS server."""
        for sub in self._subscriptions:
            await sub.unsubscribe()
            
        if self._nc:
            await self._nc.close()
            
        logger.info(f"NATS disconnected for repo: {self.repo_name}")
        
    @asynccontextmanager
    async def session(self):
        """Context manager for NATS session."""
        try:
            await self.connect()
            yield self
        finally:
            await self.disconnect()
    
    # === SYNC LANE - Request/Reply ===
    
    async def request(
        self,
        subject: str,
        payload: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Send synchronous request and wait for reply."""
        if not self._nc:
            raise RuntimeError("NATS not connected")
            
        message = NATSMessage.create(
            topic=subject,
            payload=payload,
            source=self.repo_name
        )
        
        data = message.to_json().encode()
        
        try:
            response = await self._nc.request(
                subject,
                data,
                timeout=timeout
            )
            
            reply_msg = NATSMessage.from_json(response.data.decode())
            return reply_msg.payload
            
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {subject}")
            raise
            
    async def reply(
        self,
        subject: str,
        handler: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> Subscription:
        """Subscribe to requests and send replies."""
        if not self._nc:
            raise RuntimeError("NATS not connected")
            
        async def message_handler(msg):
            try:
                request = NATSMessage.from_json(msg.data.decode())
                
                # Process request
                response_payload = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: handler(request.payload)
                )
                
                # Send reply
                response = NATSMessage.create(
                    topic=msg.reply,
                    payload=response_payload,
                    source=self.repo_name,
                    correlation_id=request.correlation_id
                )
                
                await self._nc.publish(msg.reply, response.to_json().encode())
                
            except Exception as e:
                logger.error(f"Reply handler error: {e}")
                
        sub = await self._nc.subscribe(subject, cb=message_handler)
        self._subscriptions.append(sub)
        
        logger.info(f"Reply handler registered: {subject}")
        return sub
    
    # === ASYNC LANE - Pub/Sub ===
    
    async def publish(
        self,
        subject: str,
        payload: Dict[str, Any]
    ) -> None:
        """Publish async event."""
        if not self._nc:
            raise RuntimeError("NATS not connected")
            
        message = NATSMessage.create(
            topic=subject,
            payload=payload,
            source=self.repo_name
        )
        
        await self._nc.publish(subject, message.to_json().encode())
        
    async def subscribe(
        self,
        subject: str,
        handler: Callable[[dict[str, Any]], None],
        queue: Optional[str] = None
    ) -> Subscription:
        """Subscribe to async events."""
        if not self._nc:
            raise RuntimeError("NATS not connected")
            
        async def message_handler(msg):
            try:
                message = NATSMessage.from_json(msg.data.decode())
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: handler(message.payload)
                )
            except Exception as e:
                logger.error(f"Subscribe handler error: {e}")
                
        if queue:
            sub = await self._nc.subscribe(subject, queue=queue, cb=message_handler)
        else:
            sub = await self._nc.subscribe(subject, cb=message_handler)
            
        self._subscriptions.append(sub)
        
        logger.info(f"Subscribed: {subject} (queue: {queue})")
        return sub
    
    # === JETSTREAM - Persistent Messaging ===
    
    async def js_publish(
        self,
        subject: str,
        payload: Dict[str, Any]
    ) -> None:
        """Publish to JetStream with persistence."""
        if not self._js:
            raise RuntimeError("JetStream not enabled")
            
        message = NATSMessage.create(
            topic=subject,
            payload=payload,
            source=self.repo_name
        )
        
        await self._js.publish(subject, message.to_json().encode())
        
    async def js_subscribe(
        self,
        subject: str,
        handler: Callable[[dict[str, Any]], None],
        durable: str,
        stream: str
    ) -> Subscription:
        """Subscribe to JetStream with durable consumer."""
        if not self._js:
            raise RuntimeError("JetStream not enabled")
            
        async def message_handler(msg):
            try:
                message = NATSMessage.from_json(msg.data.decode())
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: handler(message.payload)
                )
                await msg.ack()
            except Exception as e:
                logger.error(f"JetStream handler error: {e}")
                await msg.nak()
                
        sub = await self._js.subscribe(
            subject,
            durable=durable,
            stream=stream,
            cb=message_handler
        )
        
        self._subscriptions.append(sub)
        
        logger.info(f"JetStream subscribed: {subject} (durable: {durable})")
        return sub
    
    # === SCATTER-GATHER ===
    
    async def scatter_gather(
        self,
        subject_pattern: str,
        payload: Dict[str, Any],
        expected_responses: int,
        timeout: float = 30.0
    ) -> List[dict[str, Any]]:
        """Scatter request to multiple services and gather responses."""
        if not self._nc:
            raise RuntimeError("NATS not connected")
            
        responses = []
        
        # Create inbox for replies
        inbox = self._nc.new_inbox()
        
        # Subscribe to replies
        async def reply_handler(msg):
            try:
                reply_msg = NATSMessage.from_json(msg.data.decode())
                responses.append(reply_msg.payload)
            except Exception as e:
                logger.error(f"Scatter-gather reply error: {e}")
                
        sub = await self._nc.subscribe(inbox, cb=reply_handler)
        
        # Publish scatter request
        message = NATSMessage.create(
            topic=subject_pattern,
            payload=payload,
            source=self.repo_name,
            reply_to=inbox
        )
        
        await self._nc.publish(subject_pattern, message.to_json().encode())
        
        # Wait for responses or timeout
        start = asyncio.get_event_loop().time()
        while len(responses) < expected_responses:
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed >= timeout:
                break
            await asyncio.sleep(0.1)
            
        await sub.unsubscribe()
        
        return responses


# === Singleton Instance ===

_nats_client: Optional[AMOSNATSClient] = None


def get_nats_client() -> AMOSNATSClient:
    """Get singleton NATS client instance."""
    global _nats_client
    if _nats_client is None:
        _nats_client = AMOSNATSClient()
    return _nats_client


def init_nats_client(
    server_url: str,
    repo_name: str,
    jetstream_enabled: bool = True
) -> AMOSNATSClient:
    """Initialize NATS client with configuration."""
    global _nats_client
    _nats_client = AMOSNATSClient(server_url, repo_name, jetstream_enabled)
    return _nats_client
