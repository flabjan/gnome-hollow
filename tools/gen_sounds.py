"""Synthetische gnome-stem: hoge, schelmse, nasale kabouter-taal (formant-synthese, volledig origineel)."""
import numpy as np, scipy.signal as sg, subprocess, os, wave, json, sys

SR = 44100
OUT = "/home/claude/gnome-hollow/src/main/resources/assets/gnomehollow/sounds/entity/gnome"
TMP = "/home/claude/gen/wav"
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

VOW = {  # F1,F2,F3 (volwassen man); we schalen omhoog voor een klein kaboutertje
 "ee": (270,2290,3010), "ih": (390,1990,2550), "eh": (530,1840,2480), "ah": (730,1090,2440),
 "aw": (570,840,2410), "oo": (300,870,2240), "uh": (640,1190,2390), "oh": (450,1000,2400),
}
FSCALE = 1.45

def reson(x, f, bw):
    f = min(f, SR*0.45)
    r = np.exp(-np.pi*bw/SR); th = 2*np.pi*f/SR
    return sg.lfilter([1-r], [1, -2*r*np.cos(th), r*r], x)

def formants(x, vowel, nasal=False, fscale=FSCALE):
    f1, f2, f3 = [v*fscale for v in VOW[vowel]]
    g = (1.0, 0.7, 0.35)
    if nasal: g = (0.9, 0.25, 0.12)
    y = g[0]*reson(x, f1, 90) + g[1]*reson(x, f2, 130) + g[2]*reson(x, f3, 200) + 0.15*reson(x, 4200, 600)
    if nasal: y += 1.2*reson(x, 280, 60) + 0.5*reson(x, 1000, 150)
    return y

def contour(points, n):
    """points: lijst (t0..1, f0). Geeft f0 per sample."""
    t = np.linspace(0, 1, n)
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return np.interp(t, xs, ys)

def source(f0, rng, jitter=0.012, vib=(7.0, 0.015), rough=0.0):
    n = len(f0); t = np.arange(n)/SR
    f = f0 * (1 + vib[1]*np.sin(2*np.pi*vib[0]*t + rng.uniform(0, 6.28)))
    f = f * (1 + jitter*np.cumsum(rng.standard_normal(n))/np.sqrt(np.arange(1, n+1)+400))
    if rough > 0: f = f * (1 + rough*np.sign(np.sin(2*np.pi*55*t)))
    # sawtooth op 2x samplerate (minder aliasing), daarna terug
    f2 = np.repeat(f, 2); ph = np.cumsum(f2)/(SR*2)
    saw = 2*(ph % 1.0) - 1
    s = sg.resample_poly(saw, 1, 2)[:n]
    return s - np.mean(s)

def env(n, a=0.008, d=0.25, hold=0.0):
    e = np.ones(n); na = max(1, int(a*SR)); nd = max(1, int(d*n))
    e[:na] = np.linspace(0, 1, na); e[-nd:] *= np.linspace(1, 0, nd)**1.3
    return e

def noise(n, rng): return rng.standard_normal(n)

def cons(kind, rng, amp=1.0):
    """korte medeklinkers (ruis/bursts)."""
    if kind == "h":
        n = int(0.05*SR); x = noise(n, rng); x = sg.lfilter(*sg.butter(2, [1500/(SR/2), 7000/(SR/2)], "band"), x)
        return amp*0.5*x*env(n, 0.005, 0.6)
    if kind in ("k", "g"):
        n = int(0.03*SR); x = noise(n, rng); x = sg.lfilter(*sg.butter(2, [800/(SR/2), 4000/(SR/2)], "band"), x)
        return amp*0.9*x*np.exp(-np.linspace(0, 7, n))
    if kind in ("p", "b"):
        n = int(0.03*SR); x = noise(n, rng); x = sg.lfilter(*sg.butter(2, 900/(SR/2), "low"), x)
        return amp*1.0*x*np.exp(-np.linspace(0, 8, n))
    if kind == "t":
        n = int(0.02*SR); x = noise(n, rng); x = sg.lfilter(*sg.butter(2, 3000/(SR/2), "high"), x)
        return amp*0.7*x*np.exp(-np.linspace(0, 9, n))
    if kind == "s":
        n = int(0.09*SR); x = noise(n, rng); x = sg.lfilter(*sg.butter(2, 4500/(SR/2), "high"), x)
        return amp*0.45*x*env(n, 0.02, 0.5)
    return np.zeros(0)

