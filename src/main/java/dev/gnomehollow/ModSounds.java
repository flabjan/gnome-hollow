package dev.gnomehollow;

import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.sounds.SoundEvent;

/** Alle gnome-stemgeluiden. Bestanden: assets/gnomehollow/sounds/entity/gnome/*.ogg, events in sounds.json. */
public final class ModSounds {
	public static SoundEvent AMBIENT, GREET, YES, NO, HURT, DEATH, ATTACK, ALERT, LAUGH, CELEBRATE, FISH_CATCH,
			WORK_BREW, WORK_FARM, WORK_BUILD, WORK_FISH, HEAL, SNORE, STEP,
			MUSIC_WHISTLE, MUSIC_FIDDLE, MUSIC_LUTE, MUSIC_BASS, MUSIC_DRUM, MUSIC_TAP;

	private ModSounds() {}

	private static SoundEvent register(String name) {
		Identifier id = GnomeHollow.id("entity.gnome." + name);
		return Registry.register(BuiltInRegistries.SOUND_EVENT, id, SoundEvent.createVariableRangeEvent(id));
	}

	public static void init() {
		AMBIENT = register("ambient");
		GREET = register("greet");
		YES = register("yes");
		NO = register("no");
		HURT = register("hurt");
		DEATH = register("death");
		ATTACK = register("attack");
		ALERT = register("alert");
		LAUGH = register("laugh");
		CELEBRATE = register("celebrate");
		FISH_CATCH = register("fish_catch");
		WORK_BREW = register("work_brew");
		WORK_FARM = register("work_farm");
		WORK_BUILD = register("work_build");
		WORK_FISH = register("work_fish");
		HEAL = register("heal");
		SNORE = register("snore");
		STEP = register("step");
		MUSIC_WHISTLE = register("music_whistle");
		MUSIC_FIDDLE = register("music_fiddle");
		MUSIC_LUTE = register("music_lute");
		MUSIC_BASS = register("music_bass");
		MUSIC_DRUM = register("music_drum");
		MUSIC_TAP = register("music_tap");
	}
}
