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
- **Past bij het terrein:** geen platte vierkante platen meer. Het plein is een onregelmatige cirkel, de straten volgen de grond (zoals bij vanilla dorpen) en huizen krijgen een eigen fundering. Alleen waar iets staat wordt het terrein aangepast.
- **Dynamische grootte:** elk dorp heeft een eigen vorm en een eigen aantal huizen (ongeveer 2 tot 13, plus de gemeenschappelijke gebouwen). Welke beroepen er wonen is toeval; niet elk dorp heeft elk beroep.
- **Gemeenschappelijk:** een **plein met bel** (3 varianten: toadstool-put, kampvuur met podium, vijver met standbeeld), een **markt**, een **bibliotheek** en een **gemeenschappelijke tuin**. Die staan altijd in elk dorp.
- **Compacte huizen** (gnome-schaal, zoals de Ribbits: een leefhoekje, een slaapplek en opslag op een paar blokken): cottages met riet-, shingle- of paddenstoeldaken, vakwerk, een huisje met zolder, heuvelhuizen (hobbit-stijl), paddenstoelhuisjes, een wachttoren en beroepshuizen (Healer, Warrior, Farmer, Fisherman, Builder) met eigen werkplek, tuin of vijver. Grotere huizen hebben 2 bedden en 2 bewoners.
- **Decor:** paddenstoelcirkel, kampvuur met bankjes, standbeeldje, bijenkorven, vijvertje, hooibergen.
- **Verlichting:** spaarzaam (binnen een lamp, buiten een lantaarn bij de deur en enkele lampen op de straten en het plein), maar genoeg om vijandige mobs buiten het dorp te houden.
- **Geen conflicten:** gnome-dorpen genereren niet binnen 10 chunks van vanilla dorpen en staan minstens 18 chunks uit elkaar.
- **Loot:** kisten en vaten bevatten per beroep gevarieerde buit (willekeurige hoeveelheden, plus een kleine kans op iets zeldzaams).

## D. Gedrag
**Dagritme** (overdag werken, aan het eind van de middag vrije tijd, bij zonsondergang samenkomen, 's nachts slapen):
- **Werken:** elk beroep voert zijn eigen werk uit (zie onder). Werk gaat voor vrije tijd; bij gevaar gaat alles voor.
- **Vrije tijd:** zitten op bankjes of stoelen, kletsen met een vriend of buur, de markt, bibliotheek of tuin bezoeken, en thuis rusten. Elke gnome heeft een eigen favoriet (muziek, tuinieren, boeken, kletsen, markt, zitten).
- **Samenkomst:** na zonsondergang is er een gemeenschappelijke avond bij het plein (wisselend: gezellig samenzijn, muziekavond of feest), op ongeveer drie van de vier avonden.
- **Slapen:** 's nachts gaan ze naar huis en slapen in hun eigen bed (de animatie ligt plat). Wachters houden nachtwacht.
- **Onweer:** iedereen zoekt binnen beschutting; bij gewone regen alleen sommige gnomes.

**Gevaar:** gnomes zonder wapen vluchten naar huis en blijven daar tot het veilig is. Wachters (Warriors) patrouilleren dynamisch, onderbreken alles bij een bedreiging, komen anderen te hulp en blijven binnen de dorpsstraal. Daarna zoekt de Healer gewonde gnomes (wachters eerst) op en geneest ze.

**Beroepen:**
- **Healer:** brouwt, legt drankjes in kisten, geneest gnomes en spelers, en loopt na een gevecht gewonden af.
- **Fisherman:** vist bij open water en bergt de vangst op in de opslag.
- **Farmer:** oogst volgroeide gewassen, zaait opnieuw en brengt de oogst naar de opslag bij huis.
- **Builder:** haalt bouwmateriaal uit de opslag, herstelt ontbrekende lampen op lantaarnpalen en timmert kleine dingen bij (bankje, bloemen, paddenstoeltje; max. 10 per gnome).
- **Warrior:** patrouilleert, verdedigt en volgt vijanden nooit buiten de dorpsgrens.
- **Nitwit:** geen beroep, **handelt niet**, dwaalt rond, kletst, speelt muziek en doet mee aan alle sociale activiteiten.

**Sociaal:** gnomes die samen wonen of vaak kletsen worden vrienden (opgeslagen). Ze delen een huis als er bedden zijn. Ze kijken naar spelers, lopen nieuwsgierig op ze af en groeten een speler die ze kennen met een zwaai (geen reputatiesysteem).

**Muziek (zoals bij de Ribbits):** één liedje tegelijk per dorp. Meestal begint een Nitwit; gnomes die niets te doen hebben komen erbij staan, muzikanten pakken zichtbaar hun instrument (fluit, luit, bas of trom) en spelen het liedje helemaal af. Op muziek- en feestavonden doen ze dat gezamenlijk bij het plein.

**Handel:** rechtsklik opent het handelsvenster (alleen niet-Nitwits). Elke gnome heeft zijn eigen willekeurige selectie ruilaanbiedingen, geijkt op vanilla dorpelingen (grondstoffen voor emeralds, producten voor emeralds). De Builder verkoopt de nieuwe bouwblokken.

**Wat wordt opgeslagen:** thuis, dorp, vriend, favoriete bezigheid, instrument, handelsseed en bekende spelers staan in de entity-gegevens, dus blijven bewaard na opslaan, afsluiten en chunks laden/ontladen.

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

## H. Configuratie
Bij de eerste start maakt de mod `config/gnomehollow.json` aan. Daarin: `villageRadius`, `populationFactor` (kans dat een bij het genereren gespawnde gnome blijft), `ambientSoundIntervalTicks`, `musicEnabled`, `musicFrequency`, `musicSessionMinSeconds`/`MaxSeconds`, `communalEvents`, `shelterInStorms`, `guardsPatrol`, `friendships` en `randomTrades`.

**Dorpsgeneratie** (hoe vaak, hoe ver uit elkaar) pas je aan met een datapack dat `data/gnomehollow/worldgen/structure_set/gnome_villages.json` overschrijft: `spacing` en `separation` (in chunks), en `exclusion_zone` (afstand tot vanilla dorpen). De grootte van het dorp volgt uit de pools in `data/gnomehollow/worldgen/template_pool/village/` (aantal lege opties) en `size` en `max_distance_from_center` in `worldgen/structure/gnome_village.json`.

## I. Testen in het spel
- Dorp zoeken: `/locate structure gnomehollow:gnome_village` (in een nieuwe wereld, in Dark Forest of Taiga).
- Dagritme: `/time set 12500` (avond/samenkomst), `/time set 15000` (nacht), `/time set 1000` (ochtend), `/weather thunder` (schuilen).
- Dreiging: spawn een zombie in het dorp; wachters vallen aan, de rest vlucht naar huis, de Healer loopt daarna gewonde wachters af.
- Muziek: wacht overdag bij het plein; Nitwits beginnen soms een liedje, of gebruik de avond.
