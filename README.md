# Gnome Hollow (Fabric, Minecraft 26.2)

Kabouterdorpen in Dark Forest en Taiga met gnomes die echt hun beroep uitoefenen.
**Let op:** dit is broncode die nog nooit is gecompileerd. Bij de eerste build kunnen er foutmeldingen komen (zie stap 6).

# A. De mod zelf maken en installeren (Windows)

Je doet dit één keer. Reken op ongeveer 30 minuten, vooral wachttijd.

## Stap 1: Java 25 installeren
1. Ga naar https://adoptium.net en download **Temurin 25 (JDK)** voor Windows (het `.msi`-bestand).
2. Start het bestand. Zet bij het onderdeel "Custom Setup" **"Set JAVA_HOME variable"** en **"Add to PATH"** op "Will be installed on local hard drive". Klik daarna door tot het einde.
3. Open een **nieuw** Command Prompt (Windows-toets, typ `cmd`, Enter) en typ: `java -version`
   Er moet staan dat het versie **25** is. Staat er een andere versie, dan staat er nog een oude Java voor. Verwijder die dan of zet Temurin 25 bovenaan in je PATH.

## Stap 2: Gradle 9.5.1 installeren
Gradle is het programma dat van de broncode een .jar maakt.
1. Download https://services.gradle.org/distributions/gradle-9.5.1-bin.zip
2. Maak een map `C:\Gradle` en pak het zipbestand daarin uit. Daarna bestaat de map `C:\Gradle\gradle-9.5.1\bin`.
3. Voeg die map toe aan je PATH:
   - Windows-toets, typ **omgevingsvariabelen** en kies "Omgevingsvariabelen voor je account bewerken".
   - Selecteer bij "Gebruikersvariabelen" de regel **Path** en klik op **Bewerken**.
   - Klik op **Nieuw**, plak `C:\Gradle\gradle-9.5.1\bin` en klik drie keer op **OK**.
4. Sluit Command Prompt, open een **nieuwe** en typ: `gradle -v`
   Je ziet nu "Gradle 9.5.1" en bij "Launcher JVM" of "JVM" een 25. Zie je dat, dan is de installatie klaar.

