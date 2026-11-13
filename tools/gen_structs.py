"""Genereert het kabouterdorp: organische pleinen, terrein-volgende straten, compacte huizen, decor, pools, loot en worldgen-JSON."""
import json, os, math, random, shutil
from structlib import *
import gen_houses as H

OUT = ROOT
shutil.rmtree(f"{OUT}/structure", ignore_errors=True)
shutil.rmtree(f"{OUT}/worldgen", ignore_errors=True)
shutil.rmtree(f"{OUT}/loot_table/chests", ignore_errors=True)
STREET = "gnomehollow:street"; ENTR = "gnomehollow:entrance"
P = lambda n: f"gnomehollow:village/{n}"

# ====================================================================== STRATEN (terrain-matching, pad op y=0)
def street_base(name, sx, sz, h=6, edge=True):
    t = Tpl(name, sx, h, sz); rng = random.Random(sum(map(ord, name)))
    for x in range(sx):
        for z in range(sz):
            c = "dirt_path" if (x == sx//2 or not edge) else rng.choice(["dirt_path"]*5 + ["coarse_dirt", "gravel"])
            t.set(x, 0, z, c)
            for y in range(1, h): t.set(x, y, z, "air")
    return t, rng

def straight(name, L, side_z, lamp_at=None, sides=True):
    t, rng = street_base(name, 3, L)
    t.jigsaw(1, 0, 0, "north", STREET, STREET, P("streets")); t.jigsaw(1, 0, L-1, "south", STREET, STREET, P("streets"))
    if sides:
        t.jigsaw(0, 0, side_z, "west", ENTR, ENTR, P("houses")); t.jigsaw(2, 0, side_z, "east", ENTR, ENTR, P("houses"))
    if lamp_at: lamp_post(t, lamp_at[0], lamp_at[1], 1, 2)
    for z in range(L):
        for x in (0, 2):
            if rng.random() < .05 and t.get(x, 1, z) is None: t.set(x, 1, z, rng.choice(FLOWERS))
    return t

def build_streets():
    straight("street_straight_10", 10, 5)
    straight("street_straight_14", 14, 7, lamp_at=(2, 12))
    straight("street_plain_12", 12, 0, sides=False)
    t, _ = street_base("street_corner", 3, 3, edge=False)
    t.jigsaw(1, 0, 2, "south", STREET, STREET, P("streets")); t.jigsaw(0, 0, 1, "west", STREET, STREET, P("streets"))
    t, _ = street_base("street_t", 3, 3, edge=False)
    t.jigsaw(1, 0, 2, "south", STREET, STREET, P("streets")); t.jigsaw(0, 0, 1, "west", STREET, STREET, P("streets")); t.jigsaw(2, 0, 1, "east", STREET, STREET, P("streets"))
    t, _ = street_base("street_cross", 3, 3, edge=False)
    for (x, z, f) in ((1, 2, "south"), (0, 1, "west"), (2, 1, "east"), (1, 0, "north")): t.jigsaw(x, 0, z, f, STREET, STREET, P("streets"))
    t.set(1, 1, 1, "gnomehollow:gnome_stem"); t.set(1, 2, 1, "gnomehollow:toadstool_lamp")
    t, rng = street_base("street_end", 3, 3)
    t.jigsaw(1, 0, 0, "north", STREET, STREET, "minecraft:empty")
    t.set(0, 1, 2, rng.choice(FLOWERS)); t.set(2, 1, 2, rng.choice(SHROOMS)); t.stairs(1, 1, 2, "spruce_stairs", "south")

# ====================================================================== PLEINEN (rigid, organisch; alleen de cirkel + paden worden aangepast)
N = 21; C = 10
SLOTS = [(4, 0, "north"), (16, 0, "north"), (20, 4, "east"), (20, 16, "east"), (4, 20, "south"), (16, 20, "south"), (0, 4, "west"), (0, 16, "west")]
STREETS = [(C, 0, "north"), (N-1, C, "east"), (C, N-1, "south"), (0, C, "west")]
def plaza_base(name, slot_pools, seed):
    rng = random.Random(seed); t = Tpl(name, N, 14, N)
    # onregelmatige cirkel (geen vierkante plaat)
    phase = [rng.uniform(0, 6.28) for _ in range(3)]
    def radius(a): return 6.2 + 0.9*math.sin(2*a+phase[0]) + 0.6*math.sin(3*a+phase[1])
    cells = {}
    for x in range(N):
        for z in range(N):
            a = math.atan2(z-C, x-C); d = math.hypot(x-C, z-C)
            if d <= radius(a): cells[(x, z)] = True
    def lane(x, z, f):
        out = []
        for k in range(5):
            xx, zz = {"north": (x, k), "south": (x, N-1-k), "east": (N-1-k, z), "west": (k, z)}[f]
            out.append((xx, zz))
            if f in ("north", "south"): out += [(xx-1, zz), (xx+1, zz)] if (x, z) in [(c[0], c[1]) for c in STREETS] else []
            else: out += [(xx, zz-1), (xx, zz+1)] if (x, z) in [(c[0], c[1]) for c in STREETS] else []
        return out
    for (x, z, f) in SLOTS + STREETS:
        for c in lane(x, z, f): cells[c] = True
    for (x, z) in cells:
        if not (0 <= x < N and 0 <= z < N): continue
        for y in range(0, G): t.set(x, y, z, "dirt")
        t.set(x, G, z, "dirt_path" if rng.random() > .12 else "coarse_dirt")
        for y in range(G+1, 11): t.set(x, y, z, "air")
    for (x, z, f), pool_ in zip(SLOTS, slot_pools): t.jigsaw(x, G, z, f, ENTR, ENTR, pool_)
    for (x, z, f) in STREETS: t.jigsaw(x, G, z, f, STREET, STREET, P("street_first"))
    return t, rng, cells
def bench(t, x, z, face): t.stairs(x, G+1, z, "spruce_stairs", face)
def ring_benches(t, c, rad, n, start=0):
    for k in range(n):
        a = start + k*2*math.pi/n; x = c + round(rad*math.cos(a)); z = c + round(rad*math.sin(a))
        dx, dz = x-c, z-c
        face = ("east" if dx > 0 else "west") if abs(dx) >= abs(dz) else ("south" if dz > 0 else "north")
        bench(t, x, z, face)
def planter(t, x, z, rng):
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            if abs(dx) == 1 or abs(dz) == 1: t.set(x+dx, G+1, z+dz, "dark_oak_planks" if (dx+dz) % 2 else "spruce_planks")
            else: t.set(x, G, z, "podzol")
    t.set(x, G+1, z, rng.choice(FLOWERS))

def plaza_a(pools):
    t, rng, cells = plaza_base("plaza_a", pools, 11); c = C
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
    t.slab(c, G+7, c, "gnomehollow:toadstool_cap_slab")
    t.set(c, G+4, c, "bell", facing="north", attachment="ceiling", powered=False)
    ring_benches(t, c, 4.6, 6, 0.5)
    for (dx, dz) in ((6, -3), (-6, 3)): planter(t, c+dx, c+dz, rng)
    lamp_post(t, c+5, c+5, G+1, 2)
    t.gnome("nitwit", c-3, G+1, c+2, anchor=True); t.gnome("nitwit", c+3, G+1, c+2, anchor=True); t.gnome("nitwit", c, G+1, c+4)
    t.save()
def plaza_b(pools):
    t, rng, cells = plaza_base("plaza_b", pools, 22); c = C
    for x in range(c-2, c+3):
        for z in range(c-2, c+3):
            if max(abs(x-c), abs(z-c)) == 2: t.set(x, G+1, z, "gnomehollow:fieldstone")
            elif max(abs(x-c), abs(z-c)) < 2: t.set(x, G, z, "coarse_dirt")
    t.set(c, G+1, c, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)
    ring_benches(t, c, 4.4, 8, 0.2)
    for x in range(c-3, c+4):
        for z in range(c+5, c+7): t.set(x, G+1, z, "spruce_planks")
    for x in (c-3, c+3):
        for y in range(G+2, G+4): t.set(x, y, c+5, "dark_oak_fence")
    t.set(c-2, G+2, c+6, "note_block"); t.set(c+2, G+2, c+6, "jukebox")
    # bel op een stenen sokkel
    t.set(c+6, G+1, c-2, "gnomehollow:fieldstone"); t.set(c+6, G+2, c-2, "bell", facing="north", attachment="floor", powered=False)
    planter(t, c-6, c-2, rng); lamp_post(t, c-5, c+6, G+1, 2)
    t.gnome("nitwit", c-2, G+2, c+5, anchor=True); t.gnome("nitwit", c+2, G+2, c+5, anchor=True); t.gnome("nitwit", c, G+1, c-3)
    t.save()
def plaza_c(pools):
    t, rng, cells = plaza_base("plaza_c", pools, 33); c = C
    for x in range(N):
        for z in range(N):
            d = math.hypot(x-c, z-c)
            if d <= 3.6:
                for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
                t.set(x, G-3, z, "clay")
                if rng.random() < .12: t.set(x, G+1, z, "lily_pad")
            elif d <= 4.6 and (x, z) in cells:
                t.set(x, G, z, "gnomehollow:fieldstone")
                if (x+z) % 3: t.slab(x, G+1, z, "gnomehollow:fieldstone_slab")
    for x in range(c-1, c+2):
        for z in range(c-1, c+2): t.set(x, G, z, "gnomehollow:fieldstone"); t.set(x, G+1, z, "gnomehollow:fieldstone")
    for y in (G+2, G+3, G+4): t.set(c, y, c, "gnomehollow:plaster")
    t.set(c, G+3, c+1, "white_wool"); t.set(c, G+2, c+1, "white_wool"); t.set(c-1, G+3, c, "dark_oak_fence"); t.set(c+1, G+3, c, "dark_oak_fence")
    t.set(c, G+5, c, "gnomehollow:toadstool_cap"); t.slab(c, G+6, c, "gnomehollow:toadstool_cap_slab")
    for k in range(1, 4): t.set(c, G, c-3-k+0, "dirt_path") if False else None
    for k in range(-3, 0): t.set(c, G, c+k, "spruce_planks")           # bruggetje naar het eiland
    t.set(c+5, G+1, c+1, "gnomehollow:fieldstone"); t.set(c+5, G+2, c+1, "bell", facing="north", attachment="floor", powered=False)
    ring_benches(t, c, 6.0, 5, 0.9)
    planter(t, c-6, c+3, rng); lamp_post(t, c+6, c-5, G+1, 2)
    t.gnome("nitwit", c-4, G+1, c+4, anchor=True); t.gnome("nitwit", c+4, G+1, c+4, anchor=True); t.gnome("healer", c-2, G+1, c+6)
    t.save()

# ====================================================================== DECOR (compact, aan een straat of plein-slot)
def decor_base(name, sx=7, sz=6):
    rng = random.Random(sum(map(ord, name))); t = Tpl(name, sx, 9, sz); H.site(t, rng, 0, sx-1, 0, sz-1, 8)
    cx = (sx-1)//2
    for z in range(sz): t.set(cx, G, z, "dirt_path")
    t.jigsaw(cx, G, sz-1, "south", ENTR, ENTR, "minecraft:empty")
    return t, rng, cx
def build_decor():
    t, rng, cx = decor_base("decor_mushrooms")
    for (mx, mz, h) in ((1, 1, 2), (5, 2, 3), (2, 3, 1)):
        for y in range(G+1, G+1+h): t.set(mx, y, mz, "gnomehollow:gnome_stem")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1): t.slab(mx+dx, G+1+h, mz+dz, "gnomehollow:toadstool_cap_slab")
        t.set(mx, G+1+h, mz, "gnomehollow:toadstool_cap")
    H.scatter if False else scatter(t, rng, 0, 6, 0, 4, .12); t.save()
    t, rng, cx = decor_base("decor_campfire")
    t.set(3, G+1, 2, "campfire", facing="north", lit=True, signal_fire=False, waterlogged=False)
    for (x, z) in ((1, 2), (5, 2), (3, 0)): bench(t, x, z, "south")
    t.set(2, G+1, 3, "cauldron"); scatter(t, rng, 0, 6, 0, 4, .1); t.gnome("nitwit", 4, G+1, 3); t.save()
    t, rng, cx = decor_base("decor_statue")
    for x in range(2, 5):
        for z in range(1, 3): t.set(x, G+1, z, "gnomehollow:fieldstone")
    for y in (G+2, G+3): t.set(3, y, 1, "gnomehollow:plaster")
    t.set(3, G+2, 2, "white_wool"); t.set(3, G+4, 1, "gnomehollow:toadstool_cap"); t.slab(3, G+5, 1, "gnomehollow:toadstool_cap_slab")
    for (x, z) in ((1, 1), (5, 1), (1, 3), (5, 3)): t.set(x, G+1, z, rng.choice(FLOWERS))
    t.save()
    t, rng, cx = decor_base("decor_hives", 7, 6)
    for x in (2, 4): t.set(x, G+1, 1, "dark_oak_fence"); t.set(x, G+2, 1, "beehive", facing="south")
    for x in range(1, 6):
        for z in range(2, 4):
            if x != 3 and rng.random() < .7: t.set(x, G+1, z, rng.choice(["dandelion", "poppy", "cornflower", "azure_bluet", "allium"]))
    t.save()
    t, rng, cx = decor_base("decor_pond")
    for x in range(2, 5):
        for z in range(1, 3):
            for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-3, z, "clay")
            if rng.random() < .3: t.set(x, G+1, z, "lily_pad")
    bench(t, 2, 4, "north"); bench(t, 4, 4, "north"); scatter(t, rng, 0, 6, 0, 5, .12); t.gnome("nitwit", 3, G+1, 4); t.save()
    t, rng, cx = decor_base("decor_hay")
    for (x, z, h) in ((1, 1, 3), (2, 1, 2), (5, 2, 2), (4, 1, 1)):
        for y in range(G+1, G+1+h): t.set(x, y, z, "hay_block", axis="y")
    t.barrel(5, G+1, 1, "farmer"); scatter(t, rng, 0, 6, 0, 4, .1); t.save()

