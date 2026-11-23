"""Acoustic feature extraction used to match DS SBNK samples to the closest
built-in pokeemerald DirectSound sample (pitch, harmonic profile, noise, decay)."""
import numpy as np


def extend_loop(a, loop_start, min_len):
    if loop_start is None or loop_start >= len(a) - 16:
        return a
    out = [a]
    seg = a[loop_start:]
    n = len(a)
    while n < min_len:
        out.append(seg)
        n += len(seg)
    return np.concatenate(out)


def f0_estimate(x, sr, fmin=27.0, fmax=2500.0):
    x = x - np.mean(x)
    if np.max(np.abs(x)) < 1e-4:
        return None, 0.0
    n = len(x)
    # normalized autocorrelation via FFT
    N = 1 << (2 * n - 1).bit_length()
    X = np.fft.rfft(x, N)
    r = np.fft.irfft(X * np.conj(X), N)[:n]
    r = r / (r[0] + 1e-12)
    lo = max(2, int(sr / fmax))
    hi = min(n - 2, int(sr / fmin))
    if hi <= lo:
        return None, 0.0
    seg = r[lo:hi]
    # pick the first peak that is within 90% of the global maximum (avoids octave-down errors)
    gmax = np.max(seg)
    if gmax < 0.2:
        return None, float(gmax)
    peaks = [i for i in range(1, len(seg) - 1) if seg[i] >= seg[i - 1] and seg[i] >= seg[i + 1] and seg[i] >= 0.9 * gmax]
    i = peaks[0] if peaks else int(np.argmax(seg))
    # parabolic interpolation
    y0, y1, y2 = seg[i - 1] if i > 0 else seg[i], seg[i], seg[i + 1] if i + 1 < len(seg) else seg[i]
    d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 + 1e-12)
    lag = lo + i + d
    return sr / lag, float(y1)


def features(a, sr, loop_start=None):
    a = np.asarray(a, dtype=np.float64)
    full = extend_loop(a, loop_start, int(sr * 1.2))
    att = int(0.03 * sr)
    win = full[att: att + int(0.12 * sr)] if len(full) > att + 256 else full
    f0, clarity = f0_estimate(win[:4096], sr)
    spec = np.abs(np.fft.rfft(win * np.hanning(len(win)), 1 << 14))
    freqs = np.fft.rfftfreq(1 << 14, 1.0 / sr)
    p = spec ** 2 + 1e-12
    centroid = float(np.sum(freqs * p) / np.sum(p))
    flat = float(np.exp(np.mean(np.log(p))) / np.mean(p))
    harm = []
    if f0:
        for h in range(1, 13):
            f = f0 * h
            if f > sr / 2 - 50:
                harm.append(-80.0)
                continue
            k = int(round(f / (freqs[1])))
            w = max(2, int(f0 / freqs[1] / 4))
            harm.append(10 * np.log10(np.max(p[max(0, k - w):k + w + 1])))
        harm = np.array(harm)
        harm = harm - np.max(harm)
        harm = np.maximum(harm, -60)
    else:
        harm = np.full(12, -60.0)
    # envelope (on the non-looped raw sample: decay character)
    hop = max(1, int(sr * 0.01))
    env = np.array([np.sqrt(np.mean(full[i:i + hop] ** 2)) for i in range(0, min(len(full), int(sr * 1.0)), hop)]) + 1e-9
    peak_i = int(np.argmax(env))
    pk = env[peak_i]
    def at(ms):
        j = peak_i + int(ms / 10)
        return 20 * np.log10(env[min(j, len(env) - 1)] / pk)
    return dict(f0=f0, clarity=clarity, centroid=centroid, flat=flat, harm=harm.tolist(),
                d100=at(100), d300=at(300), d800=at(800), attack_ms=peak_i * 10,
                dur=len(a) / sr, looped=loop_start is not None)