## Stap 3: Het project uitpakken
1. Pak `gnome-hollow-project.zip` uit, bijvoorbeeld naar `C:\Projecten\`. Je hebt dan `C:\Projecten\gnome-hollow`.
2. Open die map in Verkenner, klik in de **adresbalk** bovenin, typ `cmd` en druk op Enter. Er opent een Command Prompt in de juiste map.

## Stap 4: Bouwen
Typ in dat Command Prompt: `gradle build`
- De eerste keer duurt dit **5 tot 15 minuten**, omdat Gradle Minecraft, Fabric en GeckoLib downloadt. Je hebt internet nodig.
- Is het gelukt, dan zie je **BUILD SUCCESSFUL**.

## Stap 5: De .jar vinden
Open de map `gnome-hollow\build\libs`. Daar staan twee bestanden:
- `gnome-hollow-1.0.0.jar` is **de mod** en dit bestand heb je nodig.
- `gnome-hollow-1.0.0-sources.jar` negeer je.

## Stap 6: Gaat er iets mis?
Kopieer de **hele** foutmelding uit Command Prompt (selecteren, rechtermuisknop kopieert) en plak hem in de chat. Dan pas ik de code aan en krijg je een nieuwe zip. Compilefouten ("error: cannot find symbol" en dergelijke) zijn bij de eerste build te verwachten. Overige problemen:
- `'gradle' is not recognized`: je Command Prompt was al open toen je het PATH aanpaste, of het pad is verkeerd. Open een nieuw venster en controleer de map uit stap 2.
- Meldingen over Java-versie of "Unsupported class file": `java -version` zegt niet 25. Doe stap 1 opnieuw.
- `Could not resolve ...` of `Connection timed out`: geen internet, een VPN of firewall. Probeer het nog een keer.

## Stap 7: Installeren in Minecraft
1. Installeer **Fabric Loader** (0.19.3 of nieuwer) voor Minecraft **26.2** via https://fabricmc.net/use/installer/ (kies Minecraft 26.2, dan Installeren).
2. Zet deze drie bestanden in je mods-map (`Windows-toets + R`, typ `%appdata%\.minecraft\mods`, Enter):
   - `gnome-hollow-1.0.0.jar`
   - **Fabric API** voor 26.2 (https://modrinth.com/mod/fabric-api, versie 0.155.2 of nieuwer)
   - **GeckoLib 5.5.3** voor Fabric 26.2 (https://modrinth.com/mod/geckolib)
3. Start Minecraft met het Fabric-profiel. Maak een Creatief-wereld en typ `/locate structure gnomehollow:gnome_village`. Of gebruik de spawn eggs in de creative-tab "Spawn Eggs".

## Bouwen via GitHub (geen installatie nodig)
1. Maak een gratis account op https://github.com en een nieuwe, lege repository.
2. Zet de **inhoud** van de map `gnome-hollow` in de repository, zodat `build.gradle` en de mappen `src` en `.github` direct in de hoofdmap staan (dus niet nog een map `gnome-hollow` erbij).
   - **Via git of GitHub Desktop:** gewoon pushen. Weigert GitHub dat met een melding over `workflow` scope, dan mist je token die rechten. Gebruik dan GitHub Desktop of maak een token met de rechten `repo` en `workflow`.
   - **Via de website:** een versleepte map met een punt-map (`.github`) wordt soms overgeslagen. Maak daarom het bestand zelf aan: **Add file > Create new file**, typ als naam `.github/workflows/build.yml` (de schuine strepen maken de mappen vanzelf) en plak de inhoud van dat bestand uit de zip.
3. Open het tabblad **Actions**. De bouw start bij elke push, of klik op **build > Run workflow**.
4. Gelukt? Open de run en download onderaan onder **Artifacts** het bestand **gnome-hollow-jar**. Daarin zit de mod.
5. Mislukt? Open de run > klik op de rode stap (meestal "Mod bouwen") en kopieer de regels met `error:` naar de chat. Bij een fout toont de stap "Diagnose - GeckoLib-klassen" ook welke klassen GeckoLib bevat.

Mac of Linux? Installeer Java 25 en Gradle 9.5.1 (bijvoorbeeld met SDKMAN: `sdk install java` en `sdk install gradle 9.5.1`), en voer daarna in de projectmap `gradle build` uit. De jar staat dan in `build/libs/`.

---

## B. Waar vind je alles in het spel?
- **Dorp:** `/locate structure gnomehollow:gnome_village`. Genereert in Dark Forest, Taiga, Old Growth Pine Taiga en Old Growth Spruce Taiga (ongeveer elke 28 chunks).
- **Gnomes:** creative-tab *Spawn Eggs* (Healer, Warrior, Farmer, Fisherman, Builder, Nitwit).
- **Blokken:** creative-tab *Building Blocks*: Toadstool Lamp, Gnome Shingles, trap en plaat (ook craftbaar).

## C. Het dorp
- **Indeling:** elk dorp begint bij een van drie pleinen (toadstool-put, kampvuur met podium, vijver met standbeeld). Rondom het plein staan 8 huizen, waaronder altijd **een Healer-, Warrior-, Farmer-, Fisherman- en Builder-huis**. Vanuit het midden van elke plein-zijde lopen straten die zich aan het terrein aanpassen, met bochten, T-splitsingen, kruispunten en doodlopende einden. Langs de straten staan willekeurige huizen en decor, dus geen twee dorpen zijn gelijk.
- **Huizen:** cottages met rieten, rode-shingle of paddenstoelhoed-daken, vakwerk, schoorstenen, veranda's, een huis met twee verdiepingen, heuvelhuizen (hobbit-stijl met boogvormige deur), paddenstoelhuizen, een wachttoren, een bouwplaats, boerderijen met akkers, een viskot met vijver en steiger, en meer. Elk beroepshuis heeft twee varianten.
- **Decor:** marktkraam, moestuin, kampvuur met stronken, standbeeldje, bijenkorven, vijvertje met bankje, hooibergen, paddenstoelcirkel.
- **Loot:** kisten en vaten bevatten buit per beroep (drankjes, pijlen, gewassen, vis, bouwmaterialen, enz.).

## D. Gedrag
- Altijd neutraal. Overdag werken ze, 's nachts gaan ze naar huis (Warriors blijven op wacht).
- **Handelen:** rechtsklik op een gnome opent het handelsvenster (zoals bij dorpelingen). Elk beroep heeft eigen ruilhandel; de Builder verkoopt de nieuwe bouwblokken.
- **Warrior:** valt hostile mobs aan en slaat terug als er een gnome wordt geraakt (alarmeert de rest).
- **Healer:** brouwt bij de brewing stand, legt soms een drankje in een kist, en geneest gewonde spelers, dorpelingen, gnomes en golems binnen 6 blokken.
- **Fisherman:** zoekt open water, vist, en stopt de vangst in een barrel in de buurt.
- **Farmer:** oogst volgroeide gewassen en plant direct opnieuw.
- **Builder:** timmert lantaarnpaaltjes rond het dorp (max. 8 per gnome).
- **Muziek:** een Nitwit begint een liedje (vier korte volksliedjes). Gnomes die toevallig niets te doen hebben komen erbij zitten en spelen een eigen stem (fluit, luit, bas, ritme). Zodra een gnome zijn eigen werk heeft, gaat dat voor.
- **Uiterlijk:** elk beroep heeft een herkenbare hoed en kleding (Healer wit met groene puntmuts, Warrior harnas met helm en rode pluim, Farmer strohoed en overall, Fisherman geel regenpak, Builder oranje vest met helm, Nitwit paarse slaphoed met bel).

## D2. Nieuwe blokken
Toadstool Lamp, Gnome Shingles, Thatch (riet), Toadstool Cap (paddenstoelhoed), Plaster (pleisterwerk), Timber Plaster (vakwerk), Gnome Mushroom Stem en Fieldstone (veldkeien). De meeste hebben trap en plaat, en zijn craftbaar of bij de Builder te ruilen (creative-tab *Building Blocks*).

## E. Bekende risico's (hier zitten waarschijnlijk de eerste compilefouten)
Ik had geen internet in mijn werkomgeving, dus niets is gecompileerd. Plekken waar Minecraft 26.2 of GeckoLib 5 mogelijk anders zijn dan ik aannam:
- Geluiden: `SoundEvent.createVariableRangeEvent`, en de overrides `playStepSound`, `setTarget` en `mobInteract` in `GnomeEntity`.
- `Identifier` (voorheen `ResourceLocation`), `Level#isBrightOutside()`, `Item.Properties#spawnEgg(..)`, `SoundEvents.NOTE_BLOCK_*.value()`, `HurtByTargetGoal#setAlertOthers()`.
- GeckoLib 5: `new AnimationController<>(naam, overgangsticks, handler)` (zonder `this`), `triggerableAnim`, `stopTriggeredAnimation("action", null)`, pad `geckolib/models/entity/`, en de generieke renderer in `GnomeRenderer`.
- Structuren: `DataVersion` staat op 4671 en `start_height` op -3. Staat het dorp een blok te hoog/laag, pas dan `start_height` aan in `data/gnomehollow/worldgen/structure/gnome_village.json`.
- Animatierichtingen (bijv. arm omhoog) kunnen gespiegeld zijn; aanpassen in `assets/gnomehollow/geckolib/animations/entity/`.
Plak de foutmeldingen terug in de chat, dan los ik ze op.

## F. Geluiden
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

## G. Opnieuw genereren
`tools/gen_assets.py` (texturen, modellen, animaties, taal, recepten) en `tools/gen_structs.py` (dorpsstructuren) maken alle assets/data opnieuw (pas de paden bovenin aan).
