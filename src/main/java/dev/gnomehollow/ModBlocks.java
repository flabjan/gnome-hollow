package dev.gnomehollow;

import java.util.function.Function;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;

public final class ModBlocks {
	public static Block TOADSTOOL_LAMP;
	public static Block GNOME_SHINGLES;
	public static Block GNOME_SHINGLE_STAIRS;
	public static Block GNOME_SHINGLE_SLAB;

	private ModBlocks() {}

	private static Block register(String name, Function<BlockBehaviour.Properties, Block> factory, BlockBehaviour.Properties props) {
		ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, GnomeHollow.id(name));
		Block block = factory.apply(props.setId(key));
		Registry.register(BuiltInRegistries.BLOCK, key, block);
		ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, GnomeHollow.id(name));
		Registry.register(BuiltInRegistries.ITEM, itemKey,
				new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
		return block;
	}

	public static void init() {
		TOADSTOOL_LAMP = register("toadstool_lamp", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(0.4f)
						.sound(SoundType.WOOD).lightLevel(state -> 13));
		GNOME_SHINGLES = register("gnome_shingles", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(1.5f, 6.0f)
						.sound(SoundType.STONE).requiresCorrectToolForDrops());
		GNOME_SHINGLE_STAIRS = register("gnome_shingle_stairs",
				props -> new StairBlock(GNOME_SHINGLES.defaultBlockState(), props),
				BlockBehaviour.Properties.ofFullCopy(GNOME_SHINGLES));
		GNOME_SHINGLE_SLAB = register("gnome_shingle_slab", SlabBlock::new,
				BlockBehaviour.Properties.ofFullCopy(GNOME_SHINGLES));
	}
}
