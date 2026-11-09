import json, os, random, math
from PIL import Image, ImageDraw

ROOT = "/home/claude/gnome-hollow/src/main/resources"
A = f"{ROOT}/assets/gnomehollow"
D = f"{ROOT}/data/gnomehollow"
MC = f"{ROOT}/data/minecraft"

def wjson(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)

# ------------------------------------------------------------------ professions
PROF = {
 "healer":    dict(hat=(60,160,80),  band=(240,240,240), tunic=(232,236,226), belt=(70,130,70),  beard=(242,242,242), emblem="cross", egg=(0x3FA34D,0xF2F2F2)),
 "warrior":   dict(hat=(130,135,145),band=(180,40,30),   tunic=(150,152,162), belt=(120,40,35),  beard=(160,85,45),    emblem="plate", egg=(0x8A8D93,0xB3261E)),
 "farmer":    dict(hat=(225,190,90), band=(150,100,40),  tunic=(120,150,70),  belt=(110,75,40),  beard=(175,175,175), emblem="straps",egg=(0xE0B84A,0x6B8E23)),
 "fisherman": dict(hat=(45,110,190), band=(235,235,235), tunic=(60,100,160),  belt=(40,60,100),  beard=(225,225,230), emblem="stripes",egg=(0x2F6FBF,0xE8E8E8)),
 "builder":   dict(hat=(230,125,30), band=(250,200,90),  tunic=(140,95,55),   belt=(80,55,30),   beard=(95,62,38),    emblem="toolbelt",egg=(0xE07B20,0x8B5A2B)),
 "nitwit":    dict(hat=(125,65,160), band=(240,210,90),  tunic=(205,125,200), belt=(240,210,90), beard=(205,150,90),  emblem="patches",egg=(0x7B3FA0,0xF0D060)),
}
SKIN = (238,190,150); SKIN_D = (205,150,115); NOSE = (225,140,120)
BOOT = (80,52,34); PANTS = (92,70,50)

# cubes: (name, origin, size, uv)
def cubes_for(p):
    right, left = [], []
    if p == "warrior":
        right = [("blade",[-4,3.5,-9],[1,1,7],[44,0],(200,205,215)), ("guard",[-5,3.5,-2],[3,1,1],[44,10],(120,90,50))]
        left  = [("shield",[4.5,2.5,-2],[1,5,4],[44,24],(150,100,55))]
    elif p == "healer":
        right = [("potion",[-4.5,3,-3.5],[2,3,2],[44,0],(230,70,110)), ("cork",[-4,6,-3],[1,1,1],[44,10],(160,110,60))]
    elif p == "farmer":
        right = [("handle",[-4,3.5,-9],[1,1,7],[44,0],(130,90,45)), ("hoehead",[-4,0.5,-10],[1,3,1],[44,16],(170,172,178))]
    elif p == "fisherman":
        right = [("rod",[-4,3.5,-9],[1,1,7],[44,0],(120,85,45)), ("line",[-4,0.5,-10],[1,3,1],[44,16],(235,235,235))]
    elif p == "builder":
        right = [("hhandle",[-4,3.5,-6],[1,1,5],[44,0],(130,90,45)), ("hhead",[-5,2.5,-8],[3,2,2],[44,10],(110,112,120))]
    return right, left

def box_regions(u, v, w, h, d):
    return {
      "top":   (u+d, v, w, d),
      "bottom":(u+d+w, v, w, d),
      "right": (u, v+d, d, h),
      "front": (u+d, v+d, w, h),
      "left":  (u+d+w, v+d, d, h),
      "back":  (u+2*d+w, v+d, w, h),
    }

def shade(c, k):
    return tuple(max(0, min(255, int(x*k))) for x in c)

def paint_box(img, uv, size, color, rng, faces=None):
    u, v = uv; w, h, d = [int(round(s)) for s in size]
    regs = box_regions(u, v, w, h, d)
    px = img.load()
    for name, (x, y, ww, hh) in regs.items():
        base = color
        if name == "top": base = shade(color, 1.1)
        if name == "bottom": base = shade(color, 0.7)
        if name in ("left","right"): base = shade(color, 0.88)
        if name == "back": base = shade(color, 0.92)
        if faces and name in faces: base = faces[name]
        for i in range(ww):
            for j in range(hh):
                n = rng.uniform(0.94, 1.06)
                px[x+i, y+j] = shade(base, n) + (255,)
    return regs