def syl(v1, dur, pts, rng, v2=None, nasal=False, c=None, amp=1.0, breath=0.04, vib=(7.0, 0.015), rough=0.0, fscale=FSCALE, a=0.008, d=0.28):
    n = int(dur*SR)
    f0 = contour(pts, n)
    src = source(f0, rng, vib=vib, rough=rough)
    if breath: src = src + breath*noise(n, rng)
    y1 = formants(src, v1, nasal, fscale)
    if v2:
        y2 = formants(src, v2, nasal, fscale)
        w = np.linspace(0, 1, n)**1.2
        y = y1*(1-w) + y2*w
    else:
        y = y1
    y = y/ (np.max(np.abs(y))+1e-9)
    y = y*env(n, a, d)*amp
    if c:
        y = np.concatenate([cons(c, rng, amp), y])
    return y

def sil(d): return np.zeros(int(d*SR))

def cat(parts, overlap=0.0):
    out = np.zeros(0)
    ov = int(overlap*SR)
    for p in parts:
        if len(out) == 0 or ov == 0: out = np.concatenate([out, p]); continue
        k = min(ov, len(out), len(p))
        out[-k:] += p[:k]*np.linspace(0, 1, k) * 1.0
        out[-k:] *= 1.0
        out = np.concatenate([out, p[k:]])
    return out

def tinkle(freqs, step, rng, amp=0.25):
    n = int((step*len(freqs) + 0.35)*SR); out = np.zeros(n)
    for i, f in enumerate(freqs):
        t = np.arange(int(0.35*SR))/SR
        s = np.sin(2*np.pi*f*t)*np.exp(-t*9) + 0.4*np.sin(2*np.pi*f*2.01*t)*np.exp(-t*14)
        o = int(i*step*SR); out[o:o+len(s)] += amp*s
    return out

def finish(x, peak=0.85, hp=180):
    x = sg.lfilter(*sg.butter(2, hp/(SR/2), "high"), x)
    x = np.tanh(1.4*x)
    x = x/(np.max(np.abs(x))+1e-9)*peak
    n = int(0.004*SR); x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x

def save(name, x):
    x = finish(x) if len(x) else x
    path = f"{TMP}/{name}.wav"
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1)*32767).astype("<i2").tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", path, "-c:a", "libvorbis", "-q:a", "4", "-ac", "1", f"{OUT}/{name}.ogg"], check=True)

R = lambda s: np.random.default_rng(s)
B = 540.0   # basis-toonhoogte (Hz): hoog en schelms

# ---------------------------------------------------------------- ambient: kabouter-gebrabbel (6)
def ambient(i):
    r = R(100+i)
    recipes = [
      [("h","ee",.11,[(0,B*1.0),(1,B*1.25)]), ("n","eh",.16,[(0,B*1.1),(1,B*0.9)],"ih")],                     # "hee-nyeh"
      [("g","ah",.12,[(0,B*0.9),(1,B*1.1)]), ("g","ah",.12,[(0,B*1.15),(1,B*0.95)]), ("h","ee",.18,[(0,B*1.3),(1,B*1.6)])],  # "gah-gah-heee?"
      [("m","uh",.18,[(0,B*0.8),(1,B*0.85)],None,True), ("h","ee",.14,[(0,B*1.3),(1,B*1.05)]), ("h","oh",.20,[(0,B*1.0),(1,B*0.7)])], # "mm-hee-hoo"
      [("b","eh",.09,[(0,B*1.2),(1,B*1.0)]), ("b","eh",.09,[(0,B*1.3),(1,B*1.05)]), ("b","eh",.09,[(0,B*1.4),(1,B*1.1)]), ("h","ah",.2,[(0,B*1.2),(1,B*0.8)])],  # "beh-beh-beh-hah"
      [("n","ee",.2,[(0,B*0.9),(1,B*1.5)],"eh"), ("","oo",.22,[(0,B*1.4),(1,B*0.9)])],                                  # "nyee-oo?"
      [("h","ih",.08,[(0,B*1.3),(1,B*1.3)]), ("h","ih",.08,[(0,B*1.4),(1,B*1.4)]), ("g","ah",.1,[(0,B*1.0),(1,B*0.9)]), ("n","oh",.22,[(0,B*1.1),(1,B*0.65)])],
    ]
    parts = []
    for p in recipes[i % len(recipes)]:
        c, v, d, pts = p[0], p[1], p[2], p[3]
        v2 = p[4] if len(p) > 4 else None; nasal = p[5] if len(p) > 5 else False
        if c == "n": nasal_c = True
        parts.append(syl(v, d*r.uniform(.95, 1.08), pts, r, v2=v2, nasal=(c in ("n","m")) or nasal, c=c if c in ("h","g","b","k","t","s","p") else None, amp=.9))
        parts.append(sil(r.uniform(.015, .04)))
    return cat(parts)
