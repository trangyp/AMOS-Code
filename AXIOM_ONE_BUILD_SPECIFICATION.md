# AXIOM ONE: Complete Build Specification

## Document Purpose
Transform the AXIOM ONE vision into an actionable, buildable technical specification.

**Version:** 1.0.0  
**Status:** MVP Specification Ready  
**Est. Build Time:** 18-24 months with 50-person team  
**MVP Scope:** 6-8 months with 20-person team

---

## 1. EXECUTIVE SUMMARY

### 1.1 What We're Building
A unified technical operating system that replaces the fragmented toolchain (GitHub, Jira, Datadog, Terraform, etc.) with a single, coherent platform where every technical object lives in one graph with unified execution, governance, and observability.

### 1.2 Core Differentiators
1. **Canonical Object Graph**: Everything is a typed, linked, versioned object
2. **Event-Sourced Core**: Complete audit trail of all technical reality
3. **Bounded AI Labor**: Agents with permissions, budgets, evidence requirements
4. **Simulation Engine**: Test future states before execution
5. **Economic Layer**: Cost attribution from code to business impact

### 1.3 MVP Definition
The wedge product is **Repo Autopsy** - a repo debugger that actually fixes issues, integrated into a next-generation IDE surface. Everything else layers on top.

---

## 2. SYSTEM ARCHITECTURE

### 2.1 The Graph Layer (Foundation)

```yaml
GraphDatabase:
  Engine: Neo4j 5.x (native graph) + PostgreSQL 16 (tabular data)
  
  CoreNodeTypes:
    - id: UUID (ulid for sortability)
    - type: enum[100+ types]
    - version: int
    - created_at: timestamp
    - modified_at: timestamp
    - created_by: UUID -> Person|Agent
    - modified_by: UUID -> Person|Agent
    - tenant_id: UUID (isolation boundary)
    - payload: JSONB (type-specific data)
    - hash: SHA256 (content verification)
    - signature: ECDSA (provenance)
    
  CoreEdgeTypes:
    - id: UUID
    - from_node: UUID
    - to_node: UUID
    - edge_type: enum[200+ relationship types]
    - weight: float (0-1, relevance score)
    - created_at: timestamp
    - evidence: JSONB (why this link exists)
    - confidence: float (AI-inferred links have <1.0)
    
  IndexStrategy:
    - B-tree: id lookups, range queries
    - GIN: full-text search on payload
    - Vector: pgvector for semantic similarity
    - Graph: Neo4j for path traversals
    
  PartitionStrategy:
    - Tenant-based (top level)
    - Type-based (secondary)
    - Time-based (tertiary for events)
```

### 2.2 The Event Store (Audit Layer)

```protobuf
// events.proto
syntax = "proto3";

message Event {
  string event_id = 1;           // ulid
  string event_type = 2;         // 50+ event types
  string aggregate_id = 3;       // affected object
  string aggregate_type = 4;     // object type
  int32 version = 5;             // aggregate version
  google.protobuf.Any payload = 6;
  
  message Metadata {
    string tenant_id = 1;
    string actor_id = 2;         // person or agent
    string actor_type = 3;       // person | agent | system
    string session_id = 4;
    string correlation_id = 5;   // distributed trace
    string causation_id = 6;     // parent event
    map<string, string> headers = 7;
    int64 timestamp_nanos = 8;
  }
  Metadata metadata = 7;
  
  message PolicyCheck {
    string policy_id = 1;
    bool passed = 2;
    string evidence_hash = 3;
  }
  repeated PolicyCheck policy_checks = 8;
}
```

```yaml
EventStore:
  Backend: Apache Kafka (event log) + S3 (cold storage)
  Retention: Hot 7 days, warm 90 days, cold 7 years (compliance)
  
  EventTypes:
    Core:
      - OBJECT_CREATED
      - OBJECT_MODIFIED
      - OBJECT_DELETED
      - OBJECT_LINKED
      - OBJECT_UNLINKED
    
    Code:
      - CODE_COMMITTED
      - CODE_REVIEWED
      - CODE_MERGED
      - CODE_REVERTED
      - REFACTOR_EXECUTED
    
    Execution:
      - EXECUTION_STARTED
      - EXECUTION_COMPLETED
      - EXECUTION_FAILED
      - EXECUTION_ROLLED_BACK
    
    Deploy:
      - DEPLOY_PLANNED
      - DEPLOY_STARTED
      - DEPLOY_STAGE_COMPLETED
      - DEPLOY_COMPLETED
      - DEPLOY_FAILED
      - DEPLOY_ROLLED_BACK
    
    AI:
      - AI_OBSERVATION
      - AI_PLAN_GENERATED
      - AI_ACTION_PROPOSED
      - AI_ACTION_EXECUTED
      - AI_ACTION_VERIFIED
    
    Security:
      - VULNERABILITY_DETECTED
      - SECRET_EXPOSED
      - POLICY_VIOLATION
      - APPROVAL_GRANTED
      - APPROVAL_REVOKED
    
    Business:
      - COST_ANOMALY_DETECTED
      - CUSTOMER_IMPACT_ESTIMATED
      - REVENUE_ATTRIBUTED
```

### 2.3 The API Layer

```yaml
APIGateway:
  Protocol: GraphQL (primary) + REST (legacy) + gRPC (internal)
  
  GraphQLSchema:
    - Query: 200+ resolvers
    - Mutation: 150+ operations
    - Subscription: 50+ real-time streams
    
  Authentication:
    - JWT with short expiry (15 min access, 7 day refresh)
    - API keys for service accounts
    - mTLS for internal services
    - WebAuthn for admin operations
    
  Authorization:
    - RBAC: 4 base roles (admin, user, service, readonly)
    - ABAC: Resource-level permissions
    - ReBAC: Relationship-based (owner of X can do Y)
    - Policy Engine: OPA (Open Policy Agent)
    
  RateLimiting:
    - Tier-based (Free: 100/hr, Pro: 10K/hr, Enterprise: unlimited)
    - Burst allowance for interactive use
    - Cost-based throttling for AI operations
```