def make_gnome_texture(name, pal):
    rng = random.Random(hash(name) & 0xffff)
    img = Image.new("RGBA", (64, 64), (0,0,0,0))
    px = img.load()
    # head
    r = paint_box(img, (0,0), (6,4,6), SKIN, rng)
    fx, fy, fw, fh = r["front"]
    px[fx+1, fy+1] = (40,30,30,255); px[fx+4, fy+1] = (40,30,30,255)       # eyes
    px[fx+1, fy+1-0] = (35,25,25,255)
    # cheeks
    px[fx+0, fy+2] = shade(SKIN, 0.9) + (255,); px[fx+5, fy+2] = shade(SKIN, 0.9) + (255,)
    paint_box(img, (26,0), (1,1,1), NOSE, rng)
    paint_box(img, (0,22), (5,3,1), pal["beard"], rng)
    # hat
    paint_box(img, (0,28), (7,1,7), pal["band"], rng)
    paint_box(img, (0,38), (5,2,5), pal["hat"], rng)
    paint_box(img, (0,46), (3,1,3), shade(pal["hat"], 1.15), rng)
    # body
    r = paint_box(img, (0,12), (5,5,3), pal["tunic"], rng)
    bx, by, bw, bh = r["front"]
    for i in range(bw):                               # belt
        px[bx+i, by+3] = shade(pal["belt"], rng.uniform(.95,1.05)) + (255,)
    px[bx+2, by+3] = (230,200,70,255)                 # buckle
    e = pal["emblem"]
    if e == "cross":
        for j in (0,1,2): px[bx+2, by+j] = (60,160,80,255)
        for i in (1,2,3): px[bx+i, by+1] = (60,160,80,255)
    elif e == "plate":
        for i in range(bw):
            for j in range(3): px[bx+i, by+j] = shade((165,168,178), rng.uniform(.93,1.07)) + (255,)
        px[bx+2, by+1] = (180,40,30,255)
    elif e == "straps":
        for j in range(bh): px[bx+1, by+j] = (110,75,40,255); px[bx+3, by+j] = (110,75,40,255)
    elif e == "stripes":
        for j in (0,2): 
            for i in range(bw): px[bx+i, by+j] = (235,235,235,255)
    elif e == "toolbelt":
        px[bx+0, by+4] = (90,90,95,255); px[bx+4, by+4] = (90,90,95,255)
    elif e == "patches":
        px[bx+1, by+1] = (90,160,230,255); px[bx+3, by+2] = (250,230,90,255); px[bx+0, by+0] = (120,200,120,255)
    # arms (sleeve colour, hand skin at the bottom row)
    for uv in ((32,12),(32,20)):
        r = paint_box(img, uv, (2,4,2), shade(pal["tunic"], 0.95), rng)
        for key in ("front","back","left","right"):
            x, y, ww, hh = r[key]
            for i in range(ww): px[x+i, y+hh-1] = SKIN + (255,)
        x, y, ww, hh = r["bottom"]
        for i in range(ww):
            for j in range(hh): px[x+i, y+j] = SKIN_D + (255,)
    # legs
    for uv in ((32,28),(32,34)):
        r = paint_box(img, uv, (2,3,2), PANTS, rng)
        for key in ("front","back","left","right"):
            x, y, ww, hh = r[key]
            for i in range(ww): px[x+i, y+hh-1] = BOOT + (255,)
    right, left = cubes_for(name.split("_")[1])
    for (_, o, s, uv, col) in right + left:
        paint_box(img, uv, s, col, rng)
    return img

# ------------------------------------------------------------------ geo + animations
def cube(origin, size, uv):
    return {"origin": origin, "size": size, "uv": uv}

