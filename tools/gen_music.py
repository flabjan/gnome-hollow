"""Synthetische instrumenten voor de gnome-muziek (alle origineel). Basistoon: fluit/luit/viool C4, bas C2."""
import numpy as np, scipy.signal as sg, subprocess, os, wave

SR = 44100
OUT = "/home/claude/gnome-hollow/src/main/resources/assets/gnomehollow/sounds/entity/gnome"
TMP = "/home/claude/gen/wav"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)
rng = np.random.default_rng(42)

def env(n, a, d_end, power=2.0):
    e = np.ones(n); na = int(a*SR); e[:na] = np.linspace(0, 1, na)
    nd = int(d_end*SR); e[-nd:] *= np.linspace(1, 0, nd)**power
    return e

def save(name, x, peak=0.8):
    x = x/(np.max(np.abs(x))+1e-9)*peak
    n = int(0.003*SR); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    p = f"{TMP}/{name}.wav"
    with wave.open(p, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1)*32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p, "-c:a", "libvorbis", "-q:a", "4", "-ac", "1", f"{OUT}/{name}.ogg"], check=True)

def karplus(freq, dur, damping=0.996, bright=0.5):
    n = int(dur*SR); period = int(SR/freq)
    buf = rng.uniform(-1, 1, period)
    buf = sg.lfilter([1-bright, bright], [1], buf)          # zachtere aanslag
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = damping*0.5*(buf[i % period] + buf[(i+1) % period])
    return out

C4 = 261.63; C2 = 65.41
t = lambda d: np.arange(int(d*SR))/SR

# fluit: zuivere toon met een beetje adem en vibrato
d = 0.55; tt = t(d)
vib = 1 + 0.004*np.sin(2*np.pi*5.5*tt)*np.clip(tt/0.15, 0, 1)
ph = 2*np.pi*np.cumsum(C4*vib)/SR
x = np.sin(ph) + 0.18*np.sin(2*ph) + 0.06*np.sin(3*ph)
br = sg.lfilter(*sg.butter(2, [2500/(SR/2), 7000/(SR/2)], "band"), rng.standard_normal(len(tt)))
x = x + 0.05*br*np.clip(1-tt/0.2, 0.3, 1)
save("music_whistle1", x*env(len(tt), 0.02, 0.18, 1.5)*np.exp(-tt*1.6))

# viool: zaagtand met vibrato, gefilterd
d = 0.6; tt = t(d)
vib = 1 + 0.006*np.sin(2*np.pi*5.8*tt)*np.clip(tt/0.2, 0, 1)
ph = np.cumsum(C4*vib)/SR
saw = 2*(ph % 1.0) - 1
x = sg.lfilter(*sg.butter(2, 3200/(SR/2), "low"), saw)
save("music_fiddle1", x*env(len(tt), 0.05, 0.2, 1.5))

# luit: getokkeld snaar (Karplus-Strong)
x = karplus(C4, 0.9, damping=0.997, bright=0.55)
x = sg.lfilter(*sg.butter(1, 4000/(SR/2), "low"), x)
save("music_lute1", x)

# bas: lage getokkelde snaar
x = karplus(C2, 1.0, damping=0.998, bright=0.8)
x = sg.lfilter(*sg.butter(2, 700/(SR/2), "low"), x)
save("music_bass1", x*np.exp(-t(1.0)*1.2))

# trom: korte, zachte toms met sweep
tt = t(0.32)
f = 55 + 95*np.exp(-tt*28)
x = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*13)
nz = sg.lfilter(*sg.butter(2, 900/(SR/2), "low"), rng.standard_normal(len(tt)))*np.exp(-tt*60)
save("music_drum1", x + 0.35*nz)

# tik: houtblokje
tt = t(0.12)
x = np.sin(2*np.pi*880*tt)*np.exp(-tt*55) + 0.6*sg.lfilter(*sg.butter(2, [1500/(SR/2), 5000/(SR/2)], "band"), rng.standard_normal(len(tt)))*np.exp(-tt*80)
save("music_tap1", x)
print("muziek-samples:", sorted(f for f in os.listdir(OUT) if f.startswith("music")))
