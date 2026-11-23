"""SSEQ (Nintendo DS sequence) interpreter used to convert Pokemon Platinum
sequences from a user-supplied, legally dumped ROM into MIDI files that
pokeemerald-expansion's mid2agb can compile.

No Nintendo data is stored in this repository: this script only reads the
SDAT the user extracts locally from their own cartridge dump.

Opcode semantics follow the NITRO sound driver (ndspy mislabels a few of them):
  0xC4 pitch bend (s8)        0xC5 pitch bend range (semitones)
  0xC7 mono(note-wait)/poly   0xC8 tie
  0xCA mod depth  0xCB mod speed  0xCC mod type  0xCD mod range  0xE0 mod delay
"""
import math
import ndspy.soundSequence as S

TICKS_PER_QUARTER = 48


def s8(v):
    v &= 0xFF
    return v - 256 if v >= 128 else v


class TrackState:
    def __init__(self):
        self.program = 0
        self.volume = 127
        self.expression = 127
        self.pan = 64
        self.transpose = 0
        self.bend = 0
        self.bend_range = 2
        self.mod_depth = 0
        self.mod_speed = 16
        self.mod_type = 0
        self.mod_range = 1
        self.mod_delay = 0
        self.priority = 64
        self.note_wait = True
        self.tie = False
        self.attack = None
        self.decay = None
        self.sustain = None
        self.release = None

    def snapshot(self):
        return dict(self.__dict__)


class Out:
    """Timeline of one track: list of (tick, kind, data)."""

    def __init__(self):
        self.items = []

    def add(self, t, kind, **data):
        self.items.append((t, kind, data))


def simulate_track(events, start_event, idx, until=None, global_out=None, max_ticks=48 * 4 * 2000):
    """Execute a track. If until is None, stop at the first backward jump
    (loop) or end of track, returning loop info. Otherwise keep following
    jumps until `until` ticks."""
    st = TrackState()
    out = Out()
    pc = idx[id(start_event)]
    t = 0
    call_stack = []
    loop_stack = []
    first_visit = {}
    loop = None
    open_tie = None  # (start_tick, key, vel)
    guard = 0
    if_flag = True
    skip_next = False
    while True:
        guard += 1
        if guard > 2_000_000:
            raise RuntimeError('runaway track')
        if until is not None and t >= until:
            break
        if t > max_ticks:
            break
        ev = events[pc]
        if not call_stack and pc not in first_visit:
            first_visit[pc] = t
        pc += 1
        if skip_next:
            skip_next = False
            # skip a conditional command
            continue

        # unwrap random / variable wrappers (use midpoint / 0 deterministically)
        if isinstance(ev, S.RandomSequenceEvent):
            val = (ev.randMin + ev.randMax) // 2
            ev = _rebuild(ev.subType, list(ev.args) + [val])
            if ev is None:
                continue
        elif isinstance(ev, S.FromVariableSequenceEvent):
            ev = _rebuild(ev.subType, [0])
            if ev is None:
                continue
        elif isinstance(ev, S.IfSequenceEvent):
            if not if_flag:
                skip_next = True
            continue

        if isinstance(ev, S.NoteSequenceEvent):
            key = ev.pitch + st.transpose
            vel = ev.velocity
            dur = ev.duration
            if st.tie:
                if open_tie is not None:
                    out.add(open_tie[0], 'note', key=open_tie[1], vel=open_tie[2], dur=max(1, t - open_tie[0]))
                open_tie = (t, key, vel)
            else:
                if dur > 0:
                    out.add(t, 'note', key=key, vel=vel, dur=dur)
            if st.note_wait:
                t += dur
        elif isinstance(ev, S.RestSequenceEvent):
            t += ev.duration
        elif isinstance(ev, S.InstrumentSwitchSequenceEvent):
            st.program = ev.instrumentID + 128 * ev.bankID
            out.add(t, 'program', value=st.program)
        elif isinstance(ev, S.JumpSequenceEvent):
            dest = idx[id(ev.destination)]
            if until is None and not call_stack and dest in first_visit:
                loop = (first_visit[dest], t)
                break
            pc = dest
        elif isinstance(ev, S.CallSequenceEvent):
            call_stack.append(pc)
            pc = idx[id(ev.destination)]
        elif isinstance(ev, S.ReturnSequenceEvent):
            if call_stack:
                pc = call_stack.pop()
        elif isinstance(ev, S.BeginLoopSequenceEvent):
            loop_stack.append([pc, ev.loopCount])
        elif isinstance(ev, S.EndLoopSequenceEvent):
            if loop_stack:
                ent = loop_stack[-1]
                if ent[1] == 0:
                    # infinite loop
                    if until is None and not call_stack:
                        loop = (first_visit.get(ent[0], 0), t)
                        break
                    pc = ent[0]
                else:
                    ent[1] -= 1
                    if ent[1] > 0:
                        pc = ent[0]
                    else:
                        loop_stack.pop()
        elif isinstance(ev, S.EndTrackSequenceEvent):
            break
        elif isinstance(ev, S.TempoSequenceEvent):
            if global_out is not None:
                global_out.add(t, 'tempo', value=ev.value)
        elif isinstance(ev, S.GlobalVolumeSequenceEvent):
            if global_out is not None:
                global_out.add(t, 'mastervol', value=ev.value)
        elif isinstance(ev, S.TrackVolumeSequenceEvent):
            st.volume = ev.value
            out.add(t, 'vol', **_vols(st))
        elif isinstance(ev, S.ExpressionSequenceEvent):
            st.expression = ev.value
            out.add(t, 'vol', **_vols(st))
        elif isinstance(ev, S.PanSequenceEvent):
            st.pan = ev.value
            out.add(t, 'pan', value=ev.value)
        elif isinstance(ev, S.TransposeSequenceEvent):
            st.transpose = s8(ev.value)
        elif type(ev).__name__ == 'PortamentoSequenceEvent':  # 0xC4 = pitch bend
            st.bend = s8(ev.value)
            out.add(t, 'bend', value=st.bend)
        elif type(ev).__name__ == 'PortamentoRangeSequenceEvent':  # 0xC5 = bend range
            st.bend_range = ev.value
            out.add(t, 'bendr', value=ev.value)
        elif isinstance(ev, S.TrackPrioritySequenceEvent):
            st.priority = ev.value
        elif isinstance(ev, S.MonoPolySequenceEvent):
            st.note_wait = bool(int(ev.value) == 0) if False else (int(getattr(ev.value, 'value', ev.value)) == 1)
        elif isinstance(ev, S.TieSequenceEvent):
            st.tie = bool(int(getattr(ev.value, 'value', ev.value)))
            if not st.tie and open_tie is not None:
                out.add(open_tie[0], 'note', key=open_tie[1], vel=open_tie[2], dur=max(1, t - open_tie[0]))
                open_tie = None
        elif type(ev).__name__ == 'VibratoDepthSequenceEvent':
            st.mod_depth = ev.value
            out.add(t, 'mod', **_mods(st))
        elif type(ev).__name__ == 'VibratoSpeedSequenceEvent':
            st.mod_speed = ev.value
            out.add(t, 'mod', **_mods(st))
        elif type(ev).__name__ == 'VibratoTypeSequenceEvent':
            st.mod_type = int(getattr(ev.value, 'value', ev.value))
            out.add(t, 'mod', **_mods(st))
        elif type(ev).__name__ == 'VibratoRangeSequenceEvent':
            st.mod_range = ev.value
            out.add(t, 'mod', **_mods(st))
        elif type(ev).__name__ == 'VibratoDelaySequenceEvent':
            st.mod_delay = ev.value
            out.add(t, 'mod', **_mods(st))
        elif type(ev).__name__ in ('AttackRateSequenceEvent', 'DecayRateSequenceEvent',
                                   'SustainRateSequenceEvent', 'ReleaseRateSequenceEvent'):
            name = type(ev).__name__.replace('RateSequenceEvent', '').lower()
            setattr(st, name, ev.value)
            out.add(t, 'adsr', which=name, value=ev.value)
        elif type(ev).__name__.startswith('Variable') and 'Equal' in type(ev).__name__ or \
                type(ev).__name__ in ('VariableGreaterThanSequenceEvent', 'VariableLessThanSequenceEvent'):
            if_flag = False
        else:
            pass  # portamento, sweep, variables, print: not representable on MP2K
    if open_tie is not None:
        out.add(open_tie[0], 'note', key=open_tie[1], vel=open_tie[2], dur=max(1, t - open_tie[0]))
    return out, loop, t, st


