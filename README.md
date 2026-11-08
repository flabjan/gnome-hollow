# Gnome Hollow (Fabric, Minecraft 26.2)

Kabouterdorpen in **Dark Forest** en **Taiga** met gnomes die echt hun beroep uitoefenen.
**Status: broncode, nog nooit gecompileerd of getest** (zie "Bekende risico's" onderaan).

## 1. De .JAR zelf bouwen

Je hebt nodig: **JDK 25** (bijv. Temurin 25) en internet (Gradle downloadt Minecraft, Fabric en GeckoLib).

**Optie A: lokaal**
1. Pak de zip uit en open een terminal in de map `gnome-hollow`.
2. Installeer Gradle 9.5.1 (of gebruik de wrapper van een Fabric-voorbeeldproject) en maak de wrapper aan:
   `gradle wrapper --gradle-version 9.5.1`
3. Bouwen: `./gradlew build` (Windows: `gradlew.bat build`).
4. Je jar staat in `build/libs/gnome-hollow-1.0.0.jar` (niet de `-sources.jar`).

**Optie B: GitHub (geen lokale installatie)**
Zet de map in een nieuwe GitHub-repo. Het bestand `.github/workflows/build.yml` bouwt de jar; download hem onder Actions > Artifacts.

## 2. Installeren
In je mods-map (Fabric): `gnome-hollow-1.0.0.jar` + **Fabric API** (0.158.0+26.2 of nieuwer) + **GeckoLib 5.5.5 (Fabric, 26.2)**. Fabric Loader 0.19.3+ en Java 25.
GeckoLib is de enige extra dependency (voor de modellen en animaties); EMF/ETF zijn niet nodig.

## 3. Waar vind je alles?
- **Dorp:** `/locate structure gnomehollow:gnome_village`. Genereert in Dark Forest, Taiga, Old Growth Pine Taiga en Old Growth Spruce Taiga (ongeveer elke 28 chunks).
- **Gnomes:** creative-tab *Spawn Eggs* (Healer, Warrior, Farmer, Fisherman, Builder, Nitwit).
- **Blokken:** creative-tab *Building Blocks*: Toadstool Lamp, Gnome Shingles, trap en plaat (ook craftbaar).

## 4. Het dorp
Plein met een put onder een paddenstoelhoed, lantaarnpalen met paddenstoellampen, boomstronken voor de band, en 6 heuvelhuisjes (hobbit-stijl met rode shingle-punthoed, ronde ramen, luifel boven de deur). De huizen zitten vast aan het plein: Healer (NW), Warrior (NO), Farmer (ZW), Builder (ZO), Fisherman (W, met vijver en steiger), Nitwits (O). Door rotatie van het dorp wisselen de windrichtingen.

## 5. Gedrag
- Altijd neutraal. Overdag werken ze, 's nachts gaan ze naar huis (Warriors blijven op wacht).
- **Warrior:** valt hostile mobs aan en slaat terug als er een gnome wordt geraakt (alarmeert de rest).
- **Healer:** loopt naar de brewing stand en brouwt (bubbels/geluid), legt soms een Healing/Regeneration-drankje in een kist. Geneest gewonde spelers, dorpelingen, gnomes en golems binnen 6 blokken.
- **Fisherman:** zoekt open water, gaat op de oever/steiger staan en vist; de vangst gaat in een barrel in de buurt.
- **Farmer:** oogst volgroeide tarwe/wortels/aardappels/bieten (alleen rijpe) en plant direct opnieuw.
- **Builder:** timmert lantaarnpaaltjes rond het dorp (max. 8 per gnome).
- **Nitwit:** speelt pentatonische muziek; andere nitwits in de buurt doen mee.

## 6. Bekende risico's (hier waarschijnlijk eventuele compilefouten)
Ik had geen internet in mijn werkomgeving, dus niets is gecompileerd. Plekken waar Minecraft 26.2 of GeckoLib 5 mogelijk anders zijn dan ik aannam:
- Geluiden: `SoundEvent.createVariableRangeEvent`, en de overrides `playStepSound`, `setTarget` en `mobInteract` in `GnomeEntity`.
- Overige 26.2 API-details zoals `Identifier`, `Level#isBrightOutside()`, `Item.Properties#spawnEgg(..)`, `SoundEvents.NOTE_BLOCK_*.value()` en `HurtByTargetGoal#setAlertOthers()` moeten nog door de echte GitHub-build worden bevestigd.
- GeckoLib 5: de nieuwe `com.geckolib`-packages, `AnimationController`, `triggerableAnim` en `stopTriggeredAnim`; renderer gebruikt de GeckoLib 5 render-state API.
- Structuren: `DataVersion` staat op 4671 en `start_height` op -3. Staat het dorp een blok te hoog/laag, pas dan `start_height` aan in `data/gnomehollow/worldgen/structure/gnome_village.json`.
- Animatierichtingen (bijv. arm omhoog) kunnen gespiegeld zijn; aanpassen in `assets/gnomehollow/geckolib/animations/entity/`.
Plak de foutmeldingen terug in de chat, dan los ik ze op.

## 7. Geluiden
Alle gnomes delen één stem: hoog, nasaal en schelms kabouter-gebrabbel (synthetisch gemaakt, volledig origineel; **geen** audio van de mod "Gnomes!" of de meme, die laatste mod is ARR-gelicenseerd). Per situatie zijn er meerdere varianten, die willekeurig worden gekozen, plus een lichte toonhoogte-variatie per beroep (Builder/Warrior dieper, Healer/Nitwit hoger).

| Situatie | Event | Varianten |
|---|---|---|
| Brabbelen (idle) | `entity.gnome.ambient` | 6 |
| Speler komt dichtbij | `greet` | 3 |
| Rechtsklik overdag / 's nachts | `yes` / `no` | 3 / 3 |
| Pijn / dood | `hurt` / `death` | 4 / 2 |
| Krijgskreet (Warrior valt aan) | `attack` | 4 |
| Schrik, vlucht voor monster | `alert` | 3 |
| Giechelen (Nitwit-muziek) | `laugh` | 3 |
| Werk af | `celebrate` | 3 |
| Vis gevangen (anders "aww" = `no`) | `fish_catch` | 2 |
| Brouwen / oogsten / bouwen / vissen | `work_brew` / `work_farm` / `work_build` / `work_fish` | 2 / 3 / 3 / 2 |
| Healer geneest | `heal` | 2 |
| Snurken 's nachts bij huis | `snore` | 2 |
| Stapjes | `step` | 3 |

**Eigen geluiden gebruiken:** vervang een bestand in `src/main/resources/assets/gnomehollow/sounds/entity/gnome/` door je eigen **mono .ogg (Vorbis)** met dezelfde naam, of voeg varianten toe en vermeld ze in `sounds.json`. Opnieuw synthetiseren kan met `tools/gen_sounds.py` (en daarna `tools/gen_sounds_json.py`); vereist `numpy`, `scipy` en `ffmpeg` met libvorbis.

## 8. Opnieuw genereren
`tools/gen_assets.py` (texturen, modellen, animaties, taal, recepten) en `tools/gen_structs.py` (dorpsstructuren) maken alle assets/data opnieuw (pas de paden bovenin aan).