def make_geo(name, prof):
    right, left = cubes_for(prof)
    bones = [
      {"name":"root","pivot":[0,0,0]},
      {"name":"leg_left","parent":"root","pivot":[1.5,3,0],"cubes":[cube([0.5,0,-1],[2,3,2],[32,34])]},
      {"name":"leg_right","parent":"root","pivot":[-1.5,3,0],"cubes":[cube([-2.5,0,-1],[2,3,2],[32,28])]},
      {"name":"body","parent":"root","pivot":[0,3,0],"cubes":[cube([-2.5,3,-1.5],[5,5,3],[0,12])]},
      {"name":"arm_left","parent":"root","pivot":[3.5,7.5,0],"cubes":[cube([2.5,4,-1],[2,4,2],[32,20])] + [cube(o,s,uv) for (_,o,s,uv,_) in left]},
      {"name":"arm_right","parent":"root","pivot":[-3.5,7.5,0],"cubes":[cube([-4.5,4,-1],[2,4,2],[32,12])] + [cube(o,s,uv) for (_,o,s,uv,_) in right]},
      {"name":"head","parent":"root","pivot":[0,8,0],"cubes":[
          cube([-3,8,-3],[6,4,6],[0,0]), cube([-0.5,8.8,-4],[1,1,1],[26,0]), cube([-2.5,7,-3.5],[5,3,1],[0,22])]},
      {"name":"hat","parent":"head","pivot":[0,12,0],"cubes":[
          cube([-3.5,12,-3.5],[7,1,7],[0,28]), cube([-2.5,13,-2.5],[5,2,5],[0,38]), cube([-1.5,15,-1.5],[3,1,3],[0,46])]},
    ]
    return {
      "format_version": "1.12.0",
      "minecraft:geometry": [{
        "description": {"identifier": f"geometry.{name}", "texture_width": 64, "texture_height": 64,
                        "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0,0.5,0]},
        "bones": bones}]
    }

def kf(d): return {f"{k:.2f}": v for k, v in d}

def make_anims():
    anims = {}
    anims["animation.gnome.idle"] = {"loop": True, "animation_length": 2.0, "bones": {
        "head": {"rotation": kf([(0,[0,0,0]),(1.0,[3,2,0]),(2.0,[0,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(1.0,[0,0.15,0]),(2.0,[0,0,0])])},
        "arm_left": {"rotation": kf([(0,[0,0,2]),(1.0,[0,0,-2]),(2.0,[0,0,2])])},
        "arm_right": {"rotation": kf([(0,[0,0,-2]),(1.0,[0,0,2]),(2.0,[0,0,-2])])},
    }}
    anims["animation.gnome.walk"] = {"loop": True, "animation_length": 0.8, "bones": {
        "leg_left": {"rotation": kf([(0,[32,0,0]),(0.4,[-32,0,0]),(0.8,[32,0,0])])},
        "leg_right": {"rotation": kf([(0,[-32,0,0]),(0.4,[32,0,0]),(0.8,[-32,0,0])])},
        "arm_left": {"rotation": kf([(0,[-28,0,0]),(0.4,[28,0,0]),(0.8,[-28,0,0])])},
        "arm_right": {"rotation": kf([(0,[28,0,0]),(0.4,[-28,0,0]),(0.8,[28,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(0.2,[0,0.4,0]),(0.4,[0,0,0]),(0.6,[0,0.4,0]),(0.8,[0,0,0])])},
        "head": {"rotation": kf([(0,[0,3,0]),(0.4,[0,-3,0]),(0.8,[0,3,0])])},
    }}
    anims["animation.gnome.attack"] = {"loop": False, "animation_length": 0.4, "bones": {
        "arm_right": {"rotation": kf([(0,[0,0,0]),(0.12,[-120,0,0]),(0.25,[-20,0,0]),(0.4,[0,0,0])])},
        "body": {"rotation": kf([(0,[0,0,0]),(0.12,[-10,0,0]),(0.25,[8,0,0]),(0.4,[0,0,0])])},
    }}
    anims["animation.gnome.work"] = {"loop": True, "animation_length": 0.9, "bones": {
        "arm_right": {"rotation": kf([(0,[-40,0,0]),(0.35,[-115,0,0]),(0.55,[-30,0,0]),(0.9,[-40,0,0])])},
        "arm_left": {"rotation": kf([(0,[-20,0,0]),(0.45,[-45,0,0]),(0.9,[-20,0,0])])},
        "body": {"rotation": kf([(0,[0,0,0]),(0.55,[10,0,0]),(0.9,[0,0,0])])},
        "head": {"rotation": kf([(0,[8,0,0]),(0.9,[8,0,0])])},
    }}
    anims["animation.gnome.fish"] = {"loop": True, "animation_length": 3.0, "bones": {
        "arm_right": {"rotation": kf([(0,[-65,0,0]),(1.0,[-62,0,3]),(2.0,[-70,0,-3]),(3.0,[-65,0,0])])},
        "arm_left": {"rotation": kf([(0,[-55,0,0]),(3.0,[-55,0,0])])},
        "body": {"rotation": kf([(0,[4,0,0]),(3.0,[4,0,0])])},
        "head": {"rotation": kf([(0,[10,0,0]),(1.5,[12,0,0]),(3.0,[10,0,0])])},
    }}
    anims["animation.gnome.play"] = {"loop": True, "animation_length": 0.6, "bones": {
        "arm_right": {"rotation": kf([(0,[-110,0,0]),(0.3,[-125,0,0]),(0.6,[-110,0,0])])},
        "arm_left": {"rotation": kf([(0,[-125,0,0]),(0.3,[-110,0,0]),(0.6,[-125,0,0])])},
        "body": {"position": kf([(0,[0,0,0]),(0.3,[0,0.6,0]),(0.6,[0,0,0])])},
        "head": {"rotation": kf([(0,[0,0,8]),(0.3,[0,0,-8]),(0.6,[0,0,8])])},
    }}
    return {"format_version": "1.8.0", "animations": anims}

for prof, pal in PROF.items():
    name = f"gnome_{prof}"
    os.makedirs(f"{A}/textures/entity", exist_ok=True)
    make_gnome_texture(name, pal).save(f"{A}/textures/entity/{name}.png")
    wjson(f"{A}/geckolib/models/entity/{name}.geo.json", make_geo(name, prof))
    wjson(f"{A}/geckolib/animations/entity/{name}.animation.json", make_anims())

# ------------------------------------------------------------------ block textures
def make_lamp():
    rng = random.Random(7)
    img = Image.new("RGBA", (16,16), (0,0,0,255)); px = img.load()
    for x in range(16):
        for y in range(16):
            k = rng.uniform(.93, 1.07)
            px[x,y] = shade((205,55,45), k) + (255,)
    for (x,y,r) in [(3,3,1.6),(10,4,2.0),(6,9,1.5),(12,11,1.8),(2,12,1.4),(8,1,1.0)]:
        for i in range(16):
            for j in range(16):
                if (i-x)**2 + (j-y)**2 <= r*r: px[i,j] = (250,240,215,255)
    for x in range(16):                                   # warm glow rim
        for y in (0,15): px[x,y] = (255,170,70,255)
    for y in range(16):
        for x in (0,15): px[x,y] = (255,170,70,255)
    return img
def make_shingles():
    rng = random.Random(11)
    img = Image.new("RGBA", (16,16), (0,0,0,255)); px = img.load()
    for y in range(16):
        row = y // 4
        off = 4 if row % 2 else 0
        for x in range(16):
            lx = (x + off) % 8
            base = (158,62,48)
            k = rng.uniform(.92,1.07)
            c = shade(base, k)
            if y % 4 == 3: c = shade(base, 0.55)
            elif lx == 7: c = shade(base, 0.7)
            elif y % 4 == 0: c = shade(base, 1.12)
            px[x,y] = c + (255,)
    return img
os.makedirs(f"{A}/textures/block", exist_ok=True)
make_lamp().save(f"{A}/textures/block/toadstool_lamp.png")
make_shingles().save(f"{A}/textures/block/gnome_shingles.png")

# icon
ic = Image.new("RGBA", (128,128), (34,52,38,255)); d = ImageDraw.Draw(ic)
d.polygon([(64,6),(30,70),(98,70)], fill=(200,50,45,255))
d.rectangle([22,68,106,78], fill=(240,230,210,255))
d.rectangle([34,78,94,106], fill=SKIN+(255,))
d.rectangle([40,88,52,94], fill=(40,30,30,255)); d.rectangle([76,88,88,94], fill=(40,30,30,255))
d.rectangle([60,94,68,102], fill=NOSE+(255,))
d.polygon([(34,100),(94,100),(64,126)], fill=(240,240,240,255))
ic.save(f"{A}/icon.png")

# ------------------------------------------------------------------ blockstates / models / items
wjson(f"{A}/blockstates/toadstool_lamp.json", {"variants": {"": {"model": "gnomehollow:block/toadstool_lamp"}}})
wjson(f"{A}/blockstates/gnome_shingles.json", {"variants": {"": {"model": "gnomehollow:block/gnome_shingles"}}})
for n in ("toadstool_lamp", "gnome_shingles"):
    wjson(f"{A}/models/block/{n}.json", {"parent": "minecraft:block/cube_all", "textures": {"all": f"gnomehollow:block/{n}"}})
tex = {"bottom": "gnomehollow:block/gnome_shingles", "top": "gnomehollow:block/gnome_shingles", "side": "gnomehollow:block/gnome_shingles"}
wjson(f"{A}/models/block/gnome_shingle_slab.json", {"parent": "minecraft:block/slab", "textures": tex})
wjson(f"{A}/models/block/gnome_shingle_slab_top.json", {"parent": "minecraft:block/slab_top", "textures": tex})
wjson(f"{A}/models/block/gnome_shingle_stairs.json", {"parent": "minecraft:block/stairs", "textures": tex})
wjson(f"{A}/models/block/gnome_shingle_stairs_inner.json", {"parent": "minecraft:block/inner_stairs", "textures": tex})
wjson(f"{A}/models/block/gnome_shingle_stairs_outer.json", {"parent": "minecraft:block/outer_stairs", "textures": tex})
wjson(f"{A}/blockstates/gnome_shingle_slab.json", {"variants": {
    "type=bottom": {"model": "gnomehollow:block/gnome_shingle_slab"},
    "type=top": {"model": "gnomehollow:block/gnome_shingle_slab_top"},
    "type=double": {"model": "gnomehollow:block/gnome_shingles"}}})
S = "gnomehollow:block/gnome_shingle_stairs"
def sv(model, y=0, x=0):
    o = {"model": model}
    if x: o["x"] = x
    if y: o["y"] = y
    if x or y: o["uvlock"] = True
    return o
variants = {}
bottom = {"east": (0,0,270,0,270), "south": (90,90,0,90,0), "west": (180,180,90,180,90), "north": (270,270,180,270,180)}
top    = {"east": (0,90,0,90,0), "south": (90,180,90,180,90), "west": (180,270,180,270,180), "north": (270,0,270,0,270)}
shapes = ["straight","outer_right","outer_left","inner_right","inner_left"]
models = [S, S+"_outer", S+"_outer", S+"_inner", S+"_inner"]
for facing, ys in bottom.items():
    for sh, m, y in zip(shapes, models, ys):
        variants[f"facing={facing},half=bottom,shape={sh}"] = sv(m, y)
for facing, ys in top.items():
    for sh, m, y in zip(shapes, models, ys):
        variants[f"facing={facing},half=top,shape={sh}"] = sv(m, y, 180)
wjson(f"{A}/blockstates/gnome_shingle_stairs.json", {"variants": variants})

def item_def(model, tints=None):
    m = {"type": "minecraft:model", "model": model}
    if tints: m["tints"] = [{"type": "minecraft:constant", "value": t} for t in tints]
    return {"model": m}
for n in ("toadstool_lamp","gnome_shingles","gnome_shingle_stairs","gnome_shingle_slab"):
    wjson(f"{A}/items/{n}.json", item_def(f"gnomehollow:block/{n}"))
for prof, pal in PROF.items():
    wjson(f"{A}/items/gnome_{prof}_spawn_egg.json", item_def("minecraft:item/template_spawn_egg", pal["egg"]))

# ------------------------------------------------------------------ lang
en = {
 "block.gnomehollow.toadstool_lamp": "Toadstool Lamp",
 "block.gnomehollow.gnome_shingles": "Gnome Shingles",
 "block.gnomehollow.gnome_shingle_stairs": "Gnome Shingle Stairs",
 "block.gnomehollow.gnome_shingle_slab": "Gnome Shingle Slab",
}
nl = dict(en)
nl.update({"block.gnomehollow.toadstool_lamp": "Paddenstoellamp","block.gnomehollow.gnome_shingles": "Kaboutershingles",
           "block.gnomehollow.gnome_shingle_stairs": "Kaboutershingle-trap","block.gnomehollow.gnome_shingle_slab": "Kaboutershingle-plaat"})
names_en = {"healer":"Healer","warrior":"Warrior","farmer":"Farmer","fisherman":"Fisherman","builder":"Builder","nitwit":"Nitwit"}
names_nl = {"healer":"Genezer","warrior":"Krijger","farmer":"Boer","fisherman":"Visser","builder":"Bouwer","nitwit":"Dwaas"}
for p in PROF:
    en[f"entity.gnomehollow.gnome_{p}"] = f"Gnome {names_en[p]}"
    en[f"item.gnomehollow.gnome_{p}_spawn_egg"] = f"Gnome {names_en[p]} Spawn Egg"
    nl[f"entity.gnomehollow.gnome_{p}"] = f"Kabouter {names_nl[p]}"
    nl[f"item.gnomehollow.gnome_{p}_spawn_egg"] = f"Kabouter {names_nl[p]} Spawn Egg"
wjson(f"{A}/lang/en_us.json", en)
wjson(f"{A}/lang/nl_nl.json", nl)

# ------------------------------------------------------------------ loot, tags, recipes
def self_drop(n, extra=None):
    pool = {"rolls": 1.0, "bonus_rolls": 0.0, "entries": [{"type": "minecraft:item", "name": f"gnomehollow:{n}"}],
            "conditions": [{"condition": "minecraft:survives_explosion"}]}
    if extra: pool["entries"][0]["functions"] = extra
    return {"type": "minecraft:block", "pools": [pool], "random_sequence": f"gnomehollow:blocks/{n}"}
for n in ("toadstool_lamp","gnome_shingles","gnome_shingle_stairs"):
    wjson(f"{D}/loot_table/blocks/{n}.json", self_drop(n))
wjson(f"{D}/loot_table/blocks/gnome_shingle_slab.json", self_drop("gnome_shingle_slab", [
    {"function": "minecraft:set_count", "count": 2.0, "add": False,
     "conditions": [{"condition": "minecraft:block_state_property", "block": "gnomehollow:gnome_shingle_slab", "properties": {"type": "double"}}]},
    {"function": "minecraft:explosion_decay"}]))
wjson(f"{MC}/tags/block/mineable/pickaxe.json", {"replace": False, "values": ["gnomehollow:gnome_shingles","gnomehollow:gnome_shingle_stairs","gnomehollow:gnome_shingle_slab"]})
wjson(f"{MC}/tags/block/mineable/axe.json", {"replace": False, "values": ["gnomehollow:toadstool_lamp"]})
wjson(f"{D}/recipe/gnome_shingles.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":["RR","RR"],"key":{"R":"minecraft:red_terracotta"},"result":{"id":"gnomehollow:gnome_shingles","count":4}})
wjson(f"{D}/recipe/gnome_shingle_stairs.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":["S  ","SS ","SSS"],"key":{"S":"gnomehollow:gnome_shingles"},"result":{"id":"gnomehollow:gnome_shingle_stairs","count":4}})
wjson(f"{D}/recipe/gnome_shingle_slab.json", {"type":"minecraft:crafting_shaped","category":"building","pattern":["SSS"],"key":{"S":"gnomehollow:gnome_shingles"},"result":{"id":"gnomehollow:gnome_shingle_slab","count":6}})
wjson(f"{D}/recipe/toadstool_lamp.json", {"type":"minecraft:crafting_shapeless","category":"building","ingredients":["minecraft:red_mushroom","minecraft:glowstone_dust"],"result":{"id":"gnomehollow:toadstool_lamp","count":1}})
print("assets ok")
