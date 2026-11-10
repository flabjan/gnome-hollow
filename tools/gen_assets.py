"""Genereert alle assets: gnome-modellen/texturen/animaties, bloktexturen, blockstates, modellen, taal, loot, recepten."""
import json, os, random, math, zlib
from PIL import Image, ImageDraw

ROOT = "/home/claude/gnome-hollow/src/main/resources"
A = f"{ROOT}/assets/gnomehollow"
D = f"{ROOT}/data/gnomehollow"
MC = f"{ROOT}/data/minecraft"

def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def shade(c, k):
    return tuple(max(0, min(255, int(x*k))) for x in c)

def seed(name): return zlib.crc32(name.encode()) & 0xffffffff

# ============================================================== GNOMES
SKIN = (238,190,150); SKIN_D = (205,150,115); NOSE = (225,140,120)
IRON = (168,172,182); IRON_D = (120,124,134); WOOD = (130,90,45); LEATHER = (110,75,40)

# kleuren per beroep: hat, band, tunic (romp), sleeve (mouwen), pants, boots, beard, belt
PROF = {
 "healer":    dict(tunic=(240,240,235), sleeve=(240,240,235), pants=(225,228,220), boots=(70,120,70),  beard=(245,245,245), belt=(60,150,80),  egg=(0x3FA34D,0xF2F2F2)),
 "warrior":   dict(tunic=(120,125,138), sleeve=(150,45,40),  pants=(70,70,80),    boots=(50,50,58),   beard=(165,85,45),    belt=(110,40,35),  egg=(0x8A8D93,0xB3261E)),
 "farmer":    dict(tunic=(70,115,175),  sleeve=(238,214,120),pants=(70,115,175),  boots=(95,65,40),   beard=(190,190,190), belt=(110,75,40),  egg=(0xE0B84A,0x6B8E23)),
 "fisherman": dict(tunic=(245,205,60),  sleeve=(245,205,60), pants=(60,100,70),   boots=(40,80,55),   beard=(230,230,235), belt=(120,100,40), egg=(0x2F6FBF,0xE8E8E8)),
 "builder":   dict(tunic=(235,125,35),  sleeve=(150,105,65), pants=(85,90,105),   boots=(90,60,38),   beard=(95,62,38),    belt=(80,55,30),   egg=(0xE07B20,0x8B5A2B)),
 "nitwit":    dict(tunic=(210,120,205), sleeve=(95,190,110), pants=(235,200,70),  boots=(200,70,70),  beard=(205,150,90),  belt=(240,210,90), egg=(0x7B3FA0,0xF0D060)),
}

