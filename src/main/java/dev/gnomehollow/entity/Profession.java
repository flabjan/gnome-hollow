package dev.gnomehollow.entity;

import dev.gnomehollow.ModEntities;
import net.minecraft.world.entity.EntityType;

public enum Profession {
	HEALER("healer", 0x3FA34D, 0xF2F2F2),
	WARRIOR("warrior", 0x8A8D93, 0xB3261E),
	FARMER("farmer", 0xE0B84A, 0x6B8E23),
	FISHERMAN("fisherman", 0x2F6FBF, 0xE8E8E8),
	BUILDER("builder", 0xE07B20, 0x8B5A2B),
	NITWIT("nitwit", 0x7B3FA0, 0xF0D060);

	public final String id;
	public final int eggPrimary;
	public final int eggSecondary;

	Profession(String id, int eggPrimary, int eggSecondary) {
		this.id = id;
		this.eggPrimary = eggPrimary;
		this.eggSecondary = eggSecondary;
	}

	public String entityName() {
		return "gnome_" + id;
	}

	public static Profession fromType(EntityType<?> type) {
		for (var e : ModEntities.TYPES.entrySet()) {
			if (e.getValue() == type) return e.getKey();
		}
		return NITWIT;
	}
}
