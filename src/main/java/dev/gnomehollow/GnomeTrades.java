package dev.gnomehollow;

import dev.gnomehollow.entity.Profession;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.ItemLike;

/** Ruilhandel per beroep. Meestal emeralds, maar ook gewoon grondstoffen tegen emeralds. */
public final class GnomeTrades {
	private GnomeTrades() {}

	private static void sell(MerchantOffers o, int emeralds, ItemStack result, int maxUses, int xp) {
		o.add(new MerchantOffer(new ItemCost(Items.EMERALD, emeralds), result, maxUses, xp, 0.05F));
	}

	private static void buy(MerchantOffers o, ItemLike item, int count, int emeralds, int maxUses, int xp) {
		o.add(new MerchantOffer(new ItemCost(item, count), new ItemStack(Items.EMERALD, emeralds), maxUses, xp, 0.05F));
	}

	private static ItemStack stack(ItemLike item, int count) {
		return new ItemStack(item, count);
	}

	public static void fill(MerchantOffers o, Profession p) {
		switch (p) {
			case HEALER -> {
				buy(o, Items.RED_MUSHROOM, 8, 1, 16, 2);
				buy(o, Items.GLOW_BERRIES, 10, 1, 12, 2);
				sell(o, 2, PotionContents.createItemStack(Items.POTION, Potions.HEALING), 8, 5);
				sell(o, 2, PotionContents.createItemStack(Items.POTION, Potions.REGENERATION), 8, 5);
				sell(o, 1, stack(Items.GLASS_BOTTLE, 4), 12, 1);
				sell(o, 6, stack(Items.GOLDEN_APPLE, 1), 3, 10);
			}
			case WARRIOR -> {
				buy(o, Items.IRON_INGOT, 4, 1, 16, 2);
				buy(o, Items.BONE, 12, 1, 12, 2);
				sell(o, 1, stack(Items.ARROW, 12), 12, 1);
				sell(o, 4, stack(Items.SHIELD, 1), 4, 5);
				sell(o, 6, stack(Items.IRON_SWORD, 1), 4, 8);
				sell(o, 8, stack(Items.IRON_CHESTPLATE, 1), 3, 10);
			}
			case FARMER -> {
				buy(o, Items.WHEAT, 20, 1, 16, 2);
				buy(o, Items.CARROT, 16, 1, 16, 2);
				buy(o, Items.POTATO, 16, 1, 16, 2);
				sell(o, 1, stack(Items.BREAD, 5), 12, 1);
				sell(o, 1, stack(Items.PUMPKIN_PIE, 3), 12, 1);
				sell(o, 3, stack(Items.CAKE, 1), 4, 5);
			}
			case FISHERMAN -> {
				buy(o, Items.STRING, 16, 1, 16, 2);
				buy(o, Items.COD, 14, 1, 16, 2);
				sell(o, 1, stack(Items.COOKED_COD, 6), 12, 1);
				sell(o, 1, stack(Items.COOKED_SALMON, 5), 12, 1);
				sell(o, 3, stack(Items.FISHING_ROD, 1), 4, 5);
				sell(o, 4, stack(Items.NAUTILUS_SHELL, 1), 2, 10);
			}
			case BUILDER -> {
				buy(o, Items.COBBLESTONE, 30, 1, 16, 2);
				buy(o, Items.CLAY_BALL, 20, 1, 16, 2);
				sell(o, 1, stack(ModBlocks.THATCH, 8), 12, 1);
				sell(o, 1, stack(ModBlocks.PLASTER, 8), 12, 1);
				sell(o, 2, stack(ModBlocks.GNOME_SHINGLES, 8), 12, 2);
				sell(o, 2, stack(ModBlocks.FIELDSTONE, 8), 12, 2);
				sell(o, 1, stack(ModBlocks.TOADSTOOL_LAMP, 2), 12, 2);
			}
			case NITWIT -> {
				buy(o, Items.POPPY, 8, 1, 16, 2);
				buy(o, Items.DANDELION, 8, 1, 16, 2);
				sell(o, 1, stack(Items.COOKIE, 8), 12, 1);
				sell(o, 2, stack(Items.FIREWORK_ROCKET, 3), 8, 2);
				sell(o, 2, stack(ModBlocks.TIMBER_PLASTER, 4), 8, 2);
				sell(o, 3, stack(Items.NOTE_BLOCK, 1), 4, 3);
			}
		}
	}
}
