"""Genereert het complete kabouterdorp: straten, pleinen, huizen, decor, pools, loot en worldgen-JSON."""
import json, os, math, random, shutil, glob
from structlib import *
import gen_houses as H

OUT = ROOT   # data/gnomehollow
shutil.rmtree(f"{OUT}/structure", ignore_errors=True)
shutil.rmtree(f"{OUT}/worldgen", ignore_errors=True)
shutil.rmtree(f"{OUT}/loot_table/chests", ignore_errors=True)

STREET = "gnomehollow:street"; ENTR = "gnomehollow:entrance"
rng0 = random.Random(2026)

# ====================================================================== STRATEN (terrain-matching, pad op y=0)
def street_base(name, sx, sz, h=6, edge=True):
    t = Tpl(name, sx, h, sz); rng = random.Random(sum(map(ord, name)))
    for x in range(sx):
        for z in range(sz):
            c = "dirt_path" if (x == sx//2 or not edge) else rng.choice(["dirt_path"]*5 + ["coarse_dirt", "gravel", "dirt_path", "moss_block"][:3])
            t.set(x, 0, z, c)
            for y in range(1, h): t.set(x, y, z, "air")
    return t, rng
def lamp(t, x, z, y=1, h=3): lamp_post(t, x, z, y, h)

def street_straight(name, L, lamps, side_z=None, west_pool="gnomehollow:village/houses", east_pool="gnomehollow:village/houses"):
    t, rng = street_base(name, 3, L)
    t.jigsaw(1, 0, 0, "north", STREET, STREET, "gnomehollow:village/streets")
    t.jigsaw(1, 0, L-1, "south", STREET, STREET, "gnomehollow:village/streets")
    side_z = L//2 if side_z is None else side_z
    t.jigsaw(0, 0, side_z, "west", ENTR, ENTR, west_pool)
    t.jigsaw(2, 0, side_z, "east", ENTR, ENTR, east_pool)
    for (x, z) in lamps: lamp(t, x, z)
    for z in range(L):
        for x in (0, 2):
            if rng.random() < .05 and t.get(x, 1, z) is None: t.set(x, 1, z, rng.choice(FLOWERS))
    return t

def build_streets():
    street_straight("street_straight_12", 12, [(0, 1), (2, 10)])
    street_straight("street_straight_16", 16, [(0, 2), (2, 13)])
    t, rng = street_base("street_plain_16", 3, 16)
    t.jigsaw(1, 0, 0, "north", STREET, STREET, "gnomehollow:village/streets"); t.jigsaw(1, 0, 15, "south", STREET, STREET, "gnomehollow:village/streets")
    lamp(t, 0, 3); lamp(t, 2, 12)
    t, _ = street_base("street_corner", 3, 3, edge=False)
    t.jigsaw(1, 0, 2, "south", STREET, STREET, "gnomehollow:village/streets"); t.jigsaw(0, 0, 1, "west", STREET, STREET, "gnomehollow:village/streets")
    lamp(t, 2, 0)
    t, _ = street_base("street_t", 3, 3, edge=False)
    t.jigsaw(1, 0, 2, "south", STREET, STREET, "gnomehollow:village/streets"); t.jigsaw(0, 0, 1, "west", STREET, STREET, "gnomehollow:village/streets")
    t.jigsaw(2, 0, 1, "east", STREET, STREET, "gnomehollow:village/streets"); lamp(t, 1, 0)
    t, _ = street_base("street_cross", 3, 3, edge=False)
    for (x, z, f) in ((1, 2, "south"), (0, 1, "west"), (2, 1, "east"), (1, 0, "north")): t.jigsaw(x, 0, z, f, STREET, STREET, "gnomehollow:village/streets")
    t.set(1, 1, 1, "gnomehollow:gnome_stem"); t.set(1, 2, 1, "gnomehollow:toadstool_lamp")
    t, rng = street_base("street_end", 3, 4)
    t.jigsaw(1, 0, 0, "north", STREET, STREET, "minecraft:empty")
    lamp(t, 1, 3, h=2); t.set(0, 1, 2, "stripped_dark_oak_log", axis="y"); t.set(2, 1, 2, "stripped_dark_oak_log", axis="y")
    t.set(0, 1, 3, rng.choice(FLOWERS)); t.set(2, 1, 3, rng.choice(SHROOMS))

# ====================================================================== PLEINEN (rigid, 25x25) met directe beroepshuizen
N = 25; C = 12
SLOTS = [(5, 0, "north"), (19, 0, "north"), (24, 5, "east"), (24, 19, "east"), (5, 24, "south"), (19, 24, "south"), (0, 5, "west"), (0, 19, "west")]
def plaza_base(name, slot_pools, seed):
    rng = random.Random(seed); t = Tpl(name, N, 14, N); ground(t, rng)
    for x in range(N):
        for z in range(N):
            d = math.hypot(x-C, z-C)
            if d <= 11.2: t.set(x, G, z, "dirt_path" if rng.random() > .1 else "coarse_dirt")
            if 8.0 <= d <= 8.9 and (round(math.atan2(z-C, x-C)*8/math.pi) % 2 == 0): t.set(x, G, z, "gnomehollow:fieldstone")
    for (x, z, f) in SLOTS:
        for k in range(4):
            xx, zz = {"north": (x, k), "south": (x, N-1-k), "east": (N-1-k, z), "west": (k, z)}[f]
            t.set(xx, G, zz, "dirt_path")
    for (x, z, f) in [(C, 0, "north"), (N-1, C, "east"), (C, N-1, "south"), (0, C, "west")]:
        for k in range(4):
            xx, zz = {"north": (x-1, k), "south": (x-1, N-1-k), "east": (N-1-k, z-1), "west": (k, z-1)}[f]
            for d_ in range(3):
                if f in ("north", "south"): t.set(x-1+d_, G, k if f == "north" else N-1-k, "dirt_path")
                else: t.set(k if f == "west" else N-1-k, G, z-1+d_, "dirt_path")
    for (x, z, f), pool_ in zip(SLOTS, slot_pools): t.jigsaw(x, G, z, f, ENTR, ENTR, pool_)
    for (x, z, f) in [(C, 0, "north"), (N-1, C, "east"), (C, N-1, "south"), (0, C, "west")]: t.jigsaw(x, G, z, f, STREET, STREET, "gnomehollow:village/street_first")
    for (x, z) in ((6, 6), (18, 6), (6, 18), (18, 18)): lamp_post(t, x, z, G+1, 3)
    scatter(t, rng, 0, N-1, 0, N-1, .08)
    return t, rng
def planter(t, x, z, rng):
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            if abs(dx) == 1 or abs(dz) == 1: t.set(x+dx, G+1, z+dz, "dark_oak_planks" if (dx+dz) % 2 else "spruce_planks")
            else: t.set(x, G, z, "podzol")
    t.set(x, G+1, z, rng.choice(FLOWERS))
def stump(t, x, z): t.set(x, G+1, z, "stripped_dark_oak_log", axis="y")
def bench(t, x, z, facing): t.stairs(x, G+1, z, "spruce_stairs", facing)

def plaza_a(name, pools):
    t, rng = plaza_base(name, pools, 11); c = C
    for x in range(c-1, c+2):
        for z in range(c-1, c+2):
            for y in (G-2, G-1, G): t.set(x, y, z, "water" if (x, z) == (c, c) else "gnomehollow:fieldstone", **({"level": 0} if (x, z) == (c, c) else {}))
            if (x, z) != (c, c): t.set(x, G+1, z, "gnomehollow:fieldstone")
    for (x, z) in ((c-1, c-1), (c+1, c-1), (c-1, c+1), (c+1, c+1)):
        for y in range(G+2, G+5): t.set(x, y, z, "dark_oak_fence")
    for x in range(c-2, c+3):
        for z in range(c-2, c+3):
            if abs(x-c) == 2 and abs(z-c) == 2: continue
            t.set(x, G+5, z, "gnomehollow:toadstool_cap")
    for x in range(c-1, c+2):
        for z in range(c-1, c+2): t.set(x, G+6, z, "gnomehollow:toadstool_cap")
    t.set(c, G+7, c, "gnomehollow:toadstool_cap_slab", type="bottom", waterlogged=False); t.set(c, G+4, c, "lantern", hanging=True)
    for (dx, dz) in ((4, 0), (-4, 0), (0, 4), (0, -4), (3, 3), (-3, -3)): stump(t, c+dx, c+dz)
    for (dx, dz) in ((7, 0), (-7, 0), (0, -7), (0, 7)): planter(t, c+dx, c+dz, rng)
    t.barrel(c-4, G+1, c+6, "plaza"); t.barrel(c-3, G+1, c+6, "plaza"); t.chest(c+3, G+1, c+6, "north", "plaza")
    for (dx, dz) in ((-2, 4), (2, 4), (0, 5)): t.gnome("nitwit", c+dx, G+1, c+dz)
    t.save(); return t
def plaza_b(name, pools):
    t, rng = plaza_base(name, pools, 22); c = C
    for x in range(c-2, c+3):
        for z in range(c-2, c+3):
            if max(abs(x-c), abs(z-c)) == 2: t.set(x, G+1, z, "gnomehollow:fieldstone")
            elif max(abs(x-c), abs(z-c)) < 2: t.set(x, G, z, "coarse_dirt")
    t.set(c, G+1, c, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)
    for k in range(8):
        a = k*math.pi/4; x = c + round(4.4*math.cos(a)); z = c + round(4.4*math.sin(a))
        t.set(x, G+1, z, "stripped_dark_oak_log", axis="x" if k % 2 == 0 else "z")
    for x in range(c-4, c+5):
        for z in range(c+5, c+8): t.set(x, G+1, z, "spruce_planks")
    for x in (c-4, c+4):
        for y in range(G+2, G+5): t.set(x, y, c+5, "dark_oak_fence")
    t.set(c-4, G+5, c+5, "gnomehollow:toadstool_lamp"); t.set(c+4, G+5, c+5, "gnomehollow:toadstool_lamp")
    t.set(c-2, G+2, c+7, "note_block"); t.set(c+2, G+2, c+7, "jukebox"); t.set(c, G+2, c+7, "red_banner", rotation=0)
    for (dx, dz) in ((7, 0), (-7, 0)): planter(t, c+dx, c+dz, rng)
    t.barrel(c-8, G+1, c+2, "plaza"); t.barrel(c+8, G+1, c+2, "plaza"); t.chest(c, G+1, c-7, "south", "plaza")
    for dx in (-2, 0, 2): t.gnome("nitwit", c+dx, G+2, c+6)
    t.save(); return t
def plaza_c(name, pools):
    t, rng = plaza_base(name, pools, 33); c = C
    for x in range(N):
        for z in range(N):
            d = math.hypot(x-c, z-c)
            if d <= 4.4:
                for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
                t.set(x, G-3, z, "clay")
                if rng.random() < .1: t.set(x, G+1, z, "lily_pad")
            elif d <= 5.3:
                t.set(x, G, z, "gnomehollow:fieldstone")
                if (x+z) % 3: t.slab(x, G+1, z, "gnomehollow:fieldstone_slab")
    for x in range(c-1, c+2):
        for z in range(c-1, c+2): t.set(x, G, z, "gnomehollow:fieldstone"); t.set(x, G+1, z, "gnomehollow:fieldstone")
    for y in (G+2, G+3, G+4): t.set(c, y, c, "gnomehollow:plaster")
    t.set(c, G+3, c+1, "white_wool"); t.set(c, G+2, c+1, "white_wool"); t.set(c-1, G+3, c, "dark_oak_fence"); t.set(c+1, G+3, c, "dark_oak_fence")
    t.set(c, G+5, c, "gnomehollow:toadstool_cap"); t.slab(c, G+6, c, "gnomehollow:toadstool_cap_slab")
    for k in range(3): t.set(c, G, c-5-k, "gnomehollow:fieldstone")           # bruggetje naar het eiland (noord)
    for k in range(1, 5): t.set(c, G, c-k, "spruce_planks")
    bench(t, c-8, c-3, "east"); bench(t, c+8, c+3, "west"); bench(t, c-3, c+8, "north"); bench(t, c+3, c-8, "south")
    for (dx, dz) in ((-6, 5), (6, -5)): stump(t, c+dx, c+dz)
    t.barrel(c-9, G+1, c+1, "plaza"); t.chest(c+9, G+1, c-2, "west", "plaza")
    for (dx, dz) in ((-5, 7), (5, 7)): t.gnome("nitwit", c+dx, G+1, c+dz)
    t.gnome("healer", c-2, G+1, c+8)
    t.save(); return t

# ====================================================================== DECOR (hangt aan een straat via 'entrance')
def decor_base(name, sx=7, sz=7, seed=0):
    rng = random.Random(sum(map(ord, name))+seed); t = Tpl(name, sx, 9, sz); ground(t, rng)
    cx = (sx-1)//2
    for z in range(sz): t.set(cx, G, z, "dirt_path")
    for z in range(sz-2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    t.jigsaw(cx, G, sz-1, "south", ENTR, ENTR, "minecraft:empty")
    return t, rng, cx
def build_decor():
    t, rng, cx = decor_base("decor_mushrooms")
    for (mx, mz, h) in ((1, 1, 2), (5, 2, 3), (2, 4, 1), (5, 5, 2)):
        for y in range(G+1, G+1+h): t.set(mx, y, mz, "gnomehollow:gnome_stem")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1): t.slab(mx+dx, G+1+h, mz+dz, "gnomehollow:toadstool_cap_slab")
        t.set(mx, G+1+h, mz, "gnomehollow:toadstool_cap")
    stump(t, 3, 2); t.set(3, G+2, 2, "spruce_pressure_plate"); t.set(3, G+1, 3, "stripped_dark_oak_log", axis="z")
    scatter(t, rng, 0, 6, 0, 5, .12); t.gnome("nitwit", 3, G+1, 4); t.save()
    t, rng, cx = decor_base("decor_market", 9, 8)
    for (x, z) in ((1, 1), (7, 1), (1, 4), (7, 4)):
        for y in range(G+1, G+4): t.set(x, y, z, "dark_oak_fence")
    for x in range(0, 9):
        for z in range(0, 6): t.slab(x, G+4, z, "gnomehollow:toadstool_cap_slab") if (x in range(0, 9) and 0 <= z <= 5 and x not in (-1,)) and False else None
    for x in range(1, 8):
        for z in range(1, 5): t.set(x, G+4, z, "gnomehollow:toadstool_cap" if (x+z) % 2 else "white_wool")
    t.barrel(2, G+1, 1, "plaza"); t.barrel(3, G+1, 1, "plaza"); t.chest(5, G+1, 1, "south", "plaza"); t.set(6, G+1, 1, "hay_block", axis="y")
    for x in range(2, 7): t.set(x, G+1, 3, "spruce_slab", type="bottom", waterlogged=False)
    t.set(4, G+3, 4, "lantern", hanging=True); t.gnome("nitwit", 4, G+1, 2); t.save()
    t, rng, cx = decor_base("decor_garden", 9, 8)
    for x in range(1, 8):
        for z in range(1, 5):
            if (x, z) == (4, 3): t.set(x, G, z, "water", level=0); continue
            t.set(x, G, z, "farmland", moisture=7); crop = rng.choice(["wheat", "carrots", "potatoes", "beetroots"]); t.set(x, G+1, z, crop, age=3 if crop == "beetroots" else 7)
    for x in range(0, 9): t.set(x, G+1, 0, "dark_oak_fence")
    for z in range(0, 6): t.set(0, G+1, z, "dark_oak_fence"); t.set(8, G+1, z, "dark_oak_fence")
    H.scarecrow(t, 6, 5); t.set(2, G+1, 5, "composter", level=0); t.save()
    t, rng, cx = decor_base("decor_campfire")
    t.set(3, G+1, 2, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)
    for (x, z) in ((1, 2), (5, 2), (3, 0), (3, 4)): stump(t, x, z)
    t.set(2, G+1, 3, "cauldron"); t.set(6, G+1, 1, "dark_oak_fence"); t.set(6, G+2, 1, "lantern", hanging=False)
    scatter(t, rng, 0, 6, 0, 4, .1); t.gnome("nitwit", 4, G+1, 3); t.save()
    t, rng, cx = decor_base("decor_statue")
    for x in range(2, 5):
        for z in range(1, 4): t.set(x, G+1, z, "gnomehollow:fieldstone")
    for y in (G+2, G+3, G+4): t.set(3, y, 2, "gnomehollow:plaster")
    t.set(3, G+3, 3, "white_wool"); t.set(3, G+5, 2, "gnomehollow:toadstool_cap"); t.set(3, G+6, 2, "gnomehollow:toadstool_cap_slab", type="bottom", waterlogged=False)
    for (x, z) in ((1, 1), (5, 1), (1, 3), (5, 3)): t.set(x, G+1, z, rng.choice(FLOWERS))
    lamp_post(t, 0, 4); scatter(t, rng, 0, 6, 0, 5, .12); t.save()
    t, rng, cx = decor_base("decor_hives", 9, 7)
    for x in (2, 4, 6):
        t.set(x, G+1, 1, "dark_oak_fence"); t.set(x, G+2, 1, "beehive", facing="south")
    for x in range(1, 8):
        for z in range(2, 5): 
            if t.get(x, G+1, z) is None and (x != 4) and rng.random() < .7: t.set(x, G+1, z, rng.choice(["dandelion", "poppy", "cornflower", "azure_bluet", "allium"]))
    t.save()
    t, rng, cx = decor_base("decor_pond", 9, 8)
    for x in range(2, 7):
        for z in range(1, 4):
            for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-3, z, "clay")
            if rng.random() < .3: t.set(x, G+1, z, "lily_pad")
    t.stairs(3, G+1, 5, "spruce_stairs", "north"); t.stairs(4, G+1, 5, "spruce_stairs", "north"); lamp_post(t, 6, 5)
    scatter(t, rng, 0, 8, 0, 6, .12); t.gnome("nitwit", 5, G+1, 5); t.save()
    t, rng, cx = decor_base("decor_hay")
    for (x, z, h) in ((1, 1, 3), (2, 1, 2), (1, 2, 2), (5, 2, 2), (4, 1, 1)):
        for y in range(G+1, G+1+h): t.set(x, y, z, "hay_block", axis="y")
    t.barrel(5, G+1, 1, "farmer"); t.set(3, G+1, 3, "composter", level=0); scatter(t, rng, 0, 6, 0, 4, .1); t.save()

