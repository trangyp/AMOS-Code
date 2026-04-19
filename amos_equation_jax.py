"""AMOS Equation JAX - GPU-accelerated equations with autodiff.

This module provides JAX-powered implementations of ML equations with:
- Automatic differentiation (grad, value_and_grad)
- JIT compilation for performance
- GPU/TPU acceleration
- Batch processing via vmap

Usage:
    from amos_equation_jax import JAXEquationKernel

    kernel = JAXEquationKernel()
    # Compute with gradients
    result = kernel.execute_with_grad("softmax", {"x": jnp.array([1.0, 2.0])})
    # Batch processing
    batch_result = kernel.execute_batch("softmax", batch_inputs)
"""


from typing import Any, Callable

import numpy as np

# JAX is optional - graceful degradation
try:
    import jax
    import jax.numpy as jnp
    from jax import grad, jit, vmap, value_and_grad
    JAX_AVAILABLE = True
except ImportError:
    JAX_AVAILABLE = False
    # Create dummy module
    class DummyJNP:
        @staticmethod
        def array(x): return np.array(x)
        @staticmethod
        def exp(x): return np.exp(x)
        @staticmethod
        def sum(x, **kwargs): return np.sum(x, **kwargs)
        @staticmethod
        def max(x, **kwargs): return np.max(x, **kwargs)
    jnp = DummyJNP()
    jax = None
    grad = lambda f: f
    jit = lambda f: f
    vmap = lambda f: f
    value_and_grad = lambda f: lambda *args: (f(*args), None)

from amos_equation_extended import ExtendedEquationKernel


