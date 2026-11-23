#!/usr/bin/env python3
"""Convert Pokemon Platinum SSEQ sequences (from the user's own legally dumped
cartridge) to mid2agb MIDI files + Emerald-instrument voicegroups.

Usage (run locally; requires `pip install ndspy mido numpy`):
  python3 tools/platinum_music/convert_platinum_music.py /path/to/pl_sound_data.sdat

Writes:
  sound/songs/midi/mus_pl_*.mid          (note/controller data only)
  sound/voicegroups/platinum/*.inc       (voicegroups built ONLY from Emerald's
                                          DirectSoundWaveData_* samples and PSG voices)
and prints the midi.cfg lines.  The SDAT, decoded DS samples and the ROM are
never copied into the repository.
"""
import math
import os
import struct
import sys
import collections

import mido
import numpy as np
import ndspy.soundArchive as SA

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sseq_sim  # noqa: E402
import swav_decode  # noqa: E402
from instrument_map import PROGRAM_MAP, KEYSPLITS, DRUM_MAP  # noqa: E402
from song_list import SONGS, SONG_GAINS  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
SAMPLES = os.path.join(REPO, 'sound', 'direct_sound_samples')

BANK_NAMES = {700: 'basic', 701: 'field', 702: 'battle', 703: 'dungeon', 704: 'opening'}

# ---------------------------------------------------------------- envelopes
ATTACK_TABLE = [0x00, 0x01, 0x05, 0x0E, 0x1A, 0x26, 0x33, 0x3F, 0x49, 0x54,
                0x5C, 0x64, 0x6D, 0x74, 0x7B, 0x7F, 0x84, 0x89, 0x8F]
DS_TICK_MS = 5.2083
GBA_FRAME_MS = 16.743


def sq(v):
    return (max(0, min(127, v)) / 127.0) ** 2


def ds_rate(v):
    if v >= 127:
        return 65535
    if v == 126:
        return 0x3C00
    if v >= 50:
        return 0x1E00 / (126 - v)
    return v * 2 + 1


def ds_attack_ms(a):
    if a >= 127:
        return 0.0
    m = ATTACK_TABLE[127 - a] if a >= 109 else 255 - a
    if m <= 0:
        return 0.0
    ticks = math.log(723.0) / math.log(255.0 / m)
    return ticks * DS_TICK_MS


def gba_adsr(a, d, s, r):
    t = ds_attack_ms(a)
    A = 255 if t < GBA_FRAME_MS else max(1, min(255, int(round(255 * GBA_FRAME_MS / t))))
    S = int(round(255 * sq(s)))

    def mult(rate):
        if rate >= 65535:
            return 0
        db_per_frame = rate / 1280.0 * (GBA_FRAME_MS / DS_TICK_MS)
        return max(0, min(255, int(round(256 * 10 ** (-db_per_frame / 20)))))
    D = 0 if S >= 255 else mult(ds_rate(d))
    R = mult(ds_rate(r))
    return A, D, S, R


def psg_adsr(a, d, s, r):
    t = ds_attack_ms(a)
    A = 0 if t < GBA_FRAME_MS else min(7, max(1, int(round(t / GBA_FRAME_MS / 15))))
    S = int(round(15 * sq(s)))

    def steps(rate):
        if rate >= 65535:
            return 0
        db_per_frame = rate / 1280.0 * (GBA_FRAME_MS / DS_TICK_MS)
        # one PSG envelope step ~= 2.5 dB at mid volume
        return min(7, max(1, int(round(2.5 / max(db_per_frame, 1e-3)))))
    D = 0 if S >= 15 else steps(ds_rate(d))
    R = steps(ds_rate(r))
    return A, D, S, R


# ---------------------------------------------------------------- sample levels
def _wav_chunks(path):
    d = open(path, 'rb').read()
    i, out = 12, {}
    while i < len(d) - 8:
        cid = d[i:i + 4]
        sz = struct.unpack('<I', d[i + 4:i + 8])[0]
        out[cid] = d[i + 8:i + 8 + sz]
        i += 8 + sz + (sz & 1)
    return out