### 2.4 The Execution Layer

```yaml
ExecutionEngine:
  RuntimeTypes:
    Local:
      - Direct process spawn
      - Docker containers
      - DevContainers (VS Code spec)
      
    Remote:
      - Kubernetes Jobs
      - Serverless (Lambda/Cloud Functions)
      - GPU nodes (training/inference)
      - Edge nodes (CDN workers)
      
  Orchestration:
    - Temporal.io for durable workflows
    - Nomad for batch workloads
    - Custom for real-time workloads
    
  Sandboxing:
    - Firecracker microVMs (AWS)
    - gVisor (Google)
    - Kata Containers (general)
    
  ResourceLimits:
    CPU: Request/Limit pattern
    Memory: Hard limits with OOM handling
    GPU: Fractional allocation (A100 slices)
    Network: Egress limits, no ingress except declared
    Storage: Quota enforcement
```

### 2.5 The Agent Layer

```yaml
AgentRuntime:
  Architecture:
    - Control Plane: Agent lifecycle, scheduling
    - Worker Pool: Sandboxed execution
    - Memory Service: Short and long-term storage
    - Tool Registry: 100+ available tools
    
  AgentProtocol:
    StateMachine:
      - OBSERVING      # Collect context
      - PLANNING       # Generate action plan
      - SIMULATING     # Test plan against reality
      - EXECUTING      # Run approved actions
      - VERIFYING      # Check outcomes
      - REPORTING      # Emit results
      - AWAITING_APPROVAL  # Human checkpoint
      
  ToolTypes:
    Read-Only:
      - search_code
      - read_file
      - query_graph
      - read_logs
      - read_metrics
      
    Write-Test:
      - edit_file
      - create_branch
      - run_tests
      - build_image
      
    Write-Production:
      - merge_pr
      - deploy_service
      - rotate_secret
      - create_incident
      
    Special:
      - request_human_approval
      - escalate_to_pager
      - rollback_deployment
      
  SafetyControls:
    - Every action logged to Event Store
    - Every write verified by test
    - Every production action requires approval (by default)
    - Budget limits (token cost, time, API calls)
    - Automatic rollback on failure
```

---

## 3. OBJECT SCHEMAS (Complete)

### 3.1 Core Identity Objects

```typescript
// Person - human user
interface Person {
  id: UUID;
  type: 'person';
  
  // Identity
  email: string;           // verified
  name: string;
  avatar_url: string;
  
  // Auth
  auth_methods: Array<{
    type: 'password' | 'sso' | 'webauthn' | 'mfa';
    provider?: string;
    last_used: timestamp;
  }>;
  
  // Org context
  orgs: OrgMembership[];
  teams: TeamMembership[];
  
  // Preferences
  timezone: string;
  theme: 'light' | 'dark' | 'system';
  keybindings: 'vim' | 'emacs' | 'default';
  notifications: NotificationConfig;
  
  // AI settings
  ai_settings: {
    default_model: string;
    auto_complete: boolean;
    diff_review: boolean;
  };
}

// Agent - AI worker
interface Agent {
  id: UUID;
  type: 'agent';
  
  // Identity
  name: string;
  role: AgentRole;
  description: string;
  
  // Capabilities
  permitted_tools: string[];
  forbidden_paths: string[];   // regex patterns
  permitted_environments: string[];
  
  // Limits
  budget: {
    tokens_per_day: number;
    api_calls_per_hour: number;
    execution_time_minutes: number;
  };
  
  // Governance
  approval_threshold: 'never' | 'risky' | 'always';
  escalation_policy: EscalationConfig;
  
  // State
  memory_spaces: UUID[];     // linked memory objects
  execution_count: number;
  success_rate: float;
  last_execution: timestamp;
}

// Team - group of people
interface Team {
  id: UUID;
  type: 'team';
  
  name: string;
  slug: string;
  description: string;
  
  members: TeamMembership[];
  
  // Ownership
  owns_services: UUID[];   // -> Service
  owns_repos: UUID[];        // -> Repository
  owns_domains: string[];
  
  // Ops
  pager_rotation: RotationConfig;
  on_call_now: UUID[];       // -> Person
  
  // Cost
  cost_center: string;
  monthly_budget: Money;
}
```

### 3.2 Code Objects

