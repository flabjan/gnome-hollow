import gzip, struct, json, os, math, random

ROOT = "/home/claude/gnome-hollow/src/main/resources/data/gnomehollow"
DATA_VERSION = 4671   # 1.21.11 -- Minecraft's datafixers tillen oudere data automatisch naar 26.2

# ---------------------------------------------------------------- minimal NBT writer
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
            if isinstance(val, L): t = 9
            else: t = TID[type(val)]
            buf += struct.pack(">b", t)
            e = k.encode(); buf += struct.pack(">H", len(e)) + e
            w_payload(buf, val)
        buf += b"\x00"
    else: raise TypeError(type(v))

def write_nbt(path, root):
    buf = bytearray(b"\x0a\x00\x00")
    w_payload(buf, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.GzipFile(path, "wb", mtime=0) as f: f.write(bytes(buf))

# ---------------------------------------------------------------- template builder
class Tpl:
    def __init__(self, sx, sy, sz):
        self.size = (sx, sy, sz); self.blocks = {}; self.ents = []
    def set(self, x, y, z, name, nbt=None, **props):
        if not (0 <= x < self.size[0] and 0 <= y < self.size[1] and 0 <= z < self.size[2]): return
        if not name.startswith("gnomehollow:") and ":" not in name: name = "minecraft:" + name
        elif ":" not in name: name = "minecraft:" + name
        self.blocks[(x,y,z)] = (name, tuple(sorted((k, str(v).lower() if isinstance(v,bool) else str(v)) for k,v in props.items())), nbt)
    def fill(self, x1,y1,z1,x2,y2,z2, name, **props):
        for x in range(x1,x2+1):
            for y in range(y1,y2+1):
                for z in range(z1,z2+1): self.set(x,y,z,name,**props)
    def gnome(self, prof, x, y, z):
        self.ents.append((x, y, z, f"gnomehollow:gnome_{prof}"))
    def save(self, rel):
        palette, index, blocks = [], {}, []
        for (x,y,z), (name, props, nbt) in sorted(self.blocks.items(), key=lambda kv: (kv[0][1], kv[0][2], kv[0][0])):
            key = (name, props, bool(nbt) and nbt.get("id") == "minecraft:jigsaw")
            k2 = (name, props)
            if k2 not in index:
                index[k2] = len(palette)
                e = {"Name": S(name)}
                if props: e["Properties"] = {k: S(v) for k, v in props}
                palette.append(e)
            b = {"pos": L(3,[I(x),I(y),I(z)]), "state": I(index[k2])}
            if nbt: b["nbt"] = nbt
            blocks.append(b)
        ents = []
        for (x,y,z,eid) in self.ents:
            ents.append({"pos": L(6,[D(x+0.5),D(y),D(z+0.5)]), "blockPos": L(3,[I(x),I(y),I(z)]),
                         "nbt": {"id": S(eid), "PersistenceRequired": B(1)}})
        root = {"DataVersion": I(DATA_VERSION), "size": L(3,[I(v) for v in self.size]),
                "palette": L(10, palette), "blocks": L(10, blocks), "entities": L(10, ents)}
        write_nbt(f"{ROOT}/structure/{rel}.nbt", root)
        print(rel, self.size, len(self.blocks), "blocks", len(self.ents), "entities")

def jigsaw(t, x, y, z, orient, name, target, pool, final="minecraft:dirt_path"):
    t.set(x, y, z, "jigsaw", orientation=orient,
          nbt={"id": S("minecraft:jigsaw"), "name": S(name), "target": S(target), "pool": S(pool),
               "final_state": S(final), "joint": S("aligned")})

G = 3  # ground layer index inside every template
FLOWERS = ["poppy","azure_bluet","lily_of_the_valley","cornflower","blue_orchid","allium","dandelion"]

def ground(t, rng, path_fn=None, flower_zone=None):
    sx, sy, sz = t.size
    t.fill(0,0,0,sx-1,G-1,sz-1,"dirt")
    for x in range(sx):
        for z in range(sz):
            t.set(x,G,z,"podzol" if rng.random() < 0.35 else "grass_block")
    t.fill(0,G+1,0,sx-1,sy-1,sz-1,"air")
    if path_fn:
        for x in range(sx):
            for z in range(sz):
                r = path_fn(x, z)
                if r: t.set(x,G,z, r)

# ================================================================= PLAZA (21 x 11 x 21)
def make_plaza():
    rng = random.Random(1001)
    t = Tpl(21, 11, 21)
    def path(x, z):
        d = math.hypot(x-10, z-10)
        if d <= 8.2: return "coarse_dirt" if rng.random() < 0.12 else "dirt_path"
        if abs(x-10) <= 1 and (z <= 2 or z >= 18): return "dirt_path"
        return None
    ground(t, rng, path)
    # connector lanes (so the jigsaw cell always sits on a path)
    for x in (5, 15):
        for z in range(0, 4): t.set(x, G, z, "dirt_path"); t.set(x, G, 20-z, "dirt_path")
    for x in range(0, 4): t.set(x, G, 10, "dirt_path"); t.set(20-x, G, 10, "dirt_path")
    # well
    for x in range(9, 12):
        for z in range(9, 12):
            if (x, z) == (10, 10):
                for y in (1, 2, G): t.set(x, y, z, "water", level=0)
            else:
                for y in (1, 2, G): t.set(x, y, z, "mossy_stone_bricks")
                t.set(x, G+1, z, "mossy_cobblestone_wall")
    for (x, z) in ((9,9),(11,9),(9,11),(11,11)):
        t.set(x, G+1, z, "spruce_fence"); t.set(x, G+2, z, "spruce_fence"); t.set(x, G+3, z, "spruce_fence")
    # toadstool cap over the well
    for x in range(8, 13):
        for z in range(8, 13):
            if (x in (8,12)) and (z in (8,12)): continue
            t.set(x, G+4, z, "red_mushroom_block", up="true", down="true", north="true", south="true", east="true", west="true")
    for x in range(9, 12):
        for z in range(9, 12):
            t.set(x, G+5, z, "red_mushroom_block", up="true", down="true", north="true", south="true", east="true", west="true")
    t.set(10, G+6, 10, "red_mushroom_block", up="true", down="true", north="true", south="true", east="true", west="true")
    # lamp posts with toadstool lamps
    for (x, z) in ((4,4),(16,4),(4,16),(16,16),(10,3),(10,17)):
        t.set(x, G+1, z, "spruce_fence"); t.set(x, G+2, z, "spruce_fence"); t.set(x, G+3, z, "gnomehollow:toadstool_lamp")
    # stump seats for the nitwit band
    for (x, z) in ((7,14),(13,14),(10,16)):
        t.set(x, G+1, z, "stripped_spruce_log", axis="y")
    # flowers and mushrooms on the grass ring
    for x in range(21):
        for z in range(21):
            if math.hypot(x-10, z-10) > 8.8 and (x, z) not in ((5,0),(15,0),(5,20),(15,20),(0,10),(20,10)) and rng.random() < 0.10:
                if t.blocks.get((x,G,z), ("",))[0] in ("minecraft:grass_block","minecraft:podzol"):
                    t.set(x, G+1, z, rng.choice(FLOWERS + ["red_mushroom","brown_mushroom","fern"]))
    for g in ((8,G+1,13),(12,G+1,13),(10,G+1,17)): t.gnome("nitwit", *g)
    # connectors
    jigsaw(t, 5, G, 0,  "north_up", "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/healers")
    jigsaw(t, 15, G, 0, "north_up", "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/warriors")
    jigsaw(t, 5, G, 20, "south_up", "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/farmers")
    jigsaw(t, 15, G, 20,"south_up", "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/builders")
    jigsaw(t, 0, G, 10, "west_up",  "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/fishermen")
    jigsaw(t, 20, G, 10,"east_up",  "gnomehollow:plaza", "gnomehollow:door", "gnomehollow:village/extras")
    t.save("village/plaza")

# ================================================================= HOUSES (9 x 14 x 14), door faces +z
def shell(t, rng, bed_color):
    # ground + foundation + clear volume
    ground(t, rng, lambda x, z: "dirt_path" if (3 <= x <= 5 and z >= 8) else None)
    # hill (hobbit style) with red gnome-hat tip
    for x in range(0, 9):
        for z in range(0, 7):
            d = math.sqrt(((x-4)/4.7)**2 + ((z-3.0)/3.9)**2)
            if d > 1.0: continue
            top = 7 + int((1.0 - d) * 4.2)
            for y in range(G+1, top+1):
                if y == top:
                    t.set(x, y, z, "gnomehollow:gnome_shingles" if top >= 10 else ("podzol" if rng.random() < .3 else "grass_block"))
                else:
                    t.set(x, y, z, "dirt")
            if top < 10 and rng.random() < 0.18:
                t.set(x, top+1, z, rng.choice(["red_mushroom","brown_mushroom","fern"]))
    # interior 5x5 (x2..6, z2..6), 3 high; plank lining, floor, ceiling
    for x in range(1, 8):
        for z in range(1, 8):
            inside = 2 <= x <= 6 and 2 <= z <= 6
            for y in range(G+1, G+4):
                t.set(x, y, z, "air" if inside else "spruce_planks")
            t.set(x, G, z, "spruce_planks")
            t.set(x, G+4, z, "spruce_planks")
    # corner posts
    for (x, z) in ((1,1),(7,1),(1,7),(7,7)):
        for y in range(G+1, G+4): t.set(x, y, z, "stripped_spruce_log", axis="y")
    # facade (z=7): door + round-ish windows
    for x in range(1, 8):
        for y in range(G+1, G+4):
            if x in (1, 7): continue
            t.set(x, y, 7, "spruce_planks")
    t.set(4, G+1, 7, "spruce_door", facing="south", half="lower", hinge="left", open="false", powered="false")
    t.set(4, G+2, 7, "spruce_door", facing="south", half="upper", hinge="left", open="false", powered="false")
    t.set(4, G+3, 7, "spruce_planks")
    for x in (2, 6): t.set(x, G+2, 7, "glass_pane", east="true", west="true")
    # shingle awning over the door + hanging lantern
    for x in (3, 4, 5): t.set(x, G+4, 8, "gnomehollow:gnome_shingle_slab", type="bottom")
    t.set(4, G+3, 8, "lantern", hanging="true")
    t.set(4, G+3, 6, "air"); 
    # ceiling lamp, bed
    t.set(4, G+3, 4, "gnomehollow:toadstool_lamp")
    t.set(6, G+1, 2, bed_color, facing="south", part="foot", occupied="false")
    t.set(6, G+1, 3, bed_color, facing="south", part="head", occupied="false")
    # front step lanes
    for x in (3, 4, 5):
        for z in range(8, 14): t.set(x, G, z, "dirt_path")
    # plant a few things around the yard
    for x in range(0, 9):
        for z in range(8, 13):
            if t.blocks.get((x,G,z), ("",))[0] in ("minecraft:grass_block","minecraft:podzol") and (x,G+1,z) not in t.blocks and rng.random() < 0.07:
                t.set(x, G+1, z, rng.choice(FLOWERS + ["red_mushroom","fern"]))

def finish_house(t, prof_name, kind_pool_name):
    jigsaw(t, 4, G, 13, "south_up", "gnomehollow:door", "gnomehollow:plaza", "minecraft:empty")

def make_healer():
    rng = random.Random(11); t = Tpl(9, 14, 14); shell(t, rng, "green_bed")
    t.set(3, G+1, 2, "brewing_stand"); t.set(4, G+1, 2, "brewing_stand")
    t.set(2, G+1, 2, "water_cauldron", level=3)
    t.set(5, G+1, 2, "chest", facing="south", type="single")
    t.set(2, G+1, 3, "lectern", facing="east"); 
    for x in (2, 5): t.set(x, G+2, 2, "potted_lily_of_the_valley") if False else None
    # herb garden in the yard
    for x in (1, 2, 6, 7):
        for z in (9, 10, 11):
            t.set(x, G, z, "podzol"); t.set(x, G+1, z, rng.choice(["lily_of_the_valley","azure_bluet","cornflower","allium","brown_mushroom","fern"]))
    t.gnome("healer", 4, G+1, 4)
    finish_house(t, "healer", ""); t.save("village/house_healer")

def make_warrior():
    rng = random.Random(12); t = Tpl(9, 14, 14); shell(t, rng, "red_bed")
    t.set(3, G+1, 2, "grindstone", face="floor", facing="north")
    t.set(4, G+1, 2, "anvil", facing="east")
    t.set(5, G+1, 2, "barrel", facing="up", open="false")
    t.set(2, G+1, 3, "barrel", facing="up", open="false")
    # training yard: hay-bale dummies with target blocks, banners
    for (x, z) in ((1, 10), (7, 10), (1, 12), (7, 12)):
        t.set(x, G+1, z, "hay_bale", axis="y"); t.set(x, G+2, z, "target")
    for (x, z) in ((2, 8), (6, 8)):
        t.set(x, G+1, z, "spruce_fence"); t.set(x, G+2, z, "spruce_fence"); t.set(x, G+3, z, "red_banner", rotation=0)
    t.gnome("warrior", 4, G+1, 4); t.gnome("warrior", 4, G+1, 11)
    finish_house(t, "warrior", ""); t.save("village/house_warrior")

def make_farmer():
    rng = random.Random(13); t = Tpl(9, 14, 14); shell(t, rng, "lime_bed")
    t.set(3, G+1, 2, "composter", level=0)
    t.set(4, G+1, 2, "barrel", facing="up", open="false")
    t.set(5, G+1, 2, "hay_bale", axis="y")
    t.set(2, G+1, 3, "chest", facing="east", type="single")
    crops = [("wheat", 7), ("carrots", 7), ("potatoes", 7), ("wheat", 7)]
    for plot_x, water_x in ((0, 1), (6, 7)):
        for x in range(plot_x, plot_x + 3):
            for z in range(9, 13):
                if (x, z) == (water_x, 10):
                    t.set(x, G, z, "water", level=0); continue
                t.set(x, G, z, "farmland", moisture=7)
                name, age = crops[(x + z) % len(crops)]
                t.set(x, G+1, z, name, age=age)
    t.gnome("farmer", 4, G+1, 4); t.gnome("farmer", 4, G+1, 10)
    finish_house(t, "farmer", ""); t.save("village/house_farmer")

def make_fisherman():
    rng = random.Random(14); t = Tpl(9, 14, 14); shell(t, rng, "blue_bed")
    t.set(3, G+1, 2, "barrel", facing="up", open="false")
    t.set(4, G+1, 2, "barrel", facing="up", open="false")
    t.set(5, G+1, 2, "water_cauldron", level=3)
    t.set(2, G+1, 3, "chest", facing="east", type="single")
    # pond with dock
    for x in range(6, 9):
        for z in range(9, 13):
            for y in (1, 2, G): t.set(x, y, z, "water", level=0)
        for z in range(9, 13): t.set(x, 0, z, "clay")
    for x in range(5, 9):
        for z in range(8, 14):
            if x == 5 or z in (8, 13): pass
    t.set(6, G, 10, "spruce_planks"); t.set(6, G, 11, "spruce_planks")
    t.set(5, G+1, 10, "lantern", hanging="false")
    t.set(5, G, 10, "spruce_planks"); t.set(5, G, 11, "spruce_planks")
    for z in (9, 12): t.set(5, G+1, z, "spruce_fence")
    t.gnome("fisherman", 4, G+1, 4); t.gnome("fisherman", 5, G+1, 11)
    finish_house(t, "fisherman", ""); t.save("village/house_fisherman")

def make_builder():
    rng = random.Random(15); t = Tpl(9, 14, 14); shell(t, rng, "orange_bed")
    t.set(3, G+1, 2, "stonecutter", facing="north")
    t.set(4, G+1, 2, "crafting_table")
    t.set(5, G+1, 2, "anvil", facing="east")
    t.set(2, G+1, 3, "chest", facing="east", type="single")
    # building site: scaffolding, stone and log piles
    for y in range(G+1, G+5):
        t.set(7, y, 10, "scaffolding", bottom="false" if y > G+1 else "true", distance=0, waterlogged="false")
    t.fill(1, G+1, 10, 2, G+1, 11, "stone_bricks"); t.set(1, G+2, 10, "stone_bricks")
    t.fill(6, G+1, 12, 7, G+1, 12, "stripped_spruce_log", axis="x"); t.set(6, G+2, 12, "stripped_spruce_log", axis="x")
    t.set(1, G+1, 12, "cobblestone"); t.set(2, G+1, 12, "mossy_cobblestone")
    t.gnome("builder", 4, G+1, 4); t.gnome("builder", 4, G+1, 11)
    finish_house(t, "builder", ""); t.save("village/house_builder")

def make_nitwit():
    rng = random.Random(16); t = Tpl(9, 14, 14); shell(t, rng, "purple_bed")
    t.set(4, G+1, 2, "note_block"); t.set(3, G+1, 2, "jukebox"); t.set(5, G+1, 2, "barrel", facing="up", open="false")
    for (x, z) in ((2, 10), (6, 10)): t.set(x, G+1, z, "stripped_spruce_log", axis="y")
    t.gnome("nitwit", 4, G+1, 4); t.gnome("nitwit", 4, G+1, 10)
    finish_house(t, "nitwit", ""); t.save("village/house_nitwit")

make_plaza(); make_healer(); make_warrior(); make_farmer(); make_fisherman(); make_builder(); make_nitwit()

# ---------------------------------------------------------------- JSON worldgen
def wjson(rel, obj):
    p = f"{ROOT}/{rel}"; os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(obj, open(p, "w"), indent=2)

def pool(name, template):
    wjson(f"worldgen/template_pool/village/{name}.json", {
        "fallback": "minecraft:empty",
        "elements": [{"weight": 1, "element": {"element_type": "minecraft:single_pool_element",
            "location": f"gnomehollow:village/{template}", "processors": "minecraft:empty", "projection": "rigid"}}]})
pool("plaza", "plaza"); pool("healers", "house_healer"); pool("warriors", "house_warrior"); pool("farmers", "house_farmer")
pool("builders", "house_builder"); pool("fishermen", "house_fisherman"); pool("extras", "house_nitwit")

wjson("worldgen/structure/gnome_village.json", {
    "type": "minecraft:jigsaw",
    "biomes": "#gnomehollow:has_structure/gnome_village",
    "step": "surface_structures",
    "spawn_overrides": {},
    "terrain_adaptation": "beard_thin",
    "start_pool": "gnomehollow:village/plaza",
    "size": 2,
    "start_height": {"absolute": -3},
    "project_start_to_heightmap": "WORLD_SURFACE_WG",
    "max_distance_from_center": 80,
    "use_expansion_hack": False})
wjson("worldgen/structure_set/gnome_villages.json", {
    "structures": [{"structure": "gnomehollow:gnome_village", "weight": 1}],
    "placement": {"type": "minecraft:random_spread", "spacing": 28, "separation": 10, "salt": 1827364509}})
wjson("tags/worldgen/biome/has_structure/gnome_village.json", {"replace": False, "values": [
    "minecraft:dark_forest", "minecraft:taiga", "minecraft:old_growth_pine_taiga", "minecraft:old_growth_spruce_taiga"]})
print("structures ok")