# (naam, bot, origin, size, kleur, accent) -- accent: None of (kleur, "h"/"v", periode)
def gear(p):
    hat, body, rarm, larm = [], [], [], []
    if p == "healer":
        hat  = [("h_brim",[-3.5,12,-3.5],[7,1,7],(70,165,90),None), ("h_mid",[-2.5,13,-2.5],[5,2,5],(245,245,245),None), ("h_tip",[-1.5,15,-1.5],[3,1,3],(70,165,90),None)]
        body = [("robe",[-3,1.5,-2],[6,3,4],(240,240,235),((60,150,80),"h",3)), ("sash",[-2.7,4.5,-1.7],[5,1,3],(60,150,80),None),
                ("cross",[-1,5.2,-2.3],[2,2,1],(60,170,85),None)]
        rarm = [("potion",[-4.5,3,-3.5],[2,3,2],(230,70,110),None), ("cork",[-4,6,-3],[1,1,1],(160,110,60),None)]
    elif p == "warrior":
        hat  = [("helm",[-3.5,11,-3.5],[7,3,7],IRON,((120,124,134),"h",2)), ("nasal",[-0.5,9,-3.6],[1,3,1],IRON_D,None), ("plume",[-0.5,14,-2],[1,2,4],(190,40,35),None)]
        body = [("plate",[-2.8,4.5,-1.8],[5,3,3],IRON,((120,124,134),"h",2)), ("tabard",[-1,2.5,-2.4],[2,3,1],(190,40,35),None)]
        rarm = [("pauld_r",[-5,7,-1.5],[3,2,3],IRON,None), ("blade",[-4,3.5,-9],[1,1,7],(205,210,220),None), ("guard",[-5,3.5,-2],[3,1,1],(120,90,50),None)]
        larm = [("pauld_l",[2,7,-1.5],[3,2,3],IRON,None), ("shield",[4.5,2.5,-2],[1,5,4],(150,100,55),((190,40,35),"v",2))]
    elif p == "farmer":
        hat  = [("h_brim",[-5,12,-5],[10,1,10],(228,194,95),((200,165,70),"h",2)), ("h_crown",[-2.5,13,-2.5],[5,2,5],(228,194,95),None)]
        body = [("strap_l",[-2,7,-1.7],[1,1,3],LEATHER,None), ("strap_r",[1,7,-1.7],[1,1,3],LEATHER,None),
                ("basket",[-2,4,1.5],[4,3,3],(196,150,80),((160,115,55),"h",1))]
        rarm = [("handle",[-4,3.5,-9],[1,1,7],WOOD,None), ("hoehead",[-4,0.5,-10],[1,3,1],(170,172,178),None)]
    elif p == "fisherman":
        hat  = [("h_brim",[-4,12,-4],[8,1,8],(250,210,60),None), ("h_crown",[-3,13,-3],[6,2,6],(250,210,60),None), ("h_flap",[-3,10,3],[6,2,1],(250,210,60),None)]
        body = [("button",[-1,4,-1.9],[2,2,1],(120,100,40),None), ("bucket",[-1.5,3,1.5],[3,3,3],(120,125,135),((90,95,105),"h",2))]
        rarm = [("rod",[-4,3.5,-9],[1,1,7],(120,85,45),None), ("line",[-4,0.5,-10],[1,3,1],(235,235,235),None)]
    elif p == "builder":
        hat  = [("h_dome",[-3.5,12,-3.5],[7,2,7],(250,205,40),None), ("h_ridge",[-0.5,14,-3],[1,1,6],(250,205,40),None), ("h_brim",[-3,12,-4.5],[6,1,1],(250,205,40),None)]
        body = [("vest",[-2.8,3,-1.8],[5,4,3],(235,125,35),((250,240,150),"v",2)), ("belt2",[-2.7,3,-1.7],[5,1,3],LEATHER,None),
                ("pouch",[1.2,2.5,-2.3],[2,2,1],(110,112,120),None), ("pack",[-2,4,1.5],[4,4,3],(120,85,50),((90,60,35),"h",2)), ("hammer",[-0.5,8,2],[1,3,1],WOOD,None)]
        rarm = [("hhandle",[-4,3.5,-6],[1,1,5],WOOD,None), ("hhead",[-5,2.5,-8],[3,2,2],(110,112,120),None)]
    elif p == "nitwit":
        hat  = [("h_base",[-3.5,12,-3.5],[7,1,7],(240,210,90),None), ("h_mid",[-2.5,13,-2.5],[5,2,5],(135,70,175),((240,210,90),"h",2)),
                ("h_tip",[0,15,-1.5],[3,1,3],(135,70,175),None), ("bell",[2.5,14,-0.5],[1,1,1],(250,215,80),None)]
        body = [("scarf",[-3,7,-2],[6,1,4],(235,70,150),((250,230,90),"v",1)), ("bellneck",[-0.5,5.8,-2.2],[1,1,1],(250,215,80),None)]
    return hat, body, rarm, larm

# vaste basis-UV's (64x64 gebied) + vrij gebied voor de rest
BASE_UV = {"head": (0,0), "nose": (26,0), "body": (0,12), "beard": (0,22), "arm_r": (32,12), "arm_l": (32,20), "leg_r": (32,28), "leg_l": (32,34)}
TEX = 128

class Packer:
    def __init__(self):
        self.regions = [[0, 40, 64, 88], [64, 0, 64, 128]]   # x, y, w, h
        self.shelves = [[r[0], r[1], 0, r[1]] for r in self.regions]   # cursor x, y, rowHeight, rowY
        self.cur = [[r[0], r[1], 0] for r in self.regions]
    def alloc(self, size):
        w, h, d = [int(math.ceil(s)) for s in size]
        bw, bh = 2*(w+d), h+d
        for i, r in enumerate(self.regions):
            cx, cy, rh = self.cur[i]
            if cx + bw > r[0] + r[2]:
                cx, cy, rh = r[0], cy + rh, 0
            if cy + bh <= r[1] + r[3]:
                self.cur[i] = [cx + bw, cy, max(rh, bh)]
                return (cx, cy)
        raise RuntimeError("texture vol")

