from __future__ import annotations

from pathlib import Path

import numpy as np
import typer
from rich import print
from scipy.io import wavfile

from hushwave import __version__
from hushwave.channel.physics import apply_channel
from hushwave.crypto.lwe import LWEParams, encrypt_zero, keygen, residual
from hushwave.stego.modem import embed_lwe, extract_soft
from hushwave.viz.ber import plot_ber_curve, symbol_error_rate

app = typer.Typer(help="hushwave — lattice noise × acoustic wave noise")


@app.command()
def version() -> None:
    print(f"hushwave {__version__}")


@app.command()
def demo(
    out: Path = typer.Option(Path("artifacts/demo.wav")),
    snr_db: float = typer.Option(22.0),
    ultrasonic: bool = typer.Option(False, help="Use ~18kHz carrier (still may be audible to some)"),
) -> None:
    """Embed toy LWE into a carrier, run a room channel, print residual stats."""
    rng = np.random.default_rng(7)
    params = LWEParams()
    s = keygen(params, rng)
    inst = encrypt_zero(params, s, rng)
    freq = 18000.0 if ultrasonic else 12000.0
    wav = embed_lwe(inst, freq=freq, rng=rng)
    rx = apply_channel(wav, snr_db=snr_db, room=True, rng=rng)
    out.parent.mkdir(parents=True, exist_ok=True)
    # float -> int16
    peak = np.max(np.abs(rx)) + 1e-9
    pcm = np.int16(np.clip(rx / peak, -1, 1) * 32000)
    wavfile.write(out, 44100, pcm)
    b_hat = extract_soft(rx, params)
    ser = float(np.mean(b_hat != inst.b))
    res = residual(inst)
    print(
        {
            "wrote": str(out),
            "snr_db": snr_db,
            "carrier_hz": freq,
            "symbol_error_rate": round(ser, 4),
            "true_error_l2": float(np.linalg.norm(res)),
            "note": "Toy modem — structure survival is the point, not perfect recovery.",
        }
    )


@app.command()
def ber(
    trials: int = typer.Option(12),
    out: Path = typer.Option(Path("artifacts/ber.png")),
) -> None:
    """Plot toy symbol-error vs SNR under multipath+AWGN."""
    snrs = [0, 5, 10, 15, 20, 25, 30]
    path = plot_ber_curve(snrs, out=out, trials=trials)
    sample = {snr: round(symbol_error_rate(snr, trials=max(3, trials // 2)), 4) for snr in (10, 20, 30)}
    print({"plot": str(path), "sample_ser": sample})


if __name__ == "__main__":
    app()
