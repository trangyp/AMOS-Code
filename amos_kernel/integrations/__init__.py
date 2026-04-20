"""Integrations - Connect kernel to existing AMOS components"""

from .equation_bridge import KernelEquationBridge, get_equation_bridge, normalize, softmax
from .facade_bridge import KernelBrainResponse, KernelFacadeClient, get_kernel_client

__all__ = [
    # Equation bridge
    "KernelEquationBridge",
    "get_equation_bridge",
    "softmax",
    "normalize",
    # Facade bridge
    "KernelFacadeClient",
    "KernelBrainResponse",
    "get_kernel_client",
]
