"""Bibliotheek voor het genereren van Minecraft structure-templates (NBT) met jigsaw-blokken."""
import gzip, struct, os, math, random, json

ROOT = "/home/claude/gnome-hollow/src/main/resources/data/gnomehollow"
DATA_VERSION = 4671

# ------------------------------------------------------------------ NBT
class I(int): pass
class B(int): pass
class D(float): pass
class S(str): pass
class L:
    def __init__(self, tid, items): self.tid, self.items = tid, items
TID = {B:1, I:3, D:6, S:8, dict:10}

def w_payload(buf, v):
    if isinstance(v, B): buf += struct.pack(">b", v)
    elif isinstance(v, I): buf += struct.pack(">i", v)
    elif isinstance(v, D): buf += struct.pack(">d", v)
    elif isinstance(v, S):
        e = v.encode(); buf += struct.pack(">H", len(e)) + e
    elif isinstance(v, L):
        buf += struct.pack(">bi", v.tid, len(v.items))
        for it in v.items: w_payload(buf, it)
    elif isinstance(v, dict):
        for k, val in v.items():
            t = 9 if isinstance(val, L) else TID[type(val)]
            buf += struct.pack(">b", t)
            e = k.encode(); buf += struct.pack(">H", len(e)) + e
            w_payload(buf, val)
        buf += b"\x00"
    else: raise TypeError(type(v))

def write_nbt(path, root):
    buf = bytearray(b"\x0a\x00\x00"); w_payload(buf, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.GzipFile(path, "wb", mtime=0) as f: f.write(bytes(buf))

G = 4   # grondlaag-index in elke template
DIR = {"north": (0,-1), "south": (0,1), "east": (1,0), "west": (-1,0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}
REGISTRY = {}     # naam -> Tpl (voor previews en controles)

class Tpl:
    def __init__(self, name, sx, sy, sz):
        self.name = name; self.size = (sx, sy, sz); self.blocks = {}; self.ents = []; self.jig = []
        REGISTRY[name] = self
    def set(self, x, y, z, name, nbt=None, **props):
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]): return
        if ":" not in name: name = "minecraft:" + name
        pr = tuple(sorted((k, str(v).lower() if isinstance(v, bool) else str(v)) for k, v in props.items()))
        self.blocks[(x, y, z)] = (name, pr, nbt)
    def get(self, x, y, z):
        b = self.blocks.get((x, y, z)); return b[0].replace("minecraft:", "") if b else None
    def fill(self, x1, y1, z1, x2, y2, z2, name, **props):
        for x in range(min(x1,x2), max(x1,x2)+1):
            for y in range(min(y1,y2), max(y1,y2)+1):
                for z in range(min(z1,z2), max(z1,z2)+1): self.set(x, y, z, name, **props)
    def stairs(self, x, y, z, name, facing, half="bottom", shape="straight"):
        self.set(x, y, z, name, facing=facing, half=half, shape=shape, waterlogged=False)
    def slab(self, x, y, z, name, type="bottom"):
        self.set(x, y, z, name, type=type, waterlogged=False)
    def door(self, x, y, z, name, facing, hinge="left"):
        self.set(x, y, z, name, facing=facing, half="lower", hinge=hinge, open=False, powered=False)
        self.set(x, y+1, z, name, facing=facing, half="upper", hinge=hinge, open=False, powered=False)
    def chest(self, x, y, z, facing, loot):
        self.set(x, y, z, "chest", nbt={"id": S("minecraft:chest"), "LootTable": S(f"gnomehollow:chests/{loot}")},
                 facing=facing, type="single", waterlogged=False)
    def barrel(self, x, y, z, loot, facing="up"):
        self.set(x, y, z, "barrel", nbt={"id": S("minecraft:barrel"), "LootTable": S(f"gnomehollow:chests/{loot}")}, facing=facing, open=False)
    def bed(self, x, y, z, color, facing):
        dx, dz = DIR[facing]
        self.set(x, y, z, f"{color}_bed", facing=facing, part="foot", occupied=False)
        self.set(x+dx, y, z+dz, f"{color}_bed", facing=facing, part="head", occupied=False)
    def pane(self, x, y, z, along="x"):
        if along == "x": self.set(x, y, z, "glass_pane", east=True, west=True)
        else: self.set(x, y, z, "glass_pane", north=True, south=True)
    def gnome(self, prof, x, y, z): self.ents.append((x, y, z, f"gnomehollow:gnome_{prof}"))
    def jigsaw(self, x, y, z, facing, name, target, pool, final="minecraft:dirt_path"):
        self.set(x, y, z, "jigsaw", orientation=f"{facing}_up",
                 nbt={"id": S("minecraft:jigsaw"), "name": S(name), "target": S(target), "pool": S(pool),
                      "final_state": S(final), "joint": S("aligned")})
        self.jig.append((x, y, z, facing, name, target, pool))
    def save(self):
        palette, index, blocks = [], {}, []
        for (x, y, z), (name, props, nbt) in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            k2 = (name, props)
            if k2 not in index:
                index[k2] = len(palette)
                e = {"Name": S(name)}
                if props: e["Properties"] = {k: S(v) for k, v in props}
                palette.append(e)
            b = {"pos": L(3, [I(x), I(y), I(z)]), "state": I(index[k2])}
            if nbt: b["nbt"] = nbt
            blocks.append(b)
        ents = [{"pos": L(6, [D(x+0.5), D(y), D(z+0.5)]), "blockPos": L(3, [I(int(x)), I(int(y)), I(int(z))]),
                 "nbt": {"id": S(eid), "PersistenceRequired": B(1)}} for (x, y, z, eid) in self.ents]
        root = {"DataVersion": I(DATA_VERSION), "size": L(3, [I(v) for v in self.size]), "palette": L(10, palette),
                "blocks": L(10, blocks), "entities": L(10, ents)}
        write_nbt(f"{ROOT}/structure/village/{self.name}.nbt", root)

