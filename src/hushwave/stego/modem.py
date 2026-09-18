from __future__ import annotations

import numpy as np

from hushwave.crypto.lwe import LWEInstance, LWEParams


def _carrier(n: int, sr: int, freq: float, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / sr
    phase = 0.01 * np.cumsum(rng.normal(0, 1, size=n))
    return np.sin(2 * np.pi * freq * t + phase)


def embed_lwe(
    instance: LWEInstance,
    sr: int = 44100,
    secs: float = 2.5,
    freq: float = 5000.0,
    depth: float = 0.35,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Frame-based amplitude modulation of LWE b-symbols onto a carrier."""
    rng = rng or np.random.default_rng()
    m = instance.params.m
    q = instance.params.q
    # map to bipolar symbols
    sym = (instance.b.astype(np.float64) / (q / 2.0)) - 1.0
    samples_per = max(32, int(sr * secs) // m)
    n = samples_per * m
    carrier = _carrier(n, sr, freq, rng)
    seq = np.repeat(sym, samples_per)
    return (0.4 * carrier * (1.0 + depth * seq)).astype(np.float64)


def extract_soft(wav: np.ndarray, params: LWEParams) -> np.ndarray:
    """Integrate energy per frame and map back toward Z_q."""
    m = params.m
    q = params.q
    n = len(wav)
    samples_per = n // m
    if samples_per < 1:
        raise ValueError("wav too short for m symbols")
    frames = wav[: samples_per * m].reshape(m, samples_per)
    # coherent-ish: correlate with expected carrier freq via abs mean of rectified signal
    soft = np.mean(frames, axis=1)
    soft = soft - np.mean(soft)
    scale = np.max(np.abs(soft)) + 1e-9
    soft = soft / scale
    return np.round((soft + 1.0) * (q / 2.0)).astype(np.int64) % q
