# AMOS Fast/Slow Thinking Optimization Fix
## Based on Research: "Agents Thinking Fast and Slow" Architecture

---

## Problem Diagnosis

### Why Thinking/Indexing Takes So Long

1. **Single-Process Architecture**: AMOS currently only uses "slow thinking" (System 2) - the deliberative Thinking Kernel that iterates through multiple steps
2. **No Fast Path**: Missing System 1 (fast, intuitive, pattern-based responses)
3. **Sequential Processing**: Indexing and thinking happen sequentially, not in parallel
4. **No Response Tiering**: All queries get full depth analysis regardless of complexity
5. **Cache Underutilization**: Speed Engine exists but isn't integrated with thinking pipeline

### Research Evidence

From **"Agents Thinking Fast and Slow: A Talker-Reasoner Architecture"** (Google Research, 2024):

> "The Talker (System 1): The fast agent that interacts via language, perceives the world, gets observations...  
> The Reasoner (System 2): The slow and deliberative agent responsible for complex problem solving...  
> The Talker and Reasoner interact through memory. The Reasoner generates beliefs; the Talker retrieves them."

---

## Solution Architecture

### Core Fix: Dual-Process Thinking System

```
┌─────────────────────────────────────────────────────────────┐
│                    AMOS Dual-Brain                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐         ┌──────────────────┐           │
│  │  FAST (System 1) │         │ SLOW (System 2)  │           │
│  │  Talker Brain    │         │ Reasoner Brain   │           │
│  ├──────────────────┤         ├──────────────────┤           │
│  │ • Vector Search  │         │ • Thinking Kernel│           │
│  │ • Pattern Cache  │         │ • Deep Analysis  │           │
│  │ • Quick Match    │         │ • Multi-step     │           │
│  │ • <100ms response│         │ • <5s response   │           │
│  └────────┬─────────┘         └────────┬─────────┘           │
│           │                          │                      │
│           └──────────┬───────────────┘                      │
│                      │                                     │
│              ┌───────▼────────┐                           │
│              │  Belief Memory │ ← Shared State             │
│              └────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Fast Thinking Path (System 1)

```python
# amos_fast_thinking.py - NEW MODULE
"""
AMOS Fast Thinking (System 1)
- Pattern matching via vector search
- Cached response retrieval
- <100ms response time
"""

class FastThinkingEngine:
    """System 1: Fast, intuitive, pattern-based thinking."""
    
    def __init__(self):
        self.vector_service = get_vector_service()
        self.cache = get_cache()
        self.latency_budget_ms = 100  # Hard limit
        
    async def think_fast(self, query: str, context: dict) -> FastThinkingResult:
        """
        Execute fast thinking path.
        
        Pipeline:
        1. Cache check (10ms)
        2. Vector semantic search (30ms)
        3. Pattern matching (20ms)
        4. Confidence scoring (10ms)
        5. Response assembly (30ms)
        """
        start = time.perf_counter()
        
        # 1. L1 Cache check
        cache_key = self._hash_query(query, context)
        cached = await self.cache.get(f"fast_think:{cache_key}")
        if cached and cached['confidence'] > 0.8:
            return FastThinkingResult(
                response=cached['response'],
                confidence=cached['confidence'],
                source="cache",
                latency_ms=self._elapsed(start)
            )
        
        # 2. Vector search for similar patterns
        similar = await self.vector_service.semantic_search(
            query=query,
            content_types=[ContentType.CONVERSATION, ContentType.KNOWLEDGE],
            top_k=3,
            tenant_id=context.get('workspace_id')
        )
        
        # 3. Pattern matching with confidence
        if similar and similar[0].similarity_score > 0.85:
            pattern = similar[0]
            result = FastThinkingResult(
                response=self._adapt_pattern(pattern, query),
                confidence=pattern.similarity_score,
                source="vector_search",
                latency_ms=self._elapsed(start),
                matched_pattern=pattern.id
            )
            
            # Cache for next time
            await self.cache.set(
                f"fast_think:{cache_key}",
                {'response': result.response, 'confidence': result.confidence},
                ttl=300
            )
            return result
        
        # Fast path failed - delegate to slow thinking
        return FastThinkingResult(
            response=None,
            confidence=0.0,
            source="fallback_to_slow",
            latency_ms=self._elapsed(start)
        )
```

### Phase 2: Parallel Indexing + Thinking

```python
# amos_parallel_cognition.py - NEW MODULE
"""
Parallel cognition: Indexing and thinking simultaneously
"""

import asyncio
from dataclasses import dataclass

