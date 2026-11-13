package dev.gnomehollow;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.nio.file.Files;
import java.nio.file.Path;
import net.fabricmc.loader.api.FabricLoader;

/**
 * Instellingen in config/gnomehollow.json (wordt bij de eerste start aangemaakt).
 * Dorpsgeneratie (hoe vaak/ver uit elkaar) stel je in met een datapack-override van
 * data/gnomehollow/worldgen/structure_set/gnome_villages.json, zie README.
 */
public final class GnomeConfig {
	/** Straal (blokken) rond het dorpscentrum waarbinnen gnomes blijven. */
	public int villageRadius = 44;
	/** Kans (0..1) dat een bij het genereren van een dorp gespawnde gnome blijft bestaan. */
	public double populationFactor = 1.0;
	/** Minimale tijd (ticks) tussen brabbelgeluiden per gnome. */
	public int ambientSoundIntervalTicks = 1800;
	public boolean musicEnabled = true;
	/** 1.0 = normaal, 0.5 = half zo vaak spontaan muziek, 0 = nooit spontaan. */
	public double musicFrequency = 1.0;
	public int musicSessionMinSeconds = 100;
	public int musicSessionMaxSeconds = 150;
	/** Gemeenschappelijke avonden (samenkomst, muziekavond, feest). */
	public boolean communalEvents = true;
	public boolean shelterInStorms = true;
	public boolean guardsPatrol = true;
	public boolean friendships = true;
	/** Elke gnome krijgt een eigen willekeurige selectie ruilaanbiedingen. */
	public boolean randomTrades = true;

	private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
	private static GnomeConfig instance = new GnomeConfig();

	public static GnomeConfig get() {
		return instance;
	}

	public static void load() {
		Path path = FabricLoader.getInstance().getConfigDir().resolve("gnomehollow.json");
		try {
			if (Files.exists(path)) {
				GnomeConfig read = GSON.fromJson(Files.readString(path), GnomeConfig.class);
				if (read != null) instance = read;
			}
			Files.writeString(path, GSON.toJson(instance));
		} catch (Exception e) {
			System.err.println("[gnomehollow] Kon de configuratie niet lezen/schrijven: " + e);
		}
	}
}