# ------------------------------------------------------------------ gedeelde bouwstenen
FLOWERS = ["poppy", "azure_bluet", "lily_of_the_valley", "cornflower", "blue_orchid", "allium", "dandelion", "oxeye_daisy"]
SHROOMS = ["red_mushroom", "brown_mushroom"]
CAP_ALL = dict(up=True, down=True, north=True, south=True, east=True, west=True)

ROOFS = {
 "thatch":   dict(block="gnomehollow:thatch", stairs="gnomehollow:thatch_stairs", slab="gnomehollow:thatch_slab"),
 "shingle":  dict(block="gnomehollow:gnome_shingles", stairs="gnomehollow:gnome_shingle_stairs", slab="gnomehollow:gnome_shingle_slab"),
 "toadstool": dict(block="gnomehollow:toadstool_cap", stairs="gnomehollow:toadstool_cap_stairs", slab="gnomehollow:toadstool_cap_slab"),
 "spruce":   dict(block="spruce_planks", stairs="spruce_stairs", slab="spruce_slab"),
}

def ground(t, rng, x0=0, x1=None, z0=0, z1=None, h=None):
    """Fundering (dirt), grondlaag (gras/podzol) en lucht erboven."""
    sx, sy, sz = t.size
    x1 = sx-1 if x1 is None else x1; z1 = sz-1 if z1 is None else z1; h = sy-1 if h is None else h
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            for y in range(0, G): t.set(x, y, z, "dirt")
            t.set(x, G, z, "podzol" if rng.random() < 0.3 else ("moss_block" if rng.random() < 0.05 else "grass_block"))
            for y in range(G+1, h+1): t.set(x, y, z, "air")

def scatter(t, rng, x0, x1, z0, z1, p=0.1, choices=None, y=G+1):
    choices = choices or (FLOWERS + SHROOMS + ["fern", "short_grass"])
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            if t.get(x, G, z) in ("grass_block", "podzol") and t.get(x, y, z) in (None, "air") and rng.random() < p:
                t.set(x, y, z, rng.choice(choices))

def path_cells(t, cells):
    for (x, z) in cells: t.set(x, G, z, "dirt_path")

def lamp_post(t, x, z, y=G+1, h=3):
    for k in range(h): t.set(x, y+k, z, "dark_oak_fence")
    t.set(x, y+h, z, "gnomehollow:toadstool_lamp")

