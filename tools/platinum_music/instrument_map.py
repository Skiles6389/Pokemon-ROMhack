"""SBNK program -> pokeemerald built-in instrument mapping for Pokemon Platinum's
BANK_BASIC / BANK_BGM_* sound banks.

Chosen by analysing every SBNK region the converted songs actually play
(sample pitch vs. root key, harmonic profile, spectral centroid, noise ratio,
decay curve, ADSR, key range), comparing against the acoustic features of each
DirectSoundWaveData_* sample in sound/direct_sound_samples/, then checking the
result by ear-proxy (rendered mGBA audio metrics).  Only Emerald's own samples
and GBA PSG voices are used -- no DS sample data is ever written to the repo.

Each entry: program -> (kind, target, transpose)
  kind 'ds'       : single DirectSound sample (target = sample name)
  kind 'ks'       : Emerald key-split family (target = keysplit name)
  kind 'drums'    : the shared Platinum drum kit
  kind 'square'   : PSG square (target = GBA duty 0-3)
  kind 'noise'    : PSG noise
transpose: semitones added to every note so the GBA sample sounds at the
same pitch as the DS instrument (octave-tuned samples / 16' organ stops).
"""

PROGRAM_MAP = {
    0:  ('noise', 0, 0),                                    # unused breath/noise hit
    1:  ('drums', None, 0),                                 # standard kit
    2:  ('ks', 'piano', 0),                                 # 8-split acoustic piano
    3:  ('ds', 'sc88pro_fingered_bass', 0),                 # picked bass (decaying)
    4:  ('ds', 'sd90_classical_detuned_ep1_low', 0),        # marimba/vibes-like mallet (pure, fast decay)
    5:  ('ds', 'sd90_classical_detuned_ep1_high', -12),     # celesta/vibraphone (near-sine, decaying)
    6:  ('drums', None, 0),                                 # alt kit (29/30/32 kick/snare layout)
    7:  ('ds', 'sd90_classical_overdrive_guitar', 0),       # bright buzzy plucked guitar
    8:  ('noise', 0, 0),
    9:  ('ds', 'sc88pro_glockenspiel', 0),                  # inharmonic high bell
    10: ('square', 2, 0),
    11: ('ds', 'sc88pro_glockenspiel', 0),                  # music-box/celesta (strong 2-octave partial)
    12: ('ds', 'sd90_classical_detuned_ep1_high', -12),     # sine mallet
    14: ('ds', 'classical_choir_voice_ahhs', 0),            # vocal formant pad
    15: ('ds', 'sc88pro_nylon_str_guitar', 0),              # acoustic guitar (BGM_FIELD wave arc)
    16: ('drums', None, 0),
    17: ('ds', 'sc88pro_organ2', 0),                        # organ (16' sub-octave stop, matches organ2)
    18: ('ds', 'sc88pro_organ2', 0),
    19: ('ds', 'sc88pro_organ2', 0),
    20: ('ks', 'strings', 0),                               # string/synth pad (battle/field arcs)
    21: ('ds', 'sd90_classical_oboe', 0),                   # reedy (strong 3rd harmonic)
    22: ('ks', 'trumpet', 0),
    24: ('ds', 'sd90_classical_detuned_ep1_low', 0),        # electric piano (slow decay to -6 dB)
    27: ('ds', 'sc88pro_nylon_str_guitar', 0),              # bright plucked
    29: ('ds', 'sd90_classical_distortion_guitar_low', 12), # distorted guitar (noisy, low)
    31: ('square', 2, 0),
    32: ('ds', 'sc88pro_fretless_bass', 0),                 # acoustic/fretless bass
    33: ('ds', 'sc88pro_fretless_bass', 0),                 # sine sub bass
    34: ('ds', 'sc88pro_fingered_bass', 0),
    35: ('ds', 'sc88pro_fingered_bass', 0),                 # main electric bass
    36: ('ds', 'sc88pro_synth_bass', 0),
    37: ('ds', 'sc88pro_slap_bass', 0),
    39: ('ds', 'sc88pro_synth_bass', 0),                    # saw synth bass (battles)
    40: ('ks', 'strings', 0),
    41: ('ks', 'trumpet', 0),
    42: ('square', 2, 0),                                   # PSG 50% square
    45: ('ds', 'sc88pro_pizzicato_strings', 0),
    46: ('ds', 'sc88pro_harp', 0),
    47: ('ds', 'sc88pro_timpani', 0),
    48: ('ks', 'strings', 0),                               # string ensemble (most used program)
    50: ('ks', 'french_horn', 0),
    51: ('ds', 'sd90_classical_distortion_guitar_high', 0),
    52: ('square', 2, 0),
    53: ('ds', 'sc88pro_square_wave', 12),                  # square lead (sample sounds +1 oct)
    54: ('ds', 'sc88pro_glockenspiel', 0),
    55: ('ds', 'classical_choir_voice_ahhs', 0),
    56: ('ks', 'trumpet', 0),
    57: ('ks', 'french_horn', 0),
    58: ('ks', 'tuba', 0),
    60: ('ks', 'french_horn', 0),
    61: ('ds', 'sd90_classical_overdrive_guitar', 0),
    62: ('square', 1, 0),
    63: ('square', 0, 0),
    64: ('ks', 'strings', 0),                               # low strings
    65: ('ks', 'strings', 0),
    67: ('square', 2, 0),
    68: ('ds', 'sd90_classical_oboe', 0),
    69: ('noise', 0, 0),
    70: ('square', 1, 0),
    71: ('ds', 'sc88pro_square_wave', 0),                   # clarinet-like odd-harmonic lead
    72: ('square', 2, 0),
    73: ('ds', 'sc88pro_flute', 0),
    74: ('ds', 'sd90_classical_shakuhachi', -12),
    78: ('ds', 'sd90_classical_whistle', -24),              # pure-sine whistle lead (Route 201)
}

