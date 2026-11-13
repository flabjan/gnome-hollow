package dev.gnomehollow;

import dev.gnomehollow.entity.Profession;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.alchemy.PotionContents;
import net.minecraft.world.item.alchemy.Potions;
import net.minecraft.world.item.trading.ItemCost;
import net.minecraft.world.item.trading.MerchantOffer;
import net.minecraft.world.item.trading.MerchantOffers;
import net.minecraft.world.level.ItemLike;

/**
 * Ruilhandel per beroep, geijkt op vanilla dorpelingen (prijzen in emeralds: grondstoffen leveren ~1 emerald per
 * stapel op, producten kosten 1-8 emeralds). Elke gnome krijgt (met zijn eigen seed) een eigen selectie.
 */
public final class GnomeTrades {
	private record Cand(boolean buy, MerchantOffer offer) {}

	private GnomeTrades() {}

	private static int around(Random r, int base, int spread) {
		return Math.max(1, base + r.nextInt(spread * 2 + 1) - spread);
	}

	private static Cand buy(Random r, ItemLike item, int count, int spread, int uses) {
		int c = around(r, count, spread);
		return new Cand(true, new MerchantOffer(new ItemCost(item, c), new ItemStack(Items.EMERALD, 1), around(r, uses, 3), 2, 0.05F));
	}

	private static Cand sell(Random r, int emeralds, ItemStack result, int uses) {
		return new Cand(false, new MerchantOffer(new ItemCost(Items.EMERALD, emeralds), result, around(r, uses, 3), 3, 0.05F));
	}

	private static ItemStack st(ItemLike item, int count) {
		return new ItemStack(item, count);
	}

	private static List<Cand> candidates(Profession p, Random r) {
		List<Cand> c = new ArrayList<>();
		switch (p) {
			case FARMER -> {
				c.add(buy(r, Items.WHEAT, 20, 2, 16)); c.add(buy(r, Items.POTATO, 26, 2, 16)); c.add(buy(r, Items.CARROT, 22, 2, 16));
				c.add(buy(r, Items.BEETROOT, 15, 1, 16)); c.add(buy(r, Items.PUMPKIN, 6, 1, 12)); c.add(buy(r, Items.MELON, 4, 1, 12));
				c.add(sell(r, 1, st(Items.BREAD, around(r, 6, 1)), 16)); c.add(sell(r, 1, st(Items.PUMPKIN_PIE, 4), 12)); c.add(sell(r, 1, st(Items.APPLE, 4), 16));
				c.add(sell(r, 1, st(Items.COOKIE, around(r, 15, 3)), 16)); c.add(sell(r, 1, st(Items.CAKE, 1), 12)); c.add(sell(r, 3, st(Items.GOLDEN_CARROT, 3), 12));
			}
			case FISHERMAN -> {
				c.add(buy(r, Items.STRING, 20, 2, 16)); c.add(buy(r, Items.COAL, 10, 1, 16)); c.add(buy(r, Items.COD, 15, 2, 16));
				c.add(sell(r, 1, st(Items.COOKED_COD, 6), 16)); c.add(sell(r, 1, st(Items.COOKED_SALMON, 5), 16)); c.add(sell(r, 3, st(Items.FISHING_ROD, 1), 8));
				c.add(sell(r, 2, st(Items.CAMPFIRE, 1), 8)); c.add(sell(r, 6, st(Items.NAUTILUS_SHELL, 1), 3)); c.add(sell(r, 1, st(Items.LILY_PAD, 4), 12));
			}
			case HEALER -> {
				c.add(buy(r, Items.ROTTEN_FLESH, 32, 3, 16)); c.add(buy(r, Items.GOLD_INGOT, 3, 1, 12)); c.add(buy(r, Items.GLOW_BERRIES, 12, 2, 16));
				c.add(buy(r, Items.RED_MUSHROOM, 8, 1, 16));
				c.add(sell(r, 1, st(Items.REDSTONE, 2), 16)); c.add(sell(r, 1, st(Items.LAPIS_LAZULI, 1), 16));
				c.add(sell(r, 3, PotionContents.createItemStack(Items.POTION, Potions.HEALING), 8)); c.add(sell(r, 4, PotionContents.createItemStack(Items.POTION, Potions.REGENERATION), 6));
				c.add(sell(r, 3, PotionContents.createItemStack(Items.POTION, Potions.SWIFTNESS), 8)); c.add(sell(r, 4, st(Items.EXPERIENCE_BOTTLE, 1), 8));
				c.add(sell(r, 1, st(Items.GLASS_BOTTLE, 4), 16));
			}
			case WARRIOR -> {
				c.add(buy(r, Items.COAL, 15, 2, 16)); c.add(buy(r, Items.IRON_INGOT, 4, 1, 12)); c.add(buy(r, Items.FLINT, 24, 2, 12)); c.add(buy(r, Items.BONE, 12, 2, 12));
				c.add(sell(r, 1, st(Items.ARROW, 16), 16)); c.add(sell(r, 2, st(Items.BOW, 1), 8)); c.add(sell(r, 5, st(Items.SHIELD, 1), 6));
				c.add(sell(r, 7, st(Items.IRON_SWORD, 1), 6)); c.add(sell(r, 5, st(Items.IRON_HELMET, 1), 6)); c.add(sell(r, 8, st(Items.IRON_CHESTPLATE, 1), 4));
			}
			case BUILDER -> {
				c.add(buy(r, Items.CLAY_BALL, 10, 1, 16)); c.add(buy(r, Items.COBBLESTONE, 30, 4, 16)); c.add(buy(r, Items.STONE, 20, 2, 16));
				c.add(sell(r, 1, st(Items.BRICK, 10), 16));
				c.add(sell(r, 1, st(ModBlocks.THATCH, 8), 16)); c.add(sell(r, 1, st(ModBlocks.PLASTER, 6), 16)); c.add(sell(r, 1, st(ModBlocks.FIELDSTONE, 4), 16));
				c.add(sell(r, 1, st(ModBlocks.GNOME_SHINGLES, 4), 16)); c.add(sell(r, 1, st(ModBlocks.TOADSTOOL_CAP, 6), 12)); c.add(sell(r, 1, st(ModBlocks.TOADSTOOL_LAMP, 1), 12));
				c.add(sell(r, 1, st(ModBlocks.TIMBER_PLASTER, 4), 12)); c.add(sell(r, 2, st(Items.LANTERN, 1), 8));
			}
			case NITWIT -> { }   // nitwits handelen niet
		}
		return c;
	}

	public static void fill(MerchantOffers offers, Profession p, int seed) {
		Random r = new Random((long) seed * 31L + p.ordinal());
		List<Cand> all = candidates(p, r);
		if (all.isEmpty()) return;
		Collections.shuffle(all, r);
		int n = GnomeConfig.get().randomTrades ? 4 + r.nextInt(3) : all.size();
		List<Cand> chosen = new ArrayList<>(all.subList(0, Math.min(n, all.size())));
		boolean hasBuy = chosen.stream().anyMatch(Cand::buy);
		boolean hasSell = chosen.stream().anyMatch(x -> !x.buy());
		if (!hasBuy) all.stream().filter(Cand::buy).findFirst().ifPresent(x -> chosen.set(chosen.size() - 1, x));
		if (!hasSell) all.stream().filter(x -> !x.buy()).findFirst().ifPresent(x -> chosen.set(0, x));
		for (Cand c : chosen) offers.add(c.offer());
	}
}