def gable_roof(t, u0, u1, v0, v1, yb, ridge, roof, fill, ov=1):
    """Zadeldak. ridge='x' (nok langs x, hellingen langs z) of 'z'. fill = blok voor de geveldriehoeken."""
    P = (lambda u, v: (u, v)) if ridge == "x" else (lambda u, v: (v, u))
    vn, vs = v0-ov, v1+ov; span = vs-vn+1
    low_f, high_f = ("south", "north") if ridge == "x" else ("east", "west")
    R = ROOFS[roof]
    for r in range(span//2):
        for u in range(u0-ov, u1+ov+1):
            for (v, f) in ((vn+r, low_f), (vs-r, high_f)):
                x, z = P(u, v); t.stairs(x, yb+r, z, R["stairs"], f)
    if span % 2 == 1:
        r = span//2; v = vn+r
        for u in range(u0-ov, u1+ov+1):
            x, z = P(u, v); t.slab(x, yb+r, z, R["slab"])
    rows = span//2 + (1 if span % 2 else 0)
    for r in range(rows):
        for u in (u0, u1):
            for v in range(vn+r+1, vs-r):
                x, z = P(u, v); t.set(x, yb+r, z, fill)
    return yb + span//2        # hoogste y van het dak

def chimney(t, x, z, y0, y1):
    for y in range(y0, y1+1):
        for (dx, dz) in ((0,0),(1,0),(0,1),(1,1)): t.set(x+dx, y, z+dz, "stone_bricks")
    t.set(x, y1+1, z, "cobblestone_wall"); t.set(x+1, y1+1, z+1, "cobblestone_wall")
    t.set(x, y1+1, z+1, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)
    t.set(x+1, y1+1, z, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)

# ------------------------------------------------------------------ preview (isometrisch)
COL = {
 "grass_block": (96,150,60), "podzol": (110,80,45), "dirt": (120,86,56), "dirt_path": (150,125,75), "coarse_dirt": (115,85,60), "moss_block": (80,130,50),
 "gnomehollow:fieldstone": (125,120,110), "gnomehollow:plaster": (236,226,206), "gnomehollow:timber_plaster": (200,185,150),
 "gnomehollow:thatch": (214,178,84), "gnomehollow:thatch_stairs": (214,178,84), "gnomehollow:thatch_slab": (214,178,84),
 "gnomehollow:gnome_shingles": (158,62,48), "gnomehollow:gnome_shingle_stairs": (158,62,48), "gnomehollow:gnome_shingle_slab": (158,62,48),
 "gnomehollow:toadstool_cap": (196,48,42), "gnomehollow:toadstool_cap_stairs": (196,48,42), "gnomehollow:toadstool_cap_slab": (196,48,42),
 "gnomehollow:gnome_stem": (238,228,204), "gnomehollow:toadstool_lamp": (255,170,70),
 "dark_oak_log": (60,45,28), "stripped_dark_oak_log": (80,60,40), "dark_oak_planks": (66,43,20), "dark_oak_fence": (66,43,20),
 "spruce_planks": (114,84,48), "spruce_stairs": (114,84,48), "spruce_slab": (114,84,48), "spruce_log": (85,60,32), "stripped_spruce_log": (115,90,55), "spruce_fence": (114,84,48),
 "glass_pane": (170,210,225), "water": (50,90,190), "stone_bricks": (125,125,125), "cobblestone_wall": (110,110,110), "cobblestone": (110,110,110),
 "oak_planks": (160,130,80), "oak_log": (110,85,50), "hay_block": (200,170,40), "hay_bale": (200,170,40),
}
def preview(names, path, scale=5):
    from PIL import Image, ImageDraw
    imgs = []
    for nm in names:
        t = REGISTRY[nm]; sx, sy, sz = t.size
        tw, th = scale*2, scale
        Wd = (sx+sz)*tw + 20; Ht = (sx+sz)*th//2 + sy*th*2 + 20
        im = Image.new("RGB", (Wd, Ht), (30, 34, 40)); dr = ImageDraw.Draw(im)
        order = sorted(t.blocks.items(), key=lambda kv: (kv[0][1], kv[0][0]+kv[0][2]))
        # tekenvolgorde: hoogte, dan achter->voor
        order = sorted(t.blocks.items(), key=lambda kv: (kv[0][0]+kv[0][2], kv[0][1]))
        for (x, y, z), (name, props, nbt) in order:
            n = name.replace("minecraft:", "")
            if n in ("air", "jigsaw", "structure_void"): continue
            c = COL.get(n) or COL.get(name)
            if c is None:
                hsh = abs(hash(n)) % 150 + 60; c = (hsh, (hsh*7) % 150 + 60, (hsh*13) % 150 + 60)
                if "leaves" in n: c = (50,120,50)
                if "stairs" in n or "slab" in n: c = (150, 110, 80)
                if "door" in n: c = (90, 60, 30)
                if "bed" in n: c = (180, 50, 50)
            sxp = (x - z)*tw + (sz*tw) + 10; syp = Ht - 10 - ((x + z)*th//2 + y*th*2)
            top = [(sxp, syp-th*2), (sxp+tw, syp-th*2+th//2+ (th//2)), (sxp, syp-th*2+th), (sxp-tw, syp-th*2+th//2+(th//2))]
            top = [(sxp, syp-th*2-th//2), (sxp+tw, syp-th*2), (sxp, syp-th*2+th//2), (sxp-tw, syp-th*2)]
            left = [(sxp-tw, syp-th*2), (sxp, syp-th*2+th//2), (sxp, syp+th//2), (sxp-tw, syp)]
            right = [(sxp+tw, syp-th*2), (sxp, syp-th*2+th//2), (sxp, syp+th//2), (sxp+tw, syp)]
            dr.polygon(left, fill=tuple(int(v*0.72) for v in c)); dr.polygon(right, fill=tuple(int(v*0.55) for v in c)); dr.polygon(top, fill=c)
        dr.text((6, 4), nm, fill=(255, 255, 255))
        imgs.append(im)
    wmax = max(i.width for i in imgs); cols = 2
    rows = (len(imgs)+cols-1)//cols
    rh = [max(i.height for i in imgs[r*cols:(r+1)*cols]) for r in range(rows)]
    sheet = Image.new("RGB", (wmax*cols, sum(rh)), (30, 34, 40)); y0 = 0
    for r in range(rows):
        for c_ in range(cols):
            k = r*cols + c_
            if k < len(imgs): sheet.paste(imgs[k], (c_*wmax, y0))
        y0 += rh[r]
    sheet.save(path)

def preview3d(names, path, elev=28, azim=-62, ymin=None):
    import numpy as np
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    n = len(names); cols = 2; rows = (n+cols-1)//cols
    fig = plt.figure(figsize=(7.2*cols, 6.4*rows))
    for i, nm in enumerate(names):
        t = REGISTRY[nm]; sx, sy, sz = t.size
        y0 = (G-1) if ymin is None else ymin
        filled = np.zeros((sx, sz, sy-y0), dtype=bool); colors = np.empty(filled.shape + (4,), dtype=float)
        for (x, y, z), (name, props, nbt) in t.blocks.items():
            nn = name.replace("minecraft:", "")
            if nn in ("air", "jigsaw") or y < y0: continue
            c = COL.get(nn) or COL.get(name)
            if c is None:
                h = (sum(ord(ch) for ch in nn)*37) % 140 + 70; c = (h, (h*5) % 140 + 70, (h*11) % 140 + 70)
                if "leaves" in nn: c = (50,120,50)
                if "stairs" in nn or "slab" in nn: c = (150,110,80)
                if "door" in nn: c = (90,60,30)
                if "bed" in nn: c = (180,50,50)
                if "pane" in nn or nn == "glass": c = (170,210,225)
                if "banner" in nn: c = (190,40,40)
                if "fence" in nn: c = (80,55,30)
            filled[x, z, y-y0] = True; colors[x, z, y-y0] = (c[0]/255, c[1]/255, c[2]/255, 1.0)
        ax = fig.add_subplot(rows, cols, i+1, projection="3d")
        ax.voxels(filled, facecolors=colors, edgecolor=(0,0,0,0.25), linewidth=0.2)
        ax.set_box_aspect((sx, sz, (sy-y0)*0.9)); ax.view_init(elev=elev, azim=azim); ax.set_axis_off(); ax.set_title(nm, fontsize=10)
    plt.tight_layout(); plt.savefig(path, dpi=80); plt.close(fig)