for i in range(6): save(f"ambient{i+1}", ambient(i))

# ---------------------------------------------------------------- greet (3): "Hii-hii!" blije begroeting
def greet(i):
    r = R(200+i)
    if i == 0: return cat([syl("ee", .13, [(0,B*1.2),(1,B*1.6)], r, c="h"), sil(.03), syl("ee", .2, [(0,B*1.5),(1,B*1.9)], r, v2="ih")])
    if i == 1: return cat([syl("eh", .1, [(0,B*1.2),(1,B*1.4)], r, c="h"), sil(.02), syl("ah", .1, [(0,B*1.4),(1,B*1.3)], r, c="g"), sil(.02), syl("oh", .22, [(0,B*1.5),(1,B*1.0)], r)])
    return cat([syl("ah", .12, [(0,B*1.1),(1,B*1.5)], r, c="h"), sil(.03), syl("ee", .12, [(0,B*1.6),(1,B*1.8)], r), sil(.03), syl("ee", .25, [(0,B*1.9),(1,B*1.4)], r, vib=(9,.03))])
for i in range(3): save(f"greet{i+1}", greet(i))

# ---------------------------------------------------------------- yes (3) / no (3): reactie op rechtsklik
def yes(i):
    r = R(300+i)
    if i == 0: return cat([syl("uh", .12, [(0,B*0.9),(1,B*0.9)], r, nasal=True), sil(.03), syl("uh", .2, [(0,B*1.25),(1,B*1.45)], r, nasal=True)])       # mm-HM!
    if i == 1: return cat([syl("ee", .1, [(0,B*1.3),(1,B*1.4)], r, c="h"), sil(.02), syl("eh", .22, [(0,B*1.5),(1,B*1.9)], r, v2="ee")])            # hee-yeh!
    return cat([syl("eh", .1, [(0,B*1.2),(1,B*1.3)], r), sil(.02), syl("ah", .1, [(0,B*1.3),(1,B*1.5)], r, c="h"), sil(.02), syl("ee", .2, [(0,B*1.6),(1,B*1.9)], r)])
def no(i):
    r = R(400+i)
    if i == 0: return cat([syl("uh", .14, [(0,B*1.2),(1,B*1.0)], r, nasal=True), sil(.04), syl("uh", .22, [(0,B*0.95),(1,B*0.7)], r, nasal=True)])    # nuh-uh
    if i == 1: return cat([syl("eh", .22, [(0,B*1.1),(1,B*0.7)], r, c="b", rough=.03), sil(.03), syl("eh", .16, [(0,B*0.9),(1,B*0.65)], r, c="b", rough=.03)])  # bleh-bleh
    return cat([syl("oh", .2, [(0,B*0.9),(1,B*0.6)], r, c="g", rough=.04), sil(.03), syl("uh", .24, [(0,B*0.8),(1,B*0.55)], r, nasal=True)])
for i in range(3): save(f"yes{i+1}", yes(i)); save(f"no{i+1}", no(i))

# ---------------------------------------------------------------- hurt (4), death (2)
def hurt(i):
    r = R(500+i)
    if i == 0: return syl("eh", .22, [(0,B*1.7),(1,B*0.9)], r, v2="ah", c="g", vib=(10,.03))
    if i == 1: return cat([syl("ee", .08, [(0,B*1.9),(1,B*2.0)], r), syl("oh", .2, [(0,B*1.6),(1,B*0.8)], r)])
    if i == 2: return syl("ah", .26, [(0,B*1.5),(1,B*0.75)], r, c="h", rough=.05)
    return cat([syl("uh", .07, [(0,B*1.2),(1,B*1.5)], r, nasal=True), syl("ee", .22, [(0,B*2.0),(1,B*1.0)], r, v2="eh", vib=(11,.04))])
for i in range(4): save(f"hurt{i+1}", hurt(i))
def death(i):
    r = R(600+i)
    if i == 0:
        return cat([syl("ah", .3, [(0,B*1.8),(0.5,B*1.3),(1,B*0.55)], r, v2="oh", vib=(9,.04), rough=.03), sil(.04),
                    syl("oh", .25, [(0,B*0.8),(1,B*0.35)], r, rough=.06), sil(.05), tinkle([2093, 1568, 1047], .06, r, .15)*0.6])
    return cat([syl("ee", .12, [(0,B*2.0),(1,B*1.9)], r), syl("ah", .45, [(0,B*1.7),(1,B*0.45)], r, v2="aw", vib=(8,.05), rough=.04), sil(.05), cons("p", r)*1.4])
