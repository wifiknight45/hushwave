from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class LWEParams:
    n: int = 64
    q: int = 4096
    m: int = 128
    sigma: float = 3.2  # discrete Gaussian-ish width for toy error


@dataclass
class LWEInstance:
    A: np.ndarray
    b: np.ndarray
    s: np.ndarray
    e: np.ndarray
    params: LWEParams


def _sample_error(m: int, sigma: float, rng: np.random.Generator) -> np.ndarray:
    # Rounded Gaussian toy sampler (not constant-time / not production)
    return np.round(rng.normal(0.0, sigma, size=m)).astype(np.int64)


def keygen(params: LWEParams, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    return rng.integers(0, params.q, size=params.n, dtype=np.int64)


def encrypt_zero(params: LWEParams, s: np.ndarray, rng: np.random.Generator | None = None) -> LWEInstance:
    """Public samples (A, b=As+e) — the 'payload' we push through the wave channel."""
    rng = rng or np.random.default_rng()
    A = rng.integers(0, params.q, size=(params.m, params.n), dtype=np.int64)
    e = _sample_error(params.m, params.sigma, rng)
    b = (A @ s + e) % params.q
    return LWEInstance(A=A, b=b, s=s, e=e, params=params)


def residual(instance: LWEInstance) -> np.ndarray:
    """b - A s mod q, centered — should look like error if channel didn't destroy structure."""
    q = instance.params.q
    r = (instance.b - instance.A @ instance.s) % q
    return np.where(r > q // 2, r - q, r)
