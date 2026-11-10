package dev.gnomehollow.goal;

import java.util.Optional;
import java.util.function.Predicate;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.world.Container;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.state.BlockState;

public final class GnomeUtil {
	private GnomeUtil() {}

	/** Zoekt het dichtstbijzijnde blok rond center dat aan de voorwaarde voldoet. */
	public static Optional<BlockPos> findNearest(Level level, BlockPos center, int rxz, int ry, Predicate<BlockState> test) {
		BlockPos best = null;
		double bestDist = Double.MAX_VALUE;
		BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
		for (int dx = -rxz; dx <= rxz; dx++) {
			for (int dz = -rxz; dz <= rxz; dz++) {
				for (int dy = -ry; dy <= ry; dy++) {
					m.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
					if (test.test(level.getBlockState(m))) {
						double d = center.distSqr(m);
						if (d < bestDist) {
							bestDist = d;
							best = m.immutable();
						}
					}
				}
			}
		}
		return Optional.ofNullable(best);
	}

	public static boolean isStandable(Level level, BlockPos p) {
		return level.getBlockState(p).getCollisionShape(level, p).isEmpty()
				&& level.getBlockState(p.above()).getCollisionShape(level, p.above()).isEmpty()
				&& level.getBlockState(p.below()).isFaceSturdy(level, p.below(), Direction.UP);
	}

	/** Zoekt een plek om te staan in de buurt van een doelblok (afstand 1 t/m 3). */
	public static Optional<BlockPos> findStandNear(Level level, BlockPos target) {
		for (int r = 1; r <= 3; r++) {
			for (int dx = -r; dx <= r; dx++) {
				for (int dz = -r; dz <= r; dz++) {
					if (Math.max(Math.abs(dx), Math.abs(dz)) != r) continue;
					for (int dy = -1; dy <= 1; dy++) {
						BlockPos p = target.offset(dx, dy, dz);
						if (isStandable(level, p)) return Optional.of(p);
					}
				}
			}
		}
		return Optional.empty();
	}

	/** Stopt een item in de dichtstbijzijnde kist/vat. Geeft true als het gelukt is. */
	public static boolean insertIntoNearbyContainer(Level level, BlockPos center, int radius, ItemStack stack) {
		BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
		Container best = null;
		double bestDist = Double.MAX_VALUE;
		for (int dx = -radius; dx <= radius; dx++) {
			for (int dz = -radius; dz <= radius; dz++) {
				for (int dy = -3; dy <= 3; dy++) {
					m.set(center.getX() + dx, center.getY() + dy, center.getZ() + dz);
					if (level.getBlockEntity(m) instanceof Container c && center.distSqr(m) < bestDist && hasRoom(c, stack)) {
						bestDist = center.distSqr(m);
						best = c;
					}
				}
			}
		}
		if (best == null) return false;
		for (int i = 0; i < best.getContainerSize(); i++) {
			ItemStack slot = best.getItem(i);
			if (slot.isEmpty()) {
				best.setItem(i, stack.copy());
				best.setChanged();
				return true;
			}
			if (ItemStack.isSameItemSameComponents(slot, stack) && slot.getCount() + stack.getCount() <= slot.getMaxStackSize()) {
				slot.grow(stack.getCount());
				best.setChanged();
				return true;
			}
		}
		return false;
	}

	private static boolean hasRoom(Container c, ItemStack stack) {
		for (int i = 0; i < c.getContainerSize(); i++) {
			ItemStack slot = c.getItem(i);
			if (slot.isEmpty()) return true;
			if (ItemStack.isSameItemSameComponents(slot, stack) && slot.getCount() + stack.getCount() <= slot.getMaxStackSize()) return true;
		}
		return false;
	}
}