class JAXEquationKernel(ExtendedEquationKernel):
    """JAX-accelerated equation kernel with autodiff support.

    Extends ExtendedEquationKernel with:
    - JIT-compiled implementations for speed
    - Automatic differentiation for gradients
    - Batch processing via vmap
    - GPU acceleration (if available)

    Example:
        >>> kernel = JAXEquationKernel()
        >>> # Standard computation
        >>> result = kernel.execute("softmax", {"x": jnp.array([1.0, 2.0])})
        >>> # With gradients
        >>> grad_result = kernel.compute_gradient("mse_loss", params, target)
        >>> # Batch processing
        >>> batch = jnp.array([[1.0, 2.0], [3.0, 4.0]])
        >>> batch_out = kernel.execute_batch("softmax", [{"x": b} for b in batch])
    """

    def __init__(self) -> None:
        """Initialize JAX kernel with JIT-compiled implementations."""
        super().__init__()
        self._jax_implementations: Dict[str, Callable] = {}
        self._jit_implementations: Dict[str, Callable] = {}
        self._grad_implementations: Dict[str, Callable] = {}

        if JAX_AVAILABLE:
            self._setup_jax_implementations()

    def _setup_jax_implementations(self) -> None:
        """Create JAX versions of key ML equations."""
        # JIT-compiled softmax
        @jit
        def jax_softmax(x: jnp.ndarray) -> jnp.ndarray:
            exp_x = jnp.exp(x - jnp.max(x))
            return exp_x / jnp.sum(exp_x)

        self._jax_implementations["softmax"] = jax_softmax
        self._jit_implementations["softmax"] = jax_softmax

        # Create gradient function for softmax (rarely used but available)
        self._grad_implementations["softmax"] = grad(lambda x: jnp.sum(jax_softmax(x)))

        # JIT-compiled sigmoid
        @jit
        def jax_sigmoid(x: float) -> float:
            return 1.0 / (1.0 + jnp.exp(-x))

        self._jax_implementations["sigmoid"] = jax_sigmoid
        self._jit_implementations["sigmoid"] = jit(jax_sigmoid)

        # ReLU with JIT
        @jit
        def jax_relu(x: float) -> float:
            return jnp.maximum(0.0, x)

        self._jax_implementations["relu"] = jax_relu
        self._jit_implementations["relu"] = jit(jax_relu)

        # MSE loss with gradients
        def mse_loss_fn(params: jnp.ndarray, x: jnp.ndarray, y: jnp.ndarray) -> float:
            pred = x @ params
            return jnp.mean((pred - y) ** 2)

        self._jax_implementations["mse_loss"] = mse_loss_fn
        self._grad_implementations["mse_loss"] = grad(mse_loss_fn)

        # Cross-entropy loss
        def ce_loss_fn(logits: jnp.ndarray, labels: jnp.ndarray) -> float:
            logits_max = jnp.max(logits, axis=-1, keepdims=True)
            logits_stable = logits - logits_max
            exp_logits = jnp.exp(logits_stable)
            probs = exp_logits / jnp.sum(exp_logits, axis=-1, keepdims=True)
            log_probs = jnp.log(probs + 1e-15)
            return -jnp.mean(jnp.sum(labels * log_probs, axis=-1))

        self._jax_implementations["cross_entropy_loss"] = ce_loss_fn
        self._grad_implementations["cross_entropy_loss"] = grad(ce_loss_fn)

    def is_jax_available(self) -> bool:
        """Check if JAX is available and functional."""
        return JAX_AVAILABLE

    def execute(
        self,
        name: str,
        parameters: Dict[str, Any],
        use_jit: bool = True
    ) -> Any:
        """Execute equation with optional JIT acceleration.

        Args:
            name: Equation name
            parameters: Parameters dictionary
            use_jit: Whether to use JIT compilation (if available)

        Returns:
            EquationResult with computed value
        """
        if not JAX_AVAILABLE or not use_jit:
            # Fall back to parent implementation
            return super().execute(name, parameters)

        # Try JAX implementation first
        if name in self._jit_implementations and use_jit:
            try:
                impl = self._jit_implementations[name]
                # Extract parameters
                if name == "softmax":
                    result = impl(parameters["x"])
                elif name == "sigmoid":
                    result = impl(parameters["x"])
                elif name == "relu":
                    result = impl(parameters["x"])
                else:
                    # Fall back to parent
                    return super().execute(name, parameters)

                from amos_equation_kernel import EquationResult
                metadata = self._metadata.get(name)
                if metadata:
                    return EquationResult(
                        value=result,
                        metadata=metadata,
                        invariants_valid=True,
                        errors=[]
                    )
            except Exception:
                # Fall back to parent on error
                pass

        return super().execute(name, parameters)

    def compute_gradient(
        self,
        name: str,
        *args: Any,
        **kwargs: Any
    ) -> Tuple[Any, Any] :
        """Compute value and gradient for an equation.

        Args:
            name: Equation name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Tuple of (value, gradient) or None if not available
        """
        if not JAX_AVAILABLE:
            return None

        if name in self._grad_implementations:
            try:
                grad_fn = self._grad_implementations[name]
                # For value_and_grad pattern
                if name in self._jax_implementations:
                    value_grad_fn = value_and_grad(self._jax_implementations[name])
                    return value_grad_fn(*args, **kwargs)
                else:
                    return None
            except Exception:
                return None

        return None

    def execute_batch(
        self,
        name: str,
        batch_params: list[dict[str, Any]],
        batch_key: str = "x"
    ) -> List[Any]:
        """Execute equation on a batch of inputs using vmap.

        Args:
            name: Equation name
            batch_params: List of parameter dictionaries
            batch_key: Key for the batched parameter

        Returns:
            List of results
        """
        if not JAX_AVAILABLE:
            # Fall back to sequential processing
            return [self.execute(name, params).value for params in batch_params]

        if name not in self._jit_implementations:
            # Fall back to sequential
            return [self.execute(name, params).value for params in batch_params]

        try:
            # Stack batch parameters
            batch_values = jnp.array([p[batch_key] for p in batch_params])

            # Create vmapped function
            impl = self._jit_implementations[name]
            vmapped_impl = vmap(impl)

            # Execute
            results = vmapped_impl(batch_values)

            # Convert back to list
            return [r for r in results]
        except Exception:
            # Fall back to sequential
            return [self.execute(name, params).value for params in batch_params]

    def create_train_step(
        self,
        loss_name: str,
        learning_rate: float = 0.01
    ) -> Optional[Callable]:
        """Create a JIT-compiled training step function.

        Args:
            loss_name: Name of the loss function
            learning_rate: Learning rate for parameter updates

        Returns:
            JIT-compiled training function or None
        """
        if not JAX_AVAILABLE:
            return None

        if loss_name not in self._grad_implementations:
            return None

        @jit
        def train_step(params: jnp.ndarray, x: jnp.ndarray, y: jnp.ndarray):
            loss, grads = value_and_grad(
                self._jax_implementations[loss_name]
            )(params, x, y)
            new_params = params - learning_rate * grads
            return new_params, loss

        return train_step

    def benchmark(
        self,
        name: str,
        parameters: Dict[str, Any],
        iterations: int = 100
    ) -> dict[str, float]:
        """Benchmark equation execution performance.

        Args:
            name: Equation name
            parameters: Test parameters
            iterations: Number of benchmark iterations

        Returns:
            Dictionary with timing results
        """
        import time
