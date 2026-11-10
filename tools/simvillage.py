import json, random, glob, os, sys
sys.path.insert(0, "/home/claude/gen")
import importlib
import structlib as S
ROOT = "/home/claude/gnome-hollow/src/main/resources/data/gnomehollow"
# templates uit REGISTRY (opnieuw genereren zonder te schrijven)
import gen_structs   # voert generatie uit en vult REGISTRY
REG = S.REGISTRY
POOLS = {os.path.basename(p)[:-5]: json.load(open(p)) for p in glob.glob(f"{ROOT}/worldgen/template_pool/village/*.json")}
DIRV = {"north": (0,-1), "east": (1,0), "south": (0,1), "west": (-1,0)}
ORDER = ["north", "east", "south", "west"]
def rotf(f, r): return ORDER[(ORDER.index(f)+r) % 4]
def rotv(x, z, r):
    for _ in range(r): x, z = -z, x
    return x, z
class Piece:
    def __init__(self, tpl, rot, ox, oz, depth):
        self.t = REG[tpl]; self.name = tpl; self.rot = rot; self.ox = ox; self.oz = oz; self.depth = depth
        sx, _, sz = self.t.size
        cs = [rotv(x, z, rot) for x in (0, sx-1) for z in (0, sz-1)]
        self.x0 = min(c[0] for c in cs)+ox; self.x1 = max(c[0] for c in cs)+ox
        self.z0 = min(c[1] for c in cs)+oz; self.z1 = max(c[1] for c in cs)+oz
        self.used = set()
    def jigs(self):
        for i, (x, y, z, f, name, target, pool) in enumerate(self.t.jig):
            rx, rz = rotv(x, z, self.rot); yield i, (rx+self.ox, rz+self.oz), rotf(f, self.rot), name, target, pool
def overlap(a, b): return not (a.x1 < b.x0 or b.x1 < a.x0 or a.z1 < b.z0 or b.z1 < a.z0)
def pick(pool_name, rng):
    p = POOLS[pool_name.split(":")[1].split("/")[1]] if pool_name != "minecraft:empty" else None
    if p is None: return None
    els = p["elements"]; tot = sum(e["weight"] for e in els); r = rng.uniform(0, tot)
    for e in els:
        r -= e["weight"]
        if r <= 0: return e, p
    return els[-1], p
def build(seed, size=6, maxd=80):
    rng = random.Random(seed)
    start = rng.choice(["plaza_a", "plaza_b", "plaza_c"]); rot = rng.randrange(4)
    placed = [Piece(start, rot, 0, 0, 0)]; queue = [placed[0]]
    while queue:
        par = queue.pop(0)
        if par.depth >= size: continue
        jl = list(par.jigs()); rng.shuffle(jl)
        for (i, cell, f, name, target, poolname) in jl:
            if poolname == "minecraft:empty": continue
            tgt = (cell[0]+DIRV[f][0], cell[1]+DIRV[f][1])
            pn = poolname; ok_any = False
            for attempt in range(2):     # tweede ronde: fallback-pool
                if pn == "minecraft:empty" or ok_any: break
                pool = POOLS[pn.split(":")[1].split("/")[1]]
                els = list(pool["elements"]); order = []
                tmp = els[:]
                while tmp:                   # gewogen shuffle (zoals vanilla)
                    tot = sum(e["weight"] for e in tmp); r = rng.uniform(0, tot)
                    for e in tmp:
                        r -= e["weight"]
                        if r <= 0: order.append(e); tmp.remove(e); break
                for el in order:
                    if el["element"]["element_type"].endswith("empty_pool_element"): ok_any = True; break
                    tname = el["element"]["location"].split("/")[-1]; tpl = REG[tname]
                    cands = [(ji, jj) for ji, jj in enumerate(tpl.jig) if jj[4] == target]
                    rng.shuffle(cands); placed_it = False
                    for ji, (x, y, z, cf, cn, ct, cp) in cands:
                        need = rotf(f, 2)
                        for r_ in range(4):
                            if rotf(cf, r_) == need: break
                        rx, rz = rotv(x, z, r_); ox, oz = tgt[0]-rx, tgt[1]-rz
                        np_ = Piece(tname, r_, ox, oz, par.depth+1)
                        if max(abs(np_.x0), abs(np_.x1), abs(np_.z0), abs(np_.z1)) > maxd: continue
                        if any(overlap(np_, q) for q in placed if q is not par): continue
                        np_.used.add(ji); placed.append(np_); queue.append(np_); placed_it = True; break
                    if placed_it: ok_any = True; break
                pn = pool["fallback"]
    return placed
if __name__ == "__main__":
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, axs = plt.subplots(2, 3, figsize=(15, 10))
    PROFS = ["healer", "warrior", "farmer", "fisherman", "builder"]
    for ax, seed in zip(axs.flat, range(1, 7)):
        pcs = build(seed)
        have = {p: any(p in q.name for q in pcs) for p in PROFS}
        houses = sum(1 for q in pcs if q.name.startswith("house_")); decor = sum(1 for q in pcs if q.name.startswith("decor"))
        print(f"seed {seed}: {len(pcs)} stukken, {houses} huizen, {decor} decor, beroepen: {[p for p,v in have.items() if v]} / ontbreekt: {[p for p,v in have.items() if not v]}")
        for q in pcs:
            col = "#b99" if q.name.startswith("street") else "#8c8" if q.name.startswith("plaza") else "#fc6" if q.name.startswith("decor") else "#6af"
            if any(p in q.name for p in PROFS): col = "#f66"
            ax.add_patch(Rectangle((q.x0, q.z0), q.x1-q.x0+1, q.z1-q.z0+1, fc=col, ec="k", lw=.5))
        ax.set_xlim(-70, 70); ax.set_ylim(70, -70); ax.set_aspect("equal"); ax.set_title(f"seed {seed}")
    plt.tight_layout(); plt.savefig("/home/claude/gen/layout.png", dpi=60)