def box_regions(u, v, w, h, d):
    return {"top": (u+d, v, w, d), "bottom": (u+d+w, v, w, d), "right": (u, v+d, d, h),
            "front": (u+d, v+d, w, h), "left": (u+d+w, v+d, d, h), "back": (u+2*d+w, v+d, w, h)}

def paint_box(img, uv, size, color, rng, faces=None, accent=None):
    u, v = uv; w, h, d = [int(math.ceil(s)) for s in size]
    px = img.load()
    for name, (x, y, ww, hh) in box_regions(u, v, w, h, d).items():
        base = color
        if name == "top": base = shade(color, 1.1)
        if name == "bottom": base = shade(color, 0.7)
        if name in ("left", "right"): base = shade(color, 0.88)
        if name == "back": base = shade(color, 0.92)
        if faces and name in faces: base = faces[name]
        for i in range(ww):
            for j in range(hh):
                c = base
                if accent and name not in ("top", "bottom"):
                    col, axis, per = accent
                    if (axis == "h" and (j % (per*2)) >= per) or (axis == "v" and (i % (per*2)) >= per):
                        c = col
                px[x+i, y+j] = shade(c, rng.uniform(0.94, 1.06)) + (255,)
    return box_regions(u, v, w, h, d)

def make_gnome(p):
    pal = PROF[p]; name = f"gnome_{p}"
    rng = random.Random(seed(name)); img = Image.new("RGBA", (TEX, TEX), (0,0,0,0)); px = img.load()
    pk = Packer()
    r = paint_box(img, BASE_UV["head"], (6,4,6), SKIN, rng)
    fx, fy, fw, fh = r["front"]
    px[fx+1, fy+1] = (40,30,30,255); px[fx+4, fy+1] = (40,30,30,255)
    px[fx+0, fy+2] = shade(SKIN, .9)+(255,); px[fx+5, fy+2] = shade(SKIN, .9)+(255,)
    paint_box(img, BASE_UV["nose"], (1,1,1), NOSE, rng)
    paint_box(img, BASE_UV["beard"], (5,3,1), pal["beard"], rng)
    r = paint_box(img, BASE_UV["body"], (5,5,3), pal["tunic"], rng)
    bx, by, bw, bh = r["front"]
    if p == "nitwit":
        px[bx+1, by+1] = (90,160,230,255); px[bx+3, by+2] = (250,230,90,255); px[bx+0, by+0] = (120,200,120,255); px[bx+4, by+3] = (240,120,120,255)
    if p == "farmer":
        for j in range(bh): px[bx+0, by+j] = pal["sleeve"]+(255,); px[bx+4, by+j] = pal["sleeve"]+(255,)
    for i in range(bw): px[bx+i, by+4] = shade(pal["belt"], rng.uniform(.95,1.05))+(255,)
    if p != "healer":
        px[bx+2, by+4] = (235,205,70,255)
    sleeves = {"arm_r": pal["sleeve"], "arm_l": pal["sleeve"]}
    if p == "nitwit": sleeves = {"arm_r": (95,190,110), "arm_l": (240,150,60)}
    for key, uv in (("arm_r", BASE_UV["arm_r"]), ("arm_l", BASE_UV["arm_l"])):
        r = paint_box(img, uv, (2,4,2), sleeves[key], rng)
        for k in ("front","back","left","right"):
            x, y, ww, hh = r[k]
            for i in range(ww): px[x+i, y+hh-1] = SKIN+(255,)
        x, y, ww, hh = r["bottom"]
        for i in range(ww):
            for j in range(hh): px[x+i, y+j] = SKIN_D+(255,)
    pants = pal["pants"]
    for uv in (BASE_UV["leg_r"], BASE_UV["leg_l"]):
        r = paint_box(img, uv, (2,3,2), pants, rng)
        if p == "nitwit" and uv == BASE_UV["leg_l"]: r = paint_box(img, uv, (2,3,2), (90,150,230), rng)
        for k in ("front","back","left","right"):
            x, y, ww, hh = r[k]
            for i in range(ww):
                px[x+i, y+hh-1] = pal["boots"]+(255,)
                if p in ("fisherman","warrior","healer"): px[x+i, y+hh-2] = pal["boots"]+(255,)
    hat, body, rarm, larm = gear(p)
    layout = {"hat": [], "body": [], "arm_right": [], "arm_left": []}
    for key, lst in (("hat", hat), ("body", body), ("arm_right", rarm), ("arm_left", larm)):
        for (cn, org, size, col, acc) in lst:
            uv = pk.alloc(size)
            paint_box(img, uv, size, col, rng, accent=acc)
            layout[key].append({"origin": org, "size": size, "uv": list(uv)})
    return img, layout