KEYSPLITS = {
    'piano':       ['sc88pro_piano1_48', 'sc88pro_piano1_60', 'sc88pro_piano1_72', 'sc88pro_piano1_84'],
    'strings':     ['sc88pro_string_ensemble_60', 'sc88pro_string_ensemble_72', 'sc88pro_string_ensemble_84'],
    'trumpet':     ['sc88pro_trumpet_60', 'sc88pro_trumpet_72', 'sc88pro_trumpet_84'],
    'tuba':        ['sc88pro_tuba_39', 'sc88pro_tuba_51'],
    'french_horn': ['sc88pro_french_horn_60', 'sc88pro_french_horn_72'],
}

# DS drum key -> (sample or 'noise', resample?, key, pan, A, D, S, R)
# Built from Emerald/R-S kit entries; DS kit is GM-like, plus 29/30/32 used by the alt kit.
_KICK = ('sc88pro_rnd_kick', False, 60, 64, 255, 0, 255, 242)
_KICK2 = ('drum_and_percussion_kick', False, 64, 64, 255, 0, 255, 0)
_SNARE = ('sc88pro_rnd_snare', False, 60, 64, 255, 0, 255, 242)
_SNARE2 = ('sc88pro_orchestra_snare', False, 60, 64, 255, 0, 255, 242)
_CRASH = ('sc88pro_orchestra_cymbal_crash', False, 30, 64, 255, 246, 0, 216)
DRUM_MAP = {
    27: ('noise', None, 60, 64, 0, 0, 15, 0),
    29: _KICK, 30: _SNARE, 32: _SNARE2,
    31: ('noise', None, 60, 64, 0, 0, 15, 0),
    34: ('noise', None, 60, 64, 0, 1, 0, 1),
    35: _KICK2, 36: _KICK,
    37: ('sd90_solo_snare', False, 64, 64, 255, 180, 175, 228),
    38: _SNARE,
    39: ('sc88pro_tr909_hand_clap', False, 60, 64, 255, 255, 255, 127),
    40: _SNARE2,
    41: ('unused_sc55_tom', True, 48, 44, 255, 210, 77, 204),
    43: ('unused_sc55_tom', True, 51, 54, 255, 216, 77, 204),
    45: ('unused_sc55_tom', True, 54, 64, 255, 216, 77, 204),
    47: ('unused_sc55_tom', True, 57, 69, 255, 210, 77, 204),
    48: ('unused_sc55_tom', True, 60, 79, 255, 204, 77, 204),
    50: ('unused_sc55_tom', True, 62, 84, 255, 204, 77, 204),
    42: ('unknown_close_hihat', False, 60, 79, 255, 127, 0, 188),
    44: ('unknown_close_hihat', True, 66, 74, 255, 100, 0, 160),
    46: ('unknown_open_hihat', False, 60, 79, 255, 242, 141, 0),
    49: _CRASH, 57: _CRASH, 58: _CRASH,
    51: ('unknown_open_hihat', True, 52, 54, 255, 230, 0, 180),
    59: ('unknown_open_hihat', True, 52, 74, 255, 230, 0, 180),
    52: ('trinity_cymbal_crash', False, 60, 44, 255, 235, 0, 165),
    53: ('dance_drums_ride_bell', False, 64, 64, 255, 165, 103, 231),
    54: ('sc88pro_tambourine', False, 66, 64, 255, 127, 77, 204),
    55: ('trinity_cymbal_crash', False, 60, 84, 255, 220, 0, 140),
    61: ('unused_heart_of_asia_indian_drum', False, 64, 64, 255, 0, 255, 0),
    62: ('sc88pro_mute_high_conga', False, 64, 64, 255, 0, 255, 0),
    63: ('sc88pro_open_low_conga', True, 72, 64, 255, 0, 255, 0),
    64: ('sc88pro_open_low_conga', False, 64, 64, 255, 0, 255, 0),
    76: ('ethnic_flavours_hyoushigi', True, 64, 64, 255, 0, 255, 0),
    77: ('ethnic_flavours_hyoushigi', True, 58, 64, 255, 0, 255, 0),
    80: ('sd90_open_triangle', False, 64, 64, 255, 165, 103, 188),
    81: ('sd90_open_triangle', False, 64, 64, 255, 242, 103, 188),
    83: ('sc88pro_jingle_bell', False, 64, 64, 255, 0, 255, 0),
}
