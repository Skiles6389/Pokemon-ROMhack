"""Decode NDS SWAV sample data (PCM8 / PCM16 / IMA-ADPCM) to float arrays.
Used only for local instrument analysis; decoded audio is never written to the repo."""
import numpy as np

IMA_STEP = [7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97,
            107, 118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796,
            876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871,
            5358, 5894, 6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623,
            27086, 29794, 32767]
IMA_IDX = [-1, -1, -1, -1, 2, 4, 6, 8]


def decode(wave):
    t = int(wave.waveType)
    data = bytes(wave.data)
    if t == 0:
        a = np.frombuffer(data, dtype=np.int8).astype(np.float32) / 128.0
    elif t == 1:
        a = np.frombuffer(data[:len(data) // 2 * 2], dtype='<i2').astype(np.float32) / 32768.0
    else:
        pred = int.from_bytes(data[0:2], 'little', signed=True)
        idx = min(88, data[2])
        out = []
        for b in data[4:]:
            for nib in (b & 0xF, b >> 4):
                step = IMA_STEP[idx]
                diff = step >> 3
                if nib & 1: diff += step >> 2
                if nib & 2: diff += step >> 1
                if nib & 4: diff += step
                if nib & 8:
                    pred = max(-32768, pred - diff)
                else:
                    pred = min(32767, pred + diff)
                idx = max(0, min(88, idx + IMA_IDX[nib & 7]))
                out.append(pred)
        a = np.array(out, dtype=np.float32) / 32768.0
    # loop offset is in 32-bit words
    if t == 0:
        mult = 4
    elif t == 1:
        mult = 2
    else:
        mult = 8
    loop_start = None
    if wave.isLooped:
        loop_start = wave.loopOffset * mult - (8 if t == 2 else 0)
    return a, int(wave.sampleRate), loop_start