# ====================================================================== POOLS
def pool(name, elements, fallback="minecraft:empty"):
    out = []
    for e in elements:
        tpl, w, proj = e
        if tpl is None: out.append({"weight": w, "element": {"element_type": "minecraft:empty_pool_element"}})
        else: out.append({"weight": w, "element": {"element_type": "minecraft:single_pool_element", "location": f"gnomehollow:village/{tpl}",
                          "processors": "minecraft:empty", "projection": proj}})
    p = f"{OUT}/worldgen/template_pool/village/{name}.json"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"fallback": fallback, "elements": out}, open(p, "w"), indent=2)

def build_pools():
    R, M = "rigid", "terrain_matching"
    pool("town_centers", [("plaza_a", 1, R), ("plaza_b", 1, R), ("plaza_c", 1, R)])
    pool("street_first", [("street_plain_16", 1, M)])
    pool("slot_houses", [("house_cottage_thatch", 2, R), ("house_cottage_shingle", 2, R), ("house_twostory", 2, R), ("house_cottage_cap", 1, R),
                         ("house_cottage_log", 1, R), ("house_burrow", 1, R), ("house_mushroom", 1, R), (None, 1, R)])
    pool("streets", [("street_straight_12", 4, M), ("street_straight_16", 2, M), ("street_corner", 4, M), ("street_t", 3, M), ("street_cross", 1, M)],
         fallback="gnomehollow:village/street_ends")
    pool("street_ends", [("street_end", 1, M)])
    pool("healers", [("house_healer_a", 1, R), ("house_healer_b", 1, R)]); pool("warriors", [("house_warrior_a", 1, R), ("house_warrior_b", 1, R)])
    pool("farmers", [("house_farmer_a", 1, R), ("house_farmer_b", 1, R)]); pool("fishermen", [("house_fisherman_a", 1, R), ("house_fisherman_b", 1, R)])
    pool("builders", [("house_builder_a", 1, R), ("house_builder_b", 1, R)])
    pool("nitwits", [("house_cottage_thatch", 1, R), ("house_cottage_shingle", 1, R), ("house_cottage_small", 1, R), ("house_mushroom", 1, R), ("house_burrow", 1, R)])
    generic = [("house_cottage_thatch", 3), ("house_cottage_shingle", 3), ("house_twostory", 2), ("house_cottage_small", 2), ("house_cottage_log", 2),
               ("house_cottage_cap", 2), ("house_burrow", 2), ("house_mushroom", 2)]
    decor = ["decor_mushrooms", "decor_market", "decor_garden", "decor_campfire", "decor_statue", "decor_hives", "decor_pond", "decor_hay"]
    pool("houses", [(n, w, R) for n, w in generic] + [(d, 1, R) for d in decor] + [(None, 3, R)])