```typescript
// Repository - code container
interface Repository {
  id: UUID;
  type: 'repository';
  
  // Identity
  name: string;
  full_name: string;         // org/name
  url: string;
  provider: 'github' | 'gitlab' | 'bitbucket' | 'axiom';
  provider_id: string;
  
  // Content
  default_branch: string;
  language: string;
  languages: Record<string, number>;  // language -> bytes
  
  // Graph links
  files: UUID[];             // -> File
  commits: UUID[];           // -> Commit (last 100)
  branches: UUID[];          // -> Branch
  releases: UUID[];          // -> Release
  
  // Runtime links
  services: UUID[];          // -> Service (deployed from this repo)
  packages: UUID[];          // -> Package (published from this repo)
  
  // Ownership
  owner_team: UUID;          // -> Team
  maintainers: UUID[];     // -> Person
  
  // Health
  health_score: float;       // 0-1 computed
  last_activity: timestamp;
  open_issues: number;
  open_prs: number;
  
  // Config
  axioms: RepoAxiomConfig;   // AXIOM-specific settings
}

// Symbol - function, class, variable
interface Symbol {
  id: UUID;
  type: 'symbol';
  
  // Identity
  name: string;
  symbol_type: 'function' | 'class' | 'method' | 'variable' | 'interface' | 'type';
  fully_qualified_name: string;
  
  // Location
  repository: UUID;
  file: UUID;
  line_start: number;
  line_end: number;
  column_start: number;
  column_end: number;
  
  // Semantic
  signature: string;         // function signature
  docstring: string;
  parameters: Parameter[];
  returns: TypeInfo;
  
  // Dependencies
  calls: UUID[];             // -> Symbol (outgoing calls)
  called_by: UUID[];         // -> Symbol (incoming calls)
  imports: UUID[];          // -> Symbol
  exported_by: UUID[];       // -> Package
  
  // Runtime links
  endpoints: UUID[];         // -> Endpoint (if HTTP handler)
  tests: UUID[];            // -> Test (that covers this)
  
  // AI embeddings
  embedding: number[];        // 1536-dim vector for semantic search
}

// Test - automated test
interface Test {
  id: UUID;
  type: 'test';
  
  name: string;
  test_type: 'unit' | 'integration' | 'e2e' | 'contract' | 'performance';
  
  // Location
  repository: UUID;
  file: UUID;
  line: number;
  
  // Scope
  tests_symbols: UUID[];    // -> Symbol (what this tests)
  
  // History
  runs: TestRun[];
  flake_rate: float;         // % of failures that are flakes
  avg_duration_ms: number;
  
  // Coverage
  coverage: {
    lines: number;
    branches: number;
    functions: number;
  };
}
```

### 3.3 Service Objects

```typescript
// Service - deployable unit
interface Service {
  id: UUID;
  type: 'service';
  
  // Identity
  name: string;
  slug: string;
  description: string;
  
  // Type
  service_type: 'api' | 'worker' | 'cron' | 'function' | 'batch' | 'stream';
  
  // Source
  repository: UUID;
  dockerfile: string;
  build_command: string;
  
  // Runtime
  environments: EnvironmentDeployment[];
  
  // Dependencies
  depends_on: UUID[];       // -> Service
  depended_by: UUID[];      // -> Service
  
  // Endpoints
  endpoints: UUID[];         // -> Endpoint
  
  // Data
  databases: UUID[];         // -> Database
  caches: UUID[];           // -> Cache
  queues: UUID[];           // -> Queue
  
  // Ownership
  team: UUID;
  on_call: UUID[];
  
  // SLOs
  slos: SLO[];
  current_availability: float;
  current_latency_p99: number;
  
  // Cost
  monthly_cost: Money;
  cost_per_request: Money;
  
  // Security
  vulnerabilities: UUID[];   // -> Vulnerability
  secrets: UUID[];          // -> Secret
}

// Endpoint - API surface
interface Endpoint {
  id: UUID;
  type: 'endpoint';
  
  // Identity
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  
  // Location
  service: UUID;
  symbol: UUID;              // -> Symbol (handler function)
  
  // Spec
  request_schema: JSONSchema;
  response_schema: JSONSchema;
  query_params: Parameter[];
  headers: HeaderSpec[];
  
  // Contract
  contract_tests: UUID[];     // -> Test
  consumers: UUID[];         // -> Service (services that call this)
  
  // Metrics
  request_rate: number;      // per minute
  error_rate: number;        // 0-1
  latency_p50: number;
  latency_p99: number;
  
  // AI
  embedding: number[];       // for semantic API discovery
}
```

### 3.4 Runtime Objects

```typescript
// Environment - deployment target
interface Environment {
  id: UUID;
  type: 'environment';
  
  name: string;
  slug: string;
  environment_type: 'local' | 'preview' | 'staging' | 'production';
  
  // Infrastructure
  region: string;
  cluster: UUID;              // -> Cluster
  
  // Deployments
  deployments: UUID[];       // -> Deployment
  current_deployment: UUID;
  
  // Configuration
  variables: EnvVar[];
  secrets: UUID[];           // -> Secret
  feature_flags: UUID[];      // -> FeatureFlag
  
  // State
  status: 'healthy' | 'degraded' | 'down' | 'maintenance';
  health_score: float;
  
  // Access
  allowed_roles: string[];
  require_approval: boolean;
}

// Deployment - specific artifact running
interface Deployment {
  id: UUID;
  type: 'deployment';
  
  // What
  service: UUID;
  environment: UUID;
  
  // Which version
  commit: UUID;
  image: string;
  image_digest: string;
  
  // When
  deployed_at: timestamp;
  deployed_by: UUID;         // Person or Agent
  
  // Status
  status: 'pending' | 'running' | 'stopping' | 'stopped' | 'failed';
  replicas: number;
  healthy_replicas: number;
  
  // Rollback
  can_rollback_to: UUID;     // -> Deployment
  rollback_reason?: string;
  
  // Cost
  hourly_cost: Money;
}

// FeatureFlag - runtime toggle
interface FeatureFlag {
  id: UUID;
  type: 'feature_flag';
  
  name: string;
  key: string;
  description: string;
  
  // State
  enabled: boolean;
  
  // Targeting
  rules: FlagRule[];         // % rollout, user segments, etc
  
  // Impact tracking
  experiments: UUID[];       // -> Experiment
  incidents_caused: UUID[];  // -> Incident
  
  // Ownership
  owner: UUID;
}
```

### 3.5 Operations Objects