# ====================================================================== POOLS
def pool(name, elements, fallback="minecraft:empty"):
    out = []
    for (tpl, w, proj) in elements:
        if tpl is None: out.append({"weight": w, "element": {"element_type": "minecraft:empty_pool_element"}})
        else: out.append({"weight": w, "element": {"element_type": "minecraft:single_pool_element", "location": f"gnomehollow:village/{tpl}", "processors": "minecraft:empty", "projection": proj}})
    p = f"{OUT}/worldgen/template_pool/village/{name}.json"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"fallback": fallback, "elements": out}, open(p, "w"), indent=2)

HOUSES = [("house_cottage_thatch", 2), ("house_cottage_cap", 1), ("house_cottage_small", 2), ("house_cottage_shingle", 1), ("house_cottage_log", 1),
          ("house_twostory", 1), ("house_burrow", 1), ("house_mushroom", 1),
          ("house_healer_a", 2), ("house_healer_b", 2), ("house_warrior_a", 2), ("house_warrior_b", 2), ("house_farmer_a", 2), ("house_farmer_b", 2),
          ("house_fisherman_a", 2), ("house_fisherman_b", 2), ("house_builder_a", 2), ("house_builder_b", 2)]
DECOR = ["decor_mushrooms", "decor_campfire", "decor_statue", "decor_hives", "decor_pond", "decor_hay"]
def build_pools():
    R, M = "rigid", "terrain_matching"
    pool("town_centers", [("plaza_a", 1, R), ("plaza_b", 1, R), ("plaza_c", 1, R)])
    pool("street_first", [("street_plain_12", 1, M)])
    pool("streets", [("street_straight_10", 4, M), ("street_straight_14", 3, M), ("street_corner", 4, M), ("street_t", 3, M), ("street_cross", 1, M), ("street_end", 3, M)], fallback=P("street_ends"))
    pool("street_ends", [("street_end", 1, M)])
    pool("market", [("house_market", 1, R)]); pool("library", [("house_library", 1, R)]); pool("garden", [("house_garden", 1, R)])
    pool("houses", [(n, w, R) for n, w in HOUSES] + [(d, 1, R) for d in DECOR] + [(None, 3, R)])
    pool("slot_houses", [(n, w, R) for n, w in HOUSES] + [(d, 1, R) for d in DECOR] + [(None, 3, R)])

