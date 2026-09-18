# Novelty thesis

**hushwave** frames acoustic steganography as an LWE noise-budget problem:

- Cryptographic error \(e\) is sampled from a lattice-friendly distribution.
- The physical channel adds its own noise \(n_{\mathrm{wave}}\) (multipath, Doppler, absorption, AWGN).
- The receiver sees something closer to \(As + e + n_{\mathrm{wave}}\) in spirit — so **wave physics eats into the same noise margin LWE relies on**.

That coupling is the story worth starring/forking — not another LSB toy.

Roadmap toward “get noticed”:
1. Side-by-side plots: crypto error spectrum vs acoustic noise spectrum
2. Near-ultrasonic air-gap demo video
3. Optional liboqs ML-KEM ciphertext as payload blobs
4. Compare against quiet_kiwi (RF) as a sibling lab
