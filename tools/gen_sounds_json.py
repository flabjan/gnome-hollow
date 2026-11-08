"""Schrijft sounds.json + ondertitels (subtitles) voor alle gnome-geluiden."""
import json, os, glob, re
A = "/home/claude/gnome-hollow/src/main/resources/assets/gnomehollow"
files = sorted(os.path.basename(f)[:-4] for f in glob.glob(f"{A}/sounds/entity/gnome/*.ogg"))
groups = {}
for f in files:
    groups.setdefault(re.sub(r"\d+$", "", f), []).append(f)
sub_en = {"ambient":"Gnome chatters","greet":"Gnome greets","yes":"Gnome agrees","no":"Gnome grumbles","hurt":"Gnome hurts",
 "death":"Gnome dies","attack":"Gnome battle cry","alert":"Gnome panics","laugh":"Gnome giggles","celebrate":"Gnome cheers",
 "fish_catch":"Gnome catches a fish","work_brew":"Gnome hums while brewing","work_farm":"Gnome harvests","work_build":"Gnome grunts while building",
 "work_fish":"Gnome hums while fishing","heal":"Gnome heals","snore":"Gnome snores"}
sub_nl = {"ambient":"Kabouter brabbelt","greet":"Kabouter groet","yes":"Kabouter stemt in","no":"Kabouter moppert","hurt":"Kabouter heeft pijn",
 "death":"Kabouter sterft","attack":"Kabouter krijgskreet","alert":"Kabouter raakt in paniek","laugh":"Kabouter giechelt","celebrate":"Kabouter juicht",
 "fish_catch":"Kabouter vangt een vis","work_brew":"Kabouter neuriet bij het brouwen","work_farm":"Kabouter oogst","work_build":"Kabouter kreunt bij het bouwen",
 "work_fish":"Kabouter neuriet bij het vissen","heal":"Kabouter geneest","snore":"Kabouter snurkt"}
sj = {}
for g, names in groups.items():
    ev = {"sounds": [{"name": f"gnomehollow:entity/gnome/{n}"} for n in names]}
    if g == "step":
        ev["sounds"] = [{"name": f"gnomehollow:entity/gnome/{n}", "volume": 0.6} for n in names]
    else:
        ev["subtitle"] = f"subtitles.gnomehollow.gnome.{g}"
    sj[f"entity.gnome.{g}"] = ev
json.dump(sj, open(f"{A}/sounds.json", "w"), indent=2)
for lang, sub in (("en_us", sub_en), ("nl_nl", sub_nl)):
    p = f"{A}/lang/{lang}.json"; d = json.load(open(p))
    for g, t in sub.items(): d[f"subtitles.gnomehollow.gnome.{g}"] = t
    json.dump(d, open(p, "w"), indent=2, ensure_ascii=False)
print(len(sj), "sound-events,", len(files), "bestanden")