from typing import Callable, List, Tuple

        results = {}

        # Benchmark NumPy implementation
        start = time.perf_counter()
        for _ in range(iterations):
            super().execute(name, parameters)
        numpy_time = time.perf_counter() - start
        results["numpy_ms"] = (numpy_time / iterations) * 1000

        # Benchmark JAX implementation if available
        if JAX_AVAILABLE and name in self._jit_implementations:
            # Warmup
            for _ in range(10):
                self.execute(name, parameters, use_jit=True)

            start = time.perf_counter()
            for _ in range(iterations):
                self.execute(name, parameters, use_jit=True)
            jax_time = time.perf_counter() - start
            results["jax_ms"] = (jax_time / iterations) * 1000
            results["speedup"] = numpy_time / jax_time if jax_time > 0 else 0

        return results


def get_jax_kernel() -> JAXEquationKernel:
    """Get or create the global JAX kernel instance."""
    return JAXEquationKernel()


# ============================================================================
# Demonstration
# ============================================================================

if __name__ == "__main__":
    print("AMOS JAX Equation Kernel")
    print("=" * 50)

    kernel = get_jax_kernel()

    print(f"\nJAX Available: {kernel.is_jax_available()}")

    if kernel.is_jax_available():
        # Test softmax with JAX
        print("\n--- Softmax with JAX ---")
        x = jnp.array([1.0, 2.0, 3.0])
        result = kernel.execute("softmax", {"x": x}, use_jit=True)
        print(f"Input: {x}")
        print(f"Output: {result.value}")
        print(f"Sum: {jnp.sum(result.value):.6f}")

        # Test batch processing
        print("\n--- Batch Processing ---")
        batch = [
            {"x": jnp.array([1.0, 2.0, 3.0])},
            {"x": jnp.array([0.0, 0.0, 0.0])},
            {"x": jnp.array([-1.0, 0.0, 1.0])},
        ]
        batch_results = kernel.execute_batch("softmax", batch)
        print(f"Batch size: {len(batch_results)}")
        for i, r in enumerate(batch_results):
            print(f"  Batch {i}: {r}")

        # Benchmark
        print("\n--- Performance Benchmark ---")
        bench = kernel.benchmark("softmax", {"x": jnp.array([1.0, 2.0, 3.0])})
        print(f"NumPy: {bench.get('numpy_ms', 0):.4f} ms")
        print(f"JAX:   {bench.get('jax_ms', 0):.4f} ms")
        print(f"Speedup: {bench.get('speedup', 0):.2f}x")
    else:
        print("JAX not available. Install with: pip install jax jaxlib")
        print("Falling back to NumPy implementations.")
