# Pokémon Platinum soundtrack → pokeemerald-expansion

These tools turn the **note sequences** (SSEQ) in your own legally dumped
Pokémon Platinum cartridge into `mid2agb` MIDI files. The MIDI files play on
**Emerald's own built-in instruments**.

**Nothing from the DS ROM goes into this repository.** That includes the `.nds`
file, the SDAT, SSEQ/SBNK/SWAR/SWAV files and decoded PCM samples. The
`.gitignore` blocks those file types. The only output files are:

* `sound/songs/midi/mus_pl_*.mid`: notes, tempo, loop markers and controllers.
* `sound/voicegroups/platinum/*.inc`: voicegroups that reference only
  `DirectSoundWaveData_*` samples and GBA PSG voices that already exist in
  pokeemerald-expansion.

## Regenerating

```sh
pip install ndspy mido numpy
# extract pl_sound_data.sdat from your own dump, OUTSIDE the repo, e.g. with ndspy:
python3 -c "import ndspy.rom; r=ndspy.rom.NintendoDSRom.fromFile('platinum.nds'); \
open('pl_sound_data.sdat','wb').write(r.getFileByName('data/sound/pl_sound_data.sdat'))"
python3 tools/platinum_music/convert_platinum_music.py /path/outside/repo/pl_sound_data.sdat
make -j$(nproc)
```

The script prints the `midi.cfg` lines. Those lines are already in
`sound/songs/midi/midi.cfg`.

## How the conversion works

| Step | File | Notes |
|---|---|---|
| SSEQ interpreter | `sseq_sim.py` | Handles notes, ties, note-wait, call/return, loop/jump, random/variable/if, volume, expression, pan, pitch bend + range, modulation, tempo and track priority. The loop is aligned across all tracks: start = latest track start, length = LCM of the track loop lengths. |
| Instrument matching | `instrument_map.py` | We decoded each DS instrument sample locally and compared its spectrum, f0, harmonic profile and decay with Emerald's samples. Each DS program then got the closest Emerald voice plus an octave fix, measured with FFT. This is not a blind General MIDI mapping. Percussion is mapped key by key onto one shared Emerald drum kit. |
| Envelopes | `convert_platinum_music.py` | DS ADSR (5.2 ms ticks, 0.1 dB steps) is converted to MP2K per-frame ADSR. Strings, horns, trumpets, tuba and piano use custom keysplits that carry the DS envelope. |
| Levels | `convert_platinum_music.py`, `song_list.py` | DS volume, expression and velocity use a squared curve. CC7 is used up to 127 first (keeps the track balance), then velocity. `SONG_GAINS` sets each song's level so it sits near Emerald's own BGM loudness in mGBA without clipping. |
| Priority | | The lead track gets CC33 = 80, bass 70, drums 60, everything else 50. This decides which voices survive when all 12 DirectSound channels are in use. |

## Engine changes

* `NUM_TRACKS_BGM`: 10 → 16. Platinum songs use up to 11 tracks.
* DirectSound channels: 5 → 12 (`src/m4a.c`).

## Wiring

* Sinnoh maps set `music` / `night_music` in `map.json`.
* `GetRegionalSongOverride()` in `src/sound.c` swaps in the Platinum battle,
  victory, encounter and evolution songs and the fanfares, but only while the
  player is in the Sinnoh map sections (`IsPlayerInSinnoh()`). Emerald and
  Kanto keep their own music.