def _vols(st):
    return dict(volume=st.volume, expression=st.expression)


def _mods(st):
    return dict(depth=st.mod_depth, speed=st.mod_speed, type=st.mod_type, range=st.mod_range, delay=st.mod_delay)


def _rebuild(subType, args):
    cls = S._EVENT_TYPES.get(subType) if hasattr(S, '_EVENT_TYPES') else None
    if subType < 0x80:
        return None  # random note: ignore
    if subType == 0x80:
        return S.RestSequenceEvent(args[-1])
    if cls is None:
        return None
    try:
        return cls(args[-1])
    except Exception:
        return None


def analyze_sequence(seq):
    seq.parse()
    events = seq.events
    idx = {id(e): i for i, e in enumerate(events)}
    tracks = [(0, events[0])]
    for e in events:
        if isinstance(e, S.BeginTrackSequenceEvent):
            tracks.append((e.trackNumber, e.firstEvent))
    return events, idx, tracks


def gcd_lcm(vals):
    l = 1
    for v in vals:
        l = l * v // math.gcd(l, v)
    return l


def convert(seq):
    """Return dict(tracks=[(trackno, Out)], global=Out, loop=(start,end)|None, length)."""
    events, idx, tracks = analyze_sequence(seq)
    # pass 1: find loops
    infos = []
    for tn, first in tracks:
        g = Out()
        out, loop, end_t, _ = simulate_track(events, first, idx, None, g)
        infos.append((tn, first, loop, end_t))
    loops = [i[2] for i in infos if i[2] is not None and i[2][1] > i[2][0]]
    if loops:
        starts = [l[0] for l in loops]
        lens = [l[1] - l[0] for l in loops]
        S0 = max(starts)
        L = gcd_lcm(lens)
        if L > 4 * max(lens):
            L = max(lens)
        loop = (S0, S0 + L)
        until = S0 + L
    else:
        loop = None
        until = max(i[3] for i in infos)
    g = Out()
    result = []
    for tn, first, _, _ in infos:
        out, _, _, _ = simulate_track(events, first, idx, until, g if tn == 0 else g)
        result.append((tn, out))
    return dict(tracks=result, glob=g, loop=loop, length=until,
                aligned=len(set(loops)) <= 1, raw_loops=[(i[0], i[2]) for i in infos])