# ====================================================================== LOOT (veel variatie; per beroep relevant)
def loot(name, rolls, entries, rare=()):
    def mk(es):
        ents = []
        for e in es:
            item, w = e[0], e[1]; cnt = e[2] if len(e) > 2 else None; extra = e[3] if len(e) > 3 else None
            d = {"type": "minecraft:item", "name": item if ":" in item else f"minecraft:{item}", "weight": w}
            fn = []
            if cnt: fn.append({"function": "minecraft:set_count", "count": {"min": cnt[0], "max": cnt[1]}})
            if extra: fn.append(extra)
            if fn: d["functions"] = fn
            ents.append(d)
        return ents
    pools = [{"rolls": {"min": rolls[0], "max": rolls[1]}, "entries": mk(entries)}]
    if rare: pools.append({"rolls": {"min": 0, "max": 1}, "bonus_rolls": 0.0, "entries": mk(rare) + [{"type": "minecraft:empty", "weight": 12}]})
    p = f"{OUT}/loot_table/chests/{name}.json"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"type": "minecraft:chest", "pools": pools}, open(p, "w"), indent=2)
def potion(i): return {"function": "minecraft:set_potion", "id": f"minecraft:{i}"}
def build_loot():
    common = [("bread", 10, (1, 4)), ("apple", 8, (1, 4)), ("carrot", 6, (2, 6)), ("baked_potato", 6, (1, 4)), ("sweet_berries", 6, (2, 7)), ("red_mushroom", 5, (1, 4)),
              ("brown_mushroom", 5, (1, 4)), ("cookie", 5, (2, 8)), ("honey_bottle", 3, (1, 2)), ("candle", 3, (1, 3)), ("book", 2, (1, 2)), ("emerald", 3, (1, 2)),
              ("lantern", 2, (1, 1)), ("rabbit_stew", 1, (1, 1)), ("milk_bucket", 1, (1, 1)), ("flower_pot", 2, (1, 2)), ("string", 3, (1, 3))]
    rare = [("golden_apple", 2, (1, 1)), ("emerald", 4, (2, 5)), ("name_tag", 2, (1, 1)), ("diamond", 1, (1, 1)), ("gnomehollow:toadstool_lamp", 3, (1, 3))]
    loot("pantry", (2, 6), common, rare)
    loot("market", (3, 8), common + [("cod", 4, (1, 3)), ("glow_berries", 4, (2, 5)), ("wheat", 4, (2, 6)), ("gnomehollow:thatch", 3, (2, 6)), ("gnomehollow:plaster", 3, (2, 6)),
                                      ("bucket", 1, (1, 1)), ("shears", 1, (1, 1))], rare)
    loot("library", (3, 7), [("book", 10, (1, 4)), ("paper", 8, (2, 8)), ("ink_sac", 5, (1, 3)), ("feather", 5, (1, 4)), ("candle", 4, (1, 3)), ("name_tag", 1, (1, 1)),
                              ("map", 1, (1, 1)), ("compass", 1, (1, 1)), ("clock", 1, (1, 1)), ("glow_ink_sac", 1, (1, 1))], [("enchanted_book", 3, (1, 1)), ("emerald", 3, (1, 4)), ("experience_bottle", 2, (1, 2))])
    loot("healer", (3, 6), [("potion", 6, (1, 1), potion("healing")), ("potion", 5, (1, 1), potion("regeneration")), ("potion", 3, (1, 1), potion("swiftness")),
        ("potion", 2, (1, 1), potion("night_vision")), ("potion", 2, (1, 1), potion("water_breathing")), ("glass_bottle", 8, (1, 3)), ("glow_berries", 6, (2, 5)),
        ("spider_eye", 4, (1, 2)), ("golden_carrot", 4, (1, 3)), ("red_mushroom", 5, (2, 4)), ("emerald", 3, (1, 2)), ("honey_bottle", 3, (1, 2)), ("nether_wart", 2, (1, 3)),
        ("redstone", 3, (1, 4)), ("sugar", 3, (1, 3))], [("golden_apple", 2, (1, 1)), ("potion", 2, (1, 1), potion("strong_healing")), ("experience_bottle", 2, (1, 3))])
    loot("warrior", (3, 6), [("iron_sword", 2, (1, 1)), ("arrow", 10, (4, 14)), ("bow", 2, (1, 1)), ("shield", 2, (1, 1)), ("iron_nugget", 8, (3, 9)), ("iron_ingot", 4, (1, 3)),
        ("bread", 8, (1, 3)), ("cooked_beef", 5, (1, 3)), ("bone", 5, (1, 3)), ("leather", 5, (1, 3)), ("golden_carrot", 3, (1, 2)), ("emerald", 3, (1, 2)),
        ("chainmail_boots", 1, (1, 1)), ("stick", 4, (2, 6)), ("flint", 4, (2, 6)), ("crossbow", 1, (1, 1))], [("iron_chestplate", 2, (1, 1)), ("iron_helmet", 2, (1, 1)), ("diamond", 1, (1, 1))])
    loot("farmer", (3, 7), [("wheat", 10, (3, 9)), ("wheat_seeds", 10, (3, 9)), ("carrot", 8, (2, 6)), ("potato", 8, (2, 6)), ("beetroot", 6, (2, 5)), ("beetroot_seeds", 5, (2, 6)),
        ("bread", 8, (1, 4)), ("hay_block", 3, (1, 2)), ("bone_meal", 8, (2, 7)), ("pumpkin_pie", 3, (1, 2)), ("melon_slice", 4, (2, 6)), ("pumpkin_seeds", 4, (2, 5)),
        ("emerald", 3, (1, 2)), ("gnomehollow:thatch", 3, (2, 6)), ("egg", 4, (1, 4)), ("leather", 2, (1, 2))], [("golden_carrot", 3, (1, 3)), ("cake", 2, (1, 1)), ("emerald", 3, (2, 4))])
    loot("fisher", (3, 7), [("cod", 10, (1, 5)), ("salmon", 8, (1, 4)), ("cooked_cod", 6, (1, 4)), ("cooked_salmon", 5, (1, 3)), ("string", 8, (2, 7)), ("fishing_rod", 2, (1, 1)),
        ("pufferfish", 2, (1, 1)), ("tropical_fish", 2, (1, 2)), ("lily_pad", 5, (1, 4)), ("ink_sac", 3, (1, 2)), ("emerald", 3, (1, 2)), ("kelp", 4, (2, 6)),
        ("bucket", 1, (1, 1)), ("stick", 3, (2, 5)), ("bowl", 3, (1, 3))], [("nautilus_shell", 3, (1, 1)), ("name_tag", 2, (1, 1)), ("emerald", 3, (2, 4))])
    loot("builder", (3, 7), [("stone_bricks", 8, (4, 12)), ("cobblestone", 8, (6, 16)), ("spruce_planks", 8, (6, 16)), ("clay_ball", 6, (4, 10)), ("brick", 5, (2, 8)),
        ("iron_nugget", 5, (2, 6)), ("copper_ingot", 4, (2, 5)), ("lantern", 4, (1, 2)), ("glass", 6, (2, 6)), ("gnomehollow:plaster", 6, (4, 8)), ("gnomehollow:thatch", 5, (4, 8)),
        ("gnomehollow:fieldstone", 5, (4, 8)), ("gnomehollow:gnome_shingles", 4, (3, 6)), ("gnomehollow:timber_plaster", 3, (2, 5)), ("emerald", 3, (1, 2)),
        ("stick", 4, (2, 6)), ("dark_oak_planks", 4, (3, 8)), ("scaffolding", 2, (1, 4))], [("shears", 2, (1, 1)), ("iron_pickaxe", 1, (1, 1)), ("emerald", 3, (2, 4))])
    loot("nitwit", (3, 6), [("cookie", 10, (2, 8)), ("firework_rocket", 6, (1, 3)), ("note_block", 3, (1, 1)), ("poppy", 8, (2, 5)), ("dandelion", 8, (2, 5)), ("gold_nugget", 5, (2, 6)),
        ("honey_bottle", 3, (1, 2)), ("emerald", 4, (1, 3)), ("sweet_berries", 5, (2, 6)), ("gnomehollow:timber_plaster", 3, (2, 5)), ("bell", 1, (1, 1)), ("lead", 2, (1, 2)),
        ("cake", 1, (1, 1)), ("pumpkin_pie", 2, (1, 2))], [("music_disc_13", 1, (1, 1)), ("golden_apple", 1, (1, 1)), ("name_tag", 2, (1, 1))])