```typescript
// Incident - operational event
interface Incident {
  id: UUID;
  type: 'incident';
  
  // Identity
  title: string;
  description: string;
  severity: 'sev1' | 'sev2' | 'sev3' | 'sev4';
  status: 'open' | 'mitigated' | 'resolved' | 'postmortem';
  
  // Timeline
  started_at: timestamp;
  detected_at: timestamp;
  mitigated_at?: timestamp;
  resolved_at?: timestamp;
  
  // Detection
  detected_by: UUID;         // Alert or Person
  alerts: UUID[];           // -> Alert
  
  // Impact
  affected_services: UUID[];
  affected_customers: number;
  estimated_revenue_impact: Money;
  
  // Response
  commander: UUID;           // -> Person (incident commander)
  responders: UUID[];
  war_room_url: string;
  
  // Root cause
  root_cause: string;
  contributing_deploys: UUID[];  // -> Deployment
  
  // Follow-up
  postmortem: UUID;          // -> Postmortem
  action_items: UUID[];      // -> Story (created tasks)
}

// Alert - detection signal
interface Alert {
  id: UUID;
  type: 'alert';
  
  // Source
  alert_rule: UUID;
  query_result: JSON;
  
  // Content
  title: string;
  description: string;
  severity: 'critical' | 'warning' | 'info';
  
  // State
  status: 'firing' | 'acknowledged' | 'resolved' | 'suppressed';
  acknowledged_by?: UUID;
  
  // Links
  service?: UUID;
  metric?: UUID;
  
  // History
  first_fired_at: timestamp;
  last_fired_at: timestamp;
  resolved_at?: timestamp;
}
```

### 3.6 AI Objects

```typescript
// PromptTemplate - reusable AI instruction
interface PromptTemplate {
  id: UUID;
  type: 'prompt_template';
  
  name: string;
  description: string;
  
  // Content
  system_prompt: string;
  user_prompt_template: string;  // Jinja2
  
  // Variables
  variables: VariableDef[];
  
  // Model
  default_model: string;
  temperature: number;
  max_tokens: number;
  
  // Safety
  safety_checks: string[];
  
  // Usage
  usage_count: number;
  avg_latency: number;
  
  // Versioning
  versions: PromptVersion[];
}

// AgentExecution - record of AI work
interface AgentExecution {
  id: UUID;
  type: 'agent_execution';
  
  // Who
  agent: UUID;
  triggered_by: UUID;        // Person or system event
  
  // Context
  observation: string;         // what the agent saw
  goal: string;              // what it was asked to do
  
  // Plan
  plan: AgentStep[];         // generated plan
  
  // Execution
  steps_executed: ExecutedStep[];
  
  // Result
  status: 'success' | 'partial' | 'failure' | 'awaiting_approval';
  result: JSON;
  
  // Evidence
  evidence_hash: string;     // IPFS hash of full trace
  
  // Cost
  tokens_used: number;
  cost: Money;
  duration_ms: number;
}

// Model - AI model reference
interface Model {
  id: UUID;
  type: 'model';
  
  // Identity
  name: string;
  provider: 'openai' | 'anthropic' | 'google' | 'local' | 'custom';
  model_id: string;          // provider's ID
  
  // Capabilities
  modalities: ('text' | 'image' | 'audio' | 'video')[];
  context_window: number;
  
  // Cost
  input_cost_per_1k: Money;
  output_cost_per_1k: Money;
  
  // Performance
  avg_latency_ms: number;
  throughput_per_min: number;
  
  // Safety
  safety_profile: SafetyProfile;
  
  // Status
  available: boolean;
  recommended: boolean;
}
```

### 3.7 Business Objects

```typescript
// Customer - business entity
interface Customer {
  id: UUID;
  type: 'customer';
  
  // Identity
  name: string;
  tenant_id: string;         // isolation boundary
  
  // Contract
  plan: 'free' | 'starter' | 'pro' | 'enterprise';
  entitlements: Entitlement[];
  
  // Usage
  monthly_usage: UsageMetrics;
  
  // Health
  health_score: float;
  churn_risk: float;
  
  // Support
  support_cases: UUID[];
  nps_score: number;
  
  // Link to technical
  affected_by_incidents: UUID[];
  uses_features: UUID[];
  
  // Revenue
  monthly_revenue: Money;
  lifetime_value: Money;
}

// CostObject - spend attribution
interface CostObject {
  id: UUID;
  type: 'cost_object';
  
  // What
  service?: UUID;
  feature?: UUID;
  team?: UUID;
  environment?: UUID;
  
  // How much
  amount: Money;
  currency: string;
  
  // When
  period_start: timestamp;
  period_end: timestamp;
  
  // Breakdown
  compute: Money;
  storage: Money;
  network: Money;
  ai_inference: Money;
  
  // Attribution
  attributed_to_features: Array<{feature: UUID, amount: Money}>;
  attributed_to_customers: Array<{customer: UUID, amount: Money}>;
}
```

---

## 4. PRODUCT SURFACES (Detailed)

### 4.1 Studio - The IDE

```yaml
Studio:
  Architecture:
    Base: VS Code core (open source)
    Extension: AXIOM extension with deep integration
    
  Layout:
    PrimaryBar:
      - FileExplorer: tree view with semantic coloring
      - SymbolNavigator: outline with dependencies
      - SearchPanel: universal search
      - GitPanel: commits, branches, PRs
      - AgentPanel: active AI workers
      
    EditorArea:
      - TabBar: with preview tabs
      - Editor: Monaco with AXIOM extensions
        - Inline diagnostics
        - Inline AI suggestions (ghost text)
        - Symbol highlighting
        - Dependency visualization
      - Breadcrumbs: file > class > method
      - Minimap: with change indicators
      
    SecondaryBar:
      - Inspector: properties of selected symbol
      - DebugPanel: breakpoints, variables, call stack
      - TestPanel: test explorer with live results
      - PreviewPanel: live reload for web apps
      
    BottomPanel:
      - Terminal: multi-shell support
      - Output: build, test, deploy logs
      - Problems: lint, type errors
      - AIChat: conversational interface
      
    StatusBar:
      - Branch/Commit
      - Environment indicator
      - AI status
      - Sync status
      
  KeyFeatures:
    MultiFileEdit:
      - Create change plan across files
      - Preview all changes
      - Apply atomically
      - Rollback if tests fail
      
    SemanticSearch:
      - "Find all functions that call X and modify Y"
      - Natural language to symbol query
      - Result as interactive graph
      
    LiveCollaboration:
      - Multi-cursor editing
      - Inline comments
      - Voice chat (optional)
      
    AIIntegration:
      - Cmd+K: quick AI command
      - Tab: accept suggestion
      - Esc: dismiss
      - Diff review: AI explains changes
```

