#!/usr/bin/env python3
"""AMOS Streamlit Dashboard v1.0.0
=================================

Modern web dashboard for the AMOS Cognitive Operating System.
Built with Streamlit for Python-native integration.

Pages:
  - Overview: System status, component health
  - Agents: Spawn and monitor agents
  - Memory: Visualize 5-tier memory
  - Tools: Execute MCP tools
  - Laws: Monitor L1-L6 compliance
  - Chat: Direct agent conversation
  - Evolution: Self-evolution oversight

Features:
  - Real-time status updates
  - Interactive agent spawning
  - Memory visualization with charts
  - Tool execution interface
  - Law compliance tracking
  - Session persistence

Usage:
  streamlit run amos_streamlit_dashboard.py

Requirements:
  pip install streamlit pandas plotly

Author: Trang Phan
Version: 1.0.0
"""

import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Try to import streamlit
try:
    import pandas as pd
    import streamlit as st
except ImportError:
    print("Error: streamlit not installed. Run: pip install streamlit pandas")
    sys.exit(1)

# Page config
st.set_page_config(
    page_title="AMOS Dashboard", page_icon="🧠", layout="wide", initial_sidebar_state="expanded"
)


# Initialize AMOS systems
@st.cache_resource
def get_amos_system():
    """Initialize AMOS unified system."""
    try:
        from amos_unified_system import AMOSUnifiedSystem

        amos = AMOSUnifiedSystem()
        amos.initialize()
        return amos
    except Exception as e:
        st.error(f"Failed to initialize AMOS: {e}")
        return None


@st.cache_resource
def get_mcp_toolkit():
    """Initialize MCP toolkit."""
    try:
        from amos_mcp_tools import AMOSMCPToolkit

        return AMOSMCPToolkit()
    except Exception as e:
        st.error(f"Failed to initialize MCP Tools: {e}")
        return None


# Sidebar navigation
st.sidebar.title("🧠 AMOS Dashboard")
st.sidebar.markdown("*Cognitive Operating System v2.0*")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "🤖 Agents", "🧠 Memory", "🔧 Tools", "⚖️ Laws", "💬 Chat", "🔄 Evolution"],
)

# Initialize systems
amos = get_amos_system()
tools = get_mcp_toolkit()

# ── PAGE: Overview ─────────────────────────────────────────────────────────

if page == "📊 Overview":
    st.title("📊 System Overview")
    st.markdown("---")

    if amos:
        status = amos.get_status()

        # Key metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Neural Providers", status.get("neural_providers", 0), "9 cloud + 7 local")

        with col2:
            st.metric("Active Agents", status.get("active_agents", 0), "Ready to spawn")

        with col3:
            st.metric("Available Tools", status.get("available_tools", 0), "MCP integrated")

        with col4:
            st.metric("Laws Active", len(status.get("laws_active", [])), "L1-L6 enforcing")

        st.markdown("---")

        # Component status
        st.subheader("Component Status")

        components = {
            "Neural Substrate": status.get("neural_ready", False),
            "Symbolic Laws": status.get("symbolic_ready", False),
            "Hybrid Orchestrator": status.get("orchestrator_ready", False),
            "MCP Bridge": status.get("mcp_ready", False),
        }

        cols = st.columns(len(components))
        for i, (name, ready) in enumerate(components.items()):
            with cols[i]:
                if ready:
                    st.success(f"✓ {name}")
                else:
                    st.error(f"✗ {name}")

        # System info
        st.markdown("---")
        st.subheader("System Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.json(
                {
                    "initialized": status.get("initialized", False),
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0",
                }
            )

        with info_col2:
            st.markdown("""
            **Architecture:** Hybrid Neural-Symbolic

            **Components:**
            - 5-Tier Memory System
            - 3-Paradigm Orchestrator
            - 10 MCP Tools
            - 27-Dim Repo Doctor
            - Self-Evolution Engine
            """)
    else:
        st.warning("AMOS system not initialized. Check logs.")

# ── PAGE: Agents ────────────────────────────────────────────────────────────