# ====================================================================== WORLDGEN
def build_worldgen():
    def wj(rel, obj):
        p = f"{OUT}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True); json.dump(obj, open(p, "w"), indent=2)
    wj("worldgen/structure/gnome_village.json", {
        "type": "minecraft:jigsaw", "biomes": "#gnomehollow:has_structure/gnome_village", "step": "surface_structures", "spawn_overrides": {},
        "terrain_adaptation": "beard_thin", "start_pool": P("town_centers"), "size": 5,
        "start_height": {"absolute": -G}, "project_start_to_heightmap": "WORLD_SURFACE_WG", "max_distance_from_center": 40, "use_expansion_hack": False})
    wj("worldgen/structure_set/gnome_villages.json", {"structures": [{"structure": "gnomehollow:gnome_village", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": 40, "separation": 18, "salt": 1827364509,
                      "exclusion_zone": {"other_set": "minecraft:villages", "chunk_count": 10}}})
    wj("tags/worldgen/biome/has_structure/gnome_village.json", {"replace": False, "values": [
        "minecraft:dark_forest", "minecraft:taiga", "minecraft:old_growth_pine_taiga", "minecraft:old_growth_spruce_taiga"]})

# ====================================================================== RUN
build_streets(); H.all_houses()
sp = lambda n: P(n)
plaza_a([sp("market"), sp("slot_houses"), sp("slot_houses"), sp("library"), sp("slot_houses"), sp("garden"), sp("slot_houses"), sp("slot_houses")])
plaza_b([sp("slot_houses"), sp("garden"), sp("slot_houses"), sp("market"), sp("library"), sp("slot_houses"), sp("slot_houses"), sp("slot_houses")])
plaza_c([sp("library"), sp("slot_houses"), sp("market"), sp("slot_houses"), sp("slot_houses"), sp("slot_houses"), sp("garden"), sp("slot_houses")])
build_decor(); build_pools(); build_loot(); build_worldgen()
for name, t in REGISTRY.items():
    if not os.path.exists(f"{OUT}/structure/village/{name}.nbt"): t.save()
print(len(REGISTRY), "templates opgeslagen")