### 4.2 Navigator - Graph Explorer

```yaml
Navigator:
  Views:
    
    GraphView:
      - Force-directed or hierarchical layout
      - Zoom/pan with mouse
      - Click node to focus
      - Right-click for actions
      - Filter by type, owner, status
      
    InspectorView:
      Header:
        - Icon (type-based)
        - Name
        - Type badge
        - Status badge
        - Owner avatar
        
      Properties:
        - Key-value table of all fields
        - Editable inline
        - History: show changes over time
        
      Relationships:
        - Tabs: Depends On | Depended By | Related
        - Each tab shows connected objects
        - Click to navigate
        
      Timeline:
        - Event feed for this object
        - Filter by event type
        
      Actions:
        - Context-aware buttons
        - "View Code" for symbols
        - "View Logs" for services
        - "Run Test" for tests
        
    PathView:
      - Show path between two objects
      - Highlight critical path
      - Show blast radius
      
    BlastRadiusView:
      - Select a change (commit, deploy)
      - Visualize affected objects
      - Color by risk level
      - Show customer impact
```

### 4.3 Forge - Build & Test

```yaml
Forge:
  
  BuildPanel:
    - Trigger: manual, on commit, on schedule
    - Config: YAML-based pipeline
    - Steps:
      - Checkout
      - Setup (language environment)
      - Install dependencies
      - Lint
      - Type check
      - Build
      - Test
      - Security scan
      - Package
      - Sign
    - 
    - Visual pipeline with status per step
    - Parallel job execution
    - Artifact browser
    
  TestPanel:
    - Test discovery from all sources
    - Tree view: suite > file > test
    - Status icons: pass/fail/skip/pending
    - Run controls: run all, run file, run single
    - Coverage overlay on code
    - Flake detection
    - Historical trends
    
  BenchmarkPanel:
    - Performance test results
    - Regression detection
    - Flame graphs
    - Memory profiles
    
  ReleasePanel:
    - Release candidate list
    - Quality gates: all must pass
    - Approvals required
    - Rollout plan
    - Changelog generation
```

### 4.4 Orbit - Deploy & Runtime

```yaml
Orbit:
  
  EnvironmentView:
    - Grid of environments
    - Status: healthy/degraded/down
    - Current deployment info
    - Quick actions: deploy, rollback, scale
    
  DeployWizard:
    Step1: Select artifact (commit, branch, image)
    Step2: Select target environment
    Step3: Review blast radius
    Step4: Simulation results
    Step5: Approval (if required)
    Step6: Execute with live status
    
  CanaryView:
    - Traffic split visualization
    - Metrics comparison (canary vs baseline)
    - Auto-rollback triggers
    - Promote button
    
  RollbackPanel:
    - One-click rollback
    - Rollback preview (what will change)
    - Emergency stop (kill switch)
    
  ServiceMeshView:
    - Topology graph
    - Traffic flow animation
    - Latency heatmap
    - Circuit breaker status
```

### 4.5 Nexus - Data & APIs

```yaml
Nexus:
  
  DatabaseBrowser:
    - Connection tree: cluster > database > schema > table > column
    - Query editor with autocomplete
    - Results grid
    - Export
    - Schema diff
    - Migration planner
    
  APIExplorer:
    - OpenAPI spec viewer
    - Interactive try-it
    - Request/response history
    - Contract diff (version comparison)
    
  EventStreamViewer:
    - Topic list
    - Live message stream
    - Filter by key, header
    - Replay to test consumer
    
  MockServer:
    - Generate mock from spec
    - Record/playback
    - Chaos injection
```

### 4.6 Pulse - Observability

```yaml
Pulse:
  
  LogExplorer:
    - Live tail
    - Search with Lucene syntax
    - Filters: service, level, time
    - Correlation (group by trace ID)
    - Pattern detection ("this error is new")
    
  TraceExplorer:
    - Flame graph view
    - Service map
    - Critical path highlighting
    - Error trace filtering
    
  MetricsDashboard:
    - Grid of charts
    - Types: line, bar, heatmap, gauge
    - Variables: service selector, time range
    - Alert overlay
    - Annotation overlay (deploys, incidents)
    
  AlertManager:
    - Alert list with status
    - Grouping by service/severity
    - Acknowledge/silence/escalate
    - Runbook link
    - Auto-suggested fixes
    
  IncidentRoom:
    - Incident timeline
    - Affected service list
    - Customer impact estimate
    - Related deploys
    - Chat with responders
    - Action log
```

### 4.7 Sentinel - Security

```yaml
Sentinel:
  
  VulnerabilityDashboard:
    - Risk score by service
    - CVE list with severity
    - Fix availability
    - ETA to remediation
    
  SecretScanner:
    - Finding list
    - Secret type detection
    - Auto-rotation where possible
    
  PolicyEngine:
    - Policy list
    - Compliance status
    - Violation feed
    - Exception workflow
    
  AIActionAudit:
    - All AI actions logged
    - Filter by agent, type, outcome
    - Replay action trace
    - Detect anomalous patterns
```

### 4.8 Ledger - Business

