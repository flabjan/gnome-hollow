package dev.gnomehollow;

import net.fabricmc.api.ModInitializer;
import net.minecraft.resources.Identifier;

public final class GnomeHollow implements ModInitializer {
	public static final String MOD_ID = "gnomehollow";

	public static Identifier id(String path) {
		return Identifier.fromNamespaceAndPath(MOD_ID, path);
	}

	@Override
	public void onInitialize() {
		ModSounds.init();
		ModBlocks.init();
		ModEntities.init();
		ModItems.init();
	}
}
