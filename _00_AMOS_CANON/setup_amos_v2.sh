#!/usr/bin/env bash
set -e

# 1. create v2 skeleton
mkdir -p _AMOS_SYSTEM_V2/amos_os/core
mkdir -p _AMOS_SYSTEM_V2/amos_os/configs
mkdir -p _AMOS_SYSTEM_V2/amos_os/personality
mkdir -p _AMOS_SYSTEM_V2/amos_os/routing
mkdir -p _AMOS_SYSTEM_V2/amos_os/bindings

mkdir -p _AMOS_SYSTEM_V2/engines/domains/tech
mkdir -p _AMOS_SYSTEM_V2/engines/domains/business
mkdir -p _AMOS_SYSTEM_V2/packs
mkdir -p _AMOS_SYSTEM_V2/archive
mkdir -p _AMOS_SYSTEM_V2/schemas
mkdir -p _AMOS_SYSTEM_V2/registries

# 2. brain root + core layers (empty JSON skeletons)
cat > _AMOS_SYSTEM_V2/amos_os/core/amos_brain_root.json << 'EOF'
{
  "name": "AMOS_BRAIN_ROOT",
  "version": "v2.0.0",
  "layers": [
    "amos_cognition.json",
    "amos_emotion.json",
    "amos_super_consciousness_engine.json",
    "amos_quantum_logic_core.json",
    "amos_perception_layer.json",
    "amos_task_inference_core.json",
    "amos_context_builder_core.json",
    "amos_structural_model_core.json",
    "amos_planning_core.json",
    "amos_expression_core.json",
    "amos_memory_layer.json",
    "amos_decision_policy_core.json",
    "amos_ubi_abi_core.json",
    "amos_evaluation_layer.json",
    "amos_meta_cognition.json"
  ]
}
EOF

for f in \
  amos_cognition \
  amos_emotion \
  amos_super_consciousness_engine \
  amos_quantum_logic_core \
  amos_perception_layer \
  amos_task_inference_core \
  amos_context_builder_core \
  amos_structural_model_core \
  amos_planning_core \
  amos_expression_core \
  amos_memory_layer \
  amos_decision_policy_core \
  amos_ubi_abi_core \
  amos_evaluation_layer \
  amos_meta_cognition
do
  cat > "_AMOS_SYSTEM_V2/amos_os/core/${f}.json" << EOF
{
  "name": "${f}",
  "version": "v2.0.0",
  "type": "brain_layer",
  "status": "draft",
  "description": "",
  "spec": {}
}
EOF
done

# 3. tech/dev master engine
cat > _AMOS_SYSTEM_V2/engines/domains/tech/amos_tech_dev_master_engine.json << 'EOF'
{
  "name": "AMOS_Tech_Dev_Master_Engine",
  "version": "v1.0.0",
  "description": "Unified engine for coding, architecture, infra, DevOps, QA and automation.",
  "sources": {
    "coding": [
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/CODING_GODMODE.json",
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/Coding_Kernel.json"
    ],
    "architecture": [
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/Tech_Architecture_Kernel.json"
    ],
    "infra": [
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/Cloud_Platform_Kernel.json",
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/DevOps_Infra_Kernel.json"
    ],
    "qa": [
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/QA_Testing_Kernel.json"
    ],
    "automation": [
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/Automation_Kernel.json",
      "_AMOS_SYSTEM/DOMAINS/TECH_SYSTEMS/Workflow_Orchestration_Kernel.json"
    ]
  },
  "capabilities": [
    "full_stack_design",
    "system_architecture",
    "api_design",
    "data_engineering",
    "ml_engineering",
    "devops_ci_cd",
    "quality_assurance",
    "automation_and_orchestration"
  ],
  "routing_rules": {
    "code_generation": ["coding", "architecture"],
    "system_design": ["architecture", "infra"],
    "pipeline_orchestration": ["automation", "infra"],
    "testing": ["qa"]
  }
}
EOF

# 4. registries
cat > _AMOS_SYSTEM_V2/registries/engine_registry.json << 'EOF'
{
  "brain": [
    "amos_os/core/amos_brain_root.json"
  ],
  "tech": [
    "engines/domains/tech/amos_tech_dev_master_engine.json"
  ],
  "business": []
}
EOF

cat > _AMOS_SYSTEM_V2/registries/agent_registry.json << 'EOF'
{
  "agents": []
}
EOF

cat > _AMOS_SYSTEM_V2/registries/brain_registry.json << 'EOF'
{
  "core": [
    "amos_os/core/amos_brain_root.json"
  ]
}
EOF

echo "AMOS v2 skeleton created in _AMOS_SYSTEM_V2/"