elif page == "🤖 Agents":
    st.title("🤖 Agent Management")
    st.markdown("---")

    # Spawn new agent
    st.subheader("Spawn New Agent")

    col1, col2, col3 = st.columns(3)

    with col1:
        agent_role = st.selectbox(
            "Agent Role", ["architect", "reviewer", "synthesizer", "auditor", "executor"]
        )

    with col2:
        agent_paradigm = st.selectbox("Paradigm", ["HYBRID", "SYMBOLIC", "NEURAL"])

    with col3:
        if st.button("🚀 Spawn Agent", type="primary"):
            if amos:
                try:
                    agent = amos.spawn_agent(agent_role, agent_paradigm)
                    st.success(f"Agent spawned: {agent.name} ({agent.agent_id})")
                    st.session_state["last_agent"] = agent
                except Exception as e:
                    st.error(f"Failed to spawn agent: {e}")
            else:
                st.error("AMOS not initialized")

    # Active agents
    st.markdown("---")
    st.subheader("Active Agents")

    if amos and hasattr(amos, "_agents"):
        agents = amos._agents
        if agents:
            agent_data = []
            for aid, agent in agents.items():
                agent_data.append(
                    {
                        "ID": agent.agent_id[:8],
                        "Name": agent.name,
                        "Role": agent.role,
                        "Paradigm": agent.paradigm.name,
                        "Capabilities": len(agent.capabilities.strengths),
                    }
                )

            df = pd.DataFrame(agent_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No active agents. Spawn one above.")
    else:
        st.info("Agent tracking not available.")

# ── PAGE: Memory ───────────────────────────────────────────────────────────

elif page == "🧠 Memory":
    st.title("🧠 Memory System")
    st.markdown("---")

    try:
        from amos_memory_system import AMOSMemoryManager

        memory = AMOSMemoryManager()

        summary = memory.get_memory_summary()

        # Memory tiers
        st.subheader("5-Tier Memory Architecture")

        col1, col2, col3, col4, col5 = st.columns(5)

        tiers = [
            ("Working", summary.get("working_memory_items", 0), "#FF6B6B"),
            ("Short-term", summary.get("short_term_items", 0), "#4ECDC4"),
            ("Episodic", summary.get("episodic_count", 0), "#45B7D1"),
            ("Semantic", summary.get("semantic_facts", 0), "#96CEB4"),
            ("Procedural", summary.get("procedural_workflows", 0), "#FFEAA7"),
        ]

        for col, (name, count, color) in zip([col1, col2, col3, col4, col5], tiers):
            with col:
                st.markdown(
                    f"""
                    <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;">
                        <h3 style="color: white; margin: 0;">{name}</h3>
                        <p style="color: white; font-size: 24px; margin: 0;">{count}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # Session info
        st.subheader("Session Information")
        st.json(
            {
                "session_id": summary.get("session_id", "unknown"),
                "storage_root": summary.get("storage_root", "unknown"),
                "persistence": summary.get("persistence_enabled", False),
            }
        )

    except Exception as e:
        st.error(f"Memory system not available: {e}")

# ── PAGE: Tools ─────────────────────────────────────────────────────────────

elif page == "🔧 Tools":
    st.title("🔧 MCP Tool Execution")
    st.markdown("---")

    if tools:
        available_tools = tools.list_tools()

        # Tool selection
        st.subheader("Select Tool")

        tool_names = [t["name"] for t in available_tools]
        selected_tool = st.selectbox("Tool", tool_names)

        # Tool parameters
        st.subheader("Parameters")

        params = {}

        if selected_tool == "filesystem.read":
            params["path"] = st.text_input("Path", value=".")

        elif selected_tool == "filesystem.write":
            params["path"] = st.text_input("Path")
            params["content"] = st.text_area("Content")

        elif selected_tool == "filesystem.search":
            params["pattern"] = st.text_input("Search Pattern")
            params["path"] = st.text_input("Path", value=".")

        elif selected_tool in ["git.status", "git.log", "git.diff"]:
            st.info("No parameters required for git commands")

        elif selected_tool == "web.search":
            params["query"] = st.text_input("Search Query")
            params["num_results"] = st.slider("Results", 1, 10, 5)

        elif selected_tool == "web.fetch":
            params["url"] = st.text_input("URL")

        elif selected_tool == "code.analyze":
            params["code"] = st.text_area("Code to analyze")
            params["language"] = st.selectbox("Language", ["python", "javascript"])

        elif selected_tool == "database.query":
            params["sql"] = st.text_area("SQL Query (SELECT only)")

        # Execute
        if st.button("▶️ Execute", type="primary"):
            with st.spinner("Executing..."):
                result = tools.execute(selected_tool, **params)

                if result.success:
                    st.success("Execution successful")
                    st.text_area("Output", result.content, height=300)

                    with st.expander("Metadata"):
                        st.json(result.metadata)
                else:
                    st.error(f"Execution failed: {result.error}")
    else:
        st.warning("MCP Toolkit not initialized")

# ── PAGE: Laws ──────────────────────────────────────────────────────────────

elif page == "⚖️ Laws":
    st.title("⚖️ Global Laws L1-L6")
    st.markdown("---")

    laws_info = {
        "L1": ("Law of Law", "All actions must comply with safety constraints"),
        "L2": ("Rule of 2", "Dual perspective required for critical decisions"),
        "L3": ("Rule of 4", "Quadrant analysis for comprehensive coverage"),
        "L4": ("Absolute Structural Integrity", "Repository state must be maintained"),
        "L5": ("Post-Theory Communication", "Clear communication of reasoning"),
        "L6": ("UBI Alignment", "Alignment with universal benefit principles"),
    }

    st.subheader("Active Laws")

    for law_id, (name, desc) in laws_info.items():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"### {law_id}")
            with col2:
                st.markdown(f"**{name}**")
                st.caption(desc)
        st.markdown("---")

    # Action validation
    st.subheader("Validate Action")

    action_to_validate = st.text_input("Action to validate")

    if st.button("✓ Validate"):
        if amos:
            result = amos.validate_action(action_to_validate)

            if result["compliant"]:
                st.success("✅ Action is compliant with all laws")
            else:
                st.error("❌ Action violates laws")
                st.json(result.get("violations", []))
        else:
            st.error("AMOS not initialized")

# ── PAGE: Chat ─────────────────────────────────────────────────────────────

elif page == "💬 Chat":
    st.title("💬 Agent Conversation")
    st.markdown("---")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Chat interface
    st.subheader("Chat with AMOS Agents")

    # Display history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input
    prompt = st.chat_input("Type your message...")

    if prompt:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                if amos:
                    try:
                        result = amos.execute(
                            prompt, agents=["architect", "reviewer"], require_consensus=True
                        )

                        response = result.get("final_decision", "No response generated")
                        st.write(response)

                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": response}
                        )

                        # Show metadata
                        with st.expander("Response Metadata"):
                            st.json(
                                {
                                    "orchestration_id": result.get("orchestration_id"),
                                    "law_compliant": result.get("law_compliant"),
                                    "paradigms": result.get("paradigms"),
                                    "agents_used": result.get("agents_used"),
                                }
                            )

                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("AMOS not initialized")

# ── PAGE: Evolution ────────────────────────────────────────────────────────

elif page == "🔄 Evolution":
    st.title("🔄 Self-Evolution Engine")
    st.markdown("---")

    try:
        from amos_self_evolution import AMOSSelfEvolutionEngine

        st.subheader("Evolution Status")

        if "evolution_engine" not in st.session_state:
            st.session_state.evolution_engine = AMOSSelfEvolutionEngine()

        engine = st.session_state.evolution_engine
        status = engine.get_status()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Proposals", status.get("proposals_total", 0))

        with col2:
            st.metric("Validated", status.get("proposals_validated", 0))

        with col3:
            st.metric("Applied", status.get("proposals_applied", 0))

        st.markdown("---")

        # Run evolution
        st.subheader("Run Evolution Cycle")

        dry_run = st.checkbox("Dry Run (no actual changes)", value=True)

        if st.button("🔄 Run Evolution", type="primary"):
            with st.spinner("Running evolution cycle..."):
                result = engine.run_evolution_cycle(dry_run=dry_run)

                st.success("Evolution cycle complete")
                st.json(result)

        st.info("Note: Evolution requires careful review. Always run with dry_run=True first.")

    except Exception as e:
        st.error(f"Self-evolution engine not available: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("AMOS v2.0.0 | Hybrid Neural-Symbolic AI")
st.sidebar.caption("© 2025 Trang Phan")

# Auto-refresh status
if page == "📊 Overview":
    time.sleep(1)
    st.rerun()
