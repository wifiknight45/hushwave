from __future__ import annotations

import numpy as np

from hushwave.crypto.lwe import LWEInstance, LWEParams


def _carrier(n: int, sr: int, freq: float, rng: np.random.Generator) -> np.ndarray:
    t = np.arange(n) / sr
    # slight phase noise so it isn't a sterile beep
    phase = 0.02 * np.cumsum(rng.normal(0, 1, size=n))
    return 0.35 * np.sin(2 * np.pi * freq * t + phase)


def embed_lwe(
    instance: LWEInstance,
    sr: int = 44100,
    secs: float = 2.0,
    freq: float = 12000.0,
    depth: float = 0.08,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    """Map centered b residuals-scale symbols onto amplitude of a carrier."""
    rng = rng or np.random.default_rng()
    n = int(sr * secs)
    carrier = _carrier(n, sr, freq, rng)
    q = instance.params.q
    # normalize b to [-1,1]
    sym = (instance.b.astype(np.float64) / (q / 2.0)) - 1.0
    # tile symbols across the buffer
    idx = np.linspace(0, len(sym) - 1, n)
    seq = np.interp(np.arange(n), np.linspace(0, n - 1, len(sym)), sym)
    return carrier * (1.0 + depth * seq)


def extract_soft(wav: np.ndarray, params: LWEParams, envelope_win: int = 64) -> np.ndarray:
    """Crude envelope → soft symbols length m (toy demod)."""
    env = np.abs(wav)
    # moving average
    ker = np.ones(envelope_win) / envelope_win
    smooth = np.convolve(env, ker, mode="same")
    # resample to m symbols
    m = params.m
    xs = np.linspace(0, len(smooth) - 1, m)
    soft = np.interp(xs, np.arange(len(smooth)), smooth)
    soft = soft - np.mean(soft)
    scale = np.max(np.abs(soft)) + 1e-9
    soft = soft / scale
    # map back toward Z_q
    return np.round((soft + 1.0) * (params.q / 2.0)).astype(np.int64) % params.q