for i in range(2): save(f"death{i+1}", death(i))

# ---------------------------------------------------------------- attack (4): oorlogskreet van de krijgers
def attack(i):
    r = R(700+i)
    if i == 0: return syl("ah", .3, [(0,B*1.2),(0.3,B*1.9),(1,B*1.1)], r, c="h", rough=.04, breath=.1)       # HYAAH!
    if i == 1: return cat([syl("eh", .1, [(0,B*1.4),(1,B*1.7)], r, c="g", rough=.05), syl("ah", .22, [(0,B*1.9),(1,B*1.2)], r, rough=.05, breath=.1)])
    if i == 2: return syl("oh", .26, [(0,B*1.0),(0.4,B*1.5),(1,B*0.9)], r, c="g", rough=.07, breath=.12)
    return cat([syl("ee", .09, [(0,B*1.7),(1,B*1.8)], r, c="h", rough=.05), syl("aw", .24, [(0,B*1.8),(1,B*1.0)], r, rough=.06, breath=.1)])
for i in range(4): save(f"attack{i+1}", attack(i))

# ---------------------------------------------------------------- alert (3): schrik/vlucht
def alert(i):
    r = R(800+i)
    if i == 0: return syl("ee", .55, [(0,B*1.9),(0.5,B*2.3),(1,B*2.0)], r, vib=(8.5,.035), breath=.08)
    if i == 1: return cat([syl("eh", .1, [(0,B*1.9),(1,B*2.1)], r, c="h"), sil(.02), syl("ee", .1, [(0,B*2.2),(1,B*2.3)], r), sil(.02), syl("ee", .35, [(0,B*2.3),(1,B*1.8)], r, vib=(9,.04))])
    return cat([syl("ah", .12, [(0,B*1.7),(1,B*2.0)], r), sil(.02), syl("ah", .12, [(0,B*1.9),(1,B*2.2)], r), sil(.02), syl("ee", .38, [(0,B*2.3),(1,B*1.7)], r, vib=(10,.04))])
for i in range(3): save(f"alert{i+1}", alert(i))

# ---------------------------------------------------------------- laugh (3): het "gnomed" gegiechel
def laugh(i):
    r = R(900+i); parts = []
    n = [5, 7, 4][i]; base = [1.5, 1.7, 1.35][i]
    for k in range(n):
        f = B*base*(1.0 - 0.04*k)
        parts.append(syl("ee", .09, [(0,f*0.95),(1,f*1.08)], r, c="h", amp=0.95-0.05*k, breath=.07, a=.006, d=.4))
        parts.append(sil(.055))
    if i == 1: parts.append(syl("oh", .22, [(0,B*1.3),(1,B*0.85)], r, c="h"))
    return cat(parts)
for i in range(3): save(f"laugh{i+1}", laugh(i))

# ---------------------------------------------------------------- celebrate (3) / fish_catch (2)
def celebrate(i):
    r = R(1000+i)
    if i == 0: return cat([syl("ee", .11, [(0,B*1.4),(1,B*1.7)], r, c="h"), sil(.02), syl("ee", .11, [(0,B*1.7),(1,B*2.0)], r), sil(.02), syl("oo", .28, [(0,B*2.0),(1,B*1.5)], r, v2="ah")])
    if i == 1: return cat([syl("ah", .12, [(0,B*1.3),(1,B*1.6)], r, c="y" and "h"), sil(.02), syl("ee", .3, [(0,B*1.7),(0.6,B*2.2),(1,B*1.9)], r, vib=(9,.03))])
    return cat([syl("uh", .1, [(0,B*1.1),(1,B*1.3)], r, nasal=True), sil(.02), syl("eh", .1, [(0,B*1.5),(1,B*1.5)], r, c="h"), sil(.02), syl("ah", .1, [(0,B*1.7),(1,B*1.7)], r, c="h"), sil(.02), syl("oh", .24, [(0,B*1.9),(1,B*1.2)], r)])
for i in range(3): save(f"celebrate{i+1}", celebrate(i))
def fish_catch(i):
    r = R(1100+i)
    if i == 0: return cat([syl("oo", .2, [(0,B*1.1),(1,B*1.7)], r, v2="ah"), sil(.03), syl("oo", .25, [(0,B*1.9),(1,B*2.2)], r, v2="ee", c="h")]) + tinkle([1760, 2349], .07, r, .08)[:int(.5*SR)].mean()*0
    return cat([syl("ah", .12, [(0,B*1.4),(1,B*1.7)], r, c="h"), sil(.02), syl("oh", .3, [(0,B*1.9),(1,B*1.4)], r)])