```yaml
Ledger:
  
  CostDashboard:
    - Total spend with trend
    - Breakdown: by service, team, environment
    - Anomaly detection
    - Forecasting
    
  UnitEconomics:
    - Cost per request
    - Cost per customer
    - Cost per feature
    - Margin analysis
    
  Customer360:
    - Customer list with health
    - Support case correlation
    - Feature adoption
    - Incident impact
    
  EngineeringROI:
    - Project cost vs value delivered
    - Technical debt cost
    - Refactor impact
```

### 4.9 Flow - Process Builder

```yaml
Flow:
  
  WorkflowEditor:
    - Canvas with node-edge UI
    - Node types: trigger, action, condition, loop, wait, approval
    - Drag to connect
    - Property panel per node
    - Test mode with step-through
    
  TriggerLibrary:
    - On commit
    - On deploy
    - On alert
    - On schedule
    - On webhook
    - On manual
    
  ActionLibrary:
    - Send notification
    - Create ticket
    - Run agent
    - Deploy service
    - Execute script
    - Wait for approval
    
  Templates:
    - Incident response
    - Release checklist
    - Onboarding
    - Security response
```

---

## 5. REPO AUTOPSY - Complete Spec

### 5.1 Input Handling

```yaml
Input:
  SupportedSources:
    - GitHub URL (public or private with token)
    - GitLab URL
    - Local path
    - ZIP upload
    - Multi-repo (org scan)
    
  Preprocessing:
    - Clone/pull repository
    - Detect language/framework
    - Parse basic structure
    - Create initial graph nodes
```

### 5.2 Analysis Pipeline

```yaml
AnalysisPipeline:
  
  Phase1_StaticAnalysis:
    - Language: tree-sitter parsers
    - Packaging: pyproject/setup/package.json analysis
    - Imports: resolve and graph
    - Symbols: extract all definitions
    - Dependencies: lockfile analysis
    
  Phase2_DynamicAnalysis:
    - Install attempt (sandboxed)
    - Build attempt
    - Test discovery and execution
    - CLI smoke test
    - API startup test
    
  Phase3_GraphConstruction:
    - Link symbols to definitions
    - Link imports to exports
    - Link tests to tested code
    - Link services to entrypoints
    
  Phase4_FaultDetection:
    PackagingIssues:
      - Missing __init__.py
      - Wrong package discovery
      - Broken console scripts
      - Lockfile drift
      
    ImportIssues:
      - Unresolved imports
      - Circular imports
      - Dead imports
      - Wrong relative imports
      
    PathIssues:
      - Hardcoded paths
      - CWD assumptions
      - Missing resource files
      
    TestIssues:
      - Uncollected tests
      - Missing fixtures
      - Stale snapshots
      - Workflow/test mismatch
      
    RuntimeIssues:
      - Broken entrypoints
      - Wrong defaults
      - Bad startup paths
      
    CIIssues:
      - Stale workflows
      - Wrong versions
      - Missing secrets
```

### 5.3 Autofix System

```yaml
AutofixSystem:
  
  SafetyTiers:
    
    Safe_AutoApply:
      - Missing __init__.py files
      - Wrong import paths (fixable)
      - Missing type stubs in pyproject.toml
      - Dead code removal
      - Formatting fixes
      
    Moderate_ReviewRequired:
      - Dependency version changes
      - CI workflow updates
      - Refactoring for circular imports
      
    HighRisk_ManualOnly:
      - Architecture changes
      - Schema migrations
      - Breaking API changes
      
  FixWorkflow:
    1. Generate patch
    2. Show diff preview
    3. Run tests to verify
    4. Create branch
    5. Open PR with detailed description
    6. Await human approval
```

### 5.4 Output Format

```yaml
Output:
  
  ReportStructure:
    Summary:
      - Total issues found
      - Breakdown by severity
      - Fixable automatically: N
      - Requires manual: N
      
    IssueList:
      For each issue:
        - id: UUID
        - severity: critical | high | medium | low
        - category: packaging | imports | paths | tests | runtime | ci
        - title: string
        - description: string
        - location: file:line
        - impact: string
        - fix_available: boolean
        - fix_type: auto | assisted | manual
        - fix_diff: string (if auto)
        - evidence: screenshot/log
        
    RootCauseAnalysis:
      - Fault tree visualization
      - Common causes identified
      - Recommended systematic fixes
      
    ActionPlan:
      - Prioritized fix order
      - Estimated time per fix
      - Risk assessment
```

---

## 6. AGENT SYSTEM - Complete Protocol

### 6.1 Agent Roles

```yaml
AgentRoles:
  
  repo_debugger:
    description: "Find and fix code issues"
    tools: [read_file, search_code, edit_file, run_tests, run_linter]
    scope: single_repository
    approval: never_for_safe_fixes
    
  patch_generator:
    description: "Generate code changes from requirements"
    tools: [read_file, edit_file, create_file, run_tests]
    scope: single_repository
    approval: always_for_tests
    
  test_writer:
    description: "Generate test coverage"
    tools: [read_file, edit_file, run_tests]
    scope: single_repository
    approval: never
    
  migration_planner:
    description: "Plan database or API migrations"
    tools: [read_schema, compare_schemas, generate_migration, simulate_migration]
    scope: multi_repository
    approval: always
    
  infra_debugger:
    description: "Diagnose infrastructure issues"
    tools: [read_logs, read_metrics, read_config, query_graph]
    scope: environment_specific
    approval: never_for_readonly
    
  release_manager:
    description: "Coordinate releases"
    tools: [query_graph, read_tests, trigger_deploy, rollback]
    scope: multi_repository
    approval: always
    
  observability_analyst:
    description: "Analyze metrics and logs"
    tools: [query_metrics, query_logs, query_traces, generate_report]
    scope: read_only
    approval: never
    
  incident_commander:
    description: "Coordinate incident response"
    tools: [query_graph, read_logs, rollback, page_team, create_war_room]
    scope: production
    approval: varies_by_action
    
  security_reviewer:
    description: "Review for security issues"
    tools: [read_code, scan_dependencies, check_secrets, query_cve]
    scope: read_only
    approval: never
    
  architecture_analyst:
    description: "Analyze system architecture"
    tools: [query_graph, read_docs, analyze_dependencies]
    scope: read_only
    approval: never
```