# ====================================================================== LOOT
def loot(name, rolls, entries):
    ents = []
    for e in entries:
        item, w = e[0], e[1]; cnt = e[2] if len(e) > 2 else None; extra = e[3] if len(e) > 3 else None
        d = {"type": "minecraft:item", "name": item if ":" in item else f"minecraft:{item}", "weight": w}
        fn = []
        if cnt: fn.append({"function": "minecraft:set_count", "count": {"min": cnt[0], "max": cnt[1]}})
        if extra: fn.append(extra)
        if fn: d["functions"] = fn
        ents.append(d)
    p = f"{OUT}/loot_table/chests/{name}.json"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"type": "minecraft:chest", "pools": [{"rolls": {"min": rolls[0], "max": rolls[1]}, "entries": ents}]}, open(p, "w"), indent=2)
def potion(i): return {"function": "minecraft:set_potion", "id": f"minecraft:{i}"}
def build_loot():
    common = [("bread", 10, (1, 3)), ("apple", 8, (1, 4)), ("carrot", 6, (2, 5)), ("baked_potato", 6, (1, 3)), ("sweet_berries", 6, (2, 6)),
              ("red_mushroom", 5, (1, 3)), ("brown_mushroom", 5, (1, 3)), ("cookie", 4, (2, 6)), ("honey_bottle", 3, (1, 1)), ("candle", 3, (1, 2)),
              ("book", 2, (1, 1)), ("emerald", 3, (1, 2)), ("lantern", 2, (1, 1)), ("rabbit_stew", 1, (1, 1))]
    loot("pantry", (3, 6), common)
    loot("plaza", (3, 6), common + [("cod", 4, (1, 3)), ("glow_berries", 4, (2, 5)), ("name_tag", 1, (1, 1)), ("gnomehollow:toadstool_lamp", 3, (1, 3))])
    loot("healer", (3, 6), [("potion", 6, (1, 1), potion("healing")), ("potion", 5, (1, 1), potion("regeneration")), ("potion", 3, (1, 1), potion("swiftness")),
        ("glass_bottle", 8, (1, 3)), ("glow_berries", 6, (2, 5)), ("spider_eye", 4, (1, 2)), ("golden_carrot", 4, (1, 3)), ("golden_apple", 1, (1, 1)),
        ("red_mushroom", 5, (2, 4)), ("emerald", 3, (1, 2)), ("honey_bottle", 3, (1, 2))])
    loot("warrior", (3, 6), [("iron_sword", 2, (1, 1)), ("arrow", 10, (4, 12)), ("bow", 2, (1, 1)), ("shield", 2, (1, 1)), ("iron_nugget", 8, (3, 8)),
        ("iron_ingot", 4, (1, 3)), ("bread", 8, (1, 3)), ("cooked_beef", 5, (1, 2)), ("bone", 5, (1, 3)), ("leather", 5, (1, 3)), ("golden_carrot", 3, (1, 2)), ("emerald", 3, (1, 2))])
    loot("farmer", (3, 6), [("wheat", 10, (3, 8)), ("wheat_seeds", 10, (3, 8)), ("carrot", 8, (2, 5)), ("potato", 8, (2, 5)), ("beetroot", 6, (2, 5)), ("bread", 8, (1, 3)),
        ("hay_block", 3, (1, 2)), ("bone_meal", 8, (2, 6)), ("pumpkin_pie", 3, (1, 2)), ("melon_slice", 4, (2, 5)), ("emerald", 3, (1, 2)), ("gnomehollow:thatch", 3, (2, 6))])
    loot("fisher", (3, 6), [("cod", 10, (1, 4)), ("salmon", 8, (1, 3)), ("cooked_cod", 6, (1, 3)), ("string", 8, (2, 6)), ("fishing_rod", 2, (1, 1)), ("pufferfish", 2, (1, 1)),
        ("tropical_fish", 2, (1, 1)), ("nautilus_shell", 1, (1, 1)), ("lily_pad", 5, (1, 3)), ("ink_sac", 3, (1, 2)), ("emerald", 3, (1, 2)), ("kelp", 4, (2, 5))])
    loot("builder", (3, 6), [("stone_bricks", 8, (4, 12)), ("cobblestone", 8, (6, 16)), ("spruce_planks", 8, (6, 16)), ("clay_ball", 6, (4, 10)), ("brick", 5, (2, 6)),
        ("iron_nugget", 5, (2, 6)), ("copper_ingot", 4, (2, 5)), ("lantern", 4, (1, 2)), ("glass", 6, (2, 6)), ("gnomehollow:plaster", 6, (4, 8)),
        ("gnomehollow:thatch", 5, (4, 8)), ("gnomehollow:fieldstone", 5, (4, 8)), ("gnomehollow:gnome_shingles", 4, (3, 6)), ("emerald", 3, (1, 2)), ("shears", 1, (1, 1))])
    loot("nitwit", (3, 6), [("cookie", 10, (2, 8)), ("firework_rocket", 6, (1, 3)), ("note_block", 3, (1, 1)), ("poppy", 8, (2, 5)), ("dandelion", 8, (2, 5)),
        ("gold_nugget", 5, (2, 6)), ("honey_bottle", 3, (1, 2)), ("emerald", 4, (1, 3)), ("sweet_berries", 5, (2, 6)), ("gnomehollow:timber_plaster", 3, (2, 5))])