def cube(origin, size, uv): return {"origin": origin, "size": size, "uv": uv}

def make_geo(name, layout):
    bones = [
      {"name":"root","pivot":[0,0,0]},
      {"name":"leg_left","parent":"root","pivot":[1.5,3,0],"cubes":[cube([0.5,0,-1],[2,3,2],list(BASE_UV["leg_l"]))]},
      {"name":"leg_right","parent":"root","pivot":[-1.5,3,0],"cubes":[cube([-2.5,0,-1],[2,3,2],list(BASE_UV["leg_r"]))]},
      {"name":"body","parent":"root","pivot":[0,3,0],"cubes":[cube([-2.5,3,-1.5],[5,5,3],list(BASE_UV["body"]))] + layout["body"]},
      {"name":"arm_left","parent":"root","pivot":[3.5,7.5,0],"cubes":[cube([2.5,4,-1],[2,4,2],list(BASE_UV["arm_l"]))] + layout["arm_left"]},
      {"name":"arm_right","parent":"root","pivot":[-3.5,7.5,0],"cubes":[cube([-4.5,4,-1],[2,4,2],list(BASE_UV["arm_r"]))] + layout["arm_right"]},
      {"name":"head","parent":"root","pivot":[0,8,0],"cubes":[
          cube([-3,8,-3],[6,4,6],list(BASE_UV["head"])), cube([-0.5,8.8,-4],[1,1,1],list(BASE_UV["nose"])), cube([-2.5,7,-3.5],[5,3,1],list(BASE_UV["beard"]))]},
      {"name":"hat","parent":"head","pivot":[0,12,0],"cubes": layout["hat"]},
    ]
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{name}", "texture_width": TEX, "texture_height": TEX,
                        "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0,0.5,0]},
        "bones": bones}]}