@dataclass
class CognitionJob:
    query: str
    context: dict
    priority: str = "normal"  # flash, normal, deep

class ParallelCognitionEngine:
    """
    Run indexing and thinking in parallel.
    
    Traditional:  Index (500ms) → Think (2000ms) = 2500ms
    Parallel:    Index (500ms) ═══════════════════
                 Think (2000ms)  ═══════════════════
                 Total: 2000ms (max, not sum)
    """
    
    def __init__(self):
        self.fast_engine = FastThinkingEngine()
        self.slow_kernel = ThinkingKernel()
        self.index_engine = get_index_engine()
        
    async def process(self, job: CognitionJob) -> ThinkingResult:
        """Process with parallel indexing and thinking."""
        
        # Always try fast path first (<100ms)
        fast_result = await self.fast_engine.think_fast(job.query, job.context)
        
        if fast_result.confidence > 0.8 and job.priority == "flash":
            # Flash priority: return immediately if confident
            return ThinkingResult(
                response=fast_result.response,
                thinking_time_ms=fast_result.latency_ms,
                mode="fast"
            )
        
        # Start parallel tasks
        index_task = asyncio.create_task(
            self.index_engine.index_query(job.query, job.context)
        )
        
        slow_task = asyncio.create_task(
            self._run_slow_thinking(job, fast_result)
        )
        
        # Wait for slow thinking (indexing continues in background)
        slow_result = await slow_task
        
        # Index result available for next query
        index_result = await index_task  # Usually completes before slow
        
        # Enrich result with index findings
        if index_result.relevant_chunks:
            slow_result.enriched_context = index_result.relevant_chunks
            
        return slow_result
```

### Phase 3: Tiered Response System

```python
# Integrated with existing amos_speed_engine.py

class TieredThinkingManager:
    """
    Route queries to appropriate thinking tier.
    """
    
    TIERS = {
        "T1_FLASH": {
            "max_latency_ms": 250,
            "thinking_depth": "none",  # Pure pattern match
            "use_fast": True,
            "use_slow": False,
        },
        "T2_QUICK": {
            "max_latency_ms": 1000,
            "thinking_depth": "shallow",  # 2-3 iterations
            "use_fast": True,
            "use_slow": True,
        },
        "T3_DEEP": {
            "max_latency_ms": 5000,
            "thinking_depth": "full",  # 10 iterations
            "use_fast": True,
            "use_slow": True,
        }
    }
    
    def select_tier(self, query: str, context: dict) -> str:
        """Auto-select tier based on query characteristics."""
        
        # Simple heuristic classification
        if any(kw in query.lower() for kw in ['quick', 'fast', 'tldr', 'brief']):
            return "T1_FLASH"
            
        if any(kw in query.lower() for kw in ['analyze', 'deep', 'complex', 'architect']):
            return "T3_DEEP"
            
        # Check complexity indicators
        complexity_score = self._assess_complexity(query)
        if complexity_score < 0.3:
            return "T1_FLASH"
        elif complexity_score > 0.7:
            return "T3_DEEP"
            
        return "T2_QUICK"
```

### Phase 4: Smart Caching Strategy

```python
# Enhanced caching for thinking patterns

class ThinkingCache:
    """
    Multi-tier cache for thinking operations.
    
    L1: In-memory (1ms access) - Fast patterns
    L2: Redis (10ms access) - Common queries
    L3: Vector DB (50ms access) - Semantic similarity
    """
    
    async def get_or_think(self, query: str, context: dict) -> ThinkingResult:
        """Try cache before thinking."""
        
        # L1: Exact match
        cache_key = hashlib.sha256(f"{query}:{json.dumps(context, sort_keys=True)}".encode()).hexdigest()
        
        l1_result = self.l1_cache.get(cache_key)
        if l1_result:
            return l1_result
        
        # L2: Vector similarity
        l2_result = await self.l2_cache.semantic_get(query, threshold=0.95)
        if l2_result:
            self.l1_cache.set(cache_key, l2_result)  # Promote to L1
            return l2_result
        
        # Miss: Execute thinking and cache
        result = await self._execute_thinking(query, context)
        
        # Store in both caches
        self.l1_cache.set(cache_key, result, ttl=300)
        await self.l2_cache.semantic_set(query, result, ttl=3600)
        
        return result
```

---

## Specific Fixes for Current Code

### Fix 1: Integrate Speed Engine with Thinking Kernel

```python
# amos_thinking_kernel.py - MODIFICATION

