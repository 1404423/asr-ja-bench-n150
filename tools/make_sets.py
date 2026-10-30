"""Recipe used to build the noisy test sets (16 kHz mono PCM16).
 - clean: 40 clips of japanese-asr/ja_asr.common_voice_8_0 (test), indices 0,112,...,4368.
 - pinkN: pink (1/f power) noise mixed at N dB SNR.      - babbleN: three other clips summed, mixed at N dB SNR.
 - peak limited to 0.95. Seeds differ between the first (10 dB) and later (5/0 dB) builds, so noise realisations are not bit-identical
   between conditions; use the same recipe with your own seed for a fresh run."""
import numpy as np
rng = np.random.default_rng(1)
def pink(n):
    f = np.fft.rfft(rng.standard_normal(n)); k = np.arange(len(f)); k[0] = 1
    return np.fft.irfft(f/np.sqrt(k), n)
def mix(x, noise, snr_db):
    noise = np.resize(noise, len(x))
    p, q = np.mean(x**2)+1e-9, np.mean(noise**2)+1e-9
    y = x + noise*np.sqrt(p/q/10**(snr_db/10))
    return (y/max(1, np.abs(y).max()/0.95)).astype("float32")
def babble(clips, k, n):
    return sum(np.resize(clips[(k+j*7) % len(clips)], n) for j in (1, 2, 3))