def kf(d): return {f"{k:.2f}": v for k, v in d}
def make_anims():
    anims = {}
    anims["animation.gnome.idle"] = {"loop": True, "animation_length": 2.0, "bones": {
        "head": {"rotation": kf([(0,[0,0,0]),(1.0,[3,2,0]),(2.0,[0,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(1.0,[0,0.15,0]),(2.0,[0,0,0])])},
        "arm_left": {"rotation": kf([(0,[0,0,2]),(1.0,[0,0,-2]),(2.0,[0,0,2])])},
        "arm_right": {"rotation": kf([(0,[0,0,-2]),(1.0,[0,0,2]),(2.0,[0,0,-2])])}}}
    anims["animation.gnome.walk"] = {"loop": True, "animation_length": 0.8, "bones": {
        "leg_left": {"rotation": kf([(0,[32,0,0]),(0.4,[-32,0,0]),(0.8,[32,0,0])])},
        "leg_right": {"rotation": kf([(0,[-32,0,0]),(0.4,[32,0,0]),(0.8,[-32,0,0])])},
        "arm_left": {"rotation": kf([(0,[-28,0,0]),(0.4,[28,0,0]),(0.8,[-28,0,0])])},
        "arm_right": {"rotation": kf([(0,[28,0,0]),(0.4,[-28,0,0]),(0.8,[28,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(0.2,[0,0.4,0]),(0.4,[0,0,0]),(0.6,[0,0.4,0]),(0.8,[0,0,0])])},
        "head": {"rotation": kf([(0,[0,3,0]),(0.4,[0,-3,0]),(0.8,[0,3,0])])}}}
    anims["animation.gnome.attack"] = {"loop": False, "animation_length": 0.4, "bones": {
        "arm_right": {"rotation": kf([(0,[0,0,0]),(0.12,[-120,0,0]),(0.25,[-20,0,0]),(0.4,[0,0,0])])},
        "body": {"rotation": kf([(0,[0,0,0]),(0.12,[-10,0,0]),(0.25,[8,0,0]),(0.4,[0,0,0])])}}}
    anims["animation.gnome.work"] = {"loop": False, "animation_length": 0.9, "bones": {
        "arm_right": {"rotation": kf([(0,[-40,0,0]),(0.35,[-115,0,0]),(0.55,[-30,0,0]),(0.9,[-40,0,0])])},
        "arm_left": {"rotation": kf([(0,[-20,0,0]),(0.45,[-45,0,0]),(0.9,[-20,0,0])])},
        "body": {"rotation": kf([(0,[0,0,0]),(0.55,[10,0,0]),(0.9,[0,0,0])])},
        "head": {"rotation": kf([(0,[8,0,0]),(0.9,[8,0,0])])}}}
    anims["animation.gnome.fish"] = {"loop": False, "animation_length": 3.0, "bones": {
        "arm_right": {"rotation": kf([(0,[-65,0,0]),(1.0,[-62,0,3]),(2.0,[-70,0,-3]),(3.0,[-65,0,0])])},
        "arm_left": {"rotation": kf([(0,[-55,0,0]),(3.0,[-55,0,0])])},
        "body": {"rotation": kf([(0,[4,0,0]),(3.0,[4,0,0])])},
        "head": {"rotation": kf([(0,[10,0,0]),(1.5,[12,0,0]),(3.0,[10,0,0])])}}}
    anims["animation.gnome.play"] = {"loop": False, "animation_length": 0.6, "bones": {
        "arm_right": {"rotation": kf([(0,[-110,0,0]),(0.3,[-125,0,0]),(0.6,[-110,0,0])])},
        "arm_left": {"rotation": kf([(0,[-125,0,0]),(0.3,[-110,0,0]),(0.6,[-125,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(0.3,[0,0.6,0]),(0.6,[0,0,0])])},
        "head": {"rotation": kf([(0,[0,0,8]),(0.3,[0,0,-8]),(0.6,[0,0,8])])}}}
    anims["animation.gnome.none"] = {"loop": True, "animation_length": 1.0, "bones": {"root": {"position": kf([(0,[0,0,0]),(1.0,[0,0,0])])}}}
    return {"format_version": "1.8.0", "animations": anims}

for p in PROF:
    name = f"gnome_{p}"
    img, layout = make_gnome(p)
    os.makedirs(f"{A}/textures/entity", exist_ok=True)
    img.save(f"{A}/textures/entity/{name}.png")
    wjson(f"{A}/geckolib/models/entity/{name}.geo.json", make_geo(name, layout))
    wjson(f"{A}/geckolib/animations/entity/{name}.animation.json", make_anims())
    wjson(f"{A}/items/{name}_spawn_egg.json", {"model": {"type": "minecraft:model", "model": "minecraft:item/template_spawn_egg",
          "tints": [{"type": "minecraft:constant", "value": v} for v in PROF[p]["egg"]]}})

# ============================================================== BLOCK TEXTURES
os.makedirs(f"{A}/textures/block", exist_ok=True)
def tex_img(): return Image.new("RGBA", (16,16), (0,0,0,255))

def t_lamp():
    rng = random.Random(7); img = tex_img(); px = img.load()
    for x in range(16):
        for y in range(16): px[x,y] = shade((205,55,45), rng.uniform(.93,1.07))+(255,)
    for (x,y,r) in [(3,3,1.6),(10,4,2.0),(6,9,1.5),(12,11,1.8),(2,12,1.4),(8,1,1.0)]:
        for i in range(16):
            for j in range(16):
                if (i-x)**2+(j-y)**2 <= r*r: px[i,j] = (250,240,215,255)
    for k in range(16):
        for (x,y) in ((k,0),(k,15),(0,k),(15,k)): px[x,y] = (255,170,70,255)
    return img
def t_shingles():
    rng = random.Random(11); img = tex_img(); px = img.load()
    for y in range(16):
        off = 4 if (y//4) % 2 else 0
        for x in range(16):
            lx = (x+off) % 8; base = (158,62,48); c = shade(base, rng.uniform(.92,1.07))
            if y % 4 == 3: c = shade(base, .55)
            elif lx == 7: c = shade(base, .7)
            elif y % 4 == 0: c = shade(base, 1.12)
            px[x,y] = c+(255,)
    return img
def t_thatch():
    rng = random.Random(21); img = tex_img(); px = img.load()
    for y in range(16):
        row = 0.88 + 0.12*math.sin(y*1.9)
        for x in range(16):
            streak = 0.9 + 0.2*rng.random()
            c = shade((214,178,84), row*streak)
            if y % 4 == 3: c = shade(c, .72)
            if rng.random() < .06: c = shade((236,206,120), 1.0)
            px[x,y] = c+(255,)
    return img
def t_cap():
    rng = random.Random(31); img = tex_img(); px = img.load()
    for x in range(16):
        for y in range(16): px[x,y] = shade((196,48,42), rng.uniform(.92,1.08))+(255,)
    for (x,y,r) in [(3,4,1.9),(11,3,1.5),(7,10,2.2),(13,12,1.6),(2,13,1.3),(9,0,1.2)]:
        for i in range(16):
            for j in range(16):
                if (i-x)**2+(j-y)**2 <= r*r: px[i,j] = (248,236,214,255)
    return img
def t_plaster():
    rng = random.Random(41); img = tex_img(); px = img.load()
    for x in range(16):
        for y in range(16): px[x,y] = shade((236,226,206), rng.uniform(.95,1.04))+(255,)
    for _ in range(5):
        x, y = rng.randrange(16), rng.randrange(16)
        for k in range(rng.randrange(2,5)):
            if 0 <= x+k < 16: px[x+k,y] = shade((200,190,170), 1)+(255,)
    return img
def t_timber():
    img = t_plaster(); px = img.load(); beam = (84,58,38)
    for k in range(16):
        for (x,y) in ((k,0),(k,1),(k,14),(k,15),(0,k),(1,k),(14,k),(15,k)): px[x,y] = shade(beam, 1.0 - 0.06*((x+y)%3))+(255,)
        px[k,k] = beam+(255,); 
        if k+1 < 16: px[k+1,k] = beam+(255,)
        px[15-k,k] = beam+(255,)
        if 14-k >= 0: px[14-k,k] = beam+(255,)
    return img
def t_stem():
    rng = random.Random(51); img = tex_img(); px = img.load()
    for x in range(16):
        col = 0.93 + 0.1*math.sin(x*1.3)
        for y in range(16): px[x,y] = shade((238,228,204), col*rng.uniform(.96,1.04))+(255,)
    return img
def t_fieldstone():
    rng = random.Random(61); img = tex_img(); px = img.load()
    pts = [(rng.uniform(0,16), rng.uniform(0,16)) for _ in range(11)]
    cols = [shade((rng.choice([128,140,150,120]), rng.choice([122,128,134,112]), rng.choice([112,118,124,104])), 1.0) for _ in pts]
    for x in range(16):
        for y in range(16):
            ds = sorted(((min(abs(x-px_), 16-abs(x-px_))**2 + min(abs(y-py), 16-abs(y-py))**2, i) for i,(px_,py) in enumerate(pts)))
            d1, i1 = ds[0]; d2, _ = ds[1]
            c = cols[i1]
            if d2 - d1 < 3.0: c = (78,74,68)
            px[x,y] = shade(c, rng.uniform(.93,1.06))+(255,)
    return img

TEXTURES = {"toadstool_lamp": t_lamp, "gnome_shingles": t_shingles, "thatch": t_thatch, "toadstool_cap": t_cap,
            "plaster": t_plaster, "timber_plaster": t_timber, "gnome_stem": t_stem, "fieldstone": t_fieldstone}
for n, fn in TEXTURES.items(): fn().save(f"{A}/textures/block/{n}.png")

ic = Image.new("RGBA", (128,128), (34,52,38,255)); d = ImageDraw.Draw(ic)
d.polygon([(64,6),(30,70),(98,70)], fill=(200,50,45,255)); d.rectangle([22,68,106,78], fill=(240,230,210,255))
d.rectangle([34,78,94,106], fill=SKIN+(255,)); d.rectangle([40,88,52,94], fill=(40,30,30,255)); d.rectangle([76,88,88,94], fill=(40,30,30,255))
d.rectangle([60,94,68,102], fill=NOSE+(255,)); d.polygon([(34,100),(94,100),(64,126)], fill=(240,240,240,255))
ic.save(f"{A}/icon.png")

# ============================================================== BLOCK JSON
FAMILIES = {   # basis: (heeft trap/plaat, mineable tool)
 "toadstool_lamp": (False, "axe"), "gnome_shingles": (True, "pickaxe"), "thatch": (True, "hoe"), "toadstool_cap": (True, "axe"),
 "plaster": (True, "pickaxe"), "timber_plaster": (False, "pickaxe"), "gnome_stem": (False, "axe"), "fieldstone": (True, "pickaxe")}
EN = {"toadstool_lamp":"Toadstool Lamp","gnome_shingles":"Gnome Shingles","thatch":"Thatch","toadstool_cap":"Toadstool Cap",
      "plaster":"Plaster","timber_plaster":"Timber Plaster","gnome_stem":"Gnome Mushroom Stem","fieldstone":"Fieldstone"}
NL = {"toadstool_lamp":"Paddenstoellamp","gnome_shingles":"Kaboutershingles","thatch":"Rieten Dak","toadstool_cap":"Paddenstoelhoed",
      "plaster":"Pleisterwerk","timber_plaster":"Vakwerk","gnome_stem":"Kabouter-paddenstoelsteel","fieldstone":"Veldkeien"}

def stairs_blockstate(model):
    variants = {}
    bottom = {"east": (0,0,270,0,270), "south": (90,90,0,90,0), "west": (180,180,90,180,90), "north": (270,270,180,270,180)}
    top    = {"east": (0,90,0,90,0), "south": (90,180,90,180,90), "west": (180,270,180,270,180), "north": (270,0,270,0,270)}
    shapes = ["straight","outer_right","outer_left","inner_right","inner_left"]
    models = [model, model+"_outer", model+"_outer", model+"_inner", model+"_inner"]
    def sv(m, y=0, x=0):
        o = {"model": m}
        if x: o["x"] = x
        if y: o["y"] = y
        if x or y: o["uvlock"] = True
        return o
    for f, ys in bottom.items():
        for sh, m, y in zip(shapes, models, ys): variants[f"facing={f},half=bottom,shape={sh}"] = sv(m, y)
    for f, ys in top.items():
        for sh, m, y in zip(shapes, models, ys): variants[f"facing={f},half=top,shape={sh}"] = sv(m, y, 180)
    return {"variants": variants}

def self_drop(n, extra=None):
    pool = {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"gnomehollow:{n}"}],
            "conditions": [{"condition": "minecraft:survives_explosion"}]}
    if extra: pool["entries"][0]["functions"] = extra
    return {"type": "minecraft:block", "pools": [pool], "random_sequence": f"gnomehollow:blocks/{n}"}

tags = {"pickaxe": [], "axe": [], "hoe": []}
en = {}; nl = {}
def item_def(model): return {"model": {"type": "minecraft:model", "model": model}}
for base, (fam, tool) in FAMILIES.items():
    names = [base] + ([f"{base}_stairs", f"{base}_slab"] if fam else [])
    if base == "gnome_shingles": names = ["gnome_shingles", "gnome_shingle_stairs", "gnome_shingle_slab"]
    sname = names[1] if fam else None; lname = names[2] if fam else None
    tex = f"gnomehollow:block/{base}"
    wjson(f"{A}/blockstates/{base}.json", {"variants": {"": {"model": f"gnomehollow:block/{base}"}}})
    wjson(f"{A}/models/block/{base}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": tex}})
    wjson(f"{A}/items/{base}.json", item_def(f"gnomehollow:block/{base}"))
    wjson(f"{D}/loot_table/blocks/{base}.json", self_drop(base))
    en[f"block.gnomehollow.{base}"] = EN[base]; nl[f"block.gnomehollow.{base}"] = NL[base]
    tags[tool].append(f"gnomehollow:{base}")
    if fam:
        t3 = {"bottom": tex, "top": tex, "side": tex}
        S = f"gnomehollow:block/{sname}"
        wjson(f"{A}/models/block/{sname}.json", {"parent": "minecraft:block/stairs", "textures": t3})
        wjson(f"{A}/models/block/{sname}_inner.json", {"parent": "minecraft:block/inner_stairs", "textures": t3})
        wjson(f"{A}/models/block/{sname}_outer.json", {"parent": "minecraft:block/outer_stairs", "textures": t3})
        wjson(f"{A}/blockstates/{sname}.json", stairs_blockstate(S))
        wjson(f"{A}/models/block/{lname}.json", {"parent": "minecraft:block/slab", "textures": t3})
        wjson(f"{A}/models/block/{lname}_top.json", {"parent": "minecraft:block/slab_top", "textures": t3})
        wjson(f"{A}/blockstates/{lname}.json", {"variants": {"type=bottom": {"model": f"gnomehollow:block/{lname}"},
              "type=top": {"model": f"gnomehollow:block/{lname}_top"}, "type=double": {"model": f"gnomehollow:block/{base}"}}})
        for n in (sname, lname): wjson(f"{A}/items/{n}.json", item_def(f"gnomehollow:block/{n}"))
        wjson(f"{D}/loot_table/blocks/{sname}.json", self_drop(sname))
        wjson(f"{D}/loot_table/blocks/{lname}.json", self_drop(lname, [
            {"function": "minecraft:set_count", "count": 2.0, "add": False,
             "conditions": [{"condition": "minecraft:block_state_property", "block": f"gnomehollow:{lname}", "properties": {"type": "double"}}]},
            {"function": "minecraft:explosion_decay"}]))
        en[f"block.gnomehollow.{sname}"] = EN[base] + " Stairs"; en[f"block.gnomehollow.{lname}"] = EN[base] + " Slab"
        nl[f"block.gnomehollow.{sname}"] = NL[base] + "-trap"; nl[f"block.gnomehollow.{lname}"] = NL[base] + "-plaat"
        tags[tool] += [f"gnomehollow:{sname}", f"gnomehollow:{lname}"]
        wjson(f"{D}/recipe/{sname}.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":["S  ","SS ","SSS"],"key":{"S":f"gnomehollow:{base}"},"result":{"id":f"gnomehollow:{sname}","count":4}})
        wjson(f"{D}/recipe/{lname}.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":["SSS"],"key":{"S":f"gnomehollow:{base}"},"result":{"id":f"gnomehollow:{lname}","count":6}})

for tool, vals in tags.items():
    wjson(f"{MC}/tags/block/mineable/{tool}.json", {"replace": False, "values": vals})

def shaped(name, pattern, key, result, count): wjson(f"{D}/recipe/{name}.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":pattern,"key":key,"result":{"id":f"gnomehollow:{name}","count":count}})
def shapeless(name, ings, count): wjson(f"{D}/recipe/{name}.json", {"type":"minecraft:crafting_shapeless","category":"building","ingredients":ings,"result":{"id":f"gnomehollow:{name}","count":count}})
shaped("gnome_shingles", ["RR","RR"], {"R":"minecraft:red_terracotta"}, None, 4)
shaped("thatch", ["WW","WW"], {"W":"minecraft:wheat"}, None, 4)
shaped("toadstool_cap", ["RR","RR"], {"R":"minecraft:red_mushroom"}, None, 4)
shaped("plaster", ["CC","CC"], {"C":"minecraft:clay_ball"}, None, 4)
shapeless("timber_plaster", ["gnomehollow:plaster", "minecraft:dark_oak_planks"], 2)
shapeless("gnome_stem", ["minecraft:mushroom_stem"], 1)
shapeless("fieldstone", ["minecraft:cobblestone", "minecraft:cobblestone", "minecraft:gravel", "minecraft:gravel"], 4)
shapeless("toadstool_lamp", ["minecraft:red_mushroom", "minecraft:glowstone_dust"], 1)

