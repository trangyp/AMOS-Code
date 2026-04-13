#!/usr/bin/env python3
"""
AMOS Blood Kernel - 04_BLOOD Subsystem

Responsible for:
- Transport and communication between all subsystems
- Message bus for event streaming
- Resource allocation (energy, nutrients)
- Signal routing and delivery
- Circulatory network management
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amos.blood")


class SignalType(Enum):
    """Types of signals that can flow through the blood stream."""
    COMMAND = auto()
    EVENT = auto()
    DATA = auto()
    ALERT = auto()
    HEARTBEAT = auto()
    RESOURCE_REQUEST = auto()
    RESOURCE_GRANT = auto()


class Priority(Enum):
    """Signal priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class Signal:
    """A signal/message flowing through the blood stream."""
    priority_val: int = field(compare=True, repr=False, default=2)
    signal_id: str = field(compare=False, default="")
    source: str = field(compare=False, default="")
    target: str = field(compare=False, default="")
    signal_type: SignalType = field(compare=False, default=SignalType.EVENT)
    payload: Dict[str, Any] = field(compare=False, default_factory=dict)
    priority: Priority = field(compare=False, default=Priority.NORMAL)
    timestamp: str = field(compare=False, default="")
    ttl: int = field(compare=False, default=60)
    delivered: bool = field(compare=False, default=False)
    seq: int = field(compare=True, default=0)
    
    _seq_counter = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        self.priority_val = self.priority.value
        if self.seq == 0:
            Signal._seq_counter += 1
            self.seq = Signal._seq_counter


@dataclass
class Resource:
    """A resource (energy, capacity, etc.)."""
    resource_type: str
    amount: float
    unit: str
    source: str
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Channel:
    """Communication channel between subsystems."""
    channel_id: str
    source: str
    target: str
    established: str = ""
    last_activity: str = ""
    message_count: int = 0
    
    def __post_init__(self):
        if not self.established:
            self.established = datetime.utcnow().isoformat()
            self.last_activity = self.established


