from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from hushwave.channel.physics import apply_channel
from hushwave.crypto.lwe import LWEParams, encrypt_zero, keygen, residual
from hushwave.stego.modem import embed_lwe, extract_soft


def symbol_error_rate(snr_db: float, trials: int = 20, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    params = LWEParams()
    errors = 0
    total = 0
    for t in range(trials):
        s = keygen(params, rng)
        inst = encrypt_zero(params, s, rng)
        wav = embed_lwe(inst, rng=rng)
        rx = apply_channel(wav, snr_db=snr_db, room=True, rng=rng)
        b_hat = extract_soft(rx, params)
        errors += int(np.sum(b_hat != inst.b))
        total += params.m
        # also track residual energy as a secondary signal of structure survival
        _ = residual(inst)
    return errors / max(total, 1)


def plot_ber_curve(snrs: list[float], out: Path, trials: int = 15) -> Path:
    rates = [symbol_error_rate(snr, trials=trials, seed=42) for snr in snrs]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.semilogy(snrs, np.clip(rates, 1e-4, 1.0), marker="o")
    ax.set_xlabel("SNR (dB)")
    ax.set_ylabel("Symbol error rate (toy demod)")
    ax.set_title("hushwave — lattice symbols vs acoustic SNR")
    ax.grid(True, which="both", alpha=0.3)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out
