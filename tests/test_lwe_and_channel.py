import numpy as np

from hushwave.channel.physics import apply_channel, awgn
from hushwave.crypto.lwe import LWEParams, encrypt_zero, keygen, residual


def test_lwe_residual_small():
    rng = np.random.default_rng(0)
    params = LWEParams(n=32, m=64, q=2048, sigma=2.0)
    s = keygen(params, rng)
    inst = encrypt_zero(params, s, rng)
    r = residual(inst)
    assert np.mean(np.abs(r)) < 20


def test_channel_changes_signal():
    x = np.sin(np.linspace(0, 20, 4000))
    y = apply_channel(x, snr_db=30, room=True, rng=np.random.default_rng(1))
    assert y.shape == x.shape
    assert not np.allclose(x, y)