### 6.2 Action Receipt

```typescript
// Every AI action produces a receipt
interface ActionReceipt {
  receipt_id: UUID;
  
  // Actor
  agent: UUID;
  role: string;
  
  // Context
  triggered_by: UUID;        // Event that triggered this
  goal: string;              // What the agent was trying to do
  
  // Plan
  plan_id: UUID;
  plan_steps: PlanStep[];
  
  // Execution
  executed_steps: ExecutedStep[];
  
  // Objects
  objects_read: UUID[];
  objects_modified: UUID[];
  objects_created: UUID[];
  
  // Policy
  policy_checks: PolicyCheck[];
  approvals_required: Approval[];
  approvals_received: Approval[];
  
  // Testing
  tests_run: TestResult[];
  
  // Outcome
  status: 'success' | 'partial' | 'failure' | 'rolled_back';
  outputs: JSON;
  
  // Evidence
  evidence_bundle: Evidence[];
  full_trace_ipfs_hash: string;
  
  // Rollback
  rollback_available: boolean;
  rollback_procedure: string;
  
  // Cost
  tokens_used: number;
  api_calls: number;
  duration_ms: number;
  cost_usd: number;
  
  // Audit
  timestamp: timestamp;
  audit_level: 'debug' | 'info' | 'warning' | 'critical';
}
```

### 6.3 Execution Loop

```yaml
AgentExecutionLoop:
  
  Step1_Observe:
    - Collect context from event trigger
    - Query graph for related objects
    - Read relevant files/logs/metrics
    - Identify constraints and policies
    
  Step2_BuildFaultModel:
    - Analyze observations
    - Identify anomalies
    - Build hypothesis of root cause
    
  Step3_GeneratePlan:
    - Create step-by-step plan
    - Identify required tools
    - Estimate resource needs
    - Flag risky steps
    
  Step4_Simulate:
    - Dry-run plan in simulation mode
    - Predict outcomes
    - Identify conflicts
    - Calculate blast radius
    
  Step5_RequestApproval:
    - If any risky steps: request human approval
    - Show simulation results
    - Explain rationale
    - Wait for response
    
  Step6_Execute:
    - Execute approved steps
    - Record every action
    - Collect evidence
    - Handle failures gracefully
    
  Step7_Verify:
    - Run verification tests
    - Check invariants
    - Validate outcomes
    
  Step8_Report:
    - Generate action receipt
    - Update graph with changes
    - Emit events to event store
    - Notify stakeholders
```

---

## 7. COMMAND MODEL

### 7.1 Universal Commands

```yaml
CommandInterface:
  
  /inspect:
    usage: /inspect <object_type> <object_id_or_query>
    examples:
      - /inspect repo axiom-platform
      - /inspect service payment-gateway
      - /inspect incident INC-2024-001
    
  /trace:
    usage: /trace <request_id_or_correlation_id>
    shows: Full distributed trace
    
  /blast-radius:
    usage: /blast-radius <change_id>
    shows: Affected services, customers, cost impact
    
  /run:
    usage: /run <test_suite | smoke_test | benchmark>
    examples:
      - /run tests payment-service
      - /run smoke-test staging
      
  /patch:
    usage: /patch <issue_id_or_auto>
    examples:
      - /patch repo-autopsy-47
      - /patch packaging
      
  /explain:
    usage: /explain <object_type> <object_id>
    ai: Uses graph context to generate explanation
    
  /diff:
    usage: /diff <env1> <env2>
    shows: Configuration, version, traffic differences
    
  /replay:
    usage: /replay incident <incident_id>
    shows: Timeline reconstruction with all events
    
  /generate:
    usage: /generate <migration | api_client | test_suite>
    ai: Generates artifact from context
    
  /compare:
    usage: /compare <dimension> <a> <b>
    examples:
      - /compare cost staging production
      - /compare performance v1.2.0 v1.3.0
      
  /open:
    usage: /open <pr | fix-branch | incident-room>
    examples:
      - /open pr repo-autopsy-fixes
      - /open incident-room INC-2024-001
      
  /simulate:
    usage: /simulate <deploy | change | incident>
    shows: Predicted outcomes before execution
```

---

## 8. TECHNICAL ARCHITECTURE

### 8.1 Desktop App

```yaml
DesktopApp:
  Framework: Electron + React + TypeScript
  
  Architecture:
    MainProcess:
      - Node.js runtime
      - File system access
      - Shell integration
      - Git operations (via libgit2)
      - Container runtime (Docker API)
      
    RendererProcess:
      - React UI
      - Monaco editor
      - Graph visualization (D3/Cytoscape)
      
    NativeModules:
      - File watching (fs events)
      - Process spawning
      - Terminal (node-pty)
      
  LocalCapabilities:
    - Full offline mode
    - Local git operations
    - Local container execution
    - Local AI model inference (optional)
    - Encrypted local cache
    
  Sync:
    - Background sync when online
    - Conflict resolution
    - Delta sync for efficiency
```

### 8.2 Cloud Backend