# ============================================================== LANG
names_en = {"healer":"Healer","warrior":"Warrior","farmer":"Farmer","fisherman":"Fisherman","builder":"Builder","nitwit":"Nitwit"}
names_nl = {"healer":"Genezer","warrior":"Krijger","farmer":"Boer","fisherman":"Visser","builder":"Bouwer","nitwit":"Dwaas"}
nl = dict(nl)
for p in PROF:
    en[f"entity.gnomehollow.gnome_{p}"] = f"Gnome {names_en[p]}"; en[f"item.gnomehollow.gnome_{p}_spawn_egg"] = f"Gnome {names_en[p]} Spawn Egg"
    nl[f"entity.gnomehollow.gnome_{p}"] = f"Kabouter {names_nl[p]}"; nl[f"item.gnomehollow.gnome_{p}_spawn_egg"] = f"Kabouter {names_nl[p]} Spawn Egg"
# bestaande ondertitels (sounds.json-generator) behouden
for lang, d_ in (("en_us", en), ("nl_nl", nl)):
    p_ = f"{A}/lang/{lang}.json"
    old = json.load(open(p_)) if os.path.exists(p_) else {}
    old = {k: v for k, v in old.items() if k.startswith("subtitles.")}
    old.update(d_)
    wjson(p_, old)
print("assets ok")
