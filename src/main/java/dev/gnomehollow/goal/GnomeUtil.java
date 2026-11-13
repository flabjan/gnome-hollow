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
	/** Zet de gnome op een zitplek (trap) en start de zit-animatie. Kijkt weg van de leuning. */
	public static void sitAt(dev.gnomehollow.entity.GnomeEntity g, Level level, BlockPos seat, BlockPos lookAt) {
		BlockState st = level.getBlockState(seat);
		float yaw = g.getYRot();
		if (st.hasProperty(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING)) {
			yaw = st.getValue(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING).getOpposite().toYRot();
		} else if (lookAt != null) {
			yaw = (float) (Math.toDegrees(Math.atan2(-(lookAt.getX() - seat.getX()), lookAt.getZ() - seat.getZ())));
		}
		g.getNavigation().stop();
		g.setPos(seat.getX() + 0.5, seat.getY() + 0.5, seat.getZ() + 0.5);
		g.setDeltaMovement(0, 0, 0);
		g.setYRot(yaw);
		g.setYBodyRot(yaw);
		g.setYHeadRot(yaw);
		g.startAnim("sit");
	}

	/** Zet de gnome in een bed (hoofdeinde = bed) en start de slaap-animatie. */
	public static void sleepAt(dev.gnomehollow.entity.GnomeEntity g, Level level, BlockPos head) {
		BlockState st = level.getBlockState(head);
		net.minecraft.core.Direction f = st.hasProperty(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING)
				? st.getValue(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING) : net.minecraft.core.Direction.SOUTH;
		float yaw = f.getOpposite().toYRot();
		g.getNavigation().stop();
		g.setPos(head.getX() + 0.5 - f.getStepX() * 0.5, head.getY() + 0.5625, head.getZ() + 0.5 - f.getStepZ() * 0.5);
		g.setDeltaMovement(0, 0, 0);
		g.setYRot(yaw);
		g.setYBodyRot(yaw);
		g.setYHeadRot(yaw);
		g.startAnim("sleep");
	}

	/** Zoekt een vrij bed (hoofdeinde) in de buurt van het huis van de gnome en claimt het. */
	public static BlockPos findFreeBed(net.minecraft.server.level.ServerLevel level, dev.gnomehollow.entity.GnomeEntity g) {
		BlockPos home = g.home();
		java.util.List<BlockPos> beds = new java.util.ArrayList<>();
		BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
		for (int dx = -6; dx <= 6; dx++) {
			for (int dz = -6; dz <= 6; dz++) {
				for (int dy = -2; dy <= 3; dy++) {
					m.set(home.getX() + dx, home.getY() + dy, home.getZ() + dz);
					if (!level.hasChunkAt(m)) continue;
					BlockState st = level.getBlockState(m);
					if (st.is(net.minecraft.tags.BlockTags.BEDS) && st.hasProperty(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING)) {
						net.minecraft.core.Direction f = st.getValue(net.minecraft.world.level.block.HorizontalDirectionalBlock.FACING);
						if (!level.getBlockState(m.relative(f)).is(net.minecraft.tags.BlockTags.BEDS)) beds.add(m.immutable());
					}
				}
			}
		}
		beds.sort(java.util.Comparator.comparingDouble(b -> b.distSqr(home)));
		for (BlockPos b : beds) {
			if (dev.gnomehollow.village.Claims.claim(level, b, g.getId())) return b;
		}
		return null;
	}

	private GnomeUtil() {}

	/** Dorpelingen en ijzergolems tellen mee als vriendelijk voor de Healer (via registry-naam, versie-onafhankelijk). */
	public static boolean isFriendlyType(net.minecraft.world.entity.LivingEntity e) {
		String path = net.minecraft.core.registries.BuiltInRegistries.ENTITY_TYPE.getKey(e.getType()).getPath();
		return path.equals("villager") || path.equals("iron_golem");
	}

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

	/** Plek op een cirkel rond center (index bepaalt de hoek), op begaanbare grond. */
	public static BlockPos ring(Level level, BlockPos center, int index, double radius) {
		double a = Math.toRadians(index * 67.0 + 20.0);
		BlockPos base = center.offset((int) Math.round(Math.cos(a) * radius), 0, (int) Math.round(Math.sin(a) * radius));
		for (int dy : new int[] {0, 1, -1, 2, -2}) {
			BlockPos p = base.above(dy);
			if (isStandable(level, p)) return p;
		}
		return findStandNear(level, base).orElse(center);
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