# ====================================================================== WORLDGEN
def build_worldgen():
    def wj(rel, obj):
        p = f"{OUT}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(obj, open(p, "w"), indent=2)
    wj("worldgen/structure/gnome_village.json", {
        "type": "minecraft:jigsaw", "biomes": "#gnomehollow:has_structure/gnome_village", "step": "surface_structures", "spawn_overrides": {},
        "terrain_adaptation": "beard_thin", "start_pool": "gnomehollow:village/town_centers", "size": 7,
        "start_height": {"absolute": -G}, "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 80, "use_expansion_hack": False})
    wj("worldgen/structure_set/gnome_villages.json", {"structures": [{"structure": "gnomehollow:gnome_village", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 34, "separation": 14, "salt": 1827364509}})
    wj("tags/worldgen/biome/has_structure/gnome_village.json", {"replace": False, "values": [
        "minecraft:dark_forest", "minecraft:taiga", "minecraft:old_growth_pine_taiga", "minecraft:old_growth_spruce_taiga"]})

# ====================================================================== RUN
build_streets()
H.all_houses()
P = lambda n: f"gnomehollow:village/{n}"
plaza_a("plaza_a", [P("healers"), P("warriors"), P("farmers"), P("slot_houses"), P("fishermen"), P("slot_houses"), P("builders"), P("slot_houses")])
plaza_b("plaza_b", [P("slot_houses"), P("builders"), P("fishermen"), P("healers"), P("slot_houses"), P("warriors"), P("farmers"), P("slot_houses")])
plaza_c("plaza_c", [P("farmers"), P("slot_houses"), P("healers"), P("builders"), P("warriors"), P("slot_houses"), P("slot_houses"), P("fishermen")])
build_decor(); build_pools(); build_loot(); build_worldgen()
for name, t in REGISTRY.items():
    if not os.path.exists(f"{OUT}/structure/village/{name}.nbt"): t.save()
print(len(REGISTRY), "templates opgeslagen")