```yaml
CloudBackend:
  
  ControlPlane:
    - Kubernetes (EKS/GKE)
    - Service mesh (Istio)
    - API Gateway (custom)
    
  Services:
    api:
      - GraphQL/REST API
      - Authentication
      - Rate limiting
      
    graph:
      - Neo4j cluster
      - Query optimization
      - Caching layer
      
    event:
      - Kafka cluster
      - Event processing
      - Stream analytics
      
    execution:
      - Temporal.io
      - Nomad (batch)
      - K8s jobs
      
    agent:
      - Agent scheduling
      - Sandboxed workers
      - Tool registry
      
    ai:
      - Model routing
      - Prompt management
      - Embedding service
      - Safety filtering
      
    observe:
      - Loki (logs)
      - Prometheus (metrics)
      - Jaeger (traces)
      - Grafana (dashboards)
      
  DataStores:
    - PostgreSQL: Transactional data
    - Neo4j: Graph data
    - Redis: Cache, sessions, rate limits
    - S3: Objects, event archives
    - Elasticsearch: Search index
    - Kafka: Event streaming
```

### 8.3 Deployment Architecture

```yaml
Deployment:
  
  Regions:
    - us-east-1 (primary)
    - us-west-2 (secondary)
    - eu-west-1 (EU)
    - ap-southeast-1 (APAC)
    
  Tenancy:
    - Cloud: Multi-tenant with strict isolation
    - Enterprise: Dedicated clusters
    - GovCloud: Isolated for compliance
    
  DR:
    - RPO: 5 minutes
    - RTO: 15 minutes
    - Cross-region replication
    - Automated failover
```

---

## 9. MVP ROADMAP

### 9.1 Phase 1: Foundation (Months 1-2)

```yaml
Goals:
  - Core graph database
  - Basic object models (Repo, Symbol, Service)
  - Git integration
  - VS Code extension shell
  
Deliverables:
  - Graph API operational
  - Repo import working
  - Basic Studio layout
  - Git sync working
```

### 9.2 Phase 2: Repo Autopsy (Months 3-4)

```yaml
Goals:
  - Complete repo debugger
  - Static analysis pipeline
  - Autofix generation
  - PR creation
  
Deliverables:
  - Repo Autopsy MVP
  - Python/JS/Go support
  - Safe autofixes working
  - 10+ issue detectors
```

### 9.3 Phase 3: AI Integration (Months 5-6)

```yaml
Goals:
  - Agent runtime
  - Basic agent roles
  - Action receipts
  - Safety controls
  
Deliverables:
  - repo_debugger agent
  - patch_generator agent
  - Action logging
  - Approval workflows
```

### 9.4 Phase 4: Runtime (Months 7-8)

```yaml
Goals:
  - Execution plane
  - Environment management
  - Deployment pipeline
  - Basic observability
  
Deliverables:
  - Local execution
  - Remote execution
  - Deploy to staging
  - Log/metric collection
```

### 9.5 Beta Launch (Month 9)

```yaml
Beta:
  - 100 design partners
  - Python/JS focus
  - Repo Autopsy as wedge
  - Studio + Navigator
```

---

## 10. MONETIZATION

### 10.1 Pricing Tiers

```yaml
Tiers:
  
  Free:
    - 1 user
    - 3 repos
    - Local mode only
    - Basic repo debugger
    - Community support
    
  Pro ($49/user/month):
    - Unlimited users
    - Unlimited repos
    - Cloud sync
    - AI agents (limited tokens)
    - Deploy to cloud
    - 7-day observability retention
    
  Team ($99/user/month):
    - Everything in Pro
    - Team collaboration
    - Advanced agents
    - Custom workflows
    - SSO
    - 30-day retention
    - Priority support
    
  Enterprise (custom):
    - Everything in Team
    - Dedicated infrastructure
    - Custom integrations
    - SLA guarantees
    - Unlimited retention
    - Security audit logs
    - On-prem option
```

### 10.2 Usage-Based Add-ons

```yaml
AddOns:
  - AI Tokens: $0.01 per 1K tokens
  - Compute Minutes: $0.05 per minute
  - Storage: $0.10 per GB/month
  - Bandwidth: $0.01 per GB
  - Advanced Agents: $20/agent/month
```

---

## 11. SUCCESS METRICS

### 11.1 Product Metrics

```yaml
Metrics:
  - Weekly Active Users
  - Repos imported
  - Issues detected by Autopsy
  - Issues fixed by Autopsy
  - AI actions executed
  - Deploys through platform
  - Incidents resolved
  - Time to root cause (reduction)
```

### 11.2 Business Metrics

```yaml
Metrics:
  - MRR/ARR
  - NRR (Net Revenue Retention)
  - CAC
  - LTV
  - Payback period
  - Gross margin
  - Enterprise deals
```

---

## 12. RISK MITIGATION

### 12.1 Technical Risks

```yaml
Risks:
  - Graph scalability: Shard by tenant, use read replicas
  - AI safety: Sandboxed execution, mandatory approvals
  - Security: SOC2, pen testing, bug bounty
  - Reliability: Multi-region, automated failover
```

### 12.2 Market Risks

```yaml
Risks:
  - Incumbents respond: Focus on integration depth
  - Developer skepticism: Build trust with transparency
  - AI backlash: Emphasize human control
```

---

## 13. CONCLUSION

This specification transforms AXIOM ONE from vision to buildable reality.

**The path:**
1. Build Repo Autopsy MVP (wedge)
2. Layer on IDE integration
3. Add AI agents with safety
4. Expand to full platform

**The moat:**
- Canonical object graph (network effects)
- Event-sourced audit trail (trust)
- Bounded AI labor (differentiation)
- Business impact mapping (enterprise value)

**The destination:**
A unified technical operating system that makes building, understanding, running, and governing software coherent, reversible, and observable.

---

**Document Version:** 1.0.0  
**Last Updated:** 2024-04-19  
**Next Review:** After MVP scoping  
**Owner:** Engineering Architecture
