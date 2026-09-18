from __future__ import annotations

import numpy as np
from scipy.signal import lfilter


def awgn(x: np.ndarray, snr_db: float, rng: np.random.Generator | None = None) -> np.ndarray:
    rng = rng or np.random.default_rng()
    p_sig = np.mean(x.astype(np.float64) ** 2) + 1e-12
    p_noise = p_sig / (10 ** (snr_db / 10.0))
    noise = rng.normal(0.0, np.sqrt(p_noise), size=x.shape)
    return x + noise


def multipath_room(x: np.ndarray, delays: list[int] | None = None, gains: list[float] | None = None) -> np.ndarray:
    """Simple FIR multipath (early reflections)."""
    delays = delays or [0, 37, 91, 160]
    gains = gains or [1.0, 0.55, 0.28, 0.12]
    tap = max(delays) + 1
    h = np.zeros(tap, dtype=np.float64)
    for d, g in zip(delays, gains):
        h[d] += g
    return lfilter(h, [1.0], x.astype(np.float64))


def doppler_stretch(x: np.ndarray, factor: float = 1.002) -> np.ndarray:
    """Crude Doppler via resampling stretch (moving source/receiver)."""
    n = len(x)
    t = np.linspace(0, 1, n)
    t_new = np.linspace(0, 1, int(n / factor))
    y = np.interp(t_new, t, x.astype(np.float64))
    # pad/trim to original length for easier BER loops
    if len(y) >= n:
        return y[:n]
    out = np.zeros(n)
    out[: len(y)] = y
    return out


def underwater_absorb(x: np.ndarray, strength: float = 0.15) -> np.ndarray:
    """Toy high-frequency attenuation (not a full ocean model)."""
    # one-pole lowpass severity ~ strength
    alpha = np.clip(1.0 - strength, 0.05, 0.99)
    y = np.zeros_like(x, dtype=np.float64)
    prev = 0.0
    for i, s in enumerate(x.astype(np.float64)):
        prev = alpha * prev + (1 - alpha) * s
        y[i] = prev
    return y


def apply_channel(
    x: np.ndarray,
    snr_db: float = 25.0,
    room: bool = True,
    doppler: bool = False,
    underwater: bool = False,
    rng: np.random.Generator | None = None,
) -> np.ndarray:
    y = x.astype(np.float64)
    if room:
        y = multipath_room(y)
    if underwater:
        y = underwater_absorb(y)
    if doppler:
        y = doppler_stretch(y)
    y = awgn(y, snr_db=snr_db, rng=rng)
    return y
