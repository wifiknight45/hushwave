[![License](https://img.shields.io/github/license/wifiknight45/hushwave)](https://github.com/wifiknight45/hushwave)
[![GitHub stars](https://img.shields.io/github/stars/wifiknight45/hushwave?style=social)](https://github.com/wifiknight45/hushwave/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/wifiknight45/hushwave)](https://github.com/wifiknight45/hushwave/commits)
[![Top language](https://img.shields.io/github/languages/top/wifiknight45/hushwave)](https://github.com/wifiknight45/hushwave)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PQC](https://img.shields.io/badge/crypto-LWE%20%2F%20PQC-purple.svg)](https://github.com/wifiknight45/hushwave)
[![Acoustics](https://img.shields.io/badge/channel-acoustic%20waves-teal.svg)](https://github.com/wifiknight45/hushwave)

# hushwave

> **Lattice noise × wave noise.**  
> A novel lab where Learning-With-Errors (LWE) ciphertext is not merely *hidden in* sound — the **cryptographic error distribution is coupled to physical acoustic channel noise** (multipath rooms, Doppler, underwater attenuation, speaker/mic band-limits).

Most audio stego treats the channel as an annoyance. **hushwave treats the channel as part of the cryptosystem’s noise budget** — the same mental model as LWE, made audible.

## Why this is different
| Typical audio stego | hushwave |
|---|---|
| LSB / echo hiding of arbitrary bytes | Structured **LWE samples** as the payload |
| Channel = distortion to fight | Channel = **calibrated noise** that interacts with lattice error |
| RF cousin: KiwiSDR labs | **Acoustic** cousin: air / room / water wave physics |

Educational + research toy — not a production cipher.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
hushwave demo          # synthesize carrier → embed toy LWE → corrupt with room multipath → recover stats
hushwave ber --snr-db 20 --trials 30
```

## Core ideas
1. **Toy LWE** (and hooks for real PQC later) produces \((A, b = As + e)\).
2. **Acoustic modem** maps samples onto a band-limited carrier (audible or near-ultrasonic).
3. **Physics channel**: FIR multipath, Doppler, underwater absorption sketch, AWGN.
4. **Decode + BER / MSE** vs SNR — plots that look great in a README/demo.

## Layout
```
src/hushwave/
  crypto/    # toy LWE + error sampling
  channel/   # multipath, Doppler, underwater, AWGN
  stego/     # embed / extract on WAV carriers
  viz/       # BER curves
```

## Disclaimer
For research, teaching, and authorized experiments only. Do not use for covert channels on systems you do not own or lack permission to test.

## License
MIT
