package dev.gnomehollow;

import java.util.ArrayList;
import java.util.List;
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
	/** Alle blokken in volgorde van registratie (gebruikt voor de creative-tab). */
	public static final List<Block> ALL = new ArrayList<>();

	public static Block TOADSTOOL_LAMP;
	public static Block GNOME_SHINGLES, GNOME_SHINGLE_STAIRS, GNOME_SHINGLE_SLAB;
	public static Block THATCH, THATCH_STAIRS, THATCH_SLAB;
	public static Block TOADSTOOL_CAP, TOADSTOOL_CAP_STAIRS, TOADSTOOL_CAP_SLAB;
	public static Block PLASTER, PLASTER_STAIRS, PLASTER_SLAB;
	public static Block TIMBER_PLASTER;
	public static Block GNOME_STEM;
	public static Block FIELDSTONE, FIELDSTONE_STAIRS, FIELDSTONE_SLAB;

	private ModBlocks() {}

	private static Block register(String name, Function<BlockBehaviour.Properties, Block> factory, BlockBehaviour.Properties props) {
		ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, GnomeHollow.id(name));
		Block block = factory.apply(props.setId(key));
		Registry.register(BuiltInRegistries.BLOCK, key, block);
		ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, GnomeHollow.id(name));
		Registry.register(BuiltInRegistries.ITEM, itemKey,
				new BlockItem(block, new Item.Properties().setId(itemKey).useBlockDescriptionPrefix()));
		ALL.add(block);
		return block;
	}

	private static Block stairs(String name, Block base) {
		return register(name, props -> new StairBlock(base.defaultBlockState(), props), BlockBehaviour.Properties.ofFullCopy(base));
	}

	private static Block slab(String name, Block base) {
		return register(name, SlabBlock::new, BlockBehaviour.Properties.ofFullCopy(base));
	}

	public static void init() {
		TOADSTOOL_LAMP = register("toadstool_lamp", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(0.4f)
						.sound(SoundType.WOOD).lightLevel(state -> 13));

		GNOME_SHINGLES = register("gnome_shingles", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(1.5f, 6.0f)
						.sound(SoundType.STONE).requiresCorrectToolForDrops());
		GNOME_SHINGLE_STAIRS = stairs("gnome_shingle_stairs", GNOME_SHINGLES);
		GNOME_SHINGLE_SLAB = slab("gnome_shingle_slab", GNOME_SHINGLES);

		THATCH = register("thatch", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_YELLOW).strength(0.5f).sound(SoundType.GRASS));
		THATCH_STAIRS = stairs("thatch_stairs", THATCH);
		THATCH_SLAB = slab("thatch_slab", THATCH);

		TOADSTOOL_CAP = register("toadstool_cap", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.COLOR_RED).strength(0.4f).sound(SoundType.WOOD));
		TOADSTOOL_CAP_STAIRS = stairs("toadstool_cap_stairs", TOADSTOOL_CAP);
		TOADSTOOL_CAP_SLAB = slab("toadstool_cap_slab", TOADSTOOL_CAP);

		PLASTER = register("plaster", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_WHITE).strength(0.8f, 3.0f)
						.sound(SoundType.STONE).requiresCorrectToolForDrops());
		PLASTER_STAIRS = stairs("plaster_stairs", PLASTER);
		PLASTER_SLAB = slab("plaster_slab", PLASTER);

		TIMBER_PLASTER = register("timber_plaster", Block::new,
				BlockBehaviour.Properties.ofFullCopy(PLASTER));

		GNOME_STEM = register("gnome_stem", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.TERRACOTTA_WHITE).strength(0.5f).sound(SoundType.WOOD));

		FIELDSTONE = register("fieldstone", Block::new,
				BlockBehaviour.Properties.of().mapColor(MapColor.STONE).strength(1.8f, 6.0f)
						.sound(SoundType.STONE).requiresCorrectToolForDrops());
		FIELDSTONE_STAIRS = stairs("fieldstone_stairs", FIELDSTONE);
		FIELDSTONE_SLAB = slab("fieldstone_slab", FIELDSTONE);
	}
}