class ThinkingKernel:
    def __init__(self, enable_meta_thinking: bool = True, speed_mode: str = "balanced"):
        self.operators = ThinkingOperators()
        self.meta_operators = MetaThinkingOperators()
        self.enable_meta_thinking = enable_meta_thinking
        self.meta_state = MetaThinkingState()
        
        # NEW: Speed integration
        self.speed_engine = SpeedEngine()
        self.selected_profile = self.speed_engine.select_profile("medium", speed_mode)
        
        # NEW: Apply speed limits
        self.max_iterations = self.selected_profile.max_reasoning_depth
        self.time_budget_ms = self.selected_profile.max_tokens * 2  # Approximate
```

### Fix 2: Vector Search Integration

```python
# amos_thinking_kernel.py - ADD to ThinkingOperators

@staticmethod
async def fast_retrieve(state: ThinkingState, query: str) -> ThinkingState:
    """
    FAST retrieval: Vector search for instant memory activation.
    
    Replaces slow keyword search with semantic vector search.
    """
    new_state = state.copy()
    
    # Use vector search service
    vector_service = get_vector_service()
    results = await vector_service.semantic_search(
        query=query,
        content_types=[ContentType.KNOWLEDGE, ContentType.DOCUMENT],
        top_k=5
    )
    
    # Add to workspace immediately
    for result in results:
        item = WorkspaceItem(
            id=f"vec_{result.id}",
            content=result.content,
            activation=result.similarity_score,
            source="vector_memory"
        )
        if len(new_state.workspace.active_items) < new_state.workspace.capacity_limit:
            new_state.workspace.active_items.append(item)
    
    new_state.transition_state.last_operation = "fast_retrieve"
    return new_state
```

### Fix 3: Pre-fetching During User Typing

```python
# amos_predictive_thinking.py - NEW MODULE

class PredictiveThinkingEngine:
    """
    Start thinking before user finishes typing.
    """
    
    async def on_partial_input(self, partial_query: str, context: dict):
        """
        Called as user types. Starts indexing and preliminary thinking.
        """
        # Index the partial query for context
        asyncio.create_task(self.index_engine.pre_index(partial_query))
        
        # Pre-activate relevant memories
        similar = await self.vector_service.semantic_search(
            query=partial_query,
            top_k=3
        )
        
        # Pre-warm cache with likely responses
        for pattern in similar:
            asyncio.create_task(self._prewarm_cache(pattern))
    
    async def on_complete_input(self, full_query: str, context: dict) -> ThinkingResult:
        """
        Called when user submits. Much faster due to pre-computation.
        """
        # Cancel pre-computation if wrong direction
        # Return fast result using pre-warmed cache
        return await self.fast_engine.think_fast(full_query, context)
```

---

## Performance Targets

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Simple Query | 2000ms | 100ms | **20x** |
| Medium Query | 3500ms | 800ms | **4.4x** |
| Complex Query | 5000ms | 2500ms | **2x** |
| Cache Hit | N/A | <50ms | Instant |
| Vector Search | N/A | <30ms | Fast retrieval |

---

## Implementation Priority

1. **P0 - Fast Path (1 day)**
   - Integrate vector search with thinking kernel
   - Add cache check before thinking
   - Implement tier selection

2. **P1 - Parallel Processing (2 days)**
   - Run indexing + thinking in parallel
   - Add predictive pre-fetching
   - Background cache warming

3. **P2 - Full Dual-System (3 days)**
   - Separate Talker/Reasoner agents
   - Shared belief memory
   - Automatic tier switching

---

## Verification

```python
# Test fast path
async def test_fast_thinking():
    engine = FastThinkingEngine()
    
    # Should complete in <100ms
    result = await engine.think_fast("What is 2+2?", {})
    assert result.latency_ms < 100
    assert result.confidence > 0.8

# Test tier selection
def test_tier_selection():
    manager = TieredThinkingManager()
    
    assert manager.select_tier("Quick summary?", {}) == "T1_FLASH"
    assert manager.select_tier("Deep architectural analysis", {}) == "T3_DEEP"
```

---

## Summary

**Root Cause**: Single-process slow-thinking architecture without fast path optimization.

**Solution**: Implement dual-process "Fast and Slow" thinking architecture with:
1. System 1 (Fast): Vector search + cache for <100ms responses
2. System 2 (Slow): Deep thinking kernel for complex analysis
3. Parallel execution: Indexing + thinking simultaneously
4. Tiered responses: Flash/Quick/Deep based on query complexity

**Expected Result**: 2-20x speedup depending on query type, with simple queries becoming nearly instantaneous.
