# Real-time Event Streaming

Kafka-based event streaming for AMOS Equation System.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              AMOS Event Streaming Platform                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Application Events  →  Kafka Topics  →  Consumers        │
│                                                             │
│   Topics:                                                   │
│   • amos.equations.events (created, updated, deleted)      │
│   • amos.users.events (registered, login)                  │
│   • amos.tasks.events (started, completed, failed)         │
│   • amos.webhooks.events (delivered)                       │
│                                                             │
│   Consumers:                                                │
│   • Analytics (real-time metrics)                          │
│   • Search Index (Elasticsearch sync)                      │
│   • Notifications (email/push)                             │
│   • Audit Log (compliance)                                │
│   • Data Warehouse (batch sync)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Start Kafka with docker-compose
docker-compose up -d kafka zookeeper

# Produce sample events
python streaming/kafka_client.py --produce

# Consume events
python streaming/kafka_client.py --consume
```

## Usage in Application

```python
from streaming.kafka_client import KafkaEventBus, DomainEvent, EventType

# Initialize
bus = KafkaEventBus(bootstrap_servers="kafka:9092")
await bus.start()

# Publish event
event = DomainEvent(
    event_id=str(uuid.uuid4()),
    event_type=EventType.EQUATION_CREATED,
    aggregate_id=equation.id,
    aggregate_type="equations",
    timestamp=datetime.utcnow(),
    version=1,
    payload={"name": equation.name, "formula": equation.formula},
    metadata={"user_id": current_user.id, "ip": request.client.host},
)

await bus.publish(event)
```

## Event Consumers

```python
# Register event handler
processor = StreamProcessor(bus)

@processor.on(EventType.EQUATION_CREATED)
async def send_welcome_email(event: DomainEvent):
    user = await get_user(event.metadata["user_id"])
    await email_service.send(user.email, "Equation created!")

@processor.on(EventType.EQUATION_CREATED)
async def update_search_index(event: DomainEvent):
    await search_index.index_document(event.aggregate_id, event.payload)
```

## Change Data Capture (CDC)

Debezium captures database changes as events:

```json
{
  "before": null,
  "after": {
    "id": 123,
    "name": "New Equation",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "op": "c",
  "source": {
    "table": "equations",
    "lsn": 123456789
  }
}
```

## Real-time Analytics

```python
from streaming.kafka_client import RealtimeAnalytics

analytics = RealtimeAnalytics(bus)
await analytics.start()

# Metrics available immediately
metrics = analytics.get_metrics()
print(f"Active users: {metrics['active_users_count']}")
```

## Event Schema

| Field | Type | Description |
|-------|------|-------------|
| event_id | UUID | Unique event identifier |
| event_type | string | Domain event type |
| aggregate_id | string | Entity identifier |
| aggregate_type | string | Entity type (equations, users) |
| timestamp | ISO8601 | Event timestamp |
| version | int | Optimistic concurrency |
| payload | JSON | Event data |
| metadata | JSON | Correlation, user info |

## Deployment

### Docker Compose

```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
  
  debezium:
    image: debezium/connect:latest
    environment:
      BOOTSTRAP_SERVERS: kafka:9092
```

### AWS MSK (Managed Kafka)

```python
bus = KafkaEventBus(
    bootstrap_servers="b-1.amos-kafka.xxxxx.cX.kafka.us-east-1.amazonaws.com:9094",
    topic_prefix="amos-prod",
)
```

## Monitoring

```bash
# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group realtime-analytics

# List topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Produce test message
kafka-console-producer.sh --topic amos.equations.events --bootstrap-server localhost:9092
```

## Scaling Considerations

- **Partitions**: Use aggregate_id as key for partition assignment
- **Consumer Groups**: Multiple consumers for parallel processing
- **Retention**: 7 days default, adjust per topic
- **Compression**: Gzip enabled for large messages

---

*Real-time insights from every event*
