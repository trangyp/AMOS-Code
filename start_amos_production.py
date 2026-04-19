#!/usr/bin/env python3
"""
AMOS SuperBrain Production Startup Script

Ensures proper initialization of all subsystems before starting the API.
"""

import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def initialize_amos():
    """Initialize AMOS SuperBrain with all subsystems."""
    logger.info("=" * 60)
    logger.info("AMOS SuperBrain v3.0 - Production Startup")
    logger.info("=" * 60)

    try:
        # Import brain components
        from amos_brain.super_brain import get_super_brain as get_brain_instance

        logger.info("Step 1: Loading SuperBrain...")
        brain = get_brain_instance()
        logger.info(f"  ✓ Brain instance: {type(brain).__name__}")

        # Initialize subsystems
        logger.info("Step 2: Initializing subsystems...")

        # Initialize kernel router
        try:
            from amos_brain.kernel_router import get_kernel_router

            kernel = get_kernel_router()
            logger.info(f"  ✓ Kernel Router: {'Active' if kernel else 'Standby'}")
        except Exception as e:
            logger.warning(f"  ⚠ Kernel Router: {e}")

        # Initialize tool registry
        try:
            from amos_brain.tools import ToolRegistry
            from amos_brain.tools_extended import (
                calculate,
                code_analyzer,
                database_query,
                file_read_write,
                git_operations,
                performance_profiler,
                security_scanner,
                web_search,
            )

            registry = ToolRegistry()
            registry.register("calculate", calculate)
            registry.register("file_rw", file_read_write)
            registry.register("db_query", database_query)
            registry.register("web_search", web_search)
            registry.register("git_ops", git_operations)
            registry.register("code_analyzer", code_analyzer)
            registry.register("security_scan", security_scanner)
            registry.register("perf_profile", performance_profiler)
            logger.info(f"  ✓ Tool Registry: {len(registry.list_tools())} tools")
        except Exception as e:
            logger.warning(f"  ⚠ Tool Registry: {e}")

        # Initialize model router
        try:
            from amos_brain.model_router import ModelRouter

            router = ModelRouter()
            logger.info("  ✓ Model Router: Ready")
        except Exception as e:
            logger.warning(f"  ⚠ Model Router: {e}")

        # Check final health
        logger.info("Step 3: Health check...")
        state = brain.get_state()
        health_score = getattr(state, "health_score", 0.0)
        logger.info(f"  ✓ Health Score: {health_score * 100:.1f}%")

        logger.info("=" * 60)
        logger.info("Initialization Complete")
        logger.info("=" * 60)

        return brain, state

    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


def start_api_server():
    """Start the FastAPI server."""
    import uvicorn

    from amos_superbrain_api import app

    logger.info("Starting API server on http://localhost:8000")
    logger.info("API documentation: http://localhost:8000/docs")

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


async def main():
    """Main entry point."""
    try:
        # Initialize the brain
        brain, state = await initialize_amos()

        # Start the API server
        start_api_server()

    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
