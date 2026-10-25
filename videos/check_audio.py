"""Check a rendered video's narration gaps (per 100 ms RMS on the decoded mp4 audio).

Speech spans come from the build's narration.wav (exact zeros between lines). Reports: lead-in (first 150 ms of each
line's clip region before speech), the loudest 100 ms window fully inside any gap, and any gap window adjacent to a
line start/end that sits between -60 and -28 dBFS. Usage: python videos/check_audio.py <video>
"""
import subprocess, sys, wave, pathlib, numpy as np
HERE = pathlib.Path(__file__).resolve().parent
v = sys.argv[1]
nar = HERE / "raw" / "build" / v / "narration.wav"
with wave.open(str(nar)) as w:
    n = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float); sr_n = w.getframerate()
raw = subprocess.run(["/opt/homebrew/bin/ffmpeg", "-v", "error", "-i", str(HERE / f"{v}.mp4"), "-ac", "1", "-ar", "48000",
                      "-f", "s16le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(float) / 32768
win = 4800                                              # 100 ms at 48 kHz
db = lambda x: 20 * np.log10(max(np.sqrt(np.mean(x ** 2)), 1e-12)) if len(x) else -240
speech = np.repeat(n != 0, 2)[: len(a)]                # narration is 24 kHz -> 48 kHz mask
speech = np.pad(speech, (0, max(0, len(a) - len(speech))))
gap_max, bad, k = -240.0, [], len(a) // win
wins_speech = [speech[i * win:(i + 1) * win].any() for i in range(k)]
for i in range(k):
    if wins_speech[i]:
        continue
    lv = db(a[i * win:(i + 1) * win]); gap_max = max(gap_max, lv)
    adj = (i > 0 and wins_speech[i - 1]) or (i + 1 < k and wins_speech[i + 1])
    if adj and -60 < lv < -28:
        bad.append((round(i / 10, 1), round(lv, 1)))
gap_wins = k - sum(wins_speech)
silent = sum(1 for i in range(k) if not wins_speech[i] and db(a[i * win:(i + 1) * win]) <= -90)
peak = 20 * np.log10(np.abs(a).max())
print(f"{v}: {gap_wins} gap windows, {silent} at <= -90 dBFS (or digital zero); loudest gap window {gap_max:.1f} dBFS; "
      f"adjacent windows between -60 and -28 dBFS: {len(bad)} {bad[:5]}; mix peak {peak:.2f} dBFS")
