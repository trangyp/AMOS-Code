"""Adapters - Bridge legacy amos_brain to kernel-first architecture"""

from .legacy_bridge import KernelAdapter, get_kernel_adapter

__all__ = ["KernelAdapter", "get_kernel_adapter"]