def _rms_steady(a, loop_start):
    a = np.asarray(a, dtype=np.float64)
    if loop_start is not None and loop_start < len(a) - 16:
        a = np.concatenate([a] + [a[loop_start:]] * 8)
    n = len(a)
    seg = a[: max(64, n // 2)] if n < 4096 else a[: 4096]
    return float(np.sqrt(np.mean(seg ** 2)) + 1e-6)


_em_rms = {}


def emerald_rms(name):
    if name not in _em_rms:
        c = _wav_chunks(os.path.join(SAMPLES, name + '.wav'))
        a = (np.frombuffer(c[b'data'], dtype=np.uint8).astype(np.float64) - 128) / 128
        ls = None
        if b'smpl' in c:
            v = struct.unpack('<9I', c[b'smpl'][:36])
            if v[7]:
                ls = struct.unpack('<6I', c[b'smpl'][36:60])[2]
        _em_rms[name] = _rms_steady(a, ls)
    return _em_rms[name]


# ---------------------------------------------------------------- bank analysis
class BankInfo:
    def __init__(self, sdat, bank_id):
        self.sdat = sdat
        self.id = bank_id
        self.bank = sdat.banks[bank_id][1]
        self._rms = {}

    def instrument(self, prog):
        if prog >= len(self.bank.instruments):
            return None
        return self.bank.instruments[prog]

    def region(self, prog, key):
        ins = self.instrument(prog)
        if ins is None:
            return None
        c = type(ins).__name__
        if c == 'SingleNoteInstrument':
            return ins.noteDefinition
        if c == 'RangeInstrument':
            i = key - ins.firstPitch
            return ins.noteDefinitions[i] if 0 <= i < len(ins.noteDefinitions) else None
        for reg in ins.regions:
            if key <= reg.lastPitch:
                return reg.noteDefinition
        return ins.regions[-1].noteDefinition

    def ds_rms(self, nd):
        if int(nd.type) != 1:
            return None
        arc = self.bank.waveArchiveIDs[nd.waveArchiveIDID]
        k = (arc, nd.waveID)
        if k not in self._rms:
            w = self.sdat.waveArchives[arc][1].waves[nd.waveID]
            a, sr, ls = swav_decode.decode(w)
            self._rms[k] = _rms_steady(a, ls)
        return self._rms[k]


# ---------------------------------------------------------------- conversion
def gm_drum_target(key):
    return key  # the generated drumset is indexed by the DS key itself


def program_gain(bank, prog, key_hist):
    """Relative loudness correction DS sample vs Emerald sample (applied to velocity)."""
    m = PROGRAM_MAP.get(prog)
    if m is None or m[0] not in ('ds', 'ks'):
        return 1.0
    key = max(key_hist, key=key_hist.get) if key_hist else 60
    nd = bank.region(prog, key)
    if nd is None or int(nd.type) != 1:
        return 1.0
    ds = bank.ds_rms(nd)
    if m[0] == 'ds':
        em = emerald_rms(m[1])
    else:
        em = float(np.mean([emerald_rms(s) for s in KEYSPLITS[m[1]]]))
    g = ds / em
    return g


def drum_gain(bank, prog, key):
    nd = bank.region(prog, key)
    e = DRUM_MAP.get(key)
    if nd is None or e is None or e[0] == 'noise' or int(nd.type) != 1:
        return 1.0
    return bank.ds_rms(nd) / emerald_rms(e[0])


def convert_song(sdat, sym, out_path, banks, report):
    seq = dict(sdat.sequences)[sym]
    bank = banks.setdefault(seq.bankID, BankInfo(sdat, seq.bankID))
    r = sseq_sim.convert(seq)
    loop = r['loop']
    until = r['length']

    # key histograms per program for gain estimation
    hist = collections.defaultdict(collections.Counter)
    for tn, out in r['tracks']:
        cur = 0
        for t, kind, d in out.items:
            if kind == 'program':
                cur = d['value']
            elif kind == 'note':
                hist[cur][d['key']] += 1
    gains = {}
    for p, h in hist.items():
        if PROGRAM_MAP.get(p, (None,))[0] == 'drums':
            continue
        gains[p] = program_gain(bank, p, h)
    # normalise so the loudest melodic instrument is at 1.0 (never boost past velocity 127)
    gmax = max([g for g in gains.values()] + [1e-6])
    gains = {p: max(0.35, min(1.0, g / gmax)) for p, g in gains.items()}

    mid = mido.MidiFile(type=1, ticks_per_beat=sseq_sim.TICKS_PER_QUARTER)
    conductor = mido.MidiTrack()
    mid.tracks.append(conductor)
    gev = []
    tempos = sorted([(t, d['value']) for t, k, d in r['glob'].items if k == 'tempo'])
    for t, bpm in tempos:
        bpm = max(1, min(510, bpm))
        gev.append((t, 0, mido.MetaMessage('set_tempo', tempo=int(round(60_000_000 / bpm)))))
    if loop:
        gev.append((loop[0], 1, mido.MetaMessage('marker', text='[')))
        gev.append((loop[1], 2, mido.MetaMessage('marker', text=']')))
    _write_track(conductor, gev, until)

    seqvol = sq(seq.volume)
    chan = 0
    stats = dict(tracks=0, notes=0, dropped=0)
    track_infos = []
    for tn, out in r['tracks']:
        notes = [x for x in out.items if x[1] == 'note']
        if not notes:
            continue
        if chan >= 16:
            stats['dropped'] += len(notes)
            continue
        if chan == 9 and False:
            chan += 1
        tr = mido.MidiTrack()
        mid.tracks.append(tr)
        ev = []
        st = dict(program=0, vol=(127, 127), pan=64, bend=0, bendr=2,
                  mod=dict(depth=0, speed=16, type=0, range=1, delay=0))
        snapshot_at_loop = None
        items = sorted(out.items, key=lambda x: x[0])
        tempo_at = _tempo_lookup(tempos)
        pitches = []

        def emit_state(t, s, order=5):
            prog = s['program']
            m = PROGRAM_MAP.get(prog)
            ev.append((t, order, mido.Message('program_change', channel=chan, program=prog & 0x7F)))
            ev.append((t, order + 1, _cc(chan, 7, _vol(s['vol'], seqvol))))
            ev.append((t, order + 1, _cc(chan, 10, s['pan'])))
            ev.append((t, order + 1, _cc(chan, 20, max(0, min(127, s['bendr'])))))
            ev.append((t, order + 1, _bend(chan, s['bend'])))
            for c, v in _mod_ccs(s['mod'], tempo_at(t)):
                ev.append((t, order + 1, _cc(chan, c, v)))

        emit_state(0, st, 3)
        for t, kind, d in items:
            if loop and snapshot_at_loop is None and t >= loop[0]:
                snapshot_at_loop = {k: (dict(v) if isinstance(v, dict) else v) for k, v in st.items()}
            if t >= until:
                break
            if kind == 'program':
                st['program'] = d['value']
                ev.append((t, 5, mido.Message('program_change', channel=chan, program=d['value'] & 0x7F)))
            elif kind == 'vol':
                st['vol'] = (d['volume'], d['expression'])
                ev.append((t, 6, _cc(chan, 7, _vol(st['vol'], seqvol))))
            elif kind == 'pan':
                st['pan'] = d['value']
                ev.append((t, 6, _cc(chan, 10, d['value'])))
            elif kind == 'bend':
                st['bend'] = d['value']
                ev.append((t, 6, _bend(chan, d['value'])))
            elif kind == 'bendr':
                st['bendr'] = d['value']
                ev.append((t, 6, _cc(chan, 20, max(0, min(127, d['value'])))))
            elif kind == 'mod':
                st['mod'] = dict(d)
                for c, v in _mod_ccs(st['mod'], tempo_at(t)):
                    ev.append((t, 6, _cc(chan, c, v)))
            elif kind == 'note':
                prog = st['program']
                m = PROGRAM_MAP.get(prog)
                if bank.instrument(prog) is None or m is None:
                    stats['dropped'] += 1
                    continue
                key = d['key']
                if m[0] == 'drums':
                    if key not in DRUM_MAP:
                        stats['dropped'] += 1
                        continue
                    g = drum_gain(bank, prog, key)
                    g = max(0.35, min(1.0, g))
                    gkey = key
                else:
                    g = gains.get(prog, 1.0)
                    gkey = key + m[2]
                    pitches.append(key)
                if not (0 <= gkey <= 127):
                    stats['dropped'] += 1
                    continue
                raw_vel = 127 * sq(d['vel']) * g
                LEVEL['vel'].append(raw_vel)
                # only volumes that actually sound count towards the headroom
                LEVEL['vol'].append(127 * sq(st['vol'][0]) * sq(st['vol'][1]) * seqvol)
                vel = max(1, min(127, int(round(raw_vel * LEVEL['vel_scale']))))
                end = min(t + d['dur'], until)
                if end <= t:
                    continue
                ev.append((t, 8, mido.Message('note_on', channel=chan, note=gkey, velocity=vel)))
                ev.append((end, 0, mido.Message('note_off', channel=chan, note=gkey, velocity=0)))
                stats['notes'] += 1
        if loop and snapshot_at_loop is not None:
            emit_state(loop[0], snapshot_at_loop, 3)
        # priority: lead/high voices and bass keep their channels, pads yield first
        avg = (sum(pitches) / len(pitches)) if pitches else 0
        track_infos.append((chan, len(notes), avg, tr, ev))
        chan += 1
        stats['tracks'] += 1

    # assign PRIO (CC 33): highest-register busy track = lead
    melodic = [ti for ti in track_infos if ti[2] > 0]
    lead = max(melodic, key=lambda ti: ti[2] * min(ti[1], 400)) if melodic else None
    bass = min(melodic, key=lambda ti: ti[2]) if melodic else None
    for ti in track_infos:
        ch, n, avg, tr, ev = ti
        prio = 50
        if ti is lead:
            prio = 80
        elif ti is bass:
            prio = 70
        elif avg == 0:
            prio = 60  # drums
        ev.append((0, 2, _cc(ch, 33, prio)))
        _write_track(tr, ev, until)
    mid.save(out_path)
    report.append(dict(sym=sym, bank=seq.bankID, loop=loop, length=until, seqvol=seq.volume, **stats))
    return mid


def _tempo_lookup(tempos):
    def f(t):
        bpm = 120
        for tt, b in tempos:
            if tt <= t:
                bpm = b
        return bpm
    return f


def _vol(v, seqvol):
    vol, expr = v
    x = 127 * sq(vol) * sq(expr) * seqvol
    return max(0, min(127, int(round(x * LEVEL['vol_scale']))))


# Overall gain applied to every song relative to the DS mix (sq() volume curve).
# 2.25 (~+7 dB) puts the converted songs at roughly the same loudness as
# Emerald's own BGM in mGBA (measured RMS, see README).  The gain is first
# spent on track volume (CC7) up to 127 without clipping any track, the
# remainder on note velocity, so relative track balance is preserved.
SONG_GAIN = 2.25
LEVEL = dict(vol=[], vel=[], vol_scale=1.0, vel_scale=1.0)


def convert_song_leveled(sdat, sym, out_path, banks, report, gain=SONG_GAIN):
    import numpy as np
    LEVEL.update(vol=[], vel=[], vol_scale=1.0, vel_scale=1.0)
    convert_song(sdat, sym, out_path, banks, [])
    vmax = max(LEVEL['vol'] + [1e-6])
    nref = float(np.percentile(LEVEL['vel'], 99.5)) if LEVEL['vel'] else 127
    a = min(gain, 127.0 / vmax)
    b = min(gain / a, 127.0 / max(nref, 1e-6))
    LEVEL.update(vol=[], vel=[], vol_scale=a, vel_scale=b)
    convert_song(sdat, sym, out_path, banks, report)
    report[-1].update(vol_scale=round(a, 3), vel_scale=round(b, 3), net_gain=round(a * b, 3))


def _cc(ch, c, v):
    return mido.Message('control_change', channel=ch, control=c, value=max(0, min(127, int(v))))


def _bend(ch, ds_bend):
    msb = 64 + int(round(ds_bend / 2))
    msb = max(0, min(127, msb))
    return mido.Message('pitchwheel', channel=ch, pitch=(msb << 7) - 8192)


def _mod_ccs(m, bpm):
    depth = int(round(m['depth'] * max(1, m['range']) / 8.0))
    depth = max(0, min(127, depth))
    lfos = max(1, min(127, int(round(m['speed'] * 240.0 / max(1, bpm)))))
    delay = max(0, min(127, int(round(m['delay'] * DS_TICK_MS / 1000.0 * bpm * 0.4))))
    t = m['type'] if m['type'] in (0, 1, 2) else 0
    return [(21, lfos), (22, t), (26, delay), (1, depth)]


def _write_track(track, events, until):
    events.sort(key=lambda e: (e[0], e[1]))
    now = 0
    for t, _, msg in events:
        msg = msg.copy(time=t - now)
        track.append(msg)
        now = t
    track.append(mido.MetaMessage('end_of_track', time=max(0, until - now)))


# ---------------------------------------------------------------- voicegroups
def voice_line_for(bank, prog):
    m = PROGRAM_MAP.get(prog)
    ins = bank.instrument(prog)
    if m is None or ins is None:
        return '\tvoice_square_1 60, 0, 0, 2, 0, 0, 15, 0'
    kind, target, _ = m
    if kind == 'drums':
        return '\tvoice_keysplit_all voicegroup_platinum_drumset'
    nd = _main_region(ins)
    if kind == 'square':
        A, D, S, R = psg_adsr(nd.attack, nd.decay, nd.sustain, nd.release)
        return f'\tvoice_square_2 60, 0, {target}, {A}, {D}, {S}, {R}'
    if kind == 'noise':
        A, D, S, R = psg_adsr(nd.attack, nd.decay, nd.sustain, nd.release)
        return f'\tvoice_noise 60, 0, 0, {A}, {D}, {S}, {R}'
    A, D, S, R = gba_adsr(nd.attack, nd.decay, nd.sustain, nd.release)
    pan = 0 if nd.pan == 64 else nd.pan
    if kind == 'ds':
        return f'\tvoice_directsound 60, {pan}, DirectSoundWaveData_{target}, {A}, {D}, {S}, {R}'
    key = (target, (A, D, S, R), pan)
    if key not in KS_NEEDED:
        n = sum(1 for k in KS_NEEDED if k[0] == target) + 1
        KS_NEEDED[key] = f'platinum_{target}_{n}'
    return f'\tvoice_keysplit voicegroup_{KS_NEEDED[key]}, keysplit_{target}'


KS_NEEDED = {}


def _main_region(ins):
    c = type(ins).__name__
    if c == 'SingleNoteInstrument':
        return ins.noteDefinition
    if c == 'RangeInstrument':
        return ins.noteDefinitions[0]
    regs = [r.noteDefinition for r in ins.regions]
    # middle region is representative of the playing range
    return regs[len(regs) // 2]


def write_voicegroups(banks, outdir):
    os.makedirs(outdir, exist_ok=True)
    files = []
    for bid in sorted(banks):
        bank = banks[bid]
        lines = [f'voice_group platinum_{BANK_NAMES[bid]}']
        for p in range(128):
            lines.append(voice_line_for(bank, p))
        path = os.path.join(outdir, f'{BANK_NAMES[bid]}.inc')
        open(path, 'w').write('\n'.join(lines) + '\n')
        files.append(path)
    lines = []
    for (target, (A, D, S, R), pan), name in sorted(KS_NEEDED.items(), key=lambda x: x[1]):
        lines.append(f'voice_group {name}')
        for smp in KEYSPLITS[target]:
            lines.append(f'\tvoice_directsound 60, {pan}, DirectSoundWaveData_{smp}, {A}, {D}, {S}, {R}')
        lines.append('')
    path = os.path.join(outdir, 'keysplits.inc')
    open(path, 'w').write('\n'.join(lines))
    files.append(path)
    # drum kit (indexed by DS key, 0..127)
    lines = ['voice_group platinum_drumset']
    for k in range(128):
        e = DRUM_MAP.get(k)
        if e is None:
            lines.append('\tvoice_square_1 60, 0, 0, 2, 0, 0, 15, 0')
        elif e[0] == 'noise':
            lines.append(f'\tvoice_noise_alt {e[2]}, 0, 0, {e[4]}, {e[5]}, {e[6]}, {e[7]}')
        else:
            macro = 'voice_directsound' if e[1] else 'voice_directsound_no_resample'
            lines.append(f'\t{macro} {e[2]}, {e[3]}, DirectSoundWaveData_{e[0]}, {e[4]}, {e[5]}, {e[6]}, {e[7]}')
    path = os.path.join(outdir, 'drumset.inc')
    open(path, 'w').write('\n'.join(lines) + '\n')
    files.append(path)
    return files


def main():
    sdat_path = sys.argv[1]
    sdat = SA.SDAT.fromFile(sdat_path)
    banks = {}
    report = []
    cfg = []
    middir = os.path.join(REPO, 'sound', 'songs', 'midi')
    for sym, name, master in SONGS:
        out = os.path.join(middir, f'mus_pl_{name}.mid')
        convert_song_leveled(sdat, sym, out, banks, report, gain=SONG_GAINS.get(name, SONG_GAIN))
        seq = dict(sdat.sequences)[sym]
        cfg.append(f'mus_pl_{name}.mid:'.ljust(32) + f'-E -R50 -G_platinum_{BANK_NAMES[seq.bankID]} -V{master:03d}')
    for bid in (700, 701, 702, 703, 704):
        banks.setdefault(bid, BankInfo(sdat, bid))
    files = write_voicegroups(banks, os.path.join(REPO, 'sound', 'voicegroups', 'platinum'))
    print('\n'.join(cfg))
    print('--- voicegroups:', ' '.join(os.path.relpath(f, REPO) for f in files))
    for r in report:
        print('REPORT', r)


if __name__ == '__main__':
    main()
