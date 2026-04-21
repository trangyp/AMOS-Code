"""AMOS Kernel API Server - Entry point for FastAPI server."""

import uvicorn

from amos_kernel import create_kernel_app


def main():
    """Run the kernel API server."""
    app = create_kernel_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
