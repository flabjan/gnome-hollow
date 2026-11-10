from structlib import *
import random, math

FS = "gnomehollow:fieldstone"; PL = "gnomehollow:plaster"; TP = "gnomehollow:timber_plaster"
LAMP = "gnomehollow:toadstool_lamp"

def new_rng(name): return random.Random(sum(ord(c)*(i+7) for i, c in enumerate(name)))

# ------------------------------------------------------------------ kern: cottage
def cottage(name, W, D, floors=1, wall="plaster", roof="thatch", ridge="x", chim="r", porch=True, bed="red", nitwits=1, loot="pantry"):
    rng = new_rng(name)
    sx, sz = W+2, D+5
    span = (D if ridge == "x" else W) + 2
    wall_top = G + 4*floors - 1; yb = wall_top + 1
    sy = yb + span//2 + 6
    t = Tpl(name, sx, sy, sz); ground(t, rng)
    x0, x1, z0, z1 = 1, W, 1, D; cx = (sx-1)//2
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            t.set(x, G-1, z, FS); t.set(x, G-2, z, FS)
    for y in range(G, wall_top+1):
        for x in range(x0, x1+1):
            for z in range(z0, z1+1):
                ring = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
                floorline = y > G and (y-G) % 4 == 0
                if not ring:
                    t.set(x, y, z, "spruce_planks" if (y == G or floorline) else "air"); continue
                if y <= G+1: b = FS
                elif floorline or (y-G) % 4 == 3: b = "dark_oak_planks" if not (wall == "stone" and not floorline) else FS
                elif wall == "plaster": b = "dark_oak_log" if corner else PL
                elif wall == "timber": b = "dark_oak_log" if corner else TP
                elif wall == "log": b = "stripped_spruce_log" if corner else "spruce_log"
                else: b = "stripped_spruce_log" if corner else FS
                if b.endswith("_log"): t.set(x, y, z, b, axis="y")
                else: t.set(x, y, z, b)
    # deur, trap, windows
    t.set(cx, G, z1, "spruce_planks")
    t.door(cx, G+1, z1, "spruce_door", "south"); t.set(cx, G+3, z1, "dark_oak_planks")
    t.slab(cx, G, z1+1, "gnomehollow:fieldstone_slab")
    for f in range(floors):
        wy = G + 2 + 4*f
        for wx in (cx-2, cx+2):
            if x0+1 <= wx <= x1-1: t.pane(wx, wy, z1, "x")
        if x0+1 <= cx <= x1-1: t.pane(cx, wy, z0, "x")
        zm = (z0+z1)//2
        t.pane(x0, wy, zm, "z"); t.pane(x1, wy, zm, "z")
    # tweede verdieping: ladder
    if floors == 2:
        t.set(cx, G+4, z0+1, "air")
        for y in range(G+1, G+6): t.set(cx, y, z0+1, "ladder", facing="south", waterlogged=False)
    # dak
    fill = TP if wall == "timber" else PL
    if wall == "stone": fill = FS
    if wall == "log": fill = "spruce_planks"
    top = gable_roof(t, (x0 if ridge == "x" else z0), (x1 if ridge == "x" else z1), (z0 if ridge == "x" else x0), (z1 if ridge == "x" else x1), yb, ridge, roof, fill)
    if ridge == "z":   # raampje in de voorgevel
        t.pane(cx, yb+1, z1, "x")
    # schoorsteen
    if chim:
        chx = x1 if chim == "r" else x0-1
        chimney(t, chx, z0+2, G+1, top+1)
        ix = x1-1 if chim == "r" else x0+1
        t.set(ix, G+1, z0+2, "furnace", facing="west" if chim == "r" else "east", lit=False)
        t.set(ix, G+1, z0+3, "campfire" if False else "lantern", hanging=False)
    # veranda
    if porch:
        for dx in (-1, 1):
            for dy in (1, 2): t.set(cx+dx, G+dy, z1+1, "dark_oak_fence")
        for dx in (-1, 0, 1): t.slab(cx+dx, G+3, z1+1, ROOFS[roof]["slab"])
        t.set(cx+2, G+1, z1+1, "dark_oak_fence"); t.set(cx+2, G+2, z1+1, "lantern", hanging=False)
    # tuin + pad
    for z in range(z1+1, sz):
        t.set(cx, G, z, "dirt_path")
    for z in range(z1+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path" if rng.random() < .7 else "coarse_dirt")
    scatter(t, rng, 0, sx-1, z1+1, sz-2, .12); scatter(t, rng, 0, sx-1, 0, z1+1, .10)
    g = dict(t=t, rng=rng, x0=x0, x1=x1, z0=z0, z1=z1, cx=cx, wall_top=wall_top, yb=yb, floors=floors, sx=sx, sz=sz, top=top, W=W, D=D)
    furnish(t, g, bed, loot)
    for k in range(nitwits): t.gnome("nitwit", cx+(-1 if k % 2 else 1)*(1+k//2), G+1, z0+3+k)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return g

def furnish(t, g, bed, loot):
    x0, x1, z0, z1, cx, wt = g["x0"], g["x1"], g["z0"], g["z1"], g["cx"], g["wall_top"]
    xi0, xi1, zi0, zi1 = x0+1, x1-1, z0+1, z1-1
    t.bed(xi0, G+1, zi0, bed, "south")
    if g["W"] >= 9: t.bed(xi0+1, G+1, zi0, bed, "south")
    tz = (zi0+zi1)//2 + 1
    t.set(cx, G+1, tz, "dark_oak_fence"); t.set(cx, G+2, tz, "spruce_pressure_plate")
    t.stairs(cx-1, G+1, tz, "spruce_stairs", "west"); t.stairs(cx+1, G+1, tz, "spruce_stairs", "east")
    for z in range(tz-1, tz+2):
        for x in range(cx-1, cx+2):
            if t.get(x, G+1, z) in (None, "air"): t.set(x, G+1, z, "red_carpet")
    t.set(xi1, G+1, zi0, "bookshelf"); t.set(xi1, G+2, zi0, "bookshelf"); t.set(xi1-1, G+1, zi0, "bookshelf")
    t.chest(xi1, G+1, zi1, "west", loot)
    t.set(xi1, G+1, zi1-1, "potted_red_mushroom")
    t.set(xi0, wt, zi1, LAMP); t.set(xi1, wt, zi0+1, LAMP)
    if g["floors"] == 2:
        t.bed(xi0, G+5, zi0, "white", "south"); t.chest(xi1, G+5, zi1, "west", loot)
        t.set(xi0, G+7, zi1, LAMP)

# ------------------------------------------------------------------ heuvelhuis (hobbit-stijl)
def burrow(name, farm=False, shop=None, nitwits=1, bed="green", loot="pantry"):
    rng = new_rng(name)
    sx, sz = 11, 14; t = Tpl(name, sx, 16, sz); ground(t, rng)
    cx = 5; zc = 4.5; rx, rz = 5.2, 4.3
    top = {}
    for x in range(sx):
        for z in range(0, 9):
            d = math.sqrt(((x-cx)/rx)**2 + ((z-zc)/rz)**2)
            if d <= 1.0: top[(x, z)] = G + 1 + int((1-d)*5.2)
    for (x, z), h in top.items():
        for y in range(G-2, G): t.set(x, y, z, FS)
        for y in range(G, h): t.set(x, y, z, "dirt")
        t.set(x, h, z, "moss_block" if rng.random() < .15 else ("podzol" if rng.random() < .2 else "grass_block"))
        if rng.random() < .22 and h >= G+3: t.set(x, h+1, z, rng.choice(FLOWERS + SHROOMS + ["fern", "azalea_leaves"]))
    # binnenruimte
    def inside(x, z, y):
        d = math.sqrt(((x-cx)/(rx-2.4))**2 + ((z-zc)/(rz-2.2))**2)
        return d <= 1.0 and (y-G) <= 3 - (1 if d > .6 else 0) + (1 if d < .3 else 0) and y > G
    for x in range(sx):
        for z in range(0, 9):
            for y in range(G, G+6):
                if (x, z) in top and y <= top[(x, z)]:
                    if inside(x, z, y): t.set(x, y, z, "air")
    for x in range(sx):
        for z in range(0, 9):
            if (x, z) in top and math.sqrt(((x-cx)/(rx-2.4))**2 + ((z-zc)/(rz-2.2))**2) <= 1.0: t.set(x, G, z, "spruce_planks")
    for (x, y, z) in list(t.blocks.keys()):
        if t.get(x, y, z) == "air" and y > G:
            for (dx, dy, dz) in ((1,0,0),(-1,0,0),(0,0,1),(0,0,-1),(0,1,0)):
                n = t.get(x+dx, y+dy, z+dz)
                if n in ("dirt", "grass_block", "moss_block", "podzol") and (x+dx, z+dz) in top and y+dy < top[(x+dx, z+dz)]:
                    t.set(x+dx, y+dy, z+dz, "dark_oak_planks" if dy == 1 else "spruce_planks")
    # deur met boogvormig kozijn
    zf = max(z for (x, z) in top if x == cx)
    for z in range(zf-2, zf+1):
        for y in range(G+1, G+3): t.set(cx, y, z, "air")
    t.door(cx, G+1, zf, "spruce_door", "south")
    for (dx, dy) in ((-1,1),(-1,2),(1,1),(1,2),(0,3)): t.set(cx+dx, G+dy, zf, "stripped_spruce_log", axis="y" if dx else "x")
    t.set(cx-1, G+3, zf, "moss_block"); t.set(cx+1, G+3, zf, "moss_block")
    t.set(cx-2, G+1, zf+1, "dark_oak_fence"); t.set(cx-2, G+2, zf+1, "lantern", hanging=False)
    t.set(cx+2, G+1, zf+1, "dark_oak_fence"); t.set(cx+2, G+2, zf+1, "lantern", hanging=False)
    t.slab(cx, G, zf+1, "gnomehollow:fieldstone_slab")
    # raampjes
    for dx in (-3, 3):
        wx = cx+dx; zz = max((z for (x, z) in top if x == wx), default=None)
        if zz is not None:
            t.set(wx, G+2, zz, "glass_pane", east=True, west=True)
            for (ddx, ddy) in ((-1,0),(1,0)): t.set(wx+ddx, G+2+ddy, zz, "stripped_spruce_log", axis="y")
            t.set(wx, G+1, zz, "spruce_planks"); t.set(wx, G+3, zz, "spruce_planks")
    # schoorsteen
    chimney(t, cx+2, 2, top[(cx+2, 2)]-1, top[(cx+2, 2)]+1) if (cx+2, 2) in top else None
    # inrichting
    t.bed(cx-3, G+1, 2, bed, "south"); t.chest(cx+3, G+1, 3, "west", loot)
    t.set(cx, G+1, 4, "dark_oak_fence"); t.set(cx, G+2, 4, "spruce_pressure_plate")
    t.stairs(cx-1, G+1, 4, "spruce_stairs", "west"); t.stairs(cx+1, G+1, 4, "spruce_stairs", "east")
    t.set(cx, G+4, 4, LAMP); t.set(cx-2, G+1, 6, "potted_fern")
    t.set(cx+2, G+1, 2, "bookshelf"); t.set(cx+2, G+2, 2, "bookshelf")
    # tuin
    for z in range(zf+1, sz): t.set(cx, G, z, "dirt_path")
    for z in range(zf+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    scatter(t, rng, 0, sx-1, zf+1, sz-2, .14)
    if farm:
        for px_, wx in ((0, 1), (8, 9)):
            for x in range(px_, px_+3):
                for z in range(zf+2, zf+5):
                    if (x, z) == (wx, zf+3): t.set(x, G, z, "water", level=0); continue
                    t.set(x, G, z, "farmland", moisture=7)
                    t.set(x, G+1, z, rng.choice(["wheat", "carrots", "potatoes"]), age=7)
        t.barrel(cx-3, G+1, 6, "farmer"); t.set(cx+3, G+1, 6, "composter", level=0)
    if shop == "healer":
        t.set(cx-3, G+1, 6, "brewing_stand"); t.set(cx-2, G+1, 7, "brewing_stand"); t.set(cx+3, G+1, 6, "water_cauldron", level=3)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ paddenstoelhuis
def mushroom_house(name, shop=None, loot="pantry", bed="pink"):
    rng = new_rng(name)
    sx, sz = 11, 15; t = Tpl(name, sx, 18, sz); ground(t, rng)
    cx, cz = 5, 5
    def dist(x, z): return math.hypot(x-cx, z-cz)
    for x in range(sx):
        for z in range(sz):
            if dist(x, z) <= 3.6:
                t.set(x, G-1, z, FS); t.set(x, G-2, z, FS)
    for y in range(G, G+7):
        for x in range(sx):
            for z in range(sz):
                d = dist(x, z)
                if d <= 3.6:
                    if d >= 2.6: t.set(x, y, z, "gnomehollow:gnome_stem")
                    else: t.set(x, y, z, "spruce_planks" if y == G else "air")
    for x in range(sx):                      # verdieping (zolder) als ring
        for z in range(sz):
            if dist(x, z) <= 2.6 and not (x == cx and z == cz-1): t.set(x, G+4, z, "spruce_planks")
    t.set(cx, G+4, cz-2, "air")
    for y in range(G+1, G+6): t.set(cx, y, cz-2, "ladder", facing="south", waterlogged=False)
    # cap
    layers = [(G+7, 5.3), (G+8, 4.4), (G+9, 3.2), (G+10, 1.9), (G+11, 0.9)]
    for (y, r) in layers:
        for x in range(sx):
            for z in range(sz):
                if dist(x, z) <= r: t.set(x, y, z, "gnomehollow:toadstool_cap")
    for x in range(sx):                      # onderkant van de hoed: lampjes
        for z in range(sz):
            if 2.6 < dist(x, z) <= 3.6 and (x + z) % 3 == 0: t.set(x, G+6, z, "gnomehollow:toadstool_cap_slab", type="top", waterlogged=False)
    # deur + ramen
    zf = cz + 3
    t.door(cx, G+1, zf, "spruce_door", "south")
    for dx in (-1, 1):
        for dy in (1, 2): t.set(cx+dx, G+dy, zf, "stripped_spruce_log", axis="y")
    t.set(cx, G+3, zf, "stripped_spruce_log", axis="x")
    t.set(cx-2, G+1, zf+1, "dark_oak_fence"); t.set(cx-2, G+2, zf+1, "lantern", hanging=False)
    t.set(cx+2, G+1, zf+1, "dark_oak_fence"); t.set(cx+2, G+2, zf+1, "lantern", hanging=False)
    for (wx, wz, along) in ((cx-3, cz, "z"), (cx+3, cz, "z"), (cx, cz-3, "x"), (cx-2, cz+2, "x"), (cx+2, cz+2, "x")):
        for y in (G+2, G+5): t.pane(wx, y, wz, along)
    # inrichting
    t.bed(cx+1, G+5, cz+1, bed, "north"); t.chest(cx-1, G+5, cz+1, "east", loot)
    t.set(cx, G+1, cz, "dark_oak_fence"); t.set(cx, G+2, cz, "spruce_pressure_plate")
    t.stairs(cx-1, G+1, cz, "spruce_stairs", "west"); t.stairs(cx+1, G+1, cz, "spruce_stairs", "east")
    t.set(cx, G+3, cz+1, LAMP); t.set(cx-2, G+1, cz+1, "bookshelf"); t.set(cx+2, G+1, cz+1, "potted_red_mushroom")
    if shop == "healer":
        t.set(cx-2, G+1, cz-1, "brewing_stand"); t.set(cx+2, G+1, cz-1, "brewing_stand"); t.set(cx+2, G+1, cz, "water_cauldron", level=3)
        t.barrel(cx-2, G+1, cz, "healer")
    # tuin met kleine paddenstoelen
    for z in range(zf+1, sz): t.set(cx, G, z, "dirt_path")
    for z in range(zf+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    for (mx, mz) in ((1, 9), (9, 10), (2, 12), (8, 13)):
        t.set(mx, G+1, mz, "gnomehollow:gnome_stem"); t.set(mx, G+2, mz, "gnomehollow:gnome_stem")
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1): t.slab(mx+dx, G+3, mz+dz, "gnomehollow:toadstool_cap_slab")
    scatter(t, rng, 0, sx-1, zf+1, sz-2, .10)
    for k in range(1 if not shop else 1): t.gnome("healer" if shop else "nitwit", cx, G+1, cz-1)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ beroepshuizen
def finish(g, gnomes):
    t, cx, z0 = g["t"], g["cx"], g["z0"]
    for i, (prof, dx, dz) in enumerate(gnomes): t.gnome(prof, cx+dx, G+1, z0+3+dz)

def healer_a():
    g = cottage("house_healer_a", 9, 8, 1, "plaster", "toadstool", "x", "r", nitwits=0, bed="green", loot="healer")
    t = g["t"]; xi1, zi0, cx = g["x1"]-1, g["z0"]+1, g["cx"]
    t.set(xi1-1, G+1, zi0, "brewing_stand"); t.set(xi1-2, G+1, zi0, "brewing_stand"); t.set(xi1-3, G+1, zi0, "water_cauldron", level=3)
    t.barrel(xi1, G+1, zi0+1, "healer")
    # kruidentuin + kas
    for x in (1, 2): 
        for z in range(g["z1"]+2, g["sz"]-1):
            t.set(x, G, z, "podzol"); t.set(x, G+1, z, random.Random(x*z).choice(["lily_of_the_valley", "azure_bluet", "cornflower", "allium", "brown_mushroom", "fern"]))
    for x in range(6, 10):
        for z in range(g["z1"]+2, g["z1"]+5):
            edge = x in (6, 9) or z in (g["z1"]+2, g["z1"]+4)
            for y in range(G+1, G+4):
                if edge and y < G+3: t.set(x, y, z, "glass")
                if y == G+3: t.set(x, y, z, "glass")
                if not edge and y == G+1: t.set(x, y, z, random.Random(x+z).choice(["blue_orchid", "allium", "lily_of_the_valley"]))
    t.set(7, G+1, g["z1"]+2, "air"); t.set(7, G+2, g["z1"]+2, "air")
    finish(g, [("healer", 0, 1)])
    return t
def healer_b(): return mushroom_house("house_healer_b", shop="healer", loot="healer", bed="green")

def warrior_a():
    g = cottage("house_warrior_a", 11, 7, 1, "stone", "shingle", "x", "r", porch=False, nitwits=0, bed="red", loot="warrior")
    t = g["t"]; xi0, xi1, zi0, cx = g["x0"]+1, g["x1"]-1, g["z0"]+1, g["cx"]
    for k in range(3): t.bed(xi0+2*k+1 if xi0+2*k+1 < xi1-1 else xi0, G+1, zi0+2, "red", "south") if k else None
    t.set(xi1-2, G+1, zi0, "grindstone", face="floor", facing="north"); t.set(xi1-3, G+1, zi0, "anvil", facing="east")
    t.barrel(xi1-4, G+1, zi0, "warrior"); t.chest(xi1, G+1, zi0+2, "west", "warrior")
    for (x, z) in ((cx-3, g["z1"]+3), (cx+3, g["z1"]+3), (cx-4, g["z1"]+5), (cx+4, g["z1"]+5)):
        t.set(x, G+1, z, "hay_block", axis="y"); t.set(x, G+2, z, "target")
    for x in (cx-2, cx+2):
        t.set(x, G+1, g["z1"]+1, "dark_oak_fence"); t.set(x, G+2, g["z1"]+1, "dark_oak_fence"); t.set(x, G+3, g["z1"]+1, "red_banner", rotation=0)
    finish(g, [("warrior", 0, 1), ("warrior", 2, 1)]); t.gnome("warrior", cx, G+1, g["z1"]+4)
    return t

def warrior_b():
    rng = new_rng("house_warrior_b"); sx, sz = 11, 14; t = Tpl("house_warrior_b", sx, 26, sz); ground(t, rng)
    cx = 5; x0, x1, z0, z1 = 3, 7, 2, 6
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            t.set(x, G-1, z, FS); t.set(x, G-2, z, FS); t.set(x, G, z, "spruce_planks")
    for y in range(G, G+13):
        for x in range(x0, x1+1):
            for z in range(z0, z1+1):
                ring = x in (x0, x1) or z in (z0, z1); corner = x in (x0, x1) and z in (z0, z1)
                if ring: t.set(x, y, z, "stripped_spruce_log" if corner else FS, **({"axis": "y"} if corner else {}))
                elif y > G: t.set(x, y, z, "air")
    for fy in (G+5, G+9):
        for x in range(x0+1, x1): 
            for z in range(z0+1, z1): t.set(x, fy, z, "spruce_planks")
        t.set(cx, fy, z0+1, "air")
    for y in range(G+1, G+10): t.set(cx, y, z0+1, "ladder", facing="south", waterlogged=False)
    for (wy) in (G+3, G+7, G+11):
        for (wx, wz, al) in ((cx, z0, "x"), (x0, 4, "z"), (x1, 4, "z")): t.pane(wx, wy, wz, al)
    t.door(cx, G+1, z1, "spruce_door", "south"); t.set(cx, G+3, z1, "dark_oak_planks")
    # galerij bovenin
    gy = G+10
    for x in range(x0-1, x1+2):
        for z in range(z0-1, z1+2):
            if x in (x0-1, x1+1) or z in (z0-1, z1+1):
                t.set(x, gy, z, "spruce_planks"); t.set(x, gy+1, z, "dark_oak_fence")
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            if x in (x0, x1) or z in (z0, z1): t.set(x, gy, z, "spruce_planks")
    for (x, z) in ((x0-1, z0-1), (x1+1, z0-1), (x0-1, z1+1), (x1+1, z1+1)):
        for y in range(gy+1, gy+4): t.set(x, y, z, "dark_oak_log", axis="y")
    # piramidedak
    ry = gy+4
    for r, s in enumerate((9, 7, 5, 3)):
        lo = cx - s//2; hi = cx + s//2; zlo = 4 - s//2 - 0; zhi = 4 + s//2
        for x in range(lo, hi+1):
            for z in range(zlo, zhi+1):
                edge_x = x in (lo, hi); edge_z = z in (zlo, zhi)
                if not (edge_x or edge_z): t.set(x, ry+r, z, "gnomehollow:gnome_shingles") if s <= 3 else None; continue
                if edge_x and edge_z: t.set(x, ry+r, z, "gnomehollow:gnome_shingles"); continue
                f = "south" if z == zlo else "north" if z == zhi else "east" if x == lo else "west"
                t.stairs(x, ry+r, z, ROOFS["shingle"]["stairs"], f)
    t.set(cx, ry+4, 4, "lantern", hanging=False); t.set(cx, ry+4, 4, LAMP)
    t.set(cx, gy+1, z0-1, "red_banner", rotation=8)
    t.set(cx+1, G+1, z0+3, "chest" if False else "air"); t.chest(x1-1, G+1, z0+2, "west", "warrior"); t.chest(x1-1, G+6, z0+2, "west", "warrior")
    t.set(x0+1, G+1, z1-1, "red_bed" if False else "air"); t.bed(x0+1, G+1, z1-1, "red", "north")
    t.set(cx, G+4, 4, LAMP); t.set(cx, G+8, 4, LAMP)
    for z in range(z1+1, sz): t.set(cx, G, z, "dirt_path")
    for z in range(z1+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    t.set(cx-2, G+1, z1+1, "dark_oak_fence"); t.set(cx-2, G+2, z1+1, "lantern", hanging=False)
    t.set(cx+2, G+1, z1+1, "dark_oak_fence"); t.set(cx+2, G+2, z1+1, "lantern", hanging=False)
    for (x, z) in ((1, 9), (9, 10)): t.set(x, G+1, z, "hay_block", axis="y"); t.set(x, G+2, z, "target")
    scatter(t, rng, 0, sx-1, z1+1, sz-2, .1)
    t.gnome("warrior", cx, G+1, 4); t.gnome("warrior", cx, G+6, 4); t.gnome("warrior", cx, G+11, 4)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

def farm_plots(t, g, rng):
    z1 = g["z1"]; sz = g["sz"]
    for px_, wx in ((1, 2), (g["sx"]-4, g["sx"]-3)):
        for x in range(px_, px_+3):
            for z in range(z1+2, min(z1+6, sz-1)):
                if (x, z) == (wx, z1+3): t.set(x, G, z, "water", level=0); continue
                t.set(x, G, z, "farmland", moisture=7)
                t.set(x, G+1, z, rng.choice(["wheat", "carrots", "potatoes", "wheat"]), age=7)
def scarecrow(t, x, z):
    t.set(x, G+1, z, "dark_oak_fence"); t.set(x, G+2, z, "hay_block", axis="y"); t.set(x, G+3, z, "carved_pumpkin", facing="south")
    t.set(x-1, G+2, z, "dark_oak_fence"); t.set(x+1, G+2, z, "dark_oak_fence")

def farmer_a():
    g = cottage("house_farmer_a", 9, 7, 1, "plaster", "thatch", "x", "l", nitwits=0, bed="lime", loot="farmer")
    t = g["t"]; xi1, zi0, cx = g["x1"]-1, g["z0"]+1, g["cx"]
    t.set(xi1-1, G+1, zi0, "composter", level=0); t.barrel(xi1-2, G+1, zi0, "farmer"); t.set(xi1-3, G+1, zi0, "hay_block", axis="y")
    farm_plots(t, g, g["rng"]); scarecrow(t, cx+3, g["z1"]+3)
    for x in range(1, g["sx"]-1):
        if x not in (cx-1, cx, cx+1): t.set(x, G+1, g["sz"]-2, "dark_oak_fence")
    finish(g, [("farmer", 0, 1), ("farmer", 1, 2)]); return t
def farmer_b(): return burrow("house_farmer_b", farm=True, nitwits=0, bed="lime", loot="farmer")

def pond(t, x0, x1, z0, z1, rng, deep=2):
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            edge = x in (x0, x1) or z in (z0, z1)
            if edge and rng.random() < .5: t.set(x, G, z, "water", level=0) if False else None
            for y in range(G-deep, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-deep-1, z, "clay")
            if rng.random() < .15: t.set(x, G+1, z, "lily_pad")
def dock(t, x, z0, z1, along_x=True):
    for z in range(z0, z1+1):
        t.set(x, G, z, "spruce_planks")
        if z in (z0, z1): 
            for dx in (-0, ): pass

def fisherman_a():
    g = cottage("house_fisherman_a", 9, 7, 1, "timber", "shingle", "z", "r", nitwits=0, bed="blue", loot="fisher")
    t = g["t"]; xi1, zi0, cx, z1, sz, sx = g["x1"]-1, g["z0"]+1, g["cx"], g["z1"], g["sz"], g["sx"]
    t.barrel(xi1-1, G+1, zi0, "fisher"); t.barrel(xi1-2, G+1, zi0, "fisher"); t.set(xi1-3, G+1, zi0, "water_cauldron", level=3)
    rng = g["rng"]
    for x in range(sx-5, sx-1):
        for z in range(z1+2, sz-1): 
            for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-3, z, "clay"); t.set(x, G+1, z, "air")
    for x in range(sx-6, sx-3): t.set(x, G, z1+3, "spruce_planks"); t.set(x, G, z1+4, "spruce_planks")
    t.set(sx-7, G+1, z1+3, "dark_oak_fence"); t.set(sx-7, G+2, z1+3, "lantern", hanging=False)
    t.barrel(sx-7, G+1, z1+4, "fisher")
    for k in range(3): t.set(2+k, G+1, z1+2, "dark_oak_fence"); 
    for k in range(3): t.set(2+k, G+2, z1+2, "dried_kelp_block")
    finish(g, [("fisherman", 0, 1), ("fisherman", 1, 3)]); t.gnome("fisherman", sx-6, G+1, z1+3); return t

def fisherman_b():
    g = cottage("house_fisherman_b", 7, 6, 1, "log", "thatch", "x", None, nitwits=0, bed="cyan", loot="fisher", porch=True)
    t = g["t"]; z1, sz, sx, cx = g["z1"], g["sz"], g["sx"], g["cx"]
    for x in range(1, sx-1):
        for z in range(z1+2, sz-1):
            if x in (cx-1, cx, cx+1) and z < z1+3: continue
            for y in range(G-2, G+1): t.set(x, y, z, "water", level=0)
            t.set(x, G-3, z, "clay"); t.set(x, G+1, z, "air")
    for z in range(z1+1, sz-1): t.set(cx, G, z, "spruce_planks")
    for x in range(cx-1, cx+2): t.set(x, G, sz-2, "spruce_planks")
    for z in (z1+2, sz-2): t.set(cx-1, G+1, z, "dark_oak_fence"); t.set(cx+1, G+1, z, "dark_oak_fence"); 
    t.set(cx+1, G+2, sz-2, "lantern", hanging=False)
    t.barrel(cx+1, G+1, z1+3, "fisher") if False else None
    t.barrel(g["x1"]-1, G+1, g["z0"]+1, "fisher"); t.barrel(g["x1"]-2, G+1, g["z0"]+1, "fisher")
    finish(g, [("fisherman", 0, 1)]); t.gnome("fisherman", cx, G+1, sz-3); return t

def builder_a():
    g = cottage("house_builder_a", 9, 8, 1, "log", "shingle", "x", "r", nitwits=0, bed="orange", loot="builder")
    t = g["t"]; xi1, zi0, cx, z1, sz, sx = g["x1"]-1, g["z0"]+1, g["cx"], g["z1"], g["sz"], g["sx"]
    t.set(xi1-1, G+1, zi0, "stonecutter", facing="north"); t.set(xi1-2, G+1, zi0, "crafting_table"); t.set(xi1-3, G+1, zi0, "anvil", facing="east")
    t.chest(xi1, G+1, zi0+1, "west", "builder")
    for k in range(4): t.set(1, G+1+k//2, z1+2+k%2+ (k//2), "stripped_spruce_log", axis="x") if False else None
    for dz in range(3):
        for dy in range(3-dz): t.set(1+dz, G+1+dy, z1+2, "stripped_spruce_log", axis="z"); t.set(1+dz, G+1+dy, z1+3, "stripped_spruce_log", axis="z")
    for y in range(G+1, G+5): t.set(sx-2, y, z1+2, "scaffolding", bottom=(y == G+1), distance=0, waterlogged=False)
    t.fill(sx-4, G+1, z1+3, sx-3, G+1, z1+4, "stone_bricks"); t.set(sx-4, G+2, z1+3, "stone_bricks"); t.set(sx-3, G+1, z1+5, "cobblestone")
    t.barrel(sx-2, G+1, z1+4, "builder")
    finish(g, [("builder", 0, 1), ("builder", 1, 3)]); t.gnome("builder", sx-4, G+1, z1+2); return t

def builder_b():
    rng = new_rng("house_builder_b"); W, D = 9, 8; sx, sz = W+2, D+5; t = Tpl("house_builder_b", sx, 18, sz); ground(t, rng)
    x0, x1, z0, z1 = 1, W, 1, D; cx = 5
    for x in range(x0, x1+1):
        for z in range(z0, z1+1): t.set(x, G-1, z, FS); t.set(x, G, z, "spruce_planks")
    for (x, z) in ((x0, z0), (x1, z0), (x0, z1), (x1, z1), (cx, z0), (cx, z1), (x0, 4), (x1, 4)):
        for y in range(G+1, G+4): t.set(x, y, z, "dark_oak_log", axis="y")
    for x in range(x0, x1+1):
        for z in range(z0, z1+1):
            if (x in (x0, x1) or z in (z0, z1)) and t.get(x, G+1, z) == "air" or t.get(x, G+1, z) is None:
                if x in (x0, x1) or z in (z0, z1):
                    if rng.random() < .85:
                        t.set(x, G+1, z, "gnomehollow:plaster") if (x+z) % 2 else t.set(x, G+1, z, "gnomehollow:timber_plaster")
    for z in (z0, z1):
        for x in range(x0, x1+1):
            if t.get(x, G+3, z) is None: t.set(x, G+3, z, "dark_oak_planks")
    for x in range(x0, x1+1):
        for z in (4,):
            if rng.random() < .8: t.set(x, G+4, z, "dark_oak_planks") if x % 2 else None
    for y in range(G+1, G+5):
        for (x, z) in ((x1+1, 2), (x1+1, 5), (x0-1 if x0 > 0 else 0, 7)):
            t.set(x, y, z, "scaffolding", bottom=(y == G+1), distance=0, waterlogged=False)
    t.door(cx, G+1, z1, "spruce_door", "south") if False else None
    t.fill(2, G+1, 3, 3, G+1, 4, "oak_planks"); t.fill(7, G+1, 3, 8, G+1, 3, "stripped_spruce_log", axis="x"); t.set(7, G+2, 3, "stripped_spruce_log", axis="x")
    t.set(2, G+1, 6, "crafting_table"); t.set(3, G+1, 6, "stonecutter", facing="south"); t.chest(8, G+1, 6, "west", "builder"); t.barrel(7, G+1, 6, "builder")
    t.set(5, G+1, 4, "anvil", facing="east")
    for z in range(z1+1, sz): t.set(cx, G, z, "dirt_path")
    for z in range(z1+2, sz):
        for dx in (-1, 1): t.set(cx+dx, G, z, "dirt_path")
    t.fill(1, G+1, z1+2, 3, G+1, z1+3, "stone_bricks"); t.fill(7, G+1, z1+2, 9, G+1, z1+2, "stripped_spruce_log", axis="x"); t.set(8, G+2, z1+2, "stripped_spruce_log", axis="x")
    t.set(cx+2, G+1, z1+1, "dark_oak_fence"); t.set(cx+2, G+2, z1+1, "lantern", hanging=False)
    scatter(t, rng, 0, sx-1, z1+1, sz-2, .05)
    t.gnome("builder", 4, G+1, 3); t.gnome("builder", 6, G+1, 10)
    t.jigsaw(cx, G, sz-1, "south", "gnomehollow:entrance", "gnomehollow:entrance", "minecraft:empty")
    return t

# ------------------------------------------------------------------ algemene huizen
def generics():
    cottage("house_cottage_thatch", 9, 7, 1, "plaster", "thatch", "x", "r", nitwits=1, bed="red")
    cottage("house_cottage_shingle", 7, 8, 1, "timber", "shingle", "z", "l", nitwits=1, bed="blue")
    cottage("house_twostory", 9, 8, 2, "timber", "shingle", "x", "r", nitwits=2, bed="yellow")
    cottage("house_cottage_small", 7, 6, 1, "plaster", "thatch", "x", None, nitwits=1, bed="white")
    cottage("house_cottage_log", 9, 7, 1, "log", "thatch", "z", "r", nitwits=1, bed="brown")
    cottage("house_cottage_cap", 7, 7, 1, "plaster", "toadstool", "x", "l", nitwits=1, bed="pink", loot="nitwit")
    burrow("house_burrow", nitwits=1)
    mushroom_house("house_mushroom", loot="nitwit")

def all_houses():
    healer_a(); healer_b(); warrior_a(); warrior_b(); farmer_a(); farmer_b()
    fisherman_a(); fisherman_b(); builder_a(); builder_b(); generics()
