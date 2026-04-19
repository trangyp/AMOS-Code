# UBI-LLM Cognitive Bridge Architecture

**Status:** ✅ Implemented  
**Date:** 2024-01-15  
**Owner:** Trang  

## Overview

The UBI-LLM Cognitive Bridge implements the **Perception → Cognition → Action** pattern from cognitive architecture research, connecting AMOS's biological intelligence analysis to LLM interactions.

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE LOOP                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PERCEPTION        COGNITION           ACTION                    │
│  ┌──────────┐    ┌──────────┐      ┌──────────┐               │
│  │  UBI     │    │   LLM    │      │  UI/UX   │               │
│  │ Engine   │ →  │ Provider │  →   │ Response │               │
│  │          │    │          │      │          │               │
│  │ • NBI    │    │ Context  │      │ • Font   │               │
│  │ • NEI    │    │ Injection│      │ • Tone   │               │
│  │ • SI     │    │          │      │ • Layout │               │
│  │ • BEI    │    │          │      │          │               │
│  └──────────┘    └──────────┘      └──────────┘               │
│       ↑                                  ↓                       │
│       └────────── Feedback Loop ────────┘                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. UBI Engine (Perception Layer)

| Domain | Full Name | Function | Risk Flags |
|--------|-----------|----------|------------|
| NBI | Neurobiological Intelligence | Cognitive load, attention | `high_cognitive_load`, `moderate_cognitive_load` |
| NEI | Neuroemotional Intelligence | Stress, arousal, valence | `high_arousal`, `negative_valence` |
| SI | Somatic Intelligence | Body state, ergonomics | `posture_strain`, `fatigue_risk` |
| BEI | Bioelectromagnetic Intelligence | Environmental coupling | `sleep_disruption`, `attention_disruption` |

### 2. Cognitive Bridge (Integration Layer)

```python
class CognitiveBridge:
    """Perception → Cognition Bridge"""
    
    def analyze_user_state(self, description: str) -> CognitiveContext:
        """Analyze biological state via UBI Engine"""
        
    def enhance_prompt(self, prompt: str, context: CognitiveContext) -> str:
        """Inject biological context into LLM prompt"""
        
    def get_response_guidelines(self) -> dict:
        """Generate UI/UX guidelines based on biological state"""
```

### 3. CognitiveContext (State Representation)

```python
@dataclass
class CognitiveContext:
    cognitive_load: str    # low, medium, high
    emotional_state: str   # calm, focused, stressed
    body_comfort: str      # comfortable, strained, fatigued
    environmental_fit: str # optimal, acceptable, poor
    timestamp: datetime
```

## Prompt Injection Strategy

The bridge injects biological context into LLM prompts:

```
[AMOS Biological Context - 14:32]
- User cognitive load: high
- Emotional state: stressed
- Physical comfort: strained
- Environment: poor

Adapt response accordingly:
- High cognitive load → Simplify, bullet points, shorter sentences
- Stressed → Calm tone, reassurance, clear structure
- Physical strain → Minimize interaction steps, offer breaks
- Poor environment → Larger text, high contrast suggestions

[User Request]
{user_prompt}
```

## Response Guidelines

Based on biological state, the bridge generates UI/UX guidelines:

| State | Font Size | Line Height | Max Width | Chunking | Tone |
|-------|-----------|-------------|-----------|----------|------|
| High cognitive load | 18px | 1.8 | 600px | ✅ | Simple |
| Stressed | 16px | 1.6 | 700px | ✅ | Calm |
| Physical strain | 18px | 1.8 | 600px | ✅ | Minimal |
| Default | 16px | 1.5 | 800px | ❌ | Neutral |

## Usage Example

```python
from clawspring.amos_cognitive_bridge import analyze_and_enhance

# User describes their current state
user_context = "Feeling overwhelmed, working for 6 hours straight, screen glare"

# Enhance prompt with biological context
enhanced_prompt, guidelines = analyze_and_enhance(
    user_prompt="Explain quantum computing",
    context_description=user_context
)

# Send to LLM with biological context
response = await llm_provider.complete(enhanced_prompt)

# Render response with appropriate UI
render_response(response, guidelines)
```

## Research Basis

This architecture implements findings from:

1. **Cognitive Architectures (2024)** - Perception-Cognition-Action loop
2. **Human-Centered AI** - Biological state-aware computing
3. **UBI Framework** - Unified Biological Intelligence domains

## Integration Points

```
┌─────────────────────────────────────────────────────────┐
│                  AMOS Ecosystem                          │
├─────────────────────────────────────────────────────────┤
│  clawspring/amos_ubi_engine.py → UBI Analysis           │
│            ↓                                             │
│  clawspring/amos_cognitive_bridge.py → Context Bridge   │
│            ↓                                             │
│  backend/llm_providers.py → LLM Integration             │
│            ↓                                             │
│  Dashboard/UI → Adaptive Rendering                      │
└─────────────────────────────────────────────────────────┘
```

## Future Enhancements

1. **Real-time Biometric Integration** - Heart rate, eye tracking
2. **Longitudinal Modeling** - User state trends over time
3. **Predictive Adaptation** - Anticipate user needs
4. **Multi-modal Feedback** - Voice tone, gesture adaptation
