package dev.gnomehollow;

import dev.gnomehollow.entity.Profession;
import net.fabricmc.fabric.api.creativetab.v1.CreativeModeTabEvents;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;

public final class ModItems {
	private ModItems() {}

	public static void init() {
		for (Profession p : Profession.values()) {
			ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, GnomeHollow.id(p.entityName() + "_spawn_egg"));
			Item egg = new Item(new Item.Properties().setId(key).spawnEgg(ModEntities.TYPES.get(p)));
			Registry.register(BuiltInRegistries.ITEM, key, egg);
			CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.SPAWN_EGGS).register(output -> output.accept(egg));
		}
		CreativeModeTabEvents.modifyOutputEvent(CreativeModeTabs.BUILDING_BLOCKS).register(e -> {
			for (var block : ModBlocks.ALL) {
				e.accept(block);
			}
		});
	}
}