class BloodKernel:
    """
    The Blood Kernel provides circulatory system functionality - 
    transporting signals, nutrients, and resources between subsystems.
    """
    
    def __init__(self, organism_root: Path):
        self.root = organism_root
        self.blood_path = organism_root / "04_BLOOD"
        self.memory_path = self.blood_path / "memory"
        self.logs_path = self.blood_path / "logs"
        
        # Ensure directories
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Message bus - priority queue
        self.signal_queue: queue.PriorityQueue = queue.PriorityQueue()
        
        # Subscribers: target -> list of (callback, filter_fn)
        self.subscribers: Dict[str, List[Tuple[Callable, Optional[Callable]]]] = defaultdict(list)
        
        # Active channels between subsystems
        self.channels: Dict[str, Channel] = {}
        
        # Resource pools
        self.resources: Dict[str, float] = {
            "energy": 100.0,
            "compute_cycles": 1000.0,
            "memory_mb": 512.0,
            "bandwidth": 100.0
        }
        
        # Resource allocations per subsystem
        self.allocations: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        
        # Signal history for analysis
        self.signal_history: List[Signal] = []
        self.max_history = 10000
        
        # Threading
        self._running = False
        self._dispatcher_thread: Optional[threading.Thread] = None
        
        logger.info(f"BloodKernel initialized at {self.blood_path}")
    
    def start(self):
        """Start the blood circulation (message dispatcher)."""
        self._running = True
        self._dispatcher_thread = threading.Thread(target=self._dispatch_loop, daemon=True)
        self._dispatcher_thread.start()
        logger.info("Blood circulation started")
    
    def stop(self):
        """Stop the blood circulation."""
        self._running = False
        if self._dispatcher_thread:
            self._dispatcher_thread.join(timeout=2.0)
        logger.info("Blood circulation stopped")
    
    def _dispatch_loop(self):
        """Main dispatch loop - processes signals from queue."""
        while self._running:
            try:
                # Get signal with timeout to allow checking _running
                signal = self.signal_queue.get(timeout=0.5)
                
                # Check TTL
                signal_age = (datetime.utcnow() - datetime.fromisoformat(signal.timestamp)).total_seconds()
                if signal_age > signal.ttl:
                    logger.debug(f"Signal {signal.signal_id} expired, dropping")
                    continue
                
                # Deliver signal
                self._deliver_signal(signal)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Dispatch error: {e}")
    
    def _deliver_signal(self, signal: Signal):
        """Deliver a signal to its target and subscribers."""
        delivered = False
        
        # Direct delivery to target
        if signal.target in self.subscribers:
            for callback, filter_fn in self.subscribers[signal.target]:
                try:
                    if filter_fn is None or filter_fn(signal):
                        callback(signal)
                        delivered = True
                except Exception as e:
                    logger.error(f"Subscriber callback error: {e}")
        
        # Broadcast to wildcard subscribers
        if "*" in self.subscribers:
            for callback, filter_fn in self.subscribers["*"]:
                try:
                    if filter_fn is None or filter_fn(signal):
                        callback(signal)
                except Exception as e:
                    logger.error(f"Broadcast callback error: {e}")
        
        signal.delivered = delivered
        
        # Update channel stats
        channel_key = f"{signal.source}->{signal.target}"
        if channel_key in self.channels:
            self.channels[channel_key].last_activity = datetime.utcnow().isoformat()
            self.channels[channel_key].message_count += 1
        
        # Store in history
        self.signal_history.append(signal)
        if len(self.signal_history) > self.max_history:
            self.signal_history = self.signal_history[-self.max_history:]
        
        logger.debug(f"Signal {signal.signal_id} delivered={delivered}")
    
    def send_signal(
        self,
        source: str,
        target: str,
        signal_type: SignalType,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
        ttl: int = 60
    ) -> str:
        """
        Send a signal through the blood stream.
        
        Args:
            source: Sending subsystem ID
            target: Target subsystem ID (or "*" for broadcast)
            signal_type: Type of signal
            payload: Signal data
            priority: Delivery priority
            ttl: Time to live in seconds
        
        Returns:
            Signal ID
        """
        signal_id = str(uuid.uuid4())[:8]
        
        signal = Signal(
            signal_id=signal_id,
            source=source,
            target=target,
            signal_type=signal_type,
            payload=payload,
            priority=priority,
            ttl=ttl
        )
        
        # Ensure channel exists
        self._ensure_channel(source, target)
        
        # Queue signal (Signal is now orderable by priority_val then seq)
        self.signal_queue.put(signal)
        
        logger.debug(f"Signal {signal_id} queued: {source} -> {target}")
        return signal_id
    
    def subscribe(
        self,
        target: str,
        callback: Callable[[Signal], None],
        filter_fn: Optional[Callable[[Signal], bool]] = None
    ):
        """
        Subscribe to signals targeting a specific subsystem.
        
        Args:
            target: Target subsystem to listen for (or "*" for all)
            callback: Function to call when signal arrives
            filter_fn: Optional filter function
        """
        self.subscribers[target].append((callback, filter_fn))
        logger.info(f"Subscriber registered for target: {target}")
    
    def unsubscribe(self, target: str, callback: Callable[[Signal], None]):
        """Unsubscribe a callback."""
        self.subscribers[target] = [
            (cb, ff) for cb, ff in self.subscribers[target] if cb != callback
        ]
    
    def _ensure_channel(self, source: str, target: str):
        """Ensure a communication channel exists."""
        channel_key = f"{source}->{target}"
        if channel_key not in self.channels:
            self.channels[channel_key] = Channel(
                channel_id=channel_key,
                source=source,
                target=target
            )
            logger.info(f"Channel established: {channel_key}")
    
    def request_resource(
        self,
        subsystem: str,
        resource_type: str,
        amount: float,
        priority: Priority = Priority.NORMAL
    ) -> bool:
        """
        Request resource allocation.
        
        Args:
            subsystem: Requesting subsystem
            resource_type: Type of resource needed
            amount: Amount requested
            priority: Request priority
        
        Returns:
            True if granted, False if insufficient
        """
        available = self.resources.get(resource_type, 0.0)
        allocated = sum(alloc.get(resource_type, 0.0) for alloc in self.allocations.values())
        free = available - allocated
        
        if amount <= free:
            self.allocations[subsystem][resource_type] += amount
            
            # Notify via signal
            self.send_signal(
                source="04_BLOOD",
                target=subsystem,
                signal_type=SignalType.RESOURCE_GRANT,
                payload={
                    "resource_type": resource_type,
                    "amount": amount,
                    "granted": True
                },
                priority=priority
            )
            logger.info(f"Resource granted: {amount} {resource_type} to {subsystem}")
            return True
        else:
            # Notify denial
            self.send_signal(
                source="04_BLOOD",
                target=subsystem,
                signal_type=SignalType.RESOURCE_GRANT,
                payload={
                    "resource_type": resource_type,
                    "amount": amount,
                    "granted": False,
                    "available": free
                },
                priority=priority
            )
            logger.warning(f"Resource denied: {amount} {resource_type} to {subsystem} (free: {free})")
            return False
    
    def release_resource(self, subsystem: str, resource_type: str, amount: float):
        """Release allocated resources."""
        current = self.allocations[subsystem].get(resource_type, 0.0)
        released = min(amount, current)
        self.allocations[subsystem][resource_type] = current - released
        
        if released > 0:
            logger.info(f"Resource released: {released} {resource_type} from {subsystem}")
    
    def add_resource(self, resource_type: str, amount: float):
        """Add resources to the pool."""
        self.resources[resource_type] = self.resources.get(resource_type, 0.0) + amount
        logger.info(f"Resource added: {amount} {resource_type}")
    
    def get_channel_stats(self) -> Dict[str, Any]:
        """Get statistics for all channels."""
        return {
            channel_id: {
                "source": ch.source,
                "target": ch.target,
                "established": ch.established,
                "last_activity": ch.last_activity,
                "message_count": ch.message_count
            }
            for channel_id, ch in self.channels.items()
        }
    
    def get_signal_flow(self, minutes: int = 5) -> Dict[str, Any]:
        """Analyze signal flow over recent period."""
        cutoff = datetime.utcnow().timestamp() - (minutes * 60)
        recent_signals = [
            s for s in self.signal_history
            if datetime.fromisoformat(s.timestamp).timestamp() > cutoff
        ]
        
        by_type = defaultdict(int)
        by_source = defaultdict(int)
        by_target = defaultdict(int)
        
        for signal in recent_signals:
            by_type[signal.signal_type.name] += 1
            by_source[signal.source] += 1
            by_target[signal.target] += 1
        
        return {
            "period_minutes": minutes,
            "total_signals": len(recent_signals),
            "by_type": dict(by_type),
            "by_source": dict(by_source),
            "by_target": dict(by_target),
            "delivery_rate": sum(1 for s in recent_signals if s.delivered) / len(recent_signals) if recent_signals else 0
        }
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status."""
        return {
            resource_type: {
                "total": total,
                "allocated": sum(alloc.get(resource_type, 0.0) for alloc in self.allocations.values()),
                "free": total - sum(alloc.get(resource_type, 0.0) for alloc in self.allocations.values()),
                "allocations_by_subsystem": {
                    sub: alloc.get(resource_type, 0.0)
                    for sub, alloc in self.allocations.items()
                }
            }
            for resource_type, total in self.resources.items()
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get current blood system state."""
        return {
            "circulation_active": self._running,
            "channels_established": len(self.channels),
            "signals_in_queue": self.signal_queue.qsize(),
            "signals_processed": len(self.signal_history),
            "subscribers_registered": sum(len(subs) for subs in self.subscribers.values()),
            "resource_pools": len(self.resources),
            "allocations_active": len(self.allocations),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on circulatory system."""
        issues = []
        
        # Check for stagnant channels (no activity > 5 min)
        now = datetime.utcnow().timestamp()
        for ch_id, ch in self.channels.items():
            last_activity = datetime.fromisoformat(ch.last_activity).timestamp()
            if now - last_activity > 300:  # 5 minutes
                issues.append(f"Stagnant channel: {ch_id}")
        
        # Check resource exhaustion
        for resource_type, total in self.resources.items():
            allocated = sum(alloc.get(resource_type, 0.0) for alloc in self.allocations.values())
            if allocated / total > 0.9:
                issues.append(f"Resource nearly exhausted: {resource_type}")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "channel_count": len(self.channels),
            "queue_depth": self.signal_queue.qsize()
        }


if __name__ == "__main__":
    # Test the blood kernel
    root = Path(__file__).parent.parent
    blood = BloodKernel(root)
    
    print("Blood State:")
    print(json.dumps(blood.get_state(), indent=2))
    
    print("\n=== Test 1: Start circulation ===")
    blood.start()
    time.sleep(0.1)
    print(f"Circulation active: {blood._running}")
    
    print("\n=== Test 2: Send signals ===")
    
    # Create a simple subscriber
    received_signals = []
    def test_handler(signal: Signal):
        received_signals.append(signal)
        print(f"  Received: {signal.signal_type.name} from {signal.source}")
    
    blood.subscribe("TEST_TARGET", test_handler)
    
    # Send various signals
    blood.send_signal(
        source="01_BRAIN",
        target="TEST_TARGET",
        signal_type=SignalType.COMMAND,
        payload={"action": "process", "data": "test"},
        priority=Priority.HIGH
    )
    
    blood.send_signal(
        source="02_SENSES",
        target="TEST_TARGET",
        signal_type=SignalType.DATA,
        payload={"sensor": "temperature", "value": 22.5}
    )
    
    blood.send_signal(
        source="03_IMMUNE",
        target="*",  # Broadcast
        signal_type=SignalType.ALERT,
        payload={"threat_level": "low", "description": "Test alert"},
        priority=Priority.CRITICAL
    )
    
    time.sleep(0.3)
    print(f"Signals received: {len(received_signals)}")
    
    print("\n=== Test 3: Resource management ===")
    
    # Request resources
    granted = blood.request_resource("01_BRAIN", "energy", 30.0)
    print(f"Resource request granted: {granted}")
    
    granted = blood.request_resource("06_MUSCLE", "energy", 200.0)
    print(f"Large request granted: {granted}")
    
    print("\nResource Status:")
    print(json.dumps(blood.get_resource_status(), indent=2))
    
    print("\n=== Test 4: Signal flow analysis ===")
    flow = blood.get_signal_flow(minutes=1)
    print(json.dumps(flow, indent=2))
    
    print("\n=== Test 5: Health check ===")
    health = blood.health_check()
    print(json.dumps(health, indent=2))
    
    blood.stop()
    
    print("\nFinal State:")
    print(json.dumps(blood.get_state(), indent=2))