for i in range(2): save(f"fish_catch{i+1}", fish_catch(i))

# ---------------------------------------------------------------- werkgeluiden
def work_brew(i):
    r = R(1200+i)
    if i == 0:  # "mm-hm-mm" neuriën
        return cat([syl("uh", .22, [(0,B*0.9),(1,B*1.05)], r, nasal=True, breath=.02), sil(.03), syl("uh", .22, [(0,B*1.1),(1,B*1.25)], r, nasal=True, breath=.02), sil(.03), syl("uh", .3, [(0,B*1.0),(1,B*0.8)], r, nasal=True, breath=.02)])
    return cat([syl("oo", .2, [(0,B*1.2),(1,B*1.2)], r, nasal=True), syl("oh", .2, [(0,B*1.4),(1,B*1.4)], r, nasal=True), syl("oo", .3, [(0,B*1.0),(1,B*0.9)], r, nasal=True)]) + 0
for i in range(2): save(f"work_brew{i+1}", work_brew(i))
def heal(i):
    r = R(1300+i)
    v = cat([syl("ee", .1, [(0,B*1.5),(1,B*1.8)], r, c="h"), sil(.02), syl("ah", .22, [(0,B*1.9),(1,B*1.5)], r, v2="ee")])
    t = tinkle([1568, 2093, 2637] if i == 0 else [2093, 2637, 3136], .07, r, .22)
    n = max(len(v), len(t)); out = np.zeros(n); out[:len(v)] += v; out[:len(t)] += t*0.7
    return out
for i in range(2): save(f"heal{i+1}", heal(i))
def work_farm(i):
    r = R(1400+i)
    return syl(["uh","ah","oh"][i], .13, [(0,B*1.2),(1,B*0.95)], r, c="h", rough=.03, amp=1.0)
for i in range(3): save(f"work_farm{i+1}", work_farm(i))
def work_build(i):
    r = R(1500+i)
    return syl(["uh","oh","ah"][i], .15, [(0,B*0.85),(1,B*0.6)], r, c="g", rough=.05, breath=.08)
for i in range(3): save(f"work_build{i+1}", work_build(i))
def work_fish(i):
    r = R(1600+i)
    if i == 0: return cat([syl("oo", .3, [(0,B*0.9),(1,B*1.0)], r, nasal=True), sil(.04), syl("oh", .3, [(0,B*1.05),(1,B*0.8)], r, nasal=True)])
    return cat([syl("uh", .18, [(0,B*1.0),(1,B*1.2)], r, nasal=True), sil(.03), syl("uh", .18, [(0,B*1.2),(1,B*0.95)], r, nasal=True), sil(.03), syl("oo", .3, [(0,B*0.9),(1,B*0.7)], r, nasal=True)])
for i in range(2): save(f"work_fish{i+1}", work_fish(i))

# ---------------------------------------------------------------- snurken (2) en stapjes (3)
def snore(i):
    r = R(1700+i); n = int((1.5+0.3*i)*SR); t = np.arange(n)/SR
    cycle = (np.sin(np.pi*np.clip(t/(n/SR), 0, 1)))**2
    x = sg.lfilter(*sg.butter(2, [120/(SR/2), 900/(SR/2)], "band"), noise(n, r))*cycle*(1+0.5*np.sin(2*np.pi*28*t))
    sq = np.sin(2*np.pi*(1500+300*np.sin(2*np.pi*3*t))*t)*cycle**4*0.08           # fluitende uitademing
    return 1.2*x/ (np.max(np.abs(x))+1e-9) + sq
for i in range(2): save(f"snore{i+1}", snore(i))
def step(i):
    r = R(1800+i); n = int(0.07*SR)
    x = sg.lfilter(*sg.butter(2, [1800/(SR/2), 5200/(SR/2)], "band"), noise(n, r))*np.exp(-np.linspace(0, 11, n))
    t = np.arange(n)/SR
    return x/ (np.max(np.abs(x))+1e-9) + 0.3*np.sin(2*np.pi*(900+i*180)*t)*np.exp(-t*90)
for i in range(3): save(f"step{i+1}", step(i))

print(len(os.listdir(OUT)), "ogg-bestanden", sum(os.path.getsize(f"{OUT}/{f}") for f in os.listdir(OUT))//1024, "KB")
