"""Compacte gnome-huisjes (Ribbits-schaal: leefruimte, slaapplek, opslag op een paar blokken)."""
from structlib import *
import random, math

FS = "gnomehollow:fieldstone"; PL = "gnomehollow:plaster"; TP = "gnomehollow:timber_plaster"
LAMP = "gnomehollow:toadstool_lamp"
YARD = 3     # rijen tuin voor de deur

def new_rng(name): return random.Random(sum(ord(c)*(i+7) for i, c in enumerate(name)))

def site(t, rng, x0, x1, z0, z1, h):
    """Fundering + grond + lucht alleen binnen de rechthoek (geen grote platen); daarbuiten blijft het terrein zoals het is."""
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            for y in range(0, G): t.set(x, y, z, "dirt")
            t.set(x, G, z, "podzol" if rng.random() < .25 else "grass_block")
            for y in range(G+1, h+1): t.set(x, y, z, "air")

# ------------------------------------------------------------------ cottage (parametrisch)
def cottage(name, W, D, wall="plaster", roof="thatch", ridge="x", chim=None, porch=True, bed="red", beds=1, gnomes=("nitwit",),
            loot="pantry", stations=(), floors=1, yard=None, lamp_door=True):
    rng = new_rng(name)
    sx, sz = W+2, D+2+YARD
    span = (D if ridge == "x" else W) + 2
    wall_top = G + 4*floors - 1; yb = wall_top + 1
    sy = yb + span//2 + 4
    t = Tpl(name, sx, sy, sz); site(t, rng, 0, sx-1, 0, sz-1, sy-1)
    x0, x1, z0, z1 = 1, W, 1, D; cx = (sx-1)//2
    for x in range(x0, x1+1):
        for z in range(z0, z1+1): t.set(x, G-1, z, FS); t.set(x, G-2, z, FS)
    for y in range(G, wall_top+1):
        for x in range(x0, x1+1):
            for z in range(z0, z1+1):
                ring = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
                floorline = y > G and (y-G) % 4 == 0
                if not ring:
                    t.set(x, y, z, "spruce_planks" if (y == G or floorline) else "air"); continue
                if y <= G+1: b = FS
                elif floorline or (y-G) % 4 == 3: b = "dark_oak_planks" if wall != "stone" else FS
                elif wall == "plaster": b = "dark_oak_log" if corner else PL
                elif wall == "timber": b = "dark_oak_log" if corner else TP
                elif wall == "log": b = "stripped_spruce_log" if corner else "spruce_log"
                else: b = "stripped_spruce_log" if corner else FS
                if b.endswith("_log"): t.set(x, y, z, b, axis="y")
                else: t.set(x, y, z, b)
    # deur + ramen
    t.set(cx, G, z1, "spruce_planks"); t.door(cx, G+1, z1, "spruce_door", "south"); t.set(cx, G+3, z1, "dark_oak_planks")
    for f in range(floors):
        wy = G + 2 + 4*f
        for wx in (cx-1, cx+1):
            if x0+1 <= wx <= x1-1 and not (f == 0 and wx == cx): t.pane(wx, wy, z1, "x")
        if x0+1 <= cx <= x1-1: t.pane(cx, wy, z0, "x")
        t.pane(x0, wy, (z0+z1)//2, "z"); t.pane(x1, wy, (z0+z1)//2, "z")
    if floors == 2:
        t.set(cx, G+4, z0+1, "air")
        for y in range(G+1, G+6): t.set(cx, y, z0+1, "ladder", facing="south", waterlogged=False)
    fill = {"timber": TP, "stone": FS, "log": "spruce_planks"}.get(wall, PL)
    top = gable_roof(t, (x0 if ridge == "x" else z0), (x1 if ridge == "x" else z1), (z0 if ridge == "x" else x0), (z1 if ridge == "x" else x1), yb, ridge, roof, fill)
    if ridge == "z": t.pane(cx, yb+1, z1, "x")
    if chim:
        chx = x1 if chim == "r" else x0-1
        chimney(t, chx, z0+1, G+1, top)
    if porch:
        for dx in (-1, 1): t.set(cx+dx, G+1, z1+1, "dark_oak_fence"); t.set(cx+dx, G+2, z1+1, "dark_oak_fence")
        for dx in (-1, 0, 1): t.slab(cx+dx, G+3, z1+1, ROOFS[roof]["slab"])
    if lamp_door: t.set(cx+1, G+2, z1+1, "lantern", hanging=True) if porch else None
    # tuin/pad
    for z in range(z1+1, sz): t.set(cx, G, z, "dirt_path")
    for z in range(z1+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path" if rng.random() < .8 else "coarse_dirt")
    scatter(t, rng, 0, sx-1, z1+1, sz-2, .12); scatter(t, rng, 0, sx-1, 0, z1, .06)
    g = dict(t=t, rng=rng, x0=x0, x1=x1, z0=z0, z1=z1, cx=cx, wall_top=wall_top, yb=yb, floors=floors, sx=sx, sz=sz, top=top, W=W, D=D)
    furnish(t, g, bed, beds, loot, stations)
    for k, prof in enumerate(gnomes): t.gnome(prof, cx + (k % 2)*(-1 if k else 1), G+1, z0+2+(k//2))
    if yard: yard(t, g)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return g

def furnish(t, g, bed, beds, loot, stations):
    x0, x1, z0, z1, cx, wt = g["x0"], g["x1"], g["z0"], g["z1"], g["cx"], g["wall_top"]
    xi0, xi1, zi0, zi1 = x0+1, x1-1, z0+1, z1-1
    t.bed(xi0, G+1, zi0, bed, "south")
    if beds >= 2: t.bed(xi0+1, G+1, zi0, bed, "south")
    used = {(xi0, zi0), (xi0, zi0+1)} | ({(xi0+1, zi0), (xi0+1, zi0+1)} if beds >= 2 else set())
    slots = [(x, zi0) for x in range(xi0+1, xi1+1) if (x, zi0) not in used]
    slots += [(xi1, z) for z in range(zi0+1, zi1)]
    slots += [(x, zi1) for x in range(xi1, xi0, -1) if x != cx]
    items = list(stations) + [("chest", loot)] 
    for (x, z), item in zip(slots, items):
        if isinstance(item, tuple):
            kind, arg = item
            if kind == "chest": t.chest(x, G+1, z, "south" if z == zi0 else "west", arg)
            elif kind == "barrel": t.barrel(x, G+1, z, arg)
            elif kind == "block": t.set(x, G+1, z, arg)
            elif kind == "blockp": t.set(x, G+1, z, arg[0], **arg[1])
        else: t.set(x, G+1, z, item)
    # tafeltje met stoel in het midden
    tz = (zi0+zi1)//2
    tx = xi1 if (xi1, tz) not in {(a, b) for (a, b) in slots[:len(items)]} else xi1-1
    if t.get(tx, G+1, tz) is None or t.get(tx, G+1, tz) == "air":
        t.set(tx, G+1, tz, "dark_oak_fence"); t.set(tx, G+2, tz, "spruce_pressure_plate")
        if t.get(tx-1, G+1, tz) in (None, "air") and tx-1 != xi0: t.stairs(tx-1, G+1, tz, "spruce_stairs", "east")
    t.set(xi0, wt, zi1, LAMP)
    if g["floors"] == 2:
        t.bed(xi0, G+5, zi0, "white", "south"); t.chest(xi1, G+5, zi1, "west", loot); t.set(xi0, G+7, zi1, LAMP)

# ------------------------------------------------------------------ erven
def farm_yard(t, g):
    rng = g["rng"]; z1, sz, sx = g["z1"], g["sz"], g["sx"]
    for px, wx in ((0, 1),):
        for x in range(px, px+3):
            for z in range(z1+2, sz-1):
                if (x, z) == (wx, z1+2): t.set(x, G, z, "water", level=0); continue
                t.set(x, G, z, "farmland", moisture=7); c = rng.choice(["wheat", "carrots", "potatoes", "beetroots"])
                t.set(x, G+1, z, c, age=3 if c == "beetroots" else 7)
    H = __import__("gen_houses")
    scarecrow(t, sx-2, z1+2)
def scarecrow(t, x, z):
    t.set(x, G+1, z, "dark_oak_fence"); t.set(x, G+2, z, "hay_block", axis="y"); t.set(x, G+3, z, "carved_pumpkin", facing="south")
    t.set(x-1, G+2, z, "dark_oak_fence"); t.set(x+1, G+2, z, "dark_oak_fence")
def fish_yard(t, g):
    z1, sz, sx = g["z1"], g["sz"], g["sx"]
    for x in range(sx-4, sx):
        for z in range(z1+1, sz):
            for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-3, z, "clay")
    for x in range(sx-5, sx-3): t.set(x, G, z1+2, "spruce_planks")
    t.set(sx-6, G+1, z1+2, "dark_oak_fence"); t.set(sx-6, G+2, z1+2, "lantern", hanging=False)
    for k in range(2): t.set(1+k, G+1, z1+1, "dark_oak_fence"); t.set(1+k, G+2, z1+1, "dried_kelp_block")
def herb_yard(t, g):
    rng = g["rng"]; z1, sz = g["z1"], g["sz"]
    for x in (0, 1):
        for z in range(z1+1, sz-1):
            t.set(x, G, z, "podzol"); t.set(x, G+1, z, rng.choice(["lily_of_the_valley", "azure_bluet", "cornflower", "allium", "brown_mushroom", "fern"]))
def guard_yard(t, g):
    z1, sz, cx = g["z1"], g["sz"], g["cx"]
    t.set(1, G+1, z1+2, "hay_block", axis="y"); t.set(1, G+2, z1+2, "target")
    for x in (cx-1, cx+1): t.set(x, G+3, z1+1, "red_banner", rotation=0) if False else None
def build_yard(t, g):
    z1, sz, sx = g["z1"], g["sz"], g["sx"]
    t.fill(0, G+1, z1+1, 1, G+1, z1+2, "stripped_spruce_log", axis="x"); t.set(0, G+2, z1+1, "stripped_spruce_log", axis="x")
    for y in range(G+1, G+4): t.set(sx-1, y, z1+1, "scaffolding", bottom=(y == G+1), distance=0, waterlogged=False)
    t.fill(sx-2, G+1, z1+2, sx-1, G+1, z1+2, "stone_bricks")

# ------------------------------------------------------------------ heuvelhuis (compact)
def burrow(name, farm=False, shop=None, gnomes=("nitwit",), bed="green", loot="pantry"):
    rng = new_rng(name); sx, sz = 9, 12; t = Tpl(name, sx, 13, sz); site(t, rng, 0, sx-1, 0, sz-1, 12)
    cx = 4; zc = 3.5; rx, rz = 4.2, 3.6; top = {}
    for x in range(sx):
        for z in range(0, 7):
            d = math.sqrt(((x-cx)/rx)**2 + ((z-zc)/rz)**2)
            if d <= 1.0: top[(x, z)] = G + 1 + int((1-d)*4.2)
    for (x, z), h in top.items():
        for y in range(G-2, G): t.set(x, y, z, FS)
        for y in range(G, h): t.set(x, y, z, "dirt")
        t.set(x, h, z, "moss_block" if rng.random() < .15 else ("podzol" if rng.random() < .2 else "grass_block"))
        if rng.random() < .2 and h >= G+2: t.set(x, h+1, z, rng.choice(FLOWERS + SHROOMS + ["fern", "azalea_leaves"]))
    def inside(x, z, y):
        d = math.sqrt(((x-cx)/(rx-1.8))**2 + ((z-zc)/(rz-1.6))**2)
        return d <= 1.0 and y > G and (y-G) <= 3 - (1 if d > .65 else 0)
    for (x, z), h in top.items():
        for y in range(G, G+5):
            if y <= h and inside(x, z, y): t.set(x, y, z, "air")
        if math.sqrt(((x-cx)/(rx-1.8))**2 + ((z-zc)/(rz-1.6))**2) <= 1.0: t.set(x, G, z, "spruce_planks")
    for (x, y, z) in list(t.blocks.keys()):
        if t.get(x, y, z) == "air" and y > G:
            for (dx, dy, dz) in ((1,0,0),(-1,0,0),(0,0,1),(0,0,-1),(0,1,0)):
                n = t.get(x+dx, y+dy, z+dz)
                if n in ("dirt", "grass_block", "moss_block", "podzol") and (x+dx, z+dz) in top and y+dy < top[(x+dx, z+dz)]:
                    t.set(x+dx, y+dy, z+dz, "dark_oak_planks" if dy == 1 else "spruce_planks")
    zf = max(z for (x, z) in top if x == cx)
    for z in range(zf-2, zf+1):
        for y in range(G+1, G+3): t.set(cx, y, z, "air")
    t.door(cx, G+1, zf, "spruce_door", "south")
    for (dx, dy) in ((-1,1),(-1,2),(1,1),(1,2),(0,3)): t.set(cx+dx, G+dy, zf, "stripped_spruce_log", axis="y" if dx else "x")
    t.set(cx-1, G+3, zf, "moss_block"); t.set(cx+1, G+3, zf, "moss_block")
    t.set(cx+2, G+1, zf+1, "dark_oak_fence"); t.set(cx+2, G+2, zf+1, "lantern", hanging=False)
    t.set(cx, G, zf+1, "dirt_path")
    if (cx+1, 2) in top: chimney(t, cx+1, 2, top[(cx+1, 2)]-1, top[(cx+1, 2)]+1)
    t.bed(cx-2, G+1, 1, bed, "south"); t.chest(cx+2, G+1, 1, "west", loot)
    t.set(cx+2, G+1, 3, "dark_oak_fence"); t.set(cx+2, G+2, 3, "spruce_pressure_plate"); t.stairs(cx+1, G+1, 3, "spruce_stairs", "east")
    t.set(cx, G+3, 2, LAMP)
    if shop == "farm": t.barrel(cx-1, G+1, 1, "farmer"); t.set(cx, G+1, 1, "composter", level=0)
    if shop == "healer": t.set(cx-1, G+1, 1, "brewing_stand"); t.set(cx, G+1, 1, "water_cauldron", level=3)
    for z in range(zf+1, sz): t.set(cx, G, z, "dirt_path")
    scatter(t, rng, 0, sx-1, zf+1, sz-2, .12)
    if farm:
        for x in range(0, 3):
            for z in range(zf+2, zf+4):
                if (x, z) == (1, zf+2): t.set(x, G, z, "water", level=0); continue
                t.set(x, G, z, "farmland", moisture=7); c = rng.choice(["wheat", "carrots", "potatoes"]); t.set(x, G+1, z, c, age=7)
    for k, prof in enumerate(gnomes): t.gnome(prof, cx - (k % 2)*2 + 1, G+1, 2)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ paddenstoelhuisje (compact)
def mushroom_house(name, shop=None, loot="pantry", bed="pink", gnomes=("nitwit",)):
    rng = new_rng(name); R = 3.4
    sx, sz = 9, 8+YARD; t = Tpl(name, sx, 15, sz); site(t, rng, 0, sx-1, 0, sz-1, 14)
    cx, cz = 4, 4
    dist = lambda x, z: math.hypot(x-cx, z-cz)
    for x in range(sx):
        for z in range(sz):
            if dist(x, z) <= R: t.set(x, G-1, z, FS); t.set(x, G-2, z, FS)
    for y in range(G, G+6):
        for x in range(sx):
            for z in range(sz):
                d = dist(x, z)
                if d <= R: t.set(x, y, z, "gnomehollow:gnome_stem" if d >= R-1.0 else ("spruce_planks" if y == G else "air"))
    for x in range(sx):
        for z in range(sz):
            if dist(x, z) <= R-1.0 and not (x == cx and z == cz-1) and not (x == cx and z == cz+1): t.set(x, G+3, z, "spruce_planks")
    for y in range(G+1, G+4): t.set(cx, y, cz-1, "ladder", facing="south", waterlogged=False)
    t.set(cx, G+3, cz-1, "air"); t.set(cx, G+4, cz-1, "ladder", facing="south", waterlogged=False)
    for (y, r) in [(G+6, 4.4), (G+7, 3.6), (G+8, 2.6), (G+9, 1.5), (G+10, 0.8)]:
        for x in range(sx):
            for z in range(sz):
                if dist(x, z) <= r: t.set(x, y, z, "gnomehollow:toadstool_cap")
    zf = cz + 3
    t.door(cx, G+1, zf, "spruce_door", "south")
    for dx in (-1, 1):
        for dy in (1, 2): t.set(cx+dx, G+dy, zf, "stripped_spruce_log", axis="y")
    t.set(cx, G+3, zf, "stripped_spruce_log", axis="x")
    t.set(cx+2, G+1, zf+1, "dark_oak_fence"); t.set(cx+2, G+2, zf+1, "lantern", hanging=False)
    for (wx, wz, al) in ((cx-3, cz, "z"), (cx+3, cz, "z"), (cx, cz-3, "x")): t.pane(wx, G+2, wz, al)
    t.bed(cx+1, G+4, cz+1, bed, "north"); t.chest(cx-1, G+4, cz+1, "east", loot)
    t.set(cx+1, G+1, cz, "dark_oak_fence"); t.set(cx+1, G+2, cz, "spruce_pressure_plate"); t.stairs(cx, G+1, cz+1, "spruce_stairs", "east")
    t.set(cx-1, G+1, cz+1, "bookshelf"); t.set(cx, G+2, cz+2, LAMP)
    if shop == "healer":
        t.set(cx-1, G+1, cz, "brewing_stand"); t.set(cx-1, G+1, cz-1, "water_cauldron", level=3); t.barrel(cx+1, G+1, cz-1, "healer")
    for z in range(zf+1, sz): t.set(cx, G, z, "dirt_path")
    for (mx, mz) in ((1, 9), (7, 9)):
        t.set(mx, G+1, mz, "gnomehollow:gnome_stem")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1): t.slab(mx+dx, G+2, mz+dz, "gnomehollow:toadstool_cap_slab")
    scatter(t, rng, 0, sx-1, zf+1, sz-2, .1)
    for k, prof in enumerate(gnomes): t.gnome(prof, cx - 1 + k, G+1, cz-1)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ wachttoren (compact)
def tower(name):
    rng = new_rng(name); sx, sz = 9, 11; t = Tpl(name, sx, 22, sz); site(t, rng, 0, sx-1, 0, sz-1, 21)
    cx = 4; x0, x1, z0, z1 = 2, 6, 1, 5
    for x in range(x0, x1+1):
        for z in range(z0, z1+1): t.set(x, G-1, z, FS); t.set(x, G-2, z, FS); t.set(x, G, z, "spruce_planks")
    for y in range(G, G+9):
        for x in range(x0, x1+1):
            for z in range(z0, z1+1):
                ring = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
                if ring: t.set(x, y, z, "stripped_spruce_log" if corner else FS, **({"axis": "y"} if corner else {}))
                elif y > G: t.set(x, y, z, "air")
    for fy in (G+4,):
        for x in range(x0+1, x1):
            for z in range(z0+1, z1): t.set(x, fy, z, "spruce_planks")
        t.set(cx, fy, z0+1, "air")
    for y in range(G+1, G+9): t.set(cx, y, z0+1, "ladder", facing="south", waterlogged=False)
    for wy in (G+2, G+6):
        for (wx, wz, al) in ((cx, z0, "x"), (x0, 3, "z"), (x1, 3, "z")): t.pane(wx, wy, wz, al)
    t.door(cx, G+1, z1, "spruce_door", "south"); t.set(cx, G+3, z1, "dark_oak_planks")
    gy = G+8
    for x in range(x0-1, x1+2):
        for z in range(z0-1, z1+2):
            if x in (x0-1, x1+1) or z in (z0-1, z1+1): t.set(x, gy, z, "spruce_planks"); t.set(x, gy+1, z, "dark_oak_fence")
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            if x in (x0, x1) or z in (z0, z1): t.set(x, gy, z, "spruce_planks")
    ry = gy+3
    for (x, z) in ((x0-1, z0-1), (x1+1, z0-1), (x0-1, z1+1), (x1+1, z1+1)):
        for y in range(gy+1, gy+3): t.set(x, y, z, "dark_oak_log", axis="y")
    for r, s in enumerate((9, 7, 5, 3)):
        lo = cx - s//2; hi = cx + s//2; zlo = 3 - s//2; zhi = 3 + s//2
        for x in range(lo, hi+1):
            for z in range(zlo, zhi+1):
                ex = x in (lo, hi); ez = z in (zlo, zhi)
                if not (ex or ez):
                    if s <= 3: t.set(x, ry+r, z, "gnomehollow:gnome_shingles")
                    continue
                if ex and ez: t.set(x, ry+r, z, "gnomehollow:gnome_shingles"); continue
                f = "south" if z == zlo else "north" if z == zhi else "east" if x == lo else "west"
                t.stairs(x, ry+r, z, ROOFS["shingle"]["stairs"], f)
    t.set(cx, ry+4, 3, LAMP); t.set(cx, G+2, 3, LAMP)
    t.chest(x1-1, G+1, z0+1, "west", "warrior"); t.chest(x1-1, G+5, z0+1, "west", "warrior"); t.bed(x0+1, G+1, 3, "red", "south")
    t.bed(x0+1, G+5, 3, "red", "south")
    t.set(cx, gy+1, z0-1, "red_banner", rotation=8)
    for z in range(z1+1, sz): t.set(cx, G, z, "dirt_path")
    t.set(cx+2, G+1, z1+1, "dark_oak_fence"); t.set(cx+2, G+2, z1+1, "lantern", hanging=False)
    t.gnome("warrior", cx, G+1, 3); t.gnome("warrior", cx, G+5, 3)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ communale kleine gebouwen
def library():
    g = cottage("house_library", 5, 6, wall="plaster", roof="toadstool", ridge="x", chim="r", bed="purple", beds=1, gnomes=("nitwit",), loot="library",
                stations=[("block", "lectern"), ("block", "bookshelf")])
    t = g["t"]; xi0, xi1, zi0, zi1 = g["x0"]+1, g["x1"]-1, g["z0"]+1, g["z1"]-1
    t.set(xi1, G+2, zi0, "bookshelf"); t.set(xi1, G+1, zi0+1, "bookshelf"); t.set(xi1, G+2, zi0+1, "bookshelf")
    return t
def market():
    rng = new_rng("house_market"); sx, sz = 9, 8; t = Tpl("house_market", sx, 10, sz); site(t, rng, 0, sx-1, 0, sz-1, 9); cx = 4
    for z in range(sz): t.set(cx, G, z, "dirt_path")
    for z in range(sz-3, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    for sxp, sk in ((1, "west"), (6, "east")):
        for z in (1, 4):
            for dx in (0, 1): 
                for dz in (0, 1):
                    pass
            for y in range(G+1, G+3): t.set(sxp, y, z, "dark_oak_fence"); t.set(sxp+1, y, z, "dark_oak_fence")
            for dx in range(0, 2):
                for dz in range(0, 3): t.set(sxp+dx, G+3, z+dz if z == 1 else z+dz-1, "gnomehollow:toadstool_cap" if (dx+dz) % 2 == 0 else "white_wool")
    t.set(1, G+1, 2, "loom", facing="east"); t.set(7, G+1, 3, "loom", facing="west")
    t.barrel(1, G+1, 1, "market"); t.chest(7, G+1, 1, "south", "market"); t.barrel(1, G+1, 4, "market"); t.set(7, G+1, 4, "hay_block", axis="y")
    t.set(2, G+2, 2, "lantern", hanging=True) if False else None
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t
def garden():
    rng = new_rng("house_garden"); sx, sz = 9, 8; t = Tpl("house_garden", sx, 8, sz); site(t, rng, 0, sx-1, 0, sz-1, 7); cx = 4
    for x in range(1, 8):
        for z in range(1, 5):
            if (x, z) in ((3, 2), (5, 3)): t.set(x, G, z, "water", level=0); continue
            t.set(x, G, z, "farmland", moisture=7); c = rng.choice(["wheat", "carrots", "potatoes", "beetroots", "wheat"])
            t.set(x, G+1, z, c, age=3 if c == "beetroots" else 7)
    for x in range(0, 9): t.set(x, G+1, 0, "dark_oak_fence")
    for z in range(0, 5): t.set(0, G+1, z, "dark_oak_fence"); t.set(8, G+1, z, "dark_oak_fence")
    t.set(cx, G+1, 0, "air")
    for z in range(0, sz): t.set(cx, G, z, "dirt_path")
    t.set(cx, G+1, 5, "air"); t.set(1, G+1, 6, "composter", level=0); t.stairs(7, G+1, 6, "spruce_stairs", "north"); t.stairs(6, G+1, 6, "spruce_stairs", "north")
    scarecrow(t, 7, 4) if False else None
    scatter(t, rng, 0, 8, 5, 6, .15)
    t.gnome("nitwit", 6, G+1, 5)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ rooster van alle huizen
def all_houses():
    # algemene huisjes (1-3 bewoners naar grootte)
    cottage("house_cottage_thatch", 5, 5, "plaster", "thatch", "x", "r", gnomes=("nitwit",), bed="red")
    cottage("house_cottage_cap", 5, 5, "plaster", "toadstool", "x", "l", gnomes=("nitwit",), bed="pink", loot="nitwit")
    cottage("house_cottage_small", 5, 4, "timber", "thatch", "z", None, gnomes=("nitwit",), bed="white")
    cottage("house_cottage_shingle", 6, 5, "timber", "shingle", "z", "l", gnomes=("nitwit", "nitwit"), bed="blue", beds=2)
    cottage("house_cottage_log", 6, 6, "log", "thatch", "x", "r", gnomes=("nitwit", "nitwit"), bed="brown", beds=2)
    cottage("house_twostory", 5, 5, "timber", "shingle", "x", "r", gnomes=("nitwit", "nitwit"), bed="yellow", floors=2)
    burrow("house_burrow"); mushroom_house("house_mushroom", loot="nitwit")
    # beroepshuizen
    cottage("house_healer_a", 6, 5, "plaster", "toadstool", "x", "r", gnomes=("healer",), bed="green", loot="healer",
            stations=[("block", "brewing_stand"), ("block", "brewing_stand"), ("blockp", ("water_cauldron", {"level": 3})), ("barrel", "healer")], yard=herb_yard)
    mushroom_house("house_healer_b", shop="healer", loot="healer", bed="green", gnomes=("healer",))
    cottage("house_warrior_a", 7, 5, "stone", "shingle", "x", "r", porch=False, gnomes=("warrior", "warrior"), bed="red", beds=2, loot="warrior",
            stations=[("blockp", ("grindstone", {"face": "floor", "facing": "north"})), ("blockp", ("anvil", {"facing": "east"})), ("barrel", "warrior")], yard=guard_yard)
    tower("house_warrior_b")
    cottage("house_farmer_a", 6, 5, "plaster", "thatch", "x", "l", gnomes=("farmer", "farmer"), bed="lime", beds=2, loot="farmer",
            stations=[("blockp", ("composter", {"level": 0})), ("barrel", "farmer"), ("blockp", ("hay_block", {"axis": "y"}))], yard=farm_yard)
    burrow("house_farmer_b", farm=True, shop="farm", gnomes=("farmer",), bed="lime", loot="farmer")
    cottage("house_fisherman_a", 6, 5, "timber", "shingle", "z", "r", gnomes=("fisherman",), bed="blue", loot="fisher",
            stations=[("barrel", "fisher"), ("barrel", "fisher"), ("blockp", ("water_cauldron", {"level": 3}))], yard=fish_yard)
    cottage("house_fisherman_b", 5, 5, "log", "thatch", "x", None, gnomes=("fisherman",), bed="cyan", loot="fisher", stations=[("barrel", "fisher")], yard=fish_yard)
    cottage("house_builder_a", 7, 6, "log", "shingle", "x", "r", gnomes=("builder", "builder"), bed="orange", beds=2, loot="builder",
            stations=[("blockp", ("stonecutter", {"facing": "south"})), ("block", "crafting_table"), ("blockp", ("anvil", {"facing": "east"})), ("barrel", "builder")], yard=build_yard)
    cottage("house_builder_b", 6, 5, "timber", "thatch", "z", "l", gnomes=("builder",), bed="orange", loot="builder",
            stations=[("blockp", ("stonecutter", {"facing": "south"})), ("barrel", "builder")], yard=build_yard)
    library(); market(); garden()
